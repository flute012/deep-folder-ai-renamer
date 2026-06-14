import os


def normalize(path):
    """正規化路徑：處理斜線、控制字元、首尾空格與引號"""
    if path is None or path == '':
        return None
    try:
        if not isinstance(path, str):
            path = str(path)
        path = path.replace('\\', os.sep).replace('/', os.sep)
        path = ''.join(c for c in path if ord(c) >= 32)
        path = path.strip(' \'"')
        abs_path = os.path.abspath(os.path.normpath(path))
        
        # ── Windows 超長路徑 (MAX_PATH 260 限制) 支援機制 ──
        if os.name == 'nt' and len(abs_path) >= 240:
            if not abs_path.startswith('\\\\?\\'):
                # 排除 UNC 路徑或是已經加過的前綴，且必須是磁碟機字母開頭的路徑
                if len(abs_path) > 2 and abs_path[1] == ':' and abs_path[2] == '\\':
                    return '\\\\?\\' + abs_path
        return abs_path
    except Exception:
        return path


def safe_join(*parts):
    """安全連接路徑，支援 UNC 網路路徑"""
    try:
        parts = [normalize(str(p)) for p in parts if p]
        parts = [p for p in parts if p]
        if not parts:
            return None

        # UNC 路徑處理（\\server\share）
        if os.name == 'nt' and parts[0].startswith('\\\\'):
            unc = '\\\\' + parts[0].split('\\')[2]
            rest = [parts[0][len(unc):]] + parts[1:]
            return os.path.normpath(os.path.join(unc, *rest))

        return os.path.normpath(os.path.join(*parts))
    except Exception:
        sep = os.sep
        return sep.join([p.rstrip('\\/') for p in parts if p])


def remove_layer(path, layer_name):
    """
    移除路徑中間某一層資料夾。
    例：remove_layer('D:\\AAE\\UU\\file.txt', 'UU') → 'D:\\AAE\\file.txt'
    """
    path = normalize(path)
    parts = path.split(os.sep)
    # 找出要移除的層（只移除第一個符合的）
    try:
        idx = parts.index(layer_name)
        new_parts = parts[:idx] + parts[idx + 1:]
        return os.sep.join(new_parts)
    except ValueError:
        return path  # 找不到就原路返回


def insert_layer(path, after_layer, new_layer):
    """
    在路徑中某一層後面插入新的一層。
    例：insert_layer('D:\\AAE\\file.txt', 'AAE', 'UU') → 'D:\\AAE\\UU\\file.txt'
    """
    path = normalize(path)
    parts = path.split(os.sep)
    try:
        idx = parts.index(after_layer)
        new_parts = parts[:idx + 1] + [new_layer] + parts[idx + 1:]
        return os.sep.join(new_parts)
    except ValueError:
        return path  # 找不到就原路返回


def replace_layer(path, old_layer, new_layer):
    """
    替換路徑中某一層的名稱。
    例：replace_layer('D:\\AAE\\UU\\file.txt', 'UU', 'VV') → 'D:\\AAE\\VV\\file.txt'
    """
    path = normalize(path)
    parts = path.split(os.sep)
    try:
        idx = parts.index(old_layer)
        parts[idx] = new_layer
        return os.sep.join(parts)
    except ValueError:
        return path


def get_parts(path):
    """把路徑拆成各層清單"""
    path = normalize(path)
    return path.split(os.sep)


def pad_number(n, width=2):
    """數字補零，例：pad_number(3, 2) → '03'"""
    return str(n).zfill(width)


def batch_pad(names, width=2):
    """
    批次對名稱裡的數字補零。
    例：['1', '2', '10'] → ['01', '02', '10']
    """
    import re
    def _pad(name):
        return re.sub(r'\d+', lambda m: m.group().zfill(width), name)
    return [_pad(n) for n in names]