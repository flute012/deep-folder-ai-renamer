import os
import sys
import json

if getattr(sys, 'frozen', False):
    _base_dir = os.path.dirname(sys.executable)
else:
    _base_dir = os.path.dirname(__file__)

_SETTINGS_FILE = os.path.join(_base_dir, '.settings')

def load_settings():
    try:
        if os.path.exists(_SETTINGS_FILE):
            with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_settings(settings):
    try:
        with open(_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# Default language is 'en' (English)
_CURRENT_LANG = load_settings().get('lang', 'en')

def get_lang():
    global _CURRENT_LANG
    return _CURRENT_LANG

def set_lang(lang):
    global _CURRENT_LANG
    _CURRENT_LANG = lang
    settings = load_settings()
    settings['lang'] = lang
    save_settings(settings)

TRANSLATIONS = {
    'File & Folder Manager V5': {
        'en': 'File & Folder Manager V5',
        'zh': '檔案與資料夾批次管理 V5'
    },
    'AI 設定': {
        'en': 'AI Settings',
        'zh': 'AI 設定'
    },
    'LLM：': {
        'en': 'LLM: ',
        'zh': 'LLM：'
    },
    'API Key：': {
        'en': 'API Key: ',
        'zh': 'API Key：'
    },
    '記住 Key': {
        'en': 'Remember Key',
        'zh': '記住 Key'
    },
    '清除已儲存 Key': {
        'en': 'Clear Saved Key',
        'zh': '清除已儲存 Key'
    },
    '🔍 全域載入過濾器 (減少掃描時間)': {
        'en': '🔍 Global Load Filter (Faster)',
        'zh': '🔍 全域載入過濾器 (減少掃描時間)'
    },
    '名稱包含關鍵字（支援 * 和 ? 萬用字元）：': {
        'en': 'Name contains (supports * and ?):',
        'zh': '名稱包含關鍵字（支援 * 和 ? 萬用字元）：'
    },
    '排除關鍵字（以逗號區隔，至多 5 個，支援 * 和 ?）：': {
        'en': 'Exclude (comma-separated, max 5, * & ?):',
        'zh': '排除關鍵字（以逗號區隔，至多 5 個，支援 * 和 ?）：'
    },
    '區分大小寫': {
        'en': 'Case Sensitive',
        'zh': '區分大小寫'
    },
    '不限': {
        'en': 'All',
        'zh': '不限'
    },
    '限檔案': {
        'en': 'Files Only',
        'zh': '限檔案'
    },
    '限資料夾': {
        'en': 'Folders Only',
        'zh': '限資料夾'
    },
    '操作模式': {
        'en': 'Operation Mode',
        'zh': '操作模式'
    },
    '來源資料夾：': {
        'en': 'Source Folder:',
        'zh': '來源資料夾：'
    },
    '🗂️ 批次範本來源目錄：': {
        'en': '🗂️ Template Source Directory:',
        'zh': '🗂️ 批次範本來源目錄：'
    },
    '📁 預覽只載入資料夾 (排除檔案)': {
        'en': '📁 Preview Folders Only (Exclude Files)',
        'zh': '📁 預覽只載入資料夾 (排除檔案)'
    },
    '預計建立的相對路徑（支援多行、多層級）：': {
        'en': 'Relative paths to create (Supports multiline):',
        'zh': '預計建立的相對路徑（支援多行、多層級）：'
    },
    '🛠️ 巢狀結構與 AI 智慧生成器': {
        'en': '🛠️ Nested Structure & AI Generator',
        'zh': '🛠️ 巢狀結構與 AI 智慧生成器'
    },
    '最後一層數字補零，位數：': {
        'en': 'Zero-pad numbers in last layer, digits:',
        'zh': '最後一層數字補零，位數：'
    },
    'Excel 檔案 (.xlsx / .xlsm)：': {
        'en': 'Excel File (.xlsx / .xlsm):',
        'zh': 'Excel 檔案 (.xlsx / .xlsm)：'
    },
    '🔍 篩選副檔名（如 .bak，空代表不限）：': {
        'en': '🔍 Filter extension (e.g. .bak, empty for all):',
        'zh': '🔍 篩選副檔名（如 .bak，空代表不限）：'
    },
    '📝 檔名包含關鍵字（空代表不限）：': {
        'en': '📝 Filename contains (empty for all):',
        'zh': '📝 檔名包含關鍵字（空代表不限）：'
    },
    '⚠️ 警告：執行後檔案將移入隱藏暫存區！': {
        'en': '⚠️ Warning: Files will move to a hidden temp folder!',
        'zh': '⚠️ 警告：執行後檔案將移入隱藏暫存區！'
    },
    '🧹 清理暫存區 (丟至回收桶)': {
        'en': '🧹 Clear Temp Folder (Move to Recycle Bin)',
        'zh': '🧹 清理暫存區 (丟至回收桶)'
    },
    '載入預覽': {
        'en': 'Load Preview',
        'zh': '載入預覽'
    },
    '重新開始': {
        'en': 'Reset',
        'zh': '重新開始'
    },
    '瀏覽': {
        'en': 'Browse',
        'zh': '瀏覽'
    },
    '💡 可直接拖曳檔案或資料夾到輸入框': {
        'en': '💡 Drag and drop files or folders directly into inputs',
        'zh': '💡 可直接拖曳檔案或資料夾到輸入框'
    },
    '請在左側選擇資料夾，然後按「載入預覽」': {
        'en': "Please select a folder on the left and click 'Load Preview'",
        'zh': '請在左側選擇資料夾，然後按「載入預覽」'
    },
    '有任何建議或合作邀約，歡迎聯繫！': {
        'en': 'For any suggestions or cooperation, welcome to contact!',
        'zh': '有任何建議或合作邀約，歡迎聯繫！'
    },
    '錯誤': {
        'en': 'Error',
        'zh': '錯誤'
    },
    '提示': {
        'en': 'Hint',
        'zh': '提示'
    },
    '成功': {
        'en': 'Success',
        'zh': '成功'
    },
    '完成': {
        'en': 'Completed',
        'zh': '完成'
    },
    '已重置預覽與相關設定。': {
        'en': 'Preview and related settings have been reset.',
        'zh': '已重置預覽與相關設定。'
    },
    '請選擇有效的來源資料夾': {
        'en': 'Please select a valid source folder',
        'zh': '請選擇有效的來源資料夾'
    },
    '請選擇有效的 Excel 檔案': {
        'en': 'Please select a valid Excel file',
        'zh': '請選擇有效的 Excel 檔案'
    },
    '批次路徑變更確認': {
        'en': 'Batch Path Change Confirmation',
        'zh': '批次路徑變更確認'
    },
    '成功 {success} 筆，失敗 {fail} 筆': {
        'en': 'Succeeded: {success}, Failed: {fail}',
        'zh': '成功 {success} 筆，失敗 {fail} 筆'
    },
    '復原 {ok_count} / {len_batch} 筆': {
        'en': 'Undone: {ok_count} / {len_batch}',
        'zh': '復原 {ok_count} / {len_batch} 筆'
    },
    '沒有可復原的操作': {
        'en': 'No operations to undo',
        'zh': '沒有可復原的操作'
    },
    '已將暫存區資料夾 (.trash_backup) 移至資源回收桶！': {
        'en': 'Moved temp directory (.trash_backup) to Recycle Bin!',
        'zh': '已將暫存區資料夾 (.trash_backup) 移至資源回收桶！'
    },
    '移至資源回收桶失敗，資料夾可能正被其他程式佔用。': {
        'en': 'Failed to move to Recycle Bin. The directory may be in use.',
        'zh': '移至資源回收桶失敗，資料夾可能正被其他程式佔用。'
    },
    '確認清理暫存區': {
        'en': 'Confirm Clearing Temp Trash',
        'zh': '確認清理暫存區'
    },
    '確定要將暫存資料夾 (.trash_backup) 移至系統資源回收桶嗎？\n\n（移至回收桶後，主介面的「復原」按鈕將無法自動還原在此之前被篩選刪除的檔案）': {
        'en': 'Are you sure you want to move the temporary trash (.trash_backup) to the Recycle Bin?\n\n(After moving, you will not be able to undo deletion operations.)',
        'zh': '確定要將暫存資料夾 (.trash_backup) 移至系統資源回收桶嗎？\n\n（移至回收桶後，主介面的「復原」按鈕將無法自動還原在此之前被篩選刪除的檔案）'
    },
    '目前來源目錄下沒有暫存區 (.trash_backup)': {
        'en': 'No temp directory (.trash_backup) found in current source directory.',
        'zh': '目前來源目錄下沒有暫存區 (.trash_backup)'
    },
    '讀取 Excel 失敗：{e}': {
        'en': 'Failed to read Excel: {e}',
        'zh': '讀取 Excel 失敗：{e}'
    },
    'Excel 內沒有符合過濾條件的資料': {
        'en': 'No matching data found in Excel.',
        'zh': 'Excel 內沒有符合過濾條件的資料'
    },
    '找不到符合過濾條件的項目': {
        'en': 'No items found matching the filter criteria.',
        'zh': '找不到符合過濾條件的項目'
    },
    '找不到符合篩選條件的檔案': {
        'en': 'No files found matching the filter criteria.',
        'zh': '找不到符合篩選條件的檔案'
    },
    '請填入副檔名或關鍵字其中一項篩選條件': {
        'en': 'Please specify extension or keyword filter.',
        'zh': '請填入副檔名或關鍵字其中一項篩選條件'
    },
    '補零位數請填數字': {
        'en': 'Please enter a number for digit width',
        'zh': '補零位數請填數字'
    },
    '請填入預計建立的相對路徑': {
        'en': 'Please input relative paths to create',
        'zh': '請填入預計建立的相對路徑'
    },
    '符合過濾條件的範本內沒有任何項目': {
        'en': 'No items found in the template folder matching filters',
        'zh': '符合過濾條件的範本內沒有任何項目'
    },
    '清除 Key：{msg}': {
        'en': 'Clear Key: {msg}',
        'zh': '清除 Key：{msg}'
    },
    'Key 儲存：{msg}': {
        'en': 'Key Saved: {msg}',
        'zh': 'Key 儲存：{msg}'
    },
    '已清除本機儲存的 API Key': {
        'en': 'Cleared local API Keys.',
        'zh': '已清除本機儲存的 API Key'
    },
    '復原': {
        'en': 'Undo',
        'zh': '復原'
    },
    '原始路徑': {
        'en': 'Original Path',
        'zh': '原始路徑'
    },
    '原始檔名': {
        'en': 'Original Name',
        'zh': '原始檔名'
    },
    '修改後路徑': {
        'en': 'New Path',
        'zh': '修改後路徑'
    },
    '修改後檔名': {
        'en': 'New Name',
        'zh': '修改後檔名'
    },
    '原始資料夾名稱': {
        'en': 'Original Folder Name',
        'zh': '原始資料夾名稱'
    },
    '修改後資料夾名稱': {
        'en': 'New Folder Name',
        'zh': '修改後資料夾名稱'
    },
    '批次：': {
        'en': 'Batch: ',
        'zh': '批次：'
    },
    '排序 A→Z': {
        'en': 'Sort A→Z',
        'zh': '排序 A→Z'
    },
    '排序 Z→A': {
        'en': 'Sort Z→A',
        'zh': '排序 Z→A'
    },
    '🤖 請 AI 繼續預測': {
        'en': '🤖 Ask AI to Predict',
        'zh': '🤖 請 AI 繼續預測'
    },
    '☑ 全選': {
        'en': '☑ Select All',
        'zh': '☑ 全選'
    },
    '☒ 取消全選': {
        'en': '☒ Uncheck All',
        'zh': '☒ 取消全選'
    },
    '✔ 接受本頁所有預測': {
        'en': '✔ Accept Page Predictions',
        'zh': '✔ 接受本頁所有預測'
    },
    '🗑 列表移除已勾選': {
        'en': '🗑 Remove Checked',
        'zh': '🗑 列表移除已勾選'
    },
    '🗑 列表移除未勾選': {
        'en': '🗑 Remove Unchecked',
        'zh': '🗑 列表移除未勾選'
    },
    '◀ 上一頁': {
        'en': '◀ Prev Page',
        'zh': '◀ 上一頁'
    },
    '下一頁 ▶': {
        'en': 'Next Page ▶',
        'zh': '下一頁 ▶'
    },
    '第 1 / 1 頁  (共 0 筆項目)': {
        'en': 'Page 1 / 1 (0 items)',
        'zh': '第 1 / 1 頁  (共 0 筆項目)'
    },
    '✔ 接受預測': {
        'en': '✔ Accept',
        'zh': '✔ 接受預測'
    },
    '↩ 撤銷預測': {
        'en': '↩ Undo',
        'zh': '↩ 撤銷預測'
    },
    '預測筆數：': {
        'en': 'Predict count: ',
        'zh': '預測筆數：'
    },
    'AI 生成': {
        'en': 'AI Generate',
        'zh': 'AI 生成'
    },
    '📂 選擇一對多派發目的地': {
        'en': '📂 Select Distribution Destinations',
        'zh': '📂 選擇一對多派發目的地'
    },
    '（支援從檔案總管拖曳多個資料夾至下方輸入框，可手動加上子資料夾階層）': {
        'en': '(Supports drag & drop multiple folders here, and child paths)',
        'zh': '（支援從檔案總管拖曳多個資料夾至下方輸入框，可手動加上子資料夾階層）'
    },
    '🔗 套用此目標路徑': {
        'en': '🔗 Apply Destinations',
        'zh': '🔗 套用此目標路徑'
    },
    '請至少先手動修改並確認一筆資料，讓 AI 有規律可以學習！': {
        'en': 'Please manually edit and confirm at least one item so AI can learn!',
        'zh': '請至少先手動修改並確認一筆資料，讓 AI 有規律可以學習！'
    },
    '當前頁面所有項目皆已完成預測與修改！': {
        'en': 'All items on this page are predicted/modified!',
        'zh': '當前頁面所有項目皆已完成預測與修改！'
    },
    '⚠️ {llm_name} 字數超限警告 (防爆機制)': {
        'en': '⚠️ {llm_name} Token Limit Warning',
        'zh': '⚠️ {llm_name} 字數超限警告 (防爆機制)'
    },
    '【模型資訊】：{llm_desc}\n\n這極可能導致 AI 額度超限、連線逾時或回傳解析失敗。\n建議您可以將左側「批次」選單調小（例如改為 9 或 15 筆）。\n\n請問您是否堅持要繼續發送請求？': {
        'en': 'Model info: {llm_desc}\n\nThis may exceed limits, timeout, or fail parsing.\nWe suggest reducing batch size (e.g. 9 or 15).\n\nDo you still want to send request?',
        'zh': '【模型資訊】：{llm_desc}\n\n這極可能導致 AI 額度超限、連線逾時或回傳解析失敗。\n建議您可以將左側「批次」選單調小（例如改為 9 或 15 筆）。\n\n請問您是否堅持要繼續發送請求？'
    },
    '【原始路徑】': {
        'en': '【Original Path】',
        'zh': '【原始路徑】'
    },
    '【原始檔名】': {
        'en': '【Original Name】',
        'zh': '【原始檔名】'
    },
    '【新目標資料夾路徑】': {
        'en': '【New Path】',
        'zh': '【新目標資料夾路徑】'
    },
    '【新檔案名稱】': {
        'en': '【New Name】',
        'zh': '【新檔案名稱】'
    },
    '【執行所有變更】': {
        'en': '【Execute All Changes】',
        'zh': '【執行所有變更】'
    },
    '【復原上一步】': {
        'en': '【Undo Last Step】',
        'zh': '【復原上一步】'
    },
    '【匯出對照表至 Excel】': {
        'en': '【Export Map to Excel】',
        'zh': '【匯出對照表至 Excel】'
    },
    '🤖 AI 序列名稱產生器': {
        'en': '🤖 AI Sequence Generator',
        'zh': '🤖 AI 序列名稱產生器'
    },
    '命名範例（第一個項目）：': {
        'en': 'Name Example (First item):',
        'zh': '命名範例（第一個項目）：'
    },
    '例：2024年Q1  /  第一季  /  2024-01月份報告': {
        'en': 'e.g. 2024-Q1 / Q1 / 2024-01 Report',
        'zh': '例：2024年Q1  /  第一季  /  2024-01月份報告'
    },
    '主題 / 背景說明（可選填）：': {
        'en': 'Theme / Context (Optional):',
        'zh': '主題 / 背景說明（可選填）：'
    },
    '例：按季度區分的財務報表資料夾': {
        'en': 'e.g. Quarterly financial report directories',
        'zh': '例：按季度區分的財務報表資料夾'
    },
    '欲生成數量：': {
        'en': 'Quantity:',
        'zh': '欲生成數量：'
    },
    '開始生成': {
        'en': 'Generate',
        'zh': '開始生成'
    },
    '取消': {
        'en': 'Cancel',
        'zh': '取消'
    },
    '請輸入命名範例！': {
        'en': 'Please input a naming example!',
        'zh': '請輸入命名範例！'
    },
    '數量請填寫數字！': {
        'en': 'Please enter a number for quantity!',
        'zh': '數量請填寫數字！'
    },
    '請先在主畫面輸入並設定 API Key！': {
        'en': 'Please set API Key in main window first!',
        'zh': '請先在主畫面輸入並設定 API Key！'
    },
    '🤖 AI 生成中，請稍候…': {
        'en': '🤖 AI Generating, please wait...',
        'zh': '🤖 AI 生成中，請稍候…'
    },
    'AI 回傳格式不正確：{raw}': {
        'en': 'AI returned invalid format: {raw}',
        'zh': 'AI 回傳格式不正確：{raw}'
    },
    'AI 生成失敗：{e}': {
        'en': 'AI generation failed: {e}',
        'zh': 'AI 生成失敗：{e}'
    },
    '🛠️ 巢狀結構與 AI 智慧生成器': {
        'en': '🛠️ Nested Structure & AI Generator',
        'zh': '🛠️ 巢狀結構與 AI 智慧生成器'
    },
    '📋 相對路徑預覽列表（可在此手動新增、刪除、調整）：': {
        'en': '📋 Relative Paths Preview (Editable):',
        'zh': '📋 相對路徑預覽列表（可在此手動新增、刪除、調整）：'
    },
    '✔ 確定帶入主視窗': {
        'en': '✔ Apply to Main Window',
        'zh': '✔ 確定帶入主視窗'
    },
    '💡 右側框內可直接手動編輯，每行代表一個要建立的相對路徑（支援多層，用 \\ 分隔）': {
        'en': '💡 Right text is editable. Each line represents a relative path (use \\ for layers).',
        'zh': '💡 右側框內可直接手動編輯，每行代表一個要建立的相對路徑（支援多層，用 \\ 分隔）'
    },
    '第一層：主分類（每行一個）': {
        'en': 'Layer 1: Main Category (One per line)',
        'zh': '第一層：主分類（每行一個）'
    },
    '第二層：子目錄（每行一個）': {
        'en': 'Layer 2: Subdirectory (One per line)',
        'zh': '第二層：子目錄（每行一個）'
    },
    '🤖 AI 生成序列': {
        'en': '🤖 AI Gen Sequence',
        'zh': '🤖 AI 生成序列'
    },
    '啟用第三層：子子目錄（選填，如草稿/定稿）': {
        'en': 'Enable Layer 3 (Optional, e.g. Draft/Final)',
        'zh': '啟用第三層：子子目錄（選填，如草稿/定稿）'
    },
    '⚡ 產生交叉路徑組合': {
        'en': '⚡ Generate Cross Combinations',
        'zh': '⚡ 產生交叉路徑組合'
    },
    '請用白話文描述您想建立的目錄結構：': {
        'en': 'Describe directory structure in plain text:',
        'zh': '請用白話文描述您想建立的目錄結構：'
    },
    '💡 提示：越詳細越準確。例如：\n「建立專案管理、合約文件兩個主目錄，\n  每個底下各有 2024、2025 年份子目錄，\n  2024 底下再分草稿、審核中、定稿三個資料夾。」': {
        'en': 'Tip: More details yield better results. e.g.\n"Create main folders Project and Contract,\neach containing subfolders 2024 and 2025,\nand split 2024 into Draft, Review, Final."',
        'zh': '💡 提示：越詳細越準確。例如：\n「建立專案管理、合約文件兩個主目錄，\n  每個底下各有 2024、2025 年份子目錄，\n  2024 底下再分草稿、審核中、定稿三個資料夾。」'
    },
    '🤖 AI 智慧生成結構': {
        'en': '🤖 AI Generate Structure',
        'zh': '🤖 AI 智慧生成結構'
    },
    '請輸入第一層目錄！': {
        'en': 'Please input Layer 1 directories!',
        'zh': '請輸入第一層目錄！'
    },
    '請輸入目錄結構需求描述！': {
        'en': 'Please describe directory structure needs!',
        'zh': '請輸入目錄結構需求描述！'
    },
    '🤖 AI 正在規劃目錄結構，請稍候…': {
        'en': '🤖 AI planning directory structure, please wait...',
        'zh': '🤖 AI 正在規劃目錄結構，請稍候…'
    },
    '目前尚無任何路徑，請先使用左側工具生成，或手動輸入。': {
        'en': 'No paths currently. Please generate or enter manually.',
        'zh': '目前尚無任何路徑，請先使用左側工具生成，或手動輸入。'
    },
    '共 {count} 條路徑': {
        'en': 'Total {count} paths',
        'zh': '共 {count} 條路徑'
    },
    '🤖 [AI 智能連動]：正在根據您的手動範例規律，預測剩餘的 {count} 筆【{predict_type}】...': {
        'en': '🤖 [AI Smart Association]: Predicting remaining {count} items of 【{predict_type}】 based on your pattern...',
        'zh': '🤖 [AI 智能連動]：正在根據您的手動範例規律，預測剩餘的 {count} 筆【{predict_type}】...'
    },
    '✨ [AI 聯動成功]：已自動為其餘 {count} 筆項目代入預測結果。': {
        'en': '✨ [AI Prediction Success]: Auto-filled prediction for other {count} items.',
        'zh': '✨ [AI 聯動成功]：已自動為其餘 {count} 筆項目代入預測結果。'
    },
    '❌ [AI 預測失敗]：連線或解析異常。': {
        'en': '❌ [AI Prediction Failed]: Connection or parse error.',
        'zh': '❌ [AI 預測失敗]：連線或解析異常。'
    },
    'AI 預測失敗，錯誤原因如下：\n{err_msg}\n\n': {
        'en': 'AI prediction failed. Reason:\n{err_msg}\n\n',
        'zh': 'AI 預測失敗，錯誤原因如下：\n{err_msg}\n\n'
    },
    'AI 預測失敗 - 是否切換為手動模式？': {
        'en': 'AI Prediction Failed - Switch to Manual?',
        'zh': 'AI 預測失敗 - 是否切換為手動模式？'
    },
    '💥 [連線異常]：無法與 AI 伺服器建立通訊。': {
        'en': '💥 [Connection Exception]: Unable to communicate with AI server.',
        'zh': '💥 [連線異常]：無法與 AI 伺服器建立通訊。'
    },
    '偵測到有 {count} 筆項目的「目標資料夾路徑」已被變更。\n\n請問您要如何批次處理這些項目？\n\n[是 (Yes)]：批次移動檔案（搬移歸檔至新資料夾）\n[否 (No)]：批次複製檔案（原地保留，複製副本至新資料夾）\n[取消 (Cancel)]：取消本次執行': {
        'en': 'Detected {count} items with changed destination paths.\n\nHow would you like to handle these items?\n\n[Yes] Batch Move (Move files to the new folder)\n[No] Batch Copy (Keep original, copy to the new folder)\n[Cancel] Cancel this operation',
        'zh': '偵測到有 {count} 筆項目的「目標資料夾路徑」已被變更。\n\n請問您要如何批次處理這些項目？\n\n[是 (Yes)]：批次移動檔案（搬移歸檔至新資料夾）\n[否 (No)]：批次複製檔案（原地保留，複製副本至新資料夾）\n[取消 (Cancel)]：取消本次執行'
    },
    '語言設定已變更，程式即將自動重啟以套用設定。': {
        'en': 'Language settings changed, restarting application to apply...',
        'zh': '語言設定已變更，程式即將自動重啟以套用設定。'
    },
    '預計新建的完整資料夾路徑': {
        'en': 'New Folder Paths to Create',
        'zh': '預計新建的完整資料夾路徑'
    },
    '原始檔名': {
        'en': 'Original Name',
        'zh': '原始檔名'
    },
    '修改後檔名': {
        'en': 'New Name',
        'zh': '修改後檔名'
    },
    'AI 延伸新增': {
        'en': 'AI Extension',
        'zh': 'AI 延伸新增'
    },
    '＋ 新增一組': {
        'en': '+ Add Group',
        'zh': '＋ 新增一組'
    },
    '📊 生成一對多派發預覽': {
        'en': '📊 Generate Distribution Preview',
        'zh': '📊 生成一對多派發預覽'
    },
    '請先輸入或拖入目標派發資料夾路徑！': {
        'en': 'Please input or drag destination folder paths first!',
        'zh': '請先輸入或拖入目標派發資料夾路徑！'
    },
    '請輸入有效的目標派發資料夾路徑！': {
        'en': 'Please input valid destination folder paths!',
        'zh': '請輸入有效的目標派發資料夾路徑！'
    },
    '請先載入來源項目！': {
        'en': 'Please load source items first!',
        'zh': '請先載入來源項目！'
    },
    '已成功為 {sources} 筆來源項目與 {targets} 筆目標路徑，生成 {dispatches} 筆笛卡兒派發對照！': {
        'en': 'Successfully generated {dispatches} distribution items from {sources} source items and {targets} target paths!',
        'zh': '已成功為 {sources} 筆來源項目與 {targets} 筆目標路徑，生成 {dispatches} 筆笛卡兒派發對照！'
    },
    '至少保留一組': {
        'en': 'Keep at least one group',
        'zh': '至少保留一組'
    },
    '請先勾選想要從列表中移除的項目': {
        'en': 'Please check items you want to remove first.',
        'zh': '請先勾選想要從列表中移除的項目'
    },
    '已從預覽列表中批次移除 {count} 筆勾選項目': {
        'en': 'Removed {count} checked items from preview list.',
        'zh': '已從預覽列表中批次移除 {count} 筆勾選項目'
    },
    '當前頁面所有項目皆已被勾選': {
        'en': 'All items on current page are already checked.',
        'zh': '當前頁面所有項目皆已被勾選'
    },
    '已從預覽列表中批次移除 {count} 筆未勾選項目': {
        'en': 'Removed {count} unchecked items from preview list.',
        'zh': '已從預覽列表中批次移除 {count} 筆未勾選項目'
    },
    '第 {page} / {total} 頁  (共 {count} 筆項目)': {
        'en': 'Page {page} / {total}  ({count} items)',
        'zh': '第 {page} / {total} 頁  (共 {count} 筆項目)'
    },
    '請至少勾選一個項目': {
        'en': 'Please check at least one item.',
        'zh': '請至少勾選一個項目'
    },
    '有 {count} 筆未填入目標名稱，繼續會略過。是否繼續？': {
        'en': '{count} items have empty target names, they will be skipped. Proceed?',
        'zh': '有 {count} 筆未填入目標名稱，繼續會略過。是否繼續？'
    },
    '已成功接受本頁共 {count} 筆 AI 預測結果！': {
        'en': 'Accepted {count} AI predictions on this page!',
        'zh': '已成功接受本頁共 {count} 筆 AI 預測結果！'
    },
    '目前本頁沒有任何待處理的 AI 預測。': {
        'en': 'No pending AI predictions on this page.',
        'zh': '目前本頁沒有任何待處理的 AI 預測。'
    },
    '已確認 {confirmed} / {total} 筆': {
        'en': 'Confirmed {confirmed} / {total} items',
        'zh': '已確認 {confirmed} / {total} 筆'
    },
    ' (⚠️ 項目過多，僅顯示前 150 筆 / 共 {total} 筆，建議使用左側過濾器)': {
        'en': ' (⚠️ Too many items, only showing first 150 / total {total}. Filter is recommended)',
        'zh': ' (⚠️ 項目過多，僅顯示前 150 筆 / 共 {total} 筆，建議使用左側過濾器)'
    },
    '（無 API Key，純手動模式）': {
        'en': '(No API Key, manual mode)',
        'zh': '（無 API Key，純手動模式）'
    },
    '請先安裝 pandas 套件：\npip install pandas openpyxl': {
        'en': 'Please install pandas and openpyxl first:\npip install pandas openpyxl',
        'zh': '請先安裝 pandas 套件：\npip install pandas openpyxl'
    },
    '目前無任何資料可供匯出': {
        'en': 'No data available to export.',
        'zh': '目前無任何資料可供匯出'
    },
    '儲存修改對照表': {
        'en': 'Save Mapping Table',
        'zh': '儲存修改對照表'
    },
    '修改對照表已匯出至：\n{save_path}': {
        'en': 'Mapping table exported to:\n{save_path}',
        'zh': '修改對照表已匯出至：\n{save_path}'
    },
    '匯出 Excel 失敗：{e}': {
        'en': 'Export to Excel failed: {e}',
        'zh': '匯出 Excel 失敗：{e}'
    },
    '會議記錄\n合約文件\n財務報表\n人事資料\n專案管理': {
        'en': 'Meeting Minutes\nContracts\nFinancial Reports\nHR Records\nProject Management',
        'zh': '會議記錄\n合約文件\n財務報表\n人事資料\n專案管理'
    },
    '2024年Q1\n2024年Q2\n2024年Q3\n2024年Q4': {
        'en': '2024-Q1\n2024-Q2\n2024-Q3\n2024-Q4',
        'zh': '2024年Q1\n2024年Q2\n2024年Q3\n2024年Q4'
    },
    '草稿\n審核中\n定稿': {
        'en': 'Draft\nReview\nFinal',
        'zh': '草稿\n審核中\n定稿'
    },
    '例：幫我建立「人事」、「財務」、「行政」三個大目錄，\n每個底下各有 2024 和 2025 兩個年份子目錄，\n2024 底下再建「上半年」、「下半年」。': {
        'en': 'e.g. Create main folders HR, Finance, Admin.\nEach should contain subfolders 2024 and 2025.\nUnder 2024, split into 1st-Half and 2nd-Half.',
        'zh': '例：幫我建立「人事」、「財務」、「行政」三個大目錄，\n每個底下各有 2024 和 2025 兩個年份子目錄，\n2024 底下再建「上半年」、「下半年」。'
    },
    '警告': {
        'en': 'Warning',
        'zh': '警告'
    },
    '有 {count} 筆未填入目標名稱，繼續會略過。是否繼續？': {
        'en': '{count} items have empty targets and will be skipped. Proceed?',
        'zh': '有 {count} 筆未填入目標名稱，繼續會略過。是否繼續？'
    }
}

def tr(text, **kwargs):
    lang = get_lang()
    if text in TRANSLATIONS:
        translated = TRANSLATIONS[text].get(lang, text)
    else:
        translated = text
    if kwargs:
        try:
            return translated.format(**kwargs)
        except KeyError:
            pass
    return translated

def get_mode_labels():
    if get_lang() == 'zh':
        return {
            'smart_rename':  '📝 AI 改名與歸檔',
            'template_copy': '✨ 範本一對多派發',
            'mkdir':         '📂 批次建立資料夾',
            'excel':         '📊 Excel 匯入對照',
            'delete_filter': '🗑️ 條件篩選刪除',
        }
    else:
        return {
            'smart_rename':  '📝 AI Rename & Organize',
            'template_copy': '✨ Bulk Template Dispatch',
            'mkdir':         '📂 Batch Create Folders',
            'excel':         '📊 Excel Import Match',
            'delete_filter': '🗑️ Filter Delete',
        }
