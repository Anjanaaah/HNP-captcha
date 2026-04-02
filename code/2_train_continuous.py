import sys
import os
import json
import torch
from torch.utils.data import Dataset
from transformers import (
    Qwen2VLForConditionalGeneration,
    AutoProcessor,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
from qwen_vl_utils import process_vision_info

# --- CONFIGURATION ---
MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"
SAVE_DIR = "./my_captcha_model" 

# --- 1. WHICH CHUNK ARE WE TRAINING? ---
if len(sys.argv) < 2:
    print("ERROR: Please specify the chunk number!")
    print("Example: python 2_train_continuous.py 1")
    sys.exit(1)

CHUNK_NUM = sys.argv[1]
TRAIN_FILE = f"C:/Users/Asus/OneDrive/Documents/Anjan_proj/dataset_chunks/train_part_{CHUNK_NUM}.json"

if not os.path.exists(TRAIN_FILE):
    print(f"❌ Error: File not found: {TRAIN_FILE}")
    sys.exit(1)

print(f"\n=== STARTING TRAINING ON CHUNK {CHUNK_NUM} ===")

# --- 2. CUSTOM DATASET CLASS (The Fix) ---
# This bypasses Hugging Face's caching and column formatting issues
class CaptchaDataset(Dataset):
    def __init__(self, json_file):
        print(f"Loading {json_file}...")
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        print(f"Loaded {len(self.data)} items.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# Instantiate the dataset directly
dataset = CaptchaDataset(TRAIN_FILE)

# --- 3. SETUP MODEL ---
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

print("Loading Base Model...")
model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_ID, quantization_config=bnb_config, device_map="auto"
)
processor = AutoProcessor.from_pretrained(MODEL_ID, min_pixels=256*28*28, max_pixels=512*28*28)

model = prepare_model_for_kbit_training(model)

# CHECK: Resume or Start New?
adapter_config_path = os.path.join(SAVE_DIR, "adapter_config.json")
if os.path.exists(adapter_config_path):
    print(f"✅ FOUND PREVIOUS MODEL in {SAVE_DIR}. Resuming...")
    model = PeftModel.from_pretrained(model, SAVE_DIR, is_trainable=True)
else:
    print("⚠️ NO PREVIOUS MODEL. Starting from scratch...")
    peft_config = LoraConfig(
        r=64, lora_alpha=128, 
        target_modules=["q_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM", bias="none"
    )
    model = get_peft_model(model, peft_config)

model.print_trainable_parameters()


# --- 4. ROBUST DATA COLLATOR (The Safety Net) ---
def collate_fn(batch):
    # Filter out bad items on the fly
    valid_messages = []
    
    for i, item in enumerate(batch):
        try:
            # Check structure
            msg = item.get("messages", [])
            if not msg: continue
            
            content = msg[0].get("content", [])
            if not content: continue
            
            # Check Image Path
            img_path = content[0].get("image")
            if img_path is None:
                print(f"⚠️ SKIPPING BAD ITEM: Image is None")
                continue
                
            # If valid, keep it
            valid_messages.append(msg)
            
        except Exception as e:
            print(f"⚠️ SKIPPING ERROR ITEM: {e}")
            continue

    if not valid_messages:
        # Return empty dummy batch if everything failed (rare)
        return {"input_ids": torch.tensor([])}

    # Process normally
    texts = [processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=False) for msg in valid_messages]
    
    # WRAP IN TRY-EXCEPT TO CATCH THE EXACT ERROR
    try:
        image_inputs, video_inputs = process_vision_info(valid_messages)
        
        inputs = processor(
            text=texts, images=image_inputs, videos=video_inputs,
            padding=True, return_tensors="pt"
        )
        inputs["labels"] = inputs["input_ids"].clone()
        return inputs
        
    except Exception as e:
        print(f"❌ CRASH IN PROCESS_VISION_INFO: {e}")
        # Print the first bad message to debug
        print(f"Bad Message Sample: {valid_messages[0]}")
        raise e

# --- 5. TRAIN ---
args = TrainingArguments(
    output_dir=f"./checkpoints_chunk_{CHUNK_NUM}", 
    per_device_train_batch_size=1, 
    gradient_accumulation_steps=8,
    num_train_epochs=3, 
    learning_rate=5e-4,
    fp16=True,
    logging_steps=20,
    save_strategy="no", 
    remove_unused_columns=False,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset, # Using our custom PyTorch dataset
    data_collator=collate_fn
)

trainer.train()

# --- 6. SAVE PROGRESS ---
print(f"Saving updated model to {SAVE_DIR}...")
trainer.save_model(SAVE_DIR)
print(f"✅ Chunk {CHUNK_NUM} Complete! Now run Chunk {int(CHUNK_NUM)+1}.")