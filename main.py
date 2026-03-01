# main.py

import eel
from cathayweb import run_cathay_crawler
from YF_hold import run_YF_crawler_hold 
from cathayweb_hold import run_cathay_crawler_hold

# 初始化 Eel，並指定網頁檔案的路徑 (即 'web' 資料夾)
eel.init('web')


# 使用 @eel.expose 讓 JavaScript 可以呼叫這個 Python 函數
@eel.expose
def run_scraper_async(headless = False, NUM_MONTHS_TO_PROCESS=3):
    """
    這個函數由前端呼叫，執行爬蟲邏輯並將結果回傳給網頁。
    """
    print("Python 接收到執行請求:", headless, NUM_MONTHS_TO_PROCESS)

    result_text = run_cathay_crawler(headless, NUM_MONTHS_TO_PROCESS)
    
    # 呼叫爬蟲核心，並傳入帳密

    # 將結果字串回傳給前端 JavaScript
    return result_text

@eel.expose
def open_local_file(filepath='C:/Users/paec5/OneDrive/桌面/Parser/YF_Stock_Parser_beautify.html'):
    """打開本地 HTML 檔案"""
    import os
    import webbrowser
    if os.path.exists(filepath):
        webbrowser.open(f'file:///{filepath}')
        return f'✅ 已打開 {filepath}'
    else:
        return f'❌ 檔案不存在: {filepath}'

@eel.expose
def get_inventory_report(rate, headless=False):
    # 1️⃣ 執行爬蟲
    result_usd_YF = run_YF_crawler_hold(headless)
    result_cathy = run_cathay_crawler_hold(headless)

    print(result_usd_YF)
    print(result_cathy)
    cathy_twd = result_cathy['result_twd_Cathy']
    cathy_usd = result_cathy['result_usd_Cathy(in twd)']

    # 2️⃣ 取出需要欄位並做匯率轉換
    yf_usd = result_usd_YF['result_usd_YF']
    yf_market_value = float(yf_usd['total_market_value'].replace(',', '')) * rate
    yf_profit = float(yf_usd['total_inventory_profit'].replace(',', '')) * rate
    yf_profit_rate = yf_usd['total_profit_rate_percent']

    cathy_twd_market_value = float(cathy_twd['total_market_value'].replace(',', ''))
    cathy_twd_profit = float(cathy_twd['total_inventory_profit'].replace(',', ''))
    cathy_twd_profit_rate = cathy_twd['total_profit_rate_percent']

    cathy_usd_market_value = float(cathy_usd['total_market_value'].replace(',', ''))
    cathy_usd_profit = float(cathy_usd['total_inventory_profit'].replace(',', ''))
    cathy_usd_profit_rate = cathy_usd['total_profit_rate_percent']

    # 3️⃣ 總市值與總獲益
    total_market_value = yf_market_value + cathy_usd_market_value + cathy_twd_market_value
    total_profit = yf_profit + cathy_usd_profit + cathy_twd_profit

    # 4️⃣ 建立文字報表
    report = f"""
📦 永豐美股庫存 (USD -> TWD)
-------------------------------
市值: {yf_market_value:,.2f}
獲益: {yf_profit:,.2f}
獲益率: {yf_profit_rate}

📦 國泰美股庫存 (USD in TWD)
-------------------------------
市值: {cathy_usd_market_value:,.2f}
獲益: {cathy_usd_profit:,.2f}
獲益率: {cathy_usd_profit_rate}

📦 國泰台股庫存 (TWD)
-------------------------------
市值: {cathy_twd_market_value:,.2f}
獲益: {cathy_twd_profit:,.2f}
獲益率: {cathy_twd_profit_rate}

===============================
💰 總市值: {total_market_value:,.2f}
💹 總獲益: {total_profit:,.2f}
"""

    return report


# 啟動 Eel 應用程式
if __name__ == '__main__':
    print("Eel Server 啟動中...")

    try:
        # 嘗試使用系統預設的瀏覽器/WebView 模式
        eel.start('index.html', size=(800, 700), mode='default')
    except EnvironmentError:
        # 如果找不到 Chrome 或 default 模式失敗，嘗試使用 Edge
        eel.start('index.html', size=(800, 700), mode='edge')

    # get_inventory_report(31,True)

    # from YF_hold import run_YF_crawler_hold 
    # print(run_YF_crawler_hold(True))
    # from cathayweb_hold import run_cathay_crawler_hold 
    # print(run_cathay_crawler_hold(True))