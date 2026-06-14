import os
import shutil
from path_utils import normalize, safe_join


# ── 結果物件 ──────────────────────────────────────────────
class OpResult:
    def __init__(self, success, message, undo_info=None):
        self.success   = success
        self.message   = message
        self.undo_info = undo_info  # 用於復原的資訊 dict

    def __repr__(self):
        status = 'OK' if self.success else 'FAIL'
        return f'[{status}] {self.message}'


# ── 檔案操作 ──────────────────────────────────────────────
def move_file(src, dst_dir, new_name=None):
    """
    搬移檔案到目標資料夾，可同時改名。
    dst_dir: 目標資料夾路徑
    new_name: 新檔名（不含副檔名），None 表示保留原名
    """
    src = normalize(src)
    dst_dir = normalize(dst_dir)

    if not os.path.isfile(src):
        return OpResult(False, f'找不到檔案: {src}')

    base = os.path.basename(src)
    ext  = os.path.splitext(base)[1]
    fname = (new_name + ext) if new_name else base
    dst = os.path.join(dst_dir, fname)

    try:
        os.makedirs(dst_dir, exist_ok=True)
        if os.path.exists(dst):
            return OpResult(False, f'目標已存在: {dst}')
        shutil.move(src, dst)
        return OpResult(True, f'搬移: {src} → {dst}',
                        undo_info={'op': 'move_file', 'src': dst, 'dst': src})
    except Exception as e:
        return OpResult(False, f'搬移失敗: {e}')


def copy_file(src, dst_dir, new_name=None):
    """複製檔案到目標資料夾，可同時改名。"""
    src = normalize(src)
    dst_dir = normalize(dst_dir)

    if not os.path.isfile(src):
        return OpResult(False, f'找不到檔案: {src}')

    base  = os.path.basename(src)
    ext   = os.path.splitext(base)[1]
    fname = (new_name + ext) if new_name else base
    dst   = os.path.join(dst_dir, fname)

    try:
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
        return OpResult(True, f'複製: {src} → {dst}',
                        undo_info={'op': 'copy_file', 'dst': dst})
    except Exception as e:
        return OpResult(False, f'複製失敗: {e}')


def rename_file(src_dir, old_name, new_name):
    """原地重新命名檔案（副檔名自動保留）。"""
    src_dir  = normalize(src_dir)
    src      = os.path.join(src_dir, old_name)
    ext      = os.path.splitext(old_name)[1]
    dst      = os.path.join(src_dir, new_name + ext)

    if not os.path.isfile(src):
        return OpResult(False, f'找不到檔案: {src}')
    if os.path.exists(dst):
        return OpResult(False, f'目標名稱已存在: {dst}')

    try:
        os.rename(src, dst)
        return OpResult(True, f'改名: {old_name} → {new_name + ext}',
                        undo_info={'op': 'rename_file', 'src': dst, 'dst': src})
    except Exception as e:
        return OpResult(False, f'改名失敗: {e}')


# ── 資料夾操作 ────────────────────────────────────────────
def move_folder(src, dst, rename=False):
    """
    搬移資料夾。
    rename=False：保留原資料夾名稱，移到 dst 底下
    rename=True ：直接以 dst 作為新完整路徑（含新名稱）
    """
    src = normalize(src)
    dst = normalize(dst)

    if not os.path.isdir(src):
        return OpResult(False, f'找不到資料夾: {src}')

    if not rename:
        dst = os.path.join(dst, os.path.basename(src))

    if os.path.exists(dst):
        return OpResult(False, f'目標已存在: {dst}')

    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        return OpResult(True, f'搬移資料夾: {src} → {dst}',
                        undo_info={'op': 'move_folder', 'src': dst, 'dst': src})
    except Exception as e:
        return OpResult(False, f'搬移資料夾失敗: {e}')


def copy_folder(src, dst, rename=False):
    """複製資料夾，rename 邏輯同 move_folder。"""
    src = normalize(src)
    dst = normalize(dst)

    if not os.path.isdir(src):
        return OpResult(False, f'找不到資料夾: {src}')

    if not rename:
        dst = os.path.join(dst, os.path.basename(src))

    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return OpResult(True, f'複製資料夾: {src} → {dst}',
                        undo_info={'op': 'copy_folder', 'dst': dst})
    except Exception as e:
        return OpResult(False, f'複製資料夾失敗: {e}')


