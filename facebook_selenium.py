import os  # 匯入作業系統模組，用於建立資料夾與路徑處理
import time  # 匯入時間模組，用於必要的小型等待
import requests  # 匯入請求模組，用於下載圖片內容
from selenium import webdriver  # 匯入 Selenium 核心瀏覽器驅動
from selenium.webdriver.chrome.service import Service  # 匯入 Chrome 服務設定
from selenium.webdriver.common.by import By  # 匯入元素定位器（ID, XPATH 等）
from selenium.webdriver.chrome.options import Options  # 匯入 Chrome 瀏覽器選項
from selenium.webdriver.support.ui import WebDriverWait  # 匯入顯式等待工具
from selenium.webdriver.support import expected_conditions as EC  # 匯入等待條件判斷
from selenium.webdriver.common.keys import Keys  # 匯入鍵盤操作（如按 Enter）
from webdriver_manager.chrome import ChromeDriverManager  # 匯入驅動管理工具，自動下載 Chrome 驅動

# --- 設定區 ---
FB_EMAIL = ""  # 設定您的臉書登入帳號
FB_PASSWORD = ""  # 設定您的臉書登入密碼
TARGET_URL = ""  # 設定您要爬取圖片的目標臉書頁面
SAVE_DIR = r"E:\facebook_picture"  # 設定圖片存檔的本機路徑
MAX_IMAGES = 10  # 設定最多要下載的圖片張數
SCROLL_TIMES = 5  # 設定滾動頁面載入更多內容的次數
MIN_IMG_SIZE = 200  # 設定過濾掉的小圖寬度阈值（避免載入 icon 或表情符號）

# 1. 建立資料夾
os.makedirs(SAVE_DIR, exist_ok=True)  # 如果資料夾不存在則自動建立，存在則不報錯
print(f"儲存資料夾: {SAVE_DIR}")  # 在終端機印出目前的儲存路徑

# 2. 瀏覽器設定
chrome_options = Options()  # 建立 Chrome 瀏覽器選項物件
chrome_options.add_argument("--disable-notifications")  # 禁用瀏覽器的桌面通知彈窗

service = Service(ChromeDriverManager().install())  # 自動下載並啟動 Chrome 服務
driver = webdriver.Chrome(service=service, options=chrome_options)  # 初始化 Chrome 瀏覽器物件
driver.maximize_window()  # 將瀏覽器視窗最大化，確保所有按鈕都能被看見
wait = WebDriverWait(driver, 15)  # 設定顯式等待，最長等待 15 秒

