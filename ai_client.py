import json
import requests
from fm_config import LLM_CONFIG, MODE_TEMPLATE_COPY

# ── Prompt 組裝 ──────────────────────────────────────────────
def build_prompt(confirmed, targets, mode, log_info=None):
    """
    confirmed: 已確認的範例 list
    targets:   這批要預測的項目 list
    mode:      當前操作模式
    """
    examples = '\n'.join(f'{o} -> {n}' for o, n in confirmed)
    target_list = '\n'.join(targets)

    # 延伸建立資料夾模式
    if log_info and log_info.get('mkdir_extend_mode'):
        count = log_info.get('count', 10)
        examples_str = '\n'.join(f'- {o}' for o, _ in confirmed)
        return (
            f"你現在是一個高階資料夾結構管理專家。使用者想要在特定目錄下『憑空批次建立結構資料夾』。\n"
            f"以下是使用者提供的已有的資料夾名稱（或範例）列表：\n"
            f"{examples_str}\n\n"
            f"任務需求：\n"
            f"請根據上述的規律與風格，繼續延伸生成後續的 {count} 個資料夾名稱。\n"
            f"如果是英文課本或常見課程（例如高中英文 D01_L1_... 之後是 D02_L2_... 等），請儘量符合該版本的真實課次名稱與順序。\n"
            f"⚠️ 重要限制：同一個資料夾層級內不可能有相同名稱的子資料夾。你生成的所有名稱必須是唯一且不重複的！\n"
            f"請嚴格只回傳一個標準的 JSON 陣列，例如 [\"D03_L3_Formosa\", \"D04_L4_Lab-Grown Meat\"]，其中反斜線 \"\\\" 必須寫成雙反斜線 \"\\\\\"。不要有任何 Markdown 標記（如 ```json）或 any 說明文字。"
        )


    if log_info and log_info.get('pure_path_mode'):
        return (
            f"你現在是一個高階資料夾路徑自動化對照與歸檔專家。\n"
            f"使用者目前正在調整檔案或資料夾的「目標資料夾路徑」。以下是使用者調整的【舊路徑 -> 新目標資料夾路徑】範例規律：\n"
            f"{examples}\n\n"
            f"任務需求：\n"
            f"請精準找出對照或歸檔的規律，為下列【變更前的舊路徑】列表，預測其【變更後的新目標資料夾路徑】：\n"
            f"{target_list}\n\n"
            f"⚠️ 核心限制與引導：\n"
            f"1. 請仔細觀察【變更前的舊路徑】（特別是最後一層的檔案或資料夾名稱，如 Game1, Game1_UG 等）與【新目標資料夾路徑】之間的對應關係。\n"
            f"   - 使用者可能根據檔名的關鍵字規律（例如是否包含 'UG'），對目標資料夾進行「新增子目錄、刪除子目錄或移動路徑層級」等變更。\n"
            f"   請依此類推，精準找出其對照邏輯，將舊路徑對應到正確的目標資料夾路徑。\n"
            f"2. 預測結果必須是「資料夾路徑」，結尾絕對不能包含 any 檔案名稱或副檔名！\n"
            f"3. 特別注意：路徑中的 Windows 反斜線 \"\\\" 必須在 JSON 中寫成雙反斜線 \"\\\\\"，以防破壞格式。\n"
            f"4. ⚠️ 重要限制：同一個資料夾內不可能有相同名稱的檔案跟資料夾。請務必確保預測出的目標路徑在結合檔名後，不會在同個目錄下發生命名重複衝突！\n"
            f"請嚴格只回傳一個標準的 JSON 陣列字串，不要任何 Markdown 標記（如 ```json）或解釋廢話，格式如：[\"D:\\\\目標路徑\\\\白板\", \"D:\\\\目標路徑\\\\地屏\"]"
        )
        
    if mode == MODE_TEMPLATE_COPY:
        return (
            f'你現在是一個高階檔案自動化管理專家。使用者目前正在將整批資料進行「多路徑派發指派」。\n'
            f'請詳細觀摩使用者手動調整的【目標資料夾路徑】範例規律：\n'
            f'{examples}\n\n'
            f'任務需求：\n'
            f'1. 請根據上述規律，為下列檔案項目精準推導出最合理的【目標資料夾路徑】：\n'
            f'{target_list}\n\n'
            f'2. 嚴格邊界限制：你只需要輸出「資料夾的目錄路徑」（例如 D:\\Downloads\\普英PPT\\61004[F]\\D01_L1_The Bet），「絕對不准」在路徑末端加上任何多餘的檔名主體字串或重新命名！\n'
            f'3. Windows 反斜線安全規則：輸出路徑中的反斜線 "\\" 必須在 JSON 陣列中寫成雙反斜線 "\\\\"，以防止破壞 JSON 解析格式。\n'
            f'4. ⚠️ 重要限制：同一個資料夾內不可能有相同名稱的檔案跟資料夾。請確保分配的目標路徑與檔案名稱組合後，不會在同一目錄下產生重複的檔名或資料夾。\n\n'
            f'請嚴格只回傳一個標準的 JSON 陣列，例如 ["D:\\\\路徑\\\\A", "D:\\\\路徑\\\\B"], 絕對不要包含 ```json 等 Markdown 標籤，不要有任何前後解釋文字。'
        )
    else:
        # 改名與歸檔模式
        return (
            f'你現在是一個專業的檔案自動化管理專家。以下是使用者手動調整的改名範例規律：\n'
            f'{examples}\n\n'
            f'請根據上述的對應規律，為下列對應的檔案項目預測其「新檔名（不含副檔名）」：\n'
            f'{target_list}\n\n'
            f'⚠️ 重要限制：在同一個資料夾內，不可能有相同名稱的檔案與子資料夾。請務必確保預測產生的新檔名不會在同一個目標資料夾下發生重複命名或與現有資料夾同名！\n\n'
            f'請嚴格只回傳一個標準的 JSON 陣列，格式如下，絕對不要包含 any Markdown 標籤(如 ```json)、不要有任何說明文字：\n'
            f'["新檔名1", "新檔名2", ...]'
        )