def rename_folder(src, new_name):
    """原地重新命名資料夾。"""
    src    = normalize(src)
    parent = os.path.dirname(src)
    dst    = os.path.join(parent, new_name)

    if not os.path.isdir(src):
        return OpResult(False, f'找不到資料夾: {src}')
    if os.path.exists(dst):
        return OpResult(False, f'目標名稱已存在: {dst}')

    try:
        os.rename(src, dst)
        return OpResult(True, f'資料夾改名: {os.path.basename(src)} → {new_name}',
                        undo_info={'op': 'rename_folder', 'src': dst, 'dst': src})
    except Exception as e:
        return OpResult(False, f'資料夾改名失敗: {e}')


def mkdir_batch(parent, names):
    """
    在 parent 底下批次建立子資料夾。
    names: 子資料夾名稱清單，例如 ['01', '02', '03']
    回傳每筆的 OpResult 清單。
    """
    parent  = normalize(parent)
    results = []
    for name in names:
        path = os.path.join(parent, name)
        try:
            if os.path.exists(path):
                results.append(OpResult(False, f'已存在: {path}'))
            else:
                os.makedirs(path)
                results.append(OpResult(True, f'建立: {path}',
                                        undo_info={'op': 'mkdir', 'path': path}))
        except Exception as e:
            results.append(OpResult(False, f'建立失敗 {path}: {e}'))
    return results


# ── 層級調整 ──────────────────────────────────────────────
def flatten_layer(src, layer_name):
    """
    移除路徑中間某一層，把該層底下的所有內容移到上一層。
    例：D:\\AAE\\UU\\01.png，移除 UU → D:\\AAE\\01.png
    """
    src = normalize(src)
    if not os.path.exists(src):
        return OpResult(False, f'路徑不存在: {src}')

    parts = src.split(os.sep)
    if layer_name not in parts:
        return OpResult(False, f'找不到層級 "{layer_name}" 在路徑中')

    idx      = parts.index(layer_name)
    new_path = os.sep.join(parts[:idx] + parts[idx + 1:])

    try:
        if os.path.exists(new_path):
            return OpResult(False, f'目標已存在: {new_path}')
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(src, new_path)
        return OpResult(True, f'移除層級 "{layer_name}": {src} → {new_path}',
                        undo_info={'op': 'flatten', 'src': new_path, 'dst': src})
    except Exception as e:
        return OpResult(False, f'層級調整失敗: {e}')


def flatten_layer(src, layer_info):
    """
    layer_info: 格式為 "UU (第1層)" 的選單字串
    """
    import re
    src = normalize(src)
    if not os.path.exists(src):
        return OpResult(False, f'路徑不存在: {src}')

    # 從 "UU (第1層)" 解析出名稱與指定的層級 index
    match = re.match(r"(.+)\s\(第(\d+)層\)", layer_info)
    if not match:
        return OpResult(False, f'層級資訊格式錯誤: {layer_info}')
    layer_name, layer_idx = match.group(1), int(match.group(2))

    parts = src.split(os.sep)
    # 加上基礎檢查：防範索引越界或名稱不符
    if layer_idx >= len(parts) or parts[layer_idx] != layer_name:
        return OpResult(False, f'精準層級不匹配: 預期第{layer_idx}層為 {layer_name}')

    new_path = os.sep.join(parts[:layer_idx] + parts[layer_idx + 1:])

    try:
        if os.path.exists(new_path):
            return OpResult(False, f'目標已存在: {new_path}')
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(src, new_path)
        return OpResult(True, f'移除層級 "{layer_name}": {src} → {new_path}',
                        undo_info={'op': 'flatten', 'src': new_path, 'dst': src})
    except Exception as e:
        return OpResult(False, f'層級調整失敗: {e}')


def insert_layer(src, layer_info, new_layer):
    import re
    src = normalize(src)
    if not os.path.exists(src):
        return OpResult(False, f'路徑不存在: {src}')

    match = re.match(r"(.+)\s\(第(\d+)層\)", layer_info)
    if not match:
        return OpResult(False, f'層級資訊格式錯誤: {layer_info}')
    after_layer, layer_idx = match.group(1), int(match.group(2))

    parts = src.split(os.sep)
    if layer_idx >= len(parts) or parts[layer_idx] != after_layer:
        return OpResult(False, f'精準層級不匹配: 預期第{layer_idx}層為 {after_layer}')

    # 在指定的層級 index 後方插入新資料夾層
    new_parts = parts[:layer_idx + 1] + [new_layer] + parts[layer_idx + 1:]
    new_path  = os.sep.join(new_parts)

    try:
        if os.path.exists(new_path):
            return OpResult(False, f'目標已存在: {new_path}')
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(src, new_path)
        return OpResult(True, f'插入層級 "{new_layer}": {src} → {new_path}',
                        undo_info={'op': 'insert', 'src': new_path, 'dst': src})
    except Exception as e:
        return OpResult(False, f'層級插入失敗: {e}')