try:
    # 3. 執行登入
    print("正在開啟 Facebook...")  # 印出進度文字
    driver.get("https://www.facebook.com")  # 讓瀏覽器前往臉書首頁
    
    # 嘗試處理 Cookie 同意彈窗
    try:
        # 尋找包含同意、接受或 Allow all 等關鍵字的按鈕並等待其可點擊
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow all') or contains(., '允許') or contains(., '接受')]")))
        cookie_button.click()  # 點擊該按鈕
        print("已點擊 Cookie 同意按鈕")  # 印出成功點擊訊息
    except:
        pass  # 如果沒有彈窗出現，就忽略此錯誤繼續執行

    # 強化的帳號輸入方式
    print("正在尋找帳號欄位...")  # 印出進度文字
    email_selectors = [  # 定義多種可能的帳號欄位選擇器，以防臉書變更介面
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.XPATH, "//input[@placeholder='電子郵件地址或手機號碼']"),
        (By.XPATH, "//input[@aria-label='電子郵件地址或手機號碼']")
    ]
    
    email_input = None  # 初始化帳號輸入框變數
    for selector in email_selectors:  # 逐一嘗試各個選擇器
        try:
            email_input = wait.until(EC.visibility_of_element_located(selector))  # 等待該欄位變為可見
            if email_input: break  # 如果找到了，就跳出循環
        except:
            continue  # 沒找到則嘗試下一個
            
    if email_input:  # 如果成功定位到帳號欄位
        email_input.clear()  # 先清空欄位內的文字
        email_input.send_keys(FB_EMAIL)  # 填入臉書帳號
        print("已填入帳號")  # 印出成功填寫訊息
    else:
        print("錯誤：找不到帳號欄位")  # 沒找到欄位則報錯
        driver.save_screenshot("login_error.png")  # 存下目前的截圖，方便您查看發生什麼事

    # 密碼欄位輸入
    try:
        pass_input = driver.find_element(By.ID, "pass")  # 嘗試用 ID 找密碼欄位
    except:
        pass_input = driver.find_element(By.NAME, "pass")  # ID 失敗則改用 Name 找
        
    pass_input.clear()  # 清空密碼欄位
    pass_input.send_keys(FB_PASSWORD)  # 填入密碼
    pass_input.send_keys(Keys.ENTER)  # 直接按下鍵盤的 Enter 鍵執行登入
    print("已填入密碼並送出")  # 印出訊息

    print("等待登入確認中...")  # 印出進度文字
    try:
        # 等待臉書首頁導航列或搜尋框出現，代表已經成功進入首頁
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='navigation'] | //input[@placeholder='搜尋 Facebook']")))
        print("登入成功！")  # 印出登入成功訊息
    except:
        print("登入判定超時，嘗試直接前往目標頁面...")  # 超時則直接嘗試跳轉目標頁面

    # 4. 前往目標頁面
    print(f"前往目標頁面: {TARGET_URL}")  # 印出目標網址
    driver.get(TARGET_URL)  # 跳轉到要爬取圖片的目標臉書頁面
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))  # 等待頁面上至少有一張圖片載入

    # 5. 多次滾動頁面載入內容
    last_height = driver.execute_script("return document.body.scrollHeight")  # 取得目前的頁面總高度
    for i in range(SCROLL_TIMES):  # 根據設定次數進行滾動
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 捲動捲軸到底部
        print(f"滾動第 {i + 1}/{SCROLL_TIMES} 次...")  # 印出當前滾動進度
        try:
            # 使用智慧等待，直到頁面高度發生變化（代表新內容已載入）
            wait.until(lambda d: d.execute_script("return document.body.scrollHeight") > last_height)
            last_height = driver.execute_script("return document.body.scrollHeight")  # 更新目前頁面高度
        except:
            time.sleep(1)  # 如果高度沒變，稍微等待 1 秒緩衝

    # 6. 抓取圖片並準備下載
    images = driver.find_elements(By.TAG_NAME, "img")  # 找出頁面上所有的 <img> 標籤
    print(f"共發現 {len(images)} 個 img 標籤")  # 印出總共發現的標籤數量

    # 7. 建立下載用 Session 並同步 Cookie
    session = requests.Session()  # 建立一個新的下載請求 Session 物件
    for cookie in driver.get_cookies():  # 將 Selenium 瀏覽器中的登入資訊 (Cookie) 提取出來
        session.cookies.set(cookie["name"], cookie["value"])  # 存入 Session 中，防止下載時被臉書擋住
    session.headers.update({"User-Agent": driver.execute_script("return navigator.userAgent;")})  # 同步瀏覽器的標頭資訊

    # 8. 下載邏輯
    count = 0  # 初始化已下載圖片計數器
    downloaded_urls = set()  # 建立一個集合來儲存已下載的網址，避免重複下載
    for img in images:  # 遍歷所有抓到的圖片標籤
        if count >= MAX_IMAGES: break  # 如果達到設定的最大張數，則停止
        src = img.get_attribute("src")  # 取得圖片的來源網址 (SRC)
        if not src or not src.startswith("https"): continue  # 如果網址無效或不是 HTTPS 則跳過
        try:
            width = img.size.get("width", 0)  # 取得圖片在畫面上的寬度
            height = img.size.get("height", 0)  # 取得圖片在畫面上的高度
            if width < MIN_IMG_SIZE or height < MIN_IMG_SIZE: continue  # 太小的圖（如頭像、小圖示）不下載
        except: continue  # 如果無法讀取圖片大小則跳過
        if src in downloaded_urls: continue  # 如果這張圖剛才下載過了則跳過
        downloaded_urls.add(src)  # 將網址加入「已下載」名單
        try:
            response = session.get(src, timeout=10)  # 使用帶有 Cookie 的 Session 下載圖片
            if response.status_code == 200 and len(response.content) > 5000:  # 檢查狀態碼與檔案大小（大於 5KB）
                file_path = os.path.join(SAVE_DIR, f"fb_img_{count}.jpg")  # 設定存檔路徑與檔名
                with open(file_path, "wb") as f:  # 以二進位寫入模式開啟檔案
                    f.write(response.content)  # 將圖片內容寫入檔案
                print(f"已儲存: {file_path}")  # 印出成功存檔訊息
                count += 1  # 下載計數加 1
        except: continue  # 下載過程出錯則嘗試下一張

    print(f"\n共成功下載 {count} 張圖片")  # 印出最終下載結果

finally:
    print("任務完成。")  # 印出結束文字
    driver.quit()  # 關閉瀏覽器，釋放電腦資源
