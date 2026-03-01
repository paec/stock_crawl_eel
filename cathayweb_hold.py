# =========================
# 國泰樹精靈 未實現損益 (美股/台股)
# =========================
from crawl_utils import (
    init_driver,
    wait_for_element,
    click_element,
    switch_to_frame,
    cathay_login
)
from selenium.webdriver.common.by import By
import config
import crypto_util as cu

# =========================
# 台幣未實現損益頁
# =========================
def get_twd_unrealized_summary(driver):

    switch_to_frame(driver, "tb")
    click_element(driver, By.ID, "tdm1")   # 證券帳務
    click_element(driver, By.ID, "i14")    # 未實現損益

    switch_to_frame(driver, "sysjustdefaultdown")
    wait_for_element(driver, By.ID, "checkSum")

    total_market_value = driver.find_element(By.ID, "Label2").text.strip()
    total_inventory_profit = driver.find_element(By.ID, "Label3").text.strip()
    total_profit_rate = driver.find_element(By.ID, "Label4").text.strip()

    return {
        "total_market_value": total_market_value,
        "total_inventory_profit": total_inventory_profit,
        "total_profit_rate_percent": total_profit_rate
    }


# =====================================================
# HK0203 → StockList (美股庫存台幣加總)
# =====================================================
def get_us_stock_twd_summary(driver):

    # 切回上層 frame
    switch_to_frame(driver, "tb")

    # 先切到「海外股票帳務」
    click_element(driver, By.ID, "tdmh2")

    # 點擊 HK0203
    click_element(driver, By.ID, "i86")

    # 進入內容 frame
    switch_to_frame(driver, "sysjustdefaultdown")
    wait_for_element(driver, By.ID, "StockList")
    
    rows = driver.find_elements(By.CSS_SELECTOR, "#StockList tr")[2:]

    total_twd_actual_investment_cost = 0
    total_twd_market_value = 0
    total_twd_profit = 0
    total_twd_profit_rate = 0

    for row in rows:
       
        tds = row.find_elements(By.TAG_NAME, "td")

        #美股但用台幣計算
        actual_investment_cost_twd = tds[6].text.split("\n")[1].replace(",", "")
        market_value_twd = tds[9].text.split("\n")[1].replace(",", "") 
        profit_twd = tds[10].text.split("\n")[1].replace(",", "")
        profit_rate = tds[11].text.split("\n")[1]

        total_twd_actual_investment_cost += float(actual_investment_cost_twd)
        total_twd_market_value += float(market_value_twd)
        total_twd_profit += float(profit_twd)
        total_twd_profit_rate += float(profit_rate)
        
    return {
        "total_market_value": f"{round(total_twd_market_value, 2):,.2f}",
        "total_inventory_profit": f"{round(total_twd_profit, 2):,.2f}",
        "total_profit_rate_percent": (
            round((total_twd_profit / total_twd_actual_investment_cost) * 100, 2)
            if total_twd_actual_investment_cost != 0
            else 0
        ).__str__() + "%"
    }


# =========================
# 主程式
# =========================
def run_cathay_crawler_hold(headless=False, NUM_MONTHS_TO_PROCESS=3):
    driver = None
    try:
        driver = init_driver(headless)

        # =========================
        # 登入
        # =========================
        cathay_login(driver, account="T124504388", password=cu.decrypt(config.YF_CATHAY_MIMA, config.KEY))

        result_twd = get_twd_unrealized_summary(driver)
        result_usd = get_us_stock_twd_summary(driver)

        # =========================
        # 最終回傳
        # =========================
        return {
            "result_twd_Cathy": result_twd,
            "result_usd_Cathy(in twd)": result_usd
        }

    except Exception as e:
        return f"🚫 爬蟲執行中發生錯誤: {type(e).__name__}: {str(e)}"

    finally:
        if driver:
            driver.quit()
