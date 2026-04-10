from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
import time

# ========================================
# 國泰新登入入口 (2026年改版後)
# ========================================
# 國泰改版後，登入入口從原本的 miniMain.aspx 變成了 portal/
# portal 頁面裡面會有一個 iframe，登入表單就在這個 iframe 裡面
PORTAL_URL = "https://exoiweb.cathaysec.com.tw/portal/"

# 用 CSS 選擇器找 portal 頁面內的登入 iframe
# 這個 iframe 的 src 屬性會包含 'weblogin.aspx'，我們用這個來精確定位
PORTAL_LOGIN_IFRAME = (By.CSS_SELECTOR, "iframe[src*='weblogin.aspx']")

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


# ========================================
#  國泰樹精靈登入 (新流程 - 從 portal 開始)
# ========================================
# 這個函數負責登入國泰證券。新版改成從 portal 頁面開始，
# 然後找到裡面的登入 iframe，填入帳號密碼後按送出。
def cathay_login(driver, account, password):
    # 第1步：進入 portal 首頁
    # portal 是國泰的新登入入口，一打開會看到左邊有個登入表單 iframe
    driver.get(PORTAL_URL)

    # 第2步：等待登入 iframe 出現，並切換進去
    # WebDriverWait 會等待最多 10 秒，直到 iframe 準備好
    # frame_to_be_available_and_switch_to_it 會自動切進這個 iframe 裡面
    # （重要：切進 iframe 後才能操作裡面的元素）
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it(PORTAL_LOGIN_IFRAME)
    )

    # 第3步：填入帳號
    # txtLoginID 是帳號的輸入框（通常是身分證字號）
    login_input = wait_for_element(driver, By.ID, "txtLoginID")
    # clear() 先把預設提示文字「請輸入身分證字號」清掉，再輸入真正的帳號
    login_input.clear()
    login_input.send_keys(account)
    
    # 第4步：點擊假密碼欄位，觸發真正密碼輸入框出現
    # 國泰用了一個 trick：先顯示假的密碼欄位（看得到但輸入不了），
    # 點擊後才會顯示真正的密碼輸入框 txtPassword1
    # 這是為了安全性設計，防止密碼被肉眼看到
    pw_fake = driver.find_element(By.ID, "txtPassword")
    pw_fake.click()
    
    # 第5步：填入密碼
    # 等 txtPassword1（真正的密碼欄位）出現後，再填入密碼
    password_input = wait_for_element(driver, By.ID, "txtPassword1")
    password_input.clear()
    password_input.send_keys(password)
    
    # 第6步：點擊登入按鈕
    # 按下「登入」按鈕後，伺服器會驗證帳號密碼
    login_button = driver.find_element(By.ID, "btnLoginGO")
    login_button.click()

    # 第7步：等待登入完成
    # 登入成功後，頁面會導向到交易頁面，其中會有一個 frame 叫「tb」
    # 我們先切回頂層頁面（default_content），然後等 tb frame 出現
    # 這樣才能確保登入真的完成了，而不是卡在登入頁或載入中
    driver.switch_to.default_content()
    # 等待最多 20 秒直到 tb frame 出現
    WebDriverWait(driver, 20).until(lambda current_driver: _frame_exists(current_driver, "tb"))
    # 設定到頂層內容，讓後續呼叫 switch_to_frame 時可以從頭找起
    driver.switch_to.default_content()

    
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

# ========================================
# 5️⃣ 切換 frame（改良版 - 支援巢狀 frame）
# ========================================
# 這是一個簡單的 wrapper 函數，用來切換到指定的 frame。
# 與原本不同的是，它現在能夠找到巢狀（frame 裡面還有 frame）的情況。
def switch_to_frame(driver, frame_name):
    # 先切回最頂層頁面，避免從巢狀位置開始找
    driver.switch_to.default_content()
    # 呼叫遞迴函數來尋找並切往目標 frame
    # 如果找不到就拋出例外，這樣可以立即發現問題
    if not _switch_to_nested_frame(driver, frame_name):
        raise Exception(f"找不到 frame: {frame_name}")


# ========================================
# 檢查 frame 是否存在的輔助函數
# ========================================
# 用途：在不改變目前 focus 的情況下，檢查某個 frame 是否存在
# 這常被用在 WebDriverWait 的條件檢查裡（比如登入等待時）
def _frame_exists(driver, frame_name):
    # 切回頂層，以便進行乾淨的搜尋
    driver.switch_to.default_content()
    # 嘗試尋找這個 frame（不實際停留在那裡，只是試著切過去然後看成功不成功）
    found = _switch_to_nested_frame(driver, frame_name)
    # 無論找到沒找到，都要切回頂層，以保持狀態一致
    driver.switch_to.default_content()
    return found


# ========================================
# 遞迴搜尋巢狀 frame 的核心函數
# ========================================
# 用途：在複雜的 frame 結構中找到目標 frame 並切進去
# 
# 背景說明：
#   - 有時網頁會有 frame 套 frame 的結構
#   - 比如：portal iframe 裡面，可能還有其他 frame（如 tb, sysjustdefaultdown）
#   - 我們需要一個能穿過這些層級去找目標的機制
# 
# 運作原理：
#   1. 先在目前層找同名的 frame，找到就直接切過去
#   2. 如果沒找到，就進去每個 frame，再遞迴地在裡面尋找
#   3. 如果某個分支找到了就回傳 True；找不到就退出來試下一個
def _switch_to_nested_frame(driver, frame_name):
    # 第1步：取得目前頁面中所有的 frame 和 iframe
    # 注意：find_elements 只會找目前層級的 frame，不會遞迴搜尋
    frames = driver.find_elements(By.CSS_SELECTOR, "frame, iframe")

    # 第2步：先檢查目前層級有沒有直接符合的 frame
    # 比較 id 和 name 屬性，因為兩種都有可能
    for frame in frames:
        if frame.get_attribute("id") == frame_name or frame.get_attribute("name") == frame_name:
            # 找到了！切進去並回傳成功
            driver.switch_to.frame(frame)
            return True

    # 第3步：目前層找不到，那就進去每一個 frame 裡面遞迴地找
    for frame in frames:
        # 切進去這個 frame
        driver.switch_to.frame(frame)
        # 在這個 frame 裡面遞迴地尋找目標 frame
        if _switch_to_nested_frame(driver, frame_name):
            # 遞迴函數找到了，直接回傳 True
            # 注意：現在的焦點已經在目標 frame 上，我們不需要再做什麼
            return True
        # 這個 frame 裡面沒找到，退出來試下一個
        driver.switch_to.parent_frame()

    # 第4步：所有 frame 都找過了還是沒有，回傳失敗
    return False
