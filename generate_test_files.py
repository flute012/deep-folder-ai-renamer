import os

def create_mock_sandbox():
    sandbox_dir = os.path.abspath(r"d:\程式\Python-各種小程式\movetofolder\辦公室測試資料夾_請用此資料夾測試")
    os.makedirs(sandbox_dir, exist_ok=True)
    
    # 1. 建立智能改名與歸檔測試檔案
    renaming_files = [
        "人事資料_張三_2025.pdf",
        "人事資料_李四_2025.pdf",
        "人事資料_王五_2025.pdf",
        "財務對帳單_客戶A_2026.xlsx",
        "財務對帳單_客戶B_2026.xlsx",
        "財務對帳單_客戶C_2026.xlsx",
    ]
    for fn in renaming_files:
        path = os.path.join(sandbox_dir, fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"這是一個測試辦公檔案: {fn}")

    # 2. 建立篩選刪除測試檔案
    trash_files = [
        "系統日誌.log",
        "舊合約_v1.bak",
        "暫存文件_202605.tmp"
    ]
    for fn in trash_files:
        path = os.path.join(sandbox_dir, fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"舊的臨時檔案: {fn}")

    # 3. 建立一對多派發用的範本資料夾
    template_dir = os.path.join(sandbox_dir, "專案公用範本")
    os.makedirs(template_dir, exist_ok=True)
    templates = ["1_專案啟動表.docx", "2_專案進度追蹤.xlsx"]
    for fn in templates:
        path = os.path.join(template_dir, fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"範本內容: {fn}")

    print("=== Success ===")
    print(f"Created sandbox directory: {sandbox_dir}")
    print("You can open File & Folder Manager V5 now and use this directory for testing!")

if __name__ == "__main__":
    create_mock_sandbox()
