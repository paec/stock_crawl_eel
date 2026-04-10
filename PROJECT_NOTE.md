# eel_cathay_app Project Note

## 1) 專案定位
- 這是一個以 Eel 為核心的桌面化前後端整合工具。
- 前端是 `web/index.html + web/main.js`，後端入口是 `main.py`。
- 前端透過 `eel.js` 呼叫 Python 的 `@eel.expose` 函式，完成爬蟲執行與報表回傳。

## 2) 前端按鈕與功能清單

### 主功能按鈕
1. `#btn-tree-spirit` (樹精靈)
- 行為: 顯示/隱藏「樹精靈」條件區塊 `#condition-container`。
- 對應執行按鈕: `#btn-confirm-condition`。

2. `#btn-yf` (永豐)
- 行為: 直接呼叫後端開啟本地 HTML 報表。
- 後端橋接: `eel.open_local_file()()`。

3. `#btn-inventory` (庫存損益)
- 行為: 顯示/隱藏庫存損益條件區塊 `#condition-container-inventory`。
- 對應執行按鈕: `#btn-confirm-inventory`。

### 條件區執行按鈕
1. `#btn-confirm-condition`
- 讀取條件: `#input-month`、`.tree-headless-toggle`。
- 橋接呼叫: `eel.run_scraper_async(headless, months)()`。

2. `#btn-confirm-inventory`
- 讀取條件: `#input-rate`、`.inventory-headless-toggle`。
- 橋接呼叫: `eel.get_inventory_report(rate, headless)()`。

### 輸出區
- 顯示元件: `#output-area`。
- 用途: 顯示執行中提示、成功結果、錯誤訊息。

### 總對照表

| 前端按鈕 / 元件 | JS 事件或呼叫 | Python 對應函式 | 後端功能 |
| --- | --- | --- | --- |
| `#btn-tree-spirit` | 顯示 / 隱藏 `#condition-container` | 無 | 展開樹精靈條件區 |
| `#btn-confirm-condition` | `eel.run_scraper_async(headless, months)()` | `run_scraper_async(headless=False, NUM_MONTHS_TO_PROCESS=3)` | 執行國泰爬蟲並回傳結果 |
| `#btn-yf` | `eel.open_local_file()()` | `open_local_file(filepath=...)` | 開啟本地永豐報表 HTML |
| `#btn-inventory` | 顯示 / 隱藏 `#condition-container-inventory` | 無 | 展開庫存損益條件區 |
| `#btn-confirm-inventory` | `eel.get_inventory_report(rate, headless)()` | `get_inventory_report(rate, headless=False)` | 產生庫存損益彙總報表 |
| `#output-area` | 顯示回傳文字 | 無 | 顯示執行中訊息、成功結果、錯誤訊息 |

## 3) JS -> Python 橋接總覽 (Eel)

### 前端呼叫點 (`web/main.js`)
1. `eel.open_local_file()()`
- 觸發來源: `#btn-yf`。
- 目的: 開啟本地永豐報表頁面。

2. `eel.get_inventory_report(rate, headless)()`
- 觸發來源: `#btn-confirm-inventory`。
- 目的: 計算並回傳庫存損益文字報表。

3. `eel.run_scraper_async(headless, months)()`
- 觸發來源: `#btn-confirm-condition`。
- 目的: 執行國泰爬蟲流程並回傳結果字串。

### Python 曝露函式 (`main.py`)
1. `@eel.expose run_scraper_async(headless=False, NUM_MONTHS_TO_PROCESS=3)`
- 內部呼叫: `run_cathay_crawler(headless, NUM_MONTHS_TO_PROCESS)`。
- 回傳: 執行結果文字。

2. `@eel.expose open_local_file(filepath=...)`
- 內部行為: 使用 `webbrowser.open(file:///...)`。
- 回傳: 開啟成功/失敗訊息。

3. `@eel.expose get_inventory_report(rate, headless=False)`
- 內部呼叫:
  - `run_YF_crawler_hold(headless)`
  - `run_cathay_crawler_hold(headless)`
- 內部運算: 匯率換算、加總市值與獲益。
- 回傳: 多段文字報表。

## 4) 後端功能對應
- `cathayweb.py`:
  - 核心函式 `run_cathay_crawler(...)`，由 `run_scraper_async(...)` 使用。
- `YF_hold.py`:
  - 函式 `run_YF_crawler_hold(...)`，由 `get_inventory_report(...)` 使用。
- `cathayweb_hold.py`:
  - 函式 `run_cathay_crawler_hold(...)`，由 `get_inventory_report(...)` 使用。
- `crawl_utils.py`:
  - Selenium / driver 初始化等共用流程支援。

## 5) 流程摘要
1. 前端按鈕觸發 JS 事件。
2. JS 讀取表單條件與 toggle 值。
3. JS 呼叫 Eel bridge (`eel.xxx()()`)。
4. Python `@eel.expose` 函式執行爬蟲或報表計算。
5. 回傳字串給前端，更新 `#output-area`。

## 6) 已觀察到的注意點
1. `open_local_file()` 預設路徑是固定本機絕對路徑。
- 影響: 換機器或部署環境時容易失效，建議改為可設定值。

2. `crawl_utils.py` 目前固定使用 Chrome profile 路徑 `C:\Users\paec5\AppData\Local\Google\Chrome\User Data\ProfileForCrawl`。
- 維護方式: 需要手動把原本 `Chrome\User Data\Default` 複製一份到 `ProfileForCrawl\Default`，讓爬蟲專用 profile 跟日常手動登入的憑證狀態一致。
- 注意事項: 如果換電腦、改帳號或 Chrome 使用者資料夾位置變更，這個路徑要同步更新，否則 Selenium 可能無法帶入已註冊的證券憑證。
- 實務建議: 若瀏覽器行為異常，可先關掉所有 `chrome.exe`，再檢查 profile 是否被鎖定或損壞。

3. 帳號與密碼目前是寫死在爬蟲程式裡統一處理。
- 帳號: `cathayweb.py`、`cathayweb_hold.py`、`YF_hold.py` 都直接傳固定帳號給登入函式。
- 密碼: 真正的密碼沒有明文存放，而是先放在 `config.py` 的加密字串中，再用 `crypto_util.decrypt(..., config.KEY)` 在執行時解密。
- 流程: `main.py` 呼叫爬蟲 → 爬蟲模組呼叫 `cathay_login(...)` 或 `YF_login(...)` → 先解密密碼 → 再登入國泰或永豐。
- 注意事項: 如果要換帳號或更新密碼，通常要同時改爬蟲模組中的帳號字串，以及 `config.py` 裡的加密密碼內容，否則登入會失敗。

4. `web/main.js` 有抓取 `#btn-clear-output` 並綁定清除邏輯，但 `web/index.html` 目前沒有這個按鈕元素。
- 意思: 這個清除功能還沒真的放到畫面上，所以現在不會出現，也不算主要流程的一部分。
- 影響: 不會拋錯 (因為有 null 檢查)，但只是少了一個可選的輔助功能。

## 7) 打包與啟動
- 啟動入口: `python main.py`
- 打包指令 (README):
  - `pyinstaller --onefile --add-data "web;web" main.py`
  - 可加上 `--noconsole` 依需求調整。
