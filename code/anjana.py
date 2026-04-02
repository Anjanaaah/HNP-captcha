import os, time, torch, io, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from PIL import Image

# --- ⚙️ CONFIGURATION (LOCKED) ---
TARGET_URL = r"C:\project\TransferTemp (1)\TransferTemp\my-Website\index.html"
READ_MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"
ADAPTER_PATH = "./my_captcha_model"
OFFLOAD_DIR = "./offload_weights"

# --- 1. LOAD AI BRAIN (OPTIMIZED CPU MODE) ---
print("\n🤖 INITIALIZING SYSTEM FOR INTEL CPU/IRIS XE...")
if not os.path.exists(OFFLOAD_DIR): os.makedirs(OFFLOAD_DIR)

# Loading for CPU stability
model = Qwen2VLForConditionalGeneration.from_pretrained(
    READ_MODEL_ID, 
    device_map="cpu", 
    torch_dtype=torch.float32, 
    offload_folder=OFFLOAD_DIR,
    local_files_only=True
)

if os.path.exists(ADAPTER_PATH):
    print("🔌 Attaching LoRA Adapter...")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH, local_files_only=True)

processor = AutoProcessor.from_pretrained(READ_MODEL_ID, local_files_only=True)

def clean_captcha_universal(text):
    text = text.replace(" ", "").strip().upper()
    if not text: return ""
    result = [text[0]]
    for i in range(1, len(text)):
        if text[i] == text[i-1]: continue 
        result.append(text[i])
    return "".join(result)

def ask_ai(image):
    # SPEED HACK: Force the AI to process a smaller image size.
    # This makes CPU inference MUCH faster without losing CAPTCHA accuracy.
    messages = [{
        "role": "user", 
        "content": [
            {
                "type": "image", 
                "image": image,
                "resized_height": 280, # Optimized for speed
                "resized_width": 280
            }, 
            {"type": "text", "text": "Read the text in this image accurately."}
        ]
    }]
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    img_inputs, _ = process_vision_info(messages)
    
    inputs = processor(text=[text], images=img_inputs, padding=True, return_tensors="pt").to(model.device)

    print("⏳ AI is thinking (Optimized for Intel Iris Xe)...")
    start_time = time.time()
    
    # Generate call with all sampling warnings disabled
    gen_ids = model.generate(
        **inputs, 
        max_new_tokens=20, 
        repetition_penalty=1.3, 
        do_sample=False, 
        temperature=None, 
        top_p=None, 
        top_k=None
    )
    
    end_time = time.time()
    print(f"✅ Predicted in {round(end_time - start_time, 2)} seconds!")
    
    output = processor.batch_decode(gen_ids, skip_special_tokens=True)[0]
    raw_text = output.split("assistant")[-1] if "assistant" in output else output
    return clean_captcha_universal(raw_text)

# --- 2. EXECUTE BOT ---
def run_bot():
    print("🚀 Launching Agent...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15) 
    
    try:
        file_url = "file:///" + TARGET_URL.replace("\\", "/")
        print(f"🌐 Opening: {file_url}")
        driver.get(file_url)
        
        # Smart Wait for elements
        print("⏳ Waiting for website...")
        auth_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'authenticate')]")))
        auth_btn.click()
        
        c_box = wait.until(EC.element_to_be_clickable((By.ID, "c-box")))
        c_box.click()
        
        print("\n❓ Use CUSTOM image? [y/n]")
        if input(">> ").lower() == 'y':
            print("🛑 Upload now and press ENTER...")
            input()

        for attempt in range(6):
            print(f"\n🧠 STARTING ANALYSIS (Attempt {attempt+1})...")
            
            canvas = wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
            time.sleep(1) 
            
            image = Image.open(io.BytesIO(canvas.screenshot_as_png))
            captcha_text = ask_ai(image)
            print(f"🤖 AI Result: '{captcha_text}'")

            input_box = wait.until(EC.element_to_be_clickable((By.ID, "captchaInput")))
            input_box.clear()
            input_box.send_keys(captcha_text)
            
            verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'verify')]")))
            verify_btn.click()
            time.sleep(2)

            try:
                if driver.find_element(By.ID, "view-3").is_displayed():
                    print("🎉 SUCCESS! CAPTCHA Bypassed."); break
            except:
                print("🔄 Wrong prediction. Retrying...")
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("Press ENTER to close Chrome...")
        
    finally: 
        driver.quit()

if __name__ == "__main__": 
    run_bot()