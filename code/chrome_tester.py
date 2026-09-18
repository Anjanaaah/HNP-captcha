from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

print("🚀 Starting bot-behaviour test...")

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.get("http://127.0.0.1:5000")
    print("🌐 HNP CAPTCHA opened")

    time.sleep(2)

    # Fill username
    driver.find_element(By.ID, "username").send_keys("botuser")

    # Fill password
    driver.find_element(By.ID, "password").send_keys("botpassword")

    # CAPTCHA input
    captcha_input = driver.find_element(By.ID, "captchaInput")
    captcha_input.click()
    captcha_input.send_keys("AAAAAA")

    # Login button
    login_button = driver.find_element(
        By.XPATH, "//button[contains(text(),'Login')]"
    )

    # Rapid automated clicks
    for i in range(10):
        login_button.click()

    print("🤖 Automated interaction completed")

    time.sleep(5)

    status = driver.find_element(By.ID, "status").text
    score = driver.find_element(By.ID, "score").text

    print("\n========== RESULT ==========")
    print("Status:", status)
    print("Score:", score)
    print("============================")

    time.sleep(3)
    driver.quit()

except Exception as e:
    import traceback
    print("\n❌ ERROR:")
    traceback.print_exc()
