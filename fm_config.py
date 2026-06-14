# ── 欄位名稱 ────────────────────────────────────────────
COL_FILE_PATH        = 'File Path'
COL_FILE             = 'File'
COL_NEW_NAME         = 'New Name'
COL_NEW_FOLDER_PATH  = 'New Folder Path'
COL_NEW_FOLDER_PATH2 = 'New Folder Path 2'
COL_NEW_FOLDER_PATH3 = 'New Folder Path 3'
COL_RENAME_FOLDER    = 'Rename Folder'

# ── LLM 設定 ─────────────────────────────────────────────
LLM_OPTIONS = ['Mistral', 'Gemini', 'Groq']

LLM_CONFIG = {
    'Mistral': {
        'url'  : 'https://api.mistral.ai/v1/chat/completions',
        'model': 'mistral-small-latest',
        'free' : True,
    },
    'Gemini': {
        'url'  : 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
        'model': 'gemini-2.0-flash',
        'free' : True,
    },
    'Groq': {
        'url'  : 'https://api.groq.com/openai/v1/chat/completions',
        'model': 'llama-3.1-8b-instant',
        'free' : True,
    },
}

# ── 操作模式 ─────────────────────────────────────────────
MODE_SMART_RENAME  = 'smart_rename'   # 智能改名與歸檔
MODE_TEMPLATE_COPY  = 'template_copy'  # 整批資料一對多派發
MODE_MKDIR          = 'mkdir'          # 批次建立資料夾
MODE_EXCEL          = 'excel'          # Excel 匯入
MODE_DELETE_FILTER  = 'delete_filter'  # 條件篩選刪除

MODE_LABELS = {
    MODE_SMART_RENAME:  '📝 智能改名與歸檔 (可同時改名、換資料夾、調層級)',
    MODE_TEMPLATE_COPY: '✨ 整批資料一對多派發 (整批範本複製到多個指定路徑)',
    MODE_MKDIR:         '📂 批次建立資料夾 (建立巢狀空目錄)',
    MODE_EXCEL:         '📊 Excel 匯入對照修改 (依外部清單批次變更)',
    MODE_DELETE_FILTER: '🗑️條件篩選刪除 (深入子資料夾篩選關鍵字)',
}

MODES_EXTENDABLE = {MODE_MKDIR, MODE_TEMPLATE_COPY}

BATCH_SIZE_OPTIONS = ['8', '10', '15', '20', '30', '50', '全部']
BATCH_SIZE_DEFAULT = '8'

AI_EXTEND_DEFAULT = 10

# ── UI 設定 ──────────────────────────────────────────────
APP_TITLE = 'File & Folder Manager V5'
WIN_SIZE  = '900x680'
BG_COLOR  = '#f7f1e4'
BTN_COLOR = '#fff7eb'