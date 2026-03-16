import requests
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import json


# 設定目標 URL
url = "https://www.google.com"

# 模擬瀏覽器標頭 (User-Agent)，避免被網站封鎖
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    # 1. 發送請求
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 如果狀態碼不是 200，會引發錯誤

    # 2. 解析 HTML 內容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 3. 取得網頁標題 (Title)
    print(f"--- 網頁標題 ---")
    print(soup.title.string)

    # 4. 找出所有的連結 (<a> 標籤)
    print(f"\n--- 前 5 個連結 ---")
    links = soup.find_all('a', limit=5) # 限制只抓 5 個避免洗版
    
    for link in links:
        title = link.get_text().strip() # 連結文字
        href = link.get('href')         # 連結網址
        if title:
            print(f"標題: {title} | 網址: {href}")

except Exception as e:
    print(f"爬取失敗: {e}")



   
    
    

