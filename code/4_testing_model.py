import torch
import os
import random
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from PIL import Image

# --- CONFIGURATION ---
BASE_MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"
ADAPTER_PATH = "./my_captcha_model" # Where your training saved
IMAGE_FOLDER = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\dataset\pictures"

# --- 1. SETUP ---
print("Loading Base Model (Brain)...")
model = Qwen2VLForConditionalGeneration.from_pretrained(
    BASE_MODEL_ID, 
    torch_dtype=torch.float16, 
    device_map="auto"
)
processor = AutoProcessor.from_pretrained(BASE_MODEL_ID, min_pixels=256*28*28, max_pixels=512*28*28)

def run_inference(model_instance, image_path):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": "Read the text in this image."}
            ]
        }
    ]
    
    # Prepare inputs
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(model.device)

    # Generate
    generated_ids = model_instance.generate(**inputs, max_new_tokens=10)
    output_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    return output_text[0]

# --- 2. PICK A TEST IMAGE ---
test_files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith('.png')]
if not test_files:
    print("No images found!")
    exit()

target_image = os.path.join(IMAGE_FOLDER, random.choice(test_files))
print(f"\n🧪 Testing on: {target_image}")

# --- 3. RUN BASE MODEL (Before Training) ---
print("\n--- BASE MODEL PREDICTION ---")
base_result = run_inference(model, target_image)
print(f"🤖 Base Model says: {base_result}")

# --- 4. RUN FINE-TUNED MODEL (After Training) ---
print("\n--- LOADING FINE-TUNED ADAPTER ---")
model = PeftModel.from_pretrained(model, ADAPTER_PATH)
print("Adapter loaded!")

print("\n--- FINE-TUNED MODEL PREDICTION ---")
finetuned_result = run_inference(model, target_image)
print(f"🚀 Your Model says: {finetuned_result}")

# --- 5. VERDICT ---
print("\n" + "="*30)
if base_result == finetuned_result:
    print("😐 Result: NO CHANGE (The model didn't learn enough yet)")
else:
    print("✨ Result: CHANGED (The training did something!)")
print("="*30)