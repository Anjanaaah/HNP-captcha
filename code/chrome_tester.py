from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("🚀 Attempting to launch Chrome...")

try:
    # This line downloads the driver and opens the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    print("🌐 Opening Google...")
    driver.get("https://www.google.com")
    
    print("✅ SUCCESS! Python has full control of Chrome.")
    time.sleep(5)
    driver.quit()
    
except Exception as e:
    print(f"\n❌ CHROME FAILED TO LAUNCH. Reason:")
    print(e)