# ── 復原 ──────────────────────────────────────────────────
def undo(undo_info):
    """根據 OpResult.undo_info 執行復原。"""
    op = undo_info.get('op')
    try:
        if op in ('move_file', 'rename_file', 'move_folder',
                  'rename_folder', 'flatten', 'insert'):
            src = undo_info['src']
            dst = undo_info['dst']
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            return OpResult(True, f'復原成功: {src} → {dst}')

        elif op == 'copy_file':
            os.remove(undo_info['dst'])
            return OpResult(True, f'復原成功（刪除複製）: {undo_info["dst"]}')

        elif op == 'copy_folder':
            shutil.rmtree(undo_info['dst'])
            return OpResult(True, f'復原成功（刪除複製資料夾）: {undo_info["dst"]}')

        elif op == 'mkdir':
            path = undo_info['path']
            if not os.listdir(path):  # 只在資料夾是空的時候才刪
                os.rmdir(path)
                return OpResult(True, f'復原成功（刪除資料夾）: {path}')
            else:
                return OpResult(False, f'資料夾非空，無法自動復原: {path}')

        else:
            return OpResult(False, f'未知的復原操作: {op}')

    except Exception as e:
        return OpResult(False, f'復原失敗: {e}')


def clean_empty_parent_dirs(start_dir, limit_dir):
    """
    遞迴刪除空的母資料夾，直到限制的根目錄（不含該根目錄本身）。
    """
    if not limit_dir:
        return
    
    start_dir = normalize(start_dir)
    limit_dir = normalize(limit_dir)
    
    try:
        # 確保 start_dir 是 limit_dir 的子目錄（或者是其內部路徑）
        rel = os.path.relpath(start_dir, limit_dir)
        if rel.startswith('..') or rel == '.':
            return
    except Exception:
        return
        
    curr = start_dir
    while curr and curr != limit_dir:
        if os.path.exists(curr) and os.path.isdir(curr):
            try:
                # 檢查是否為空資料夾
                if not os.listdir(curr):
                    os.rmdir(curr)
                else:
                    break # 非空，停止向上清理
            except Exception:
                break
        else:
            break
        curr = os.path.dirname(curr)


def send_to_recycle_bin(path):
    """將檔案或資料夾移至系統資源回收桶 (Windows 平台)。"""
    import shutil
    if os.name != 'nt':
        # 非 Windows 平台使用 shutil 刪除（備用）
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception:
            return False

    from ctypes import Structure, byref, windll
    from ctypes.wintypes import HWND, UINT, LPCWSTR, BOOL, LPVOID

    class SHFILEOPSTRUCTW(Structure):
        _fields_ = [
            ("hwnd", HWND),
            ("wFunc", UINT),
            ("pFrom", LPCWSTR),
            ("pTo", LPCWSTR),
            ("fFlags", UINT),
            ("fAnyOperationsAborted", BOOL),
            ("hNameMappings", LPVOID),
            ("lpszProgressTitle", LPCWSTR),
        ]

    path = normalize(path)
    if not os.path.exists(path):
        return False

    # SHFileOperationW 不支援 \\?\ 延伸路徑前綴，需移除
    api_path = path
    if api_path.startswith('\\\\?\\'):
        api_path = api_path[4:]

    # Windows API 需要以雙 Null 結尾的字串 (\0\0)
    pFrom = api_path + '\0'
    fop = SHFILEOPSTRUCTW()
    fop.wFunc = 3  # FO_DELETE
    fop.pFrom = pFrom
    # FOF_ALLOWUNDO = 0x0040 (丟入回收桶而非直接刪除)
    # FOF_NOCONFIRMATION = 0x0010 (不顯示確認視窗)
    # FOF_SILENT = 0x0004 (隱藏進度條)
    fop.fFlags = 0x0040 | 0x0010 | 0x0004

    try:
        result = windll.shell32.SHFileOperationW(byref(fop))
        return result == 0
    except Exception:
        return False


