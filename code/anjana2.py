import os, time, io, requests, base64
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Your specific live link
COLAB_URL = "https://unimpatiently-unpillaged-tanya.ngrok-free.dev/solve" 
TARGET_URL = r"C:\project\TransferTemp (1)\TransferTemp\my-Website\index.html"

def ask_colab_ai(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    print("📡 Sending image to Cloud GPU...")
    try:
        # Pinging the Colab server
        response = requests.post(COLAB_URL, json={"image": img_str}, timeout=45)
        response.raise_for_status()
        prediction = response.json().get("prediction", "")
        return str(prediction).strip().upper()
    
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return ""

def run_bot():
    print("\n🚀 --- STARTING AUTOMATION AGENT ---")
    
    # 1. PRE-FLIGHT CHECK: Is Colab actually awake?
    print("🔍 Checking Cloud GPU status...")
    try:
        # A simple GET request just to see if the tunnel is open
        test_ping = requests.get(COLAB_URL.replace("/solve", ""), timeout=5)
        print("✅ Cloud GPU is Online.")
    except:
        print("⚠️ Warning: Could not reach Colab. Make sure the Colab cell is RUNNING.")

    # 2. LAUNCH CHROME
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # This helps avoid some bot-detection flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        file_path = "file:///" + TARGET_URL.replace("\\", "/")
        print(f"🌐 Opening Local Page: {TARGET_URL}")
        driver.get(file_path)
        
        # Step 1: AUTHENTICATE
        print("⏳ Clicking 'Authenticate'...")
        # Using a flexible XPATH that finds the button regardless of case
        auth_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(),'AUTH','auth'),'auth')] | //*[contains(text(),'Authenticate')]")))
        auth_btn.click()
        
        # Step 2: CHECKBOX
        print("⏳ Clicking Security Checkbox...")
        wait.until(EC.element_to_be_clickable((By.ID, "c-box"))).click()
        
        # Loop for Retries
        for attempt in range(6):
            print(f"\n🧠 SOLVING CAPTCHA (Attempt {attempt+1}/6)")
            
            # Find the captcha canvas
            canvas = wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
            time.sleep(1.5) # Wait for the image to fully draw
            
            # Screenshot only the canvas
            image = Image.open(io.BytesIO(canvas.screenshot_as_png))
            
            # Send to Colab
            captcha_text = ask_colab_ai(image)
            
            if not captcha_text:
                print("❌ No text received from AI. Trying next attempt...")
                continue
                
            print(f"🤖 AI Prediction: '{captcha_text}'")

            # Step 3: TYPE RESULT
            input_box = wait.until(EC.element_to_be_clickable((By.ID, "captchaInput")))
            input_box.clear()
            input_box.send_keys(captcha_text)
            
            # Step 4: VERIFY
            print("⏳ Verifying...")
            verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(),'VER','ver'),'ver')] | //*[contains(text(),'Verify')]")))
            verify_btn.click()
            
            time.sleep(2.5) # Wait for page transition

            # Check if we successfully bypassed (Change 'view-3' if your success ID is different)
            try:
                if driver.find_element(By.ID, "view-3").is_displayed():
                    print("\n🎉 SUCCESS! Mission Accomplished.")
                    break
            except:
                print("🔄 Prediction incorrect or page did not advance. Retrying...")
                
    except Exception as e:
        print(f"\n❌ BOT CRASHED: {e}")
    finally:
        print("\n🏁 Process Finished.")
        input("Press ENTER to close the browser and exit...")
        driver.quit()

if __name__ == "__main__": 
    run_bot()
    