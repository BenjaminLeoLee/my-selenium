from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. 自動下載並設定 Chrome 驅動程式
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

try:
    # 2. 前往 Google
    driver.get("https://www.google.com")
    
    # 3. 定位搜尋框 (Google 搜尋框的 name 屬性通常是 'q')
    search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    
    # 4. 輸入關鍵字並按下 Enter
    search_box.send_keys("Python Selenium 教學")
    search_box.send_keys(Keys.RETURN)
    
    # 5. 等待網頁載入
    # 抓取搜尋結果的標題 (Google 搜尋結果的標題通常在 <h3> 標籤中)
    titles = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "h3")))
    
    print("--- 搜尋結果標題 ---")
    for title in titles[:5]: # 只印前 5 個
        print(title.text)

finally:
    # 7. 關閉瀏覽器
    driver.quit()
