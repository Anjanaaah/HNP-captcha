import os, time, torch, io, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from PIL import Image

# --- ⚙️ CONFIGURATION ---
TARGET_URL = r"C:\Users\Asus\OneDrive\Documents\Anjan_proj\my-Website\index.html"
READ_MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"
ADAPTER_PATH = "./my_captcha_model"
OFFLOAD_DIR = "./offload_weights"

# --- 1. LOAD AI BRAIN ---
print("\n🤖 INITIALIZING CASE-SENSITIVE AI SYSTEM...")
if not os.path.exists(OFFLOAD_DIR): os.makedirs(OFFLOAD_DIR)

bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)

# Load with local_files_only=True for speed/offline support
model = Qwen2VLForConditionalGeneration.from_pretrained(
    READ_MODEL_ID, quantization_config=bnb_config, device_map="auto", 
    offload_folder=OFFLOAD_DIR, local_files_only=True
)
if os.path.exists(ADAPTER_PATH):
    model = PeftModel.from_pretrained(model, ADAPTER_PATH, local_files_only=True)

processor = AutoProcessor.from_pretrained(READ_MODEL_ID, local_files_only=True)

# --- 🛠️ UPDATED: CASE-SENSITIVE CLEANER ---
def clean_captcha_case_sensitive(text):
    """ Removes hallucinated duplicates while PRESERVING Case """
    text = text.replace(" ", "").strip() # NO .upper() HERE
    if not text: return ""
    
    result = [text[0]]
    for i in range(1, len(text)):
        # Only skip if it's the EXACT same character (e.g., '9' == '9' or 'a' == 'a')
        # If it's 'A' and then 'a', we KEEP both.
        if text[i] == text[i-1]: 
            continue 
        result.append(text[i])
    return "".join(result)

def ask_ai(image):
    # Prompting the model to be specific about casing
    messages = [{"role": "user", "content": [
        {"type": "image", "image": image}, 
        {"type": "text", "text": "Read the text in this image. Distinguish between uppercase and lowercase letters."}
    ]}]
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    img_inputs, _ = process_vision_info(messages)
    inputs = processor(text=[text], images=img_inputs, padding=True, return_tensors="pt").to(model.device)

    # REPETITION PENALTY is key here to stop '999' while allowing 'Aa'
    gen_ids = model.generate(
        **inputs, 
        max_new_tokens=20, 
        repetition_penalty=1.2, 
        temperature=0.01, # Lower temperature = more literal/exact reading
        do_sample=False
    )
    
    output = processor.batch_decode(gen_ids, skip_special_tokens=True)[0]
    raw_text = output.split("assistant")[-1] if "assistant" in output else output
    
    return clean_captcha_case_sensitive(raw_text)

# --- 2. EXECUTE BOT ---
def run_bot():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(TARGET_URL)
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[contains(text(), 'AUTHENTICATE')]").click()
        time.sleep(1)
        driver.find_element(By.ID, "c-box").click()
        time.sleep(2)
        
        # Choice for custom upload
        print("\n❓ Use CUSTOM image? [y/n]")
        if input(">> ").lower() == 'y':
            print("🛑 Upload now and press ENTER...")
            input()

        for attempt in range(6):
            print(f"🧠 Reading (Attempt {attempt+1})...")
            canvas = driver.find_element(By.TAG_NAME, "canvas")
            image = Image.open(io.BytesIO(canvas.screenshot_as_png))
            
            captcha_text = ask_ai(image)
            print(f"🤖 Predicted (Case Sensitive): '{captcha_text}'")

            input_box = driver.find_element(By.ID, "captchaInput")
            input_box.clear()
            input_box.send_keys(captcha_text)
            
            driver.find_element(By.XPATH, "//*[contains(text(), 'VERIFY')]").click()
            time.sleep(1.5)

            if driver.find_element(By.ID, "view-3").is_displayed():
                print("🎉 SUCCESS! Case recognized correctly."); break
    finally: driver.quit()

if __name__ == "__main__": run_bot()