# ── 各 LLM 呼叫 ───────────────────────────────────────────
def _call_mistral(api_key, prompt):
    cfg = LLM_CONFIG['Mistral']
    headers = { 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json' }
    body = { 'model': cfg['model'], 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 4000 }
    resp = requests.post(cfg['url'], headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content'].strip()

def _call_gemini(api_key, prompt):
    cfg = LLM_CONFIG['Gemini']
    url = f"{cfg['url']}?key={api_key}"
    body = { 'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'maxOutputTokens': 4000} }
    resp = requests.post(url, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()

def _call_groq(api_key, prompt):
    cfg = LLM_CONFIG['Groq']
    headers = { 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json' }
    body = { 'model': cfg['model'], 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 4000 }
    resp = requests.post(cfg['url'], headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content'].strip()

_CALLERS = { 'Mistral': _call_mistral, 'Gemini' : _call_gemini, 'Groq'   : _call_groq }

def predict(llm, api_key, confirmed, targets, mode, log_info=None):
    if llm not in _CALLERS: return False, f'不支援的 LLM: {llm}'
    if not api_key: return False, 'API Key 不可為空'
    if not confirmed: return False, '請至少提供一筆確認範例'
    if not targets: return False, '沒有需要預測的項目'

    prompt = build_prompt(confirmed, targets, mode, log_info)

    try:
        raw = _CALLERS[llm](api_key, prompt)
    except requests.exceptions.Timeout: return False, '請求逾時，請稍後再試'
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else '?'
        if code == 401: return False, 'API Key 無效或已過期'
        if code == 429: return False, '已超過免費額度限制，請稍後再試'
        return False, f'API 錯誤 ({code}): {e}'
    except Exception as e: return False, f'連線失敗: {e}'

    try:
        clean = raw.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        if '\\' in clean and '\\\\' not in clean:
            import re
            clean = re.sub(r'(?<!\\)\\(?!"|\\)', r'\\\\', clean)

        try:
            names = json.loads(clean)
        except json.JSONDecodeError:
            # 截斷容錯處理
            import re
            pattern = r'"(?:[^"\\]|\\.)*"'
            matches = list(re.finditer(pattern, clean))
            if matches:
                fixed_clean = '[' + ', '.join(m.group(0) for m in matches) + ']'
                names = json.loads(fixed_clean)
                print(f"⚠️ [智慧容錯]：偵測到 AI 回傳內容被截斷。已成功自動修復並載入前 {len(names)} 筆完整項目！")
            else:
                raise

        if not isinstance(names, list): return False, f'AI 回傳格式錯誤（非陣列）: {raw}'
        if len(names) == 0: return False, 'AI 回傳了空陣列，無法進行預測'
        if len(names) > len(targets):
            return False, f'AI 回傳筆數不符（預期最多 {len(targets)} 筆，收到 {len(names)} 筆）'
        return True, names
    except json.JSONDecodeError:
        return False, f'AI 回傳無法解析為 JSON: {raw}'

# ── API Key 加密儲存 ──────────────────────────────────────
import base64
import os as _os
import sys as _sys

if getattr(_sys, 'frozen', False):
    _base_dir = _os.path.dirname(_sys.executable)
else:
    _base_dir = _os.path.dirname(__file__)

_KEY_FILE = _os.path.join(_base_dir, '.api_keys')

def _derive_key():
    import hashlib
    seed = _os.environ.get('COMPUTERNAME', _os.environ.get('USERNAME', 'default')) + 'fmv5'
    raw = hashlib.sha256(seed.encode()).digest()
    return base64.urlsafe_b64encode(raw)

def save_keys(keys: dict):
    try:
        from cryptography.fernet import Fernet
        f = Fernet(_derive_key())
        data = json.dumps(keys).encode()
        encrypted = f.encrypt(data)
        with open(_KEY_FILE, 'wb') as fp: fp.write(encrypted)
        return True, '已儲存'
    except ImportError: return False, '請安裝 cryptography 套件：pip install cryptography'
    except Exception as e: return False, f'儲存失敗: {e}'

def load_keys() -> dict:
    try:
        from cryptography.fernet import Fernet
        if not _os.path.exists(_KEY_FILE): return {}
        f = Fernet(_derive_key())
        with open(_KEY_FILE, 'rb') as fp: encrypted = fp.read()
        data = f.decrypt(encrypted)
        return json.loads(data.decode())
    except Exception: return {}

def delete_keys():
    try:
        if _os.path.exists(_KEY_FILE): _os.remove(_KEY_FILE)
        return True, '已清除'
    except Exception as e: return False, f'清除失敗: {e}'