from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
import time

# -----------------------------
# 1️⃣ WebDriver 初始化
# -----------------------------
def init_driver(headless):
    chrome_options = Options()

    #指定profile (因為使用預設新開的瀏覽器，會有證券憑證未註冊的問題)
    #指定使用ProfileForCrawl下的Default，要把原本...\Chrome\User Data\下的Default，複製一份進...\Chrome\User Data\ProfileForCrawl
    #讓ProfileForCrawl下的Default，跟原本我們手動開啟瀏覽器使用的Default Profile是同一份 (為避免干擾所以複製一份出來用)
    chrome_options.add_argument(r"--user-data-dir=C:\Users\paec5\AppData\Local\Google\Chrome\User Data\ProfileForCrawl")


    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_argument("--disable-notifications")
    
    # 執行 Eel 時通常需要 headless 模式，如果您需要看到瀏覽器操作過程可以註解掉下面這行
    if headless == False:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver


# -----------------------------
#  國泰樹精靈登入
# -----------------------------
def cathay_login(driver, account, password):
    driver.get("https://iweb.cathaysec.com.tw/cathayweb/weblogin.aspx?a=https://iweb.cathaysec.com.tw/cathayweb/")
    
    # 輸入帳號
    login_input = wait_for_element(driver, By.ID, "txtLoginID")
    login_input.send_keys(account)
    
    # 觸發真正密碼欄位顯示
    pw_fake = driver.find_element(By.ID, "txtPassword")
    pw_fake.click()
    
    password_input = wait_for_element(driver, By.ID, "txtPassword1")
    password_input.send_keys(password)
    
    # 點擊登入
    login_button = driver.find_element(By.ID, "btnLoginGO")
    login_button.click()

    
# -----------------------------
# 2️⃣ 等待元素
# -----------------------------
def wait_for_element(driver, by, identifier, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, identifier))
        )
    except Exception as e:
        print(f"❌ 等待元素失敗: {by} = {identifier}")
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("👉 已將 page_source 寫入 debug_page_source.html")
        raise e

def wait_for_clickable(driver, by, identifier, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, identifier))
    )

# -----------------------------
# 3️⃣ 點擊元素 (處理 StaleElement)
# -----------------------------
def click_element(driver, by, identifier, retries=3, wait_time=0.5):
    for _ in range(retries):
        try:
            elem = wait_for_clickable(driver, by, identifier)
            elem.click()
            return
        except StaleElementReferenceException:
            print(f"retry {identifier}")
            time.sleep(wait_time)
    raise Exception(f"無法點擊元素: {identifier}")

# -----------------------------
# 5️⃣ 切換 frame
# -----------------------------
def switch_to_frame(driver, frame_name):
    driver.switch_to.default_content()
    driver.switch_to.frame(frame_name)
