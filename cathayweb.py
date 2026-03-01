# =========================
# 國泰樹精靈 美股 成本/匯率/配股配息
# =========================
from crawl_utils import cathay_login,init_driver, wait_for_element, wait_for_clickable, click_element, switch_to_frame
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from collections import defaultdict
from operator import itemgetter
import time
import config
import crypto_util as cu

# -----------------------------
# 6️⃣ 解析 dataGridStock
# -----------------------------
def parse_data_grid(driver):
    data_grid = driver.find_element(By.ID, "dataGridStock")
    rows = data_grid.find_elements(By.TAG_NAME, "tr")

    buy_list = []
    dividend_list = []

    for row in rows[2:]:  # 跳過 header
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 13:
            continue

        # 取得欄位文字
        # cols[12] 是 "實際應收/付(-)金額"
        raw_amount = cols[12].text.split("\n")[-1].strip().replace(",", "")
        try:
            amount = abs(float(raw_amount))  # 取絕對值
        except ValueError:
            amount = 0.0

        record = {
            "交易日期": cols[0].text.strip(),
            "商品代碼": cols[1].text.strip(),
            "匯率": cols[8].text.split("\n")[-1].strip(), # 匯率在第 8 欄
            "成交金額": cols[9].text.strip(), # 成交金額在第 9 欄
            "實際應收/付(-)金額": amount
        }

        trade_type = cols[5].text.strip()
        if trade_type == "買進":
            buy_list.append(record)
        elif trade_type == "一般除息":
            dividend_list.append(record)

    return buy_list, dividend_list

# -----------------------------
# 7️⃣ 輸出結果函式 (已修改：回傳字串)
# -----------------------------
def generate_result_string(buy_list, dividend_list):
    lines = []

    # 買進資料
    lines.append("買進資料:")
    # 欄位順序：交易日期 | 成交金額 | 匯率
    lines.append("交易日期\t成交金額\t匯率")
    buy_sorted = sorted(buy_list, key=itemgetter("交易日期"))
    for r in buy_sorted:
        date = r['交易日期'].replace("\n", " ").strip()
        amount = str(r['成交金額']).replace("\n", " ").strip()
        exchange_rate = str(r['匯率']).replace("\n", " ").strip()
        lines.append(f"{date}\t{amount}\t{exchange_rate}")

    lines.append("\n一般除息資料:")
    dividend_dict = defaultdict(list)
    for r in dividend_list:
        dividend_dict[r["商品代碼"]].append(r)

    # 欄位順序：商品代碼 | 交易日期 | 實際應收/付(-)金額
    for code in sorted(dividend_dict.keys()):
        lines.append(f"\n商品代碼: {code}")
        lines.append("交易日期\t實際應收付")
        records = sorted(dividend_dict[code], key=itemgetter("交易日期"))
        for r in records:
            date = r['交易日期'].replace("\n", " ").strip()
            actual = str(r['實際應收/付(-)金額']).replace("\n", " ").strip()
            lines.append(f"{date}\t{actual}")

    final_content = "\n".join(lines)

    # ------------------------------------------------------------------
    # [已保留但未使用] 原本輸出到 output.txt 檔案的程式碼
    # ------------------------------------------------------------------
    # with open("output.txt", "w", encoding="utf-8") as f:
    #     f.write(final_content)
    # ------------------------------------------------------------------
    
    return final_content # 關鍵：回傳字串供 Eel 傳給網頁

# -----------------------------
# 8️⃣ 遍歷下拉選單 (整合解析和輸出)
# -----------------------------
def process_dropdown(driver, drp_date_id, query_btn_id, top_n=3):
    all_buy = []
    all_dividend = []

    for i in range(top_n):
        select_elem = Select(driver.find_element(By.ID, drp_date_id))
        select_elem.select_by_index(i)

        driver.find_element(By.ID, query_btn_id).click()
        wait_for_element(driver, By.ID, "dataGridStock") # 等待資料載入

        # 處理資料
        buy_list, dividend_list = parse_data_grid(driver)
        all_buy.extend(buy_list)
        all_dividend.extend(dividend_list)
    
    # 最終回傳整理結果字串
    return generate_result_string(all_buy, all_dividend)

# -----------------------------
# 9️⃣ 主程式流程
# -----------------------------
def run_cathay_crawler(headless = False, NUM_MONTHS_TO_PROCESS=3):
    driver = None
    try:
        driver = init_driver(headless)
        
        # 登入
        cathay_login(driver, account="T124504388", password=cu.decrypt(config.YF_CATHAY_MIMA, config.KEY))
        
        # 導航至對帳單頁面
        switch_to_frame(driver, "tb")
        click_element(driver, By.ID, "tdmh2") # 海外帳務
        click_element(driver, By.ID, "i86")   # 對帳單
        
        # 處理資料
        switch_to_frame(driver, "sysjustdefaultdown")
        result_text = process_dropdown(driver, "drpDate", "btnQuery", top_n=NUM_MONTHS_TO_PROCESS)
        
        return result_text
        
    except Exception as e:
        # 如果出錯，回傳錯誤訊息字串
        return f"🚫 爬蟲執行中發生錯誤: {type(e).__name__}: {str(e)}"
    finally:
        if driver:
            driver.quit() # 確保瀏覽器關閉