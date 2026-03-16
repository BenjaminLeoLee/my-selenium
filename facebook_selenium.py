import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- 設定區 ---
FB_EMAIL = "wesley_8185@hotmail.com"
FB_PASSWORD = "p0939669630"
TARGET_URL = "https://www.facebook.com/sindy.su.9"  # 目標頁面
SAVE_DIR = r"E:\facebook_picture"
MAX_IMAGES = 10  # 最多下載幾張
SCROLL_TIMES = 5  # 滾動頁面次數
MIN_IMG_SIZE = 200  # 最小圖片寬度（過濾掉 icon 等小圖）

# 1. 建立資料夾
os.makedirs(SAVE_DIR, exist_ok=True)
print(f"儲存資料夾: {SAVE_DIR}")

# 2. 瀏覽器設定 (關閉通知彈窗)
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
# chrome_options.add_argument("--start-maximized") # 視窗最大化

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window() # 確保所有元素都可見
wait = WebDriverWait(driver, 15)

try:
    # 3. 執行登入
    print("正在開啟 Facebook...")
    driver.get("https://www.facebook.com")
    
    # 嘗試處理 Cookie 同意彈窗
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow all') or contains(., '允許') or contains(., '接受')]")))
        cookie_button.click()
        print("已點擊 Cookie 同意按鈕")
    except:
        pass

    # 強化的帳號輸入方式 (嘗試多種可能的選擇器)
    print("正在尋找帳號欄位...")
    email_selectors = [
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.XPATH, "//input[@placeholder='電子郵件地址或手機號碼']"),
        (By.XPATH, "//input[@aria-label='電子郵件地址或手機號碼']")
    ]
    
    email_input = None
    for selector in email_selectors:
        try:
            email_input = wait.until(EC.visibility_of_element_located(selector))
            if email_input: break
        except:
            continue
            
    if email_input:
        email_input.clear()
        email_input.send_keys(FB_EMAIL)
        print("已填入帳號")
    else:
        print("錯誤：找不到帳號欄位")
        driver.save_screenshot("login_error.png") # 存下截圖方便後續除錯

    # 密碼欄位輸入
    try:
        pass_input = driver.find_element(By.ID, "pass")
    except:
        pass_input = driver.find_element(By.NAME, "pass")
        
    pass_input.clear()
    pass_input.send_keys(FB_PASSWORD)
    pass_input.send_keys(Keys.ENTER)
    print("已填入密碼並送出")
    
    print("等待登入確認中...")
    try:
        # 等待首頁特有的元素出現，代表登入成功
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='navigation'] | //input[@placeholder='搜尋 Facebook']")))
        print("登入成功！")
    except:
        print("登入判定超時，嘗試直接前往目標頁面...")

    # 4. 前往目標頁面
    print(f"前往目標頁面: {TARGET_URL}")
    driver.get(TARGET_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))

    # 5. 多次滾動頁面
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(SCROLL_TIMES):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"滾動第 {i + 1}/{SCROLL_TIMES} 次...")
        try:
            wait.until(lambda d: d.execute_script("return document.body.scrollHeight") > last_height)
            last_height = driver.execute_script("return document.body.scrollHeight")
        except:
            time.sleep(1)

    # 6. 抓取圖片並下載
    images = driver.find_elements(By.TAG_NAME, "img")
    print(f"共發現 {len(images)} 個 img 標籤")

    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])
    session.headers.update({"User-Agent": driver.execute_script("return navigator.userAgent;")})

    count = 0
    downloaded_urls = set()
    for img in images:
        if count >= MAX_IMAGES: break
        src = img.get_attribute("src")
        if not src or not src.startswith("https"): continue
        try:
            width = img.size.get("width", 0)
            height = img.size.get("height", 0)
            if width < MIN_IMG_SIZE or height < MIN_IMG_SIZE: continue
        except: continue
        if src in downloaded_urls: continue
        downloaded_urls.add(src)
        try:
            response = session.get(src, timeout=10)
            if response.status_code == 200 and len(response.content) > 5000:
                file_path = os.path.join(SAVE_DIR, f"fb_img_{count}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"已儲存: {file_path}")
                count += 1
        except: continue

    print(f"\n共成功下載 {count} 張圖片")

finally:
    print("任務完成。")
    driver.quit()
