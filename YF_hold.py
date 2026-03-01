# =========================
# 永豐豐存股 未實現損益
# =========================
from crawl_utils import (
    init_driver,
    wait_for_element,
    click_element,
    switch_to_frame
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import config
import crypto_util as cu

# ----------------------------------
# 永豐豐存股登入
# ----------------------------------
def YF_login(driver, account, password):
    # 直接開資產頁
    driver.get("https://aiinvest.sinotrade.com.tw/Account/Asset")

    # ---------- 1️⃣ 先判斷是否已登入 ----------
    try:
        wait_for_element(driver, By.ID, "AccountHeaderSelect", timeout=5)
        print("✅ 已是登入狀態，略過登入流程")
        return
    except:
        print("🔐 尚未登入，開始執行登入流程")

    # ---------- 2️⃣ 輸入帳密 ----------
    id_input = wait_for_element(driver, By.ID, "txt_IDNO")
    id_input.clear()
    id_input.send_keys(account)

    pw_input = wait_for_element(driver, By.ID, "txt_PW")
    pw_input.clear()
    pw_input.send_keys(password)

    # 點擊登入
    click_element(driver, By.ID, "Btn_Next")

    # ---------- 3️⃣ 登入後確認 ----------
    wait_for_element(driver, By.ID, "AccountHeaderSelect")

    print("✅ 永豐豐存股登入成功")



# =========================
# 主程式（永豐）
# =========================
def run_YF_crawler_hold(headless=False, NUM_MONTHS_TO_PROCESS=3):
    driver = None
    try:
        driver = init_driver(headless)
        # 登入
        YF_login(driver, account="T124504388", password=cu.decrypt(config.YF_CATHAY_MIMA, config.KEY))
        # 點擊美股帳戶
        click_usa_account(driver)

        return {"result_usd_YF": get_us_stock_summary(driver)}



    except Exception as e:
        return f"🚫 永豐爬蟲執行中發生錯誤: {type(e).__name__}: {str(e)}"

    finally:
        if driver:
            driver.quit()

# =====================================================
# 選單內 點擊 美股|經紀部
# ====================  =================================
def click_usa_account(driver):

    select_elem = wait_for_element(driver, By.ID, "AccountHeaderSelect")

    # 包裝成 Select 對象
    select = Select(select_elem)

    # 方法 1️⃣ 根據 index 選擇（第二個選項 index = 1）=> "美股｜經紀部 9A95-01052136"
    select.select_by_index(1)

# =====================================================
# 獲取 報酬率 / 損益試算 / 庫存總市值
# =====================================================
def get_us_stock_summary(driver):

    # 等待上方資訊區塊出現
    wait_for_element(driver, By.CLASS_NAME, "top-area")

    # ✅ 庫存總市值
    market_value = driver.find_element(By.CLASS_NAME, "totalvalue") \
                         .text.replace(",", "")

    # 取得所有 not-total-item
    items = driver.find_elements(By.CLASS_NAME, "not-total-item")

    profit_rate = None
    profit_amount = None

    for item in items:
        title = item.find_element(By.XPATH, ".//div").text.strip()
        value = item.find_element(By.CLASS_NAME, "not-total-number").text.strip()

        if "報酬率" in title:
            profit_rate = value

        elif "損益試算" in title:
            profit_amount = value.replace(",", "")

    return {
        "total_market_value": f"{float(market_value):,.2f}",
        "total_inventory_profit": f"{float(profit_amount):,.2f}",
        "total_profit_rate_percent": profit_rate
    }
