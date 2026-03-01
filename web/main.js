// eel_cathay_app/web/main.js

document.addEventListener('DOMContentLoaded', () => {
    const treeButton = document.getElementById('btn-tree-spirit');
    const btnConfirm = document.getElementById('btn-confirm-condition');
    const conditionContainer = document.getElementById('condition-container');
    const conditionContainerInventory = document.getElementById('condition-container-inventory');
    const btnConfirmInventory = document.getElementById('btn-confirm-inventory');

    // **新增：獲取清除按鈕**
    const clearButton = document.getElementById('btn-clear-output');
    const outputArea = document.getElementById('output-area');
    const spinner = document.getElementById('spinner');

    const btnTree = document.getElementById('btn-tree-spirit');

    btnTree.addEventListener('click', () => {
        conditionContainerInventory.classList.add('d-none'); // 關閉"庫存損益"條件
        conditionContainer.classList.toggle('d-none');
        if (!conditionContainer.classList.contains('d-none')) {
            setTimeout(() => {
                conditionContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    });
    if (btnConfirm) {
        btnConfirm.addEventListener('click', () => {
            // 1️⃣ 隱藏設定區塊
            conditionContainer.classList.add('d-none');

            // 2️⃣ 執行你的 Python function (eel 綁定的)
            runTreeSpirit();
        });
    }

    const btnYF = document.getElementById('btn-yf'); // 永豐按鈕
    if (btnYF) {
        btnYF.addEventListener('click', async () => {
            try {
                // 呼叫 Python 後端函數打開本地檔案
                await eel.open_local_file()();
            } catch (error) {
                outputArea.textContent = `🚫 打開檔案失敗: ${error}`;
            }
        });
    }

    const btnInventory = document.getElementById('btn-inventory');
    if (btnInventory) {
        btnInventory.addEventListener('click', () => {
            // 關閉樹精靈條件
            conditionContainer.classList.add('d-none');

            // 顯示庫存損益條件
            conditionContainerInventory.classList.toggle('d-none');

            setTimeout(() => {
                conditionContainerInventory.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }, 100);
        });
    }
    if (btnConfirmInventory) {
        btnConfirmInventory.addEventListener('click', async () => {
            
            const headless = document.querySelector(".inventory-headless-toggle").checked;
            console.log(headless)
            
            const rate = parseFloat(
                document.getElementById('input-rate').value
            ) || 31;

            // 關閉條件卡
            conditionContainerInventory.classList.add('d-none');

            outputArea.textContent = '▶️ 產生庫存損益報表中...';
            outputArea.style.color = '#ffc107';

            try {
                const result = await eel.get_inventory_report(rate, headless)();
                outputArea.textContent = result;
                outputArea.style.color = '#00ff00';
            } catch (error) {
                outputArea.textContent = `🚫 取得庫存損益失敗:\n${error}`;
                outputArea.style.color = '#dc3545';
            }
        });
    }


    // **新增：為清除按鈕添加事件監聽器**
    if (clearButton) {
        clearButton.addEventListener('click', clearOutput);
    }
    
    // **新增：清除函式**
    function clearOutput() {
        outputArea.textContent = '等待指令中...';
        // 恢復到初始的終端機綠色字體
        outputArea.style.color = '#00ff00'; 
    }
    // **新增結束**


    async function runTreeSpirit() {
        const months = parseInt(document.getElementById('input-month').value) || 3;
        const headless = document.querySelector(".tree-headless-toggle").checked;
        // 1. 鎖定按鈕並顯示載入中
        treeButton.disabled = true;
        spinner.classList.remove('visually-hidden');
        outputArea.textContent = '▶️ 正在啟動 Python 爬蟲和 Chrome Driver，請稍候...';
        outputArea.style.color = '#ffc107'; // 顯示黃色提示

        try {
            // 2. 呼叫 Python 中的 run_scraper_async 函數
            // Eel 會自動將 Python 函數的返回值傳回給這個 Promise
            const result = await eel.run_scraper_async(headless, months)();
            
            // 3. 顯示結果
            outputArea.textContent = result;
            outputArea.style.color = '#00ff00'; // 切回成功綠色

        } catch (error) {
            // 處理 Python 執行錯誤
            outputArea.textContent = `🚫 執行失敗，請檢查 Python log:\n${error}`;
            outputArea.style.color = '#dc3545'; // 顯示錯誤紅色
        } finally {
            // 4. 解鎖按鈕並隱藏載入中
            treeButton.disabled = false;
            spinner.classList.add('visually-hidden');
        }
    }
});