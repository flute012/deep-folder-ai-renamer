import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import shutil
import fnmatch


def match_keyword(name, pattern, case_sensitive=False):
    """
    檢查名稱是否符合關鍵字條件。
    - 預設為不區分大小寫的子字串匹配。
    - 若輸入包含 '*' 或 '?'，則使用萬用字元進行比對。
    - case_sensitive=True 時區分大小寫。
    """
    if not pattern:
        return True
    if case_sensitive:
        if '*' in pattern or '?' in pattern:
            return fnmatch.fnmatchcase(name, pattern)
        return pattern in name
    else:
        name_lower = name.lower()
        pattern_lower = pattern.lower()
        if '*' in pattern or '?' in pattern:
            return fnmatch.fnmatchcase(name_lower, pattern_lower)
        return pattern_lower in name_lower


try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False


from fm_config import (
    APP_TITLE, BG_COLOR, BTN_COLOR,
    LLM_OPTIONS,
    MODE_SMART_RENAME, MODE_TEMPLATE_COPY, MODE_MKDIR, MODE_EXCEL, MODE_DELETE_FILTER
)
from i18n import tr, get_lang, set_lang, get_mode_labels
from path_utils import normalize, batch_pad
from file_ops import (
    move_file, copy_file, rename_file, mkdir_batch, flatten_layer, insert_layer, undo, OpResult,
    move_folder, copy_folder, rename_folder, clean_empty_parent_dirs, send_to_recycle_bin
)
from ai_client import predict, save_keys, load_keys, delete_keys, build_prompt
from preview import PreviewPanel

class SlideSwitch(tk.Canvas):
    def __init__(self, parent, current_lang, callback=None):
        super().__init__(parent, width=110, height=28, bg=BG_COLOR, highlightthickness=0, bd=0, cursor='hand2')
        self.current_lang = current_lang
        self.callback = callback
        self.animating = False
        
        self.bg_track = '#E2DDD2'
        self.bg_handle = '#2563EB'
        self.color_active = 'white'
        self.color_inactive = '#6B5C3E'
        
        self.x_en = 28
        self.x_zh = 82
        self.current_x = self.x_en if current_lang == 'en' else self.x_zh
        
        # Track background
        self.track_id = self.create_line(14, 14, 96, 14, width=28, fill=self.bg_track, capstyle='round')
        
        # Sliding handle
        self.handle_id = self.create_line(self.current_x - 15, 14, self.current_x + 15, 14, width=22, fill=self.bg_handle, capstyle='round')
        
        # Texts
        fill_en = self.color_active if current_lang == 'en' else self.color_inactive
        fill_zh = self.color_active if current_lang == 'zh' else self.color_inactive
        
        self.text_en_id = self.create_text(self.x_en, 14, text='EN', fill=fill_en, font=('Arial', 9, 'bold'))
        self.text_zh_id = self.create_text(self.x_zh, 14, text='繁中', fill=fill_zh, font=('Arial', 9, 'bold'))
        
        self.bind('<Button-1>', self._on_click)
        
    def _on_click(self, event):
        if self.animating:
            return
            
        if self.current_lang == 'en':
            new_lang = 'zh'
            target_x = self.x_zh
        else:
            new_lang = 'en'
            target_x = self.x_en
            
        self.current_lang = new_lang
        self.animating = True
        
        if new_lang == 'en':
            self.itemconfig(self.text_en_id, fill=self.color_active)
            self.itemconfig(self.text_zh_id, fill=self.color_inactive)
        else:
            self.itemconfig(self.text_en_id, fill=self.color_inactive)
            self.itemconfig(self.text_zh_id, fill=self.color_active)
            
        self._animate_slide(self.current_x, target_x)
        
    def _animate_slide(self, current_x, target_x, step=6):
        if current_x == target_x:
            self.current_x = target_x
            self.animating = False
            if self.callback:
                self.callback(self.current_lang)
            return
            
        if current_x < target_x:
            new_x = min(current_x + step, target_x)
        else:
            new_x = max(current_x - step, target_x)
            
        self.coords(self.handle_id, new_x - 15, 14, new_x + 15, 14)
        self.after(15, lambda: self._animate_slide(new_x, target_x, step))

class App(TkinterDnD.Tk if HAS_DND else tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(tr(APP_TITLE))
        self.configure(bg=BG_COLOR)
        self.resizable(True, True)
        self.after(0, lambda: self.state('zoomed'))

        self._undo_stack = []
        self._llm_var    = tk.StringVar(value=LLM_OPTIONS[0])
        self._api_keys   = load_keys()
        self._save_key   = tk.BooleanVar(value=bool(self._api_keys))
        self._mode_var   = tk.StringVar(value=MODE_SMART_RENAME)
        self._preview    = None

        self._apply_drop_support()
        self._build()

    def _has_key(self):
        return bool(self._key_entry.get().strip())

    def _build(self):
        self._left = tk.Frame(self, bg=BG_COLOR, width=320)
        self._left.pack(side='left', fill='y', padx=(12,6), pady=12)
        self._left.pack_propagate(False)

        self._right = tk.Frame(self, bg=BG_COLOR)
        self._right.pack(side='left', fill='both', expand=True, padx=(6,12), pady=12)

        self._build_left(self._left)
        self._build_right(self._right)

    def _build_left(self, parent):
        sec = self._section(parent, tr('AI 設定'))
        tk.Label(sec, text=tr('LLM：'), bg=BG_COLOR).grid(row=0, column=0, sticky='w')
        ttk.Combobox(sec, textvariable=self._llm_var, values=LLM_OPTIONS, state='readonly', width=12).grid(row=0, column=1, sticky='w', padx=4)

        tk.Label(sec, text=tr('API Key：'), bg=BG_COLOR).grid(row=1, column=0, sticky='w', pady=(6,0))
        self._key_entry = tk.Entry(sec, show='●', width=22, font=('Arial', 10))
        self._key_entry.grid(row=1, column=1, sticky='w', padx=4, pady=(6,0), ipady=3)
        self._key_entry.bind('<KeyRelease>', self._on_key_entry_change)
        self._llm_var.trace_add('write', self._on_llm_change)
        self._fill_key()

        btn_frame = tk.Frame(sec, bg=BG_COLOR)
        btn_frame.grid(row=2, column=1, sticky='w', padx=4, pady=(2,0))
        tk.Checkbutton(btn_frame, text=tr('記住 Key'), variable=self._save_key, bg=BG_COLOR, command=self._on_save_key_toggle).pack(side='left', padx=(0, 6))
        tk.Button(btn_frame, text=tr('清除已儲存 Key'), command=self._clear_keys, bg=BTN_COLOR, relief='flat', padx=6).pack(side='left')

        sec_filter = self._section(parent, tr('🔍 全域載入過濾器 (減少掃描時間)'))
        tk.Label(sec_filter, text=tr('名稱包含關鍵字（支援 * 和 ? 萬用字元）：'), bg=BG_COLOR).pack(anchor='w')
        self._global_kw_var = tk.StringVar()
        tk.Entry(sec_filter, textvariable=self._global_kw_var, width=28, font=('Arial', 10)).pack(anchor='w', pady=2, ipady=3)

        tk.Label(sec_filter, text=tr('排除關鍵字（以逗號區隔，至多 5 個，支援 * 和 ?）：'), bg=BG_COLOR).pack(anchor='w', pady=(4,0))
        self._exclude_kw_var = tk.StringVar()
        tk.Entry(sec_filter, textvariable=self._exclude_kw_var, width=28, font=('Arial', 10)).pack(anchor='w', pady=2, ipady=3)

        self._case_sensitive_var = tk.BooleanVar(value=False)
        tk.Checkbutton(sec_filter, text=tr('區分大小寫'), variable=self._case_sensitive_var, bg=BG_COLOR).pack(anchor='w')

        self._filter_type_var = tk.StringVar(value='all')
        type_frame = tk.Frame(sec_filter, bg=BG_COLOR)
        type_frame.pack(anchor='w', pady=2)
        tk.Radiobutton(type_frame, text=tr('不限'), variable=self._filter_type_var, value='all', bg=BG_COLOR).pack(side='left')
        tk.Radiobutton(type_frame, text=tr('限檔案'), variable=self._filter_type_var, value='file', bg=BG_COLOR).pack(side='left', padx=4)
        tk.Radiobutton(type_frame, text=tr('限資料夾'), variable=self._filter_type_var, value='dir', bg=BG_COLOR).pack(side='left')

        sec2 = self._section(parent, tr('操作模式'))
        for i, (mode, label) in enumerate(get_mode_labels().items()):
            tk.Radiobutton(sec2, text=label, variable=self._mode_var, value=mode, bg=BG_COLOR, command=self._on_mode_change, anchor='w', wraplength=260, justify='left').grid(row=i, column=0, sticky='w', pady=1)

        self._input_frame = tk.Frame(parent, bg=BG_COLOR)
        self._input_frame.pack(fill='x', pady=(8,0))
        self._build_input()

        tk.Label(parent, text=tr('💡 可直接拖曳檔案或資料夾到輸入框'), bg=BG_COLOR, fg='#64748B', font=('Arial', 8), wraplength=260, justify='left').pack(anchor='w', pady=(8,0))

        # ── 聯繫資訊 (底部) ──
        spacer = tk.Frame(parent, bg=BG_COLOR)
        spacer.pack(fill='both', expand=True)

        about_frame = tk.Frame(parent, bg='#EDE9DB', relief='flat', bd=0, padx=10, pady=8)
        about_frame.pack(fill='x', side='bottom', pady=(8, 0))

        tk.Frame(about_frame, bg='#C8B98A', height=1).pack(fill='x', pady=(0, 6))
        tk.Label(about_frame, text='✦ File & Folder Manager V5', bg='#EDE9DB', fg='#6B5C3E',
                 font=('Arial', 9, 'bold')).pack(anchor='w')
        tk.Label(about_frame, text='by Zelene Lai', bg='#EDE9DB', fg='#8B7D62',
                 font=('Arial', 8, 'italic')).pack(anchor='w')
        tk.Label(about_frame, text='📧 elaboratec2@gmail.com', bg='#EDE9DB', fg='#6B5C3E',
                 font=('Arial', 8), cursor='hand2').pack(anchor='w', pady=(4, 0))
        tk.Label(about_frame, text='🧵 Threads @zelenelai', bg='#EDE9DB', fg='#6B5C3E',
                 font=('Arial', 8), cursor='hand2').pack(anchor='w')
        tk.Label(about_frame, text=tr('有任何建議或合作邀約，歡迎聯繫！'), bg='#EDE9DB', fg='#A0926F',
                 font=('Arial', 7), wraplength=260).pack(anchor='w', pady=(4, 0))

        # ── 語系切換 (放在自我介紹前) ──
        lang_container = tk.Frame(parent, bg=BG_COLOR)
        lang_container.pack(fill='x', side='bottom', pady=(8, 0))

        tk.Label(lang_container, text=tr('語言 / Language：'), bg=BG_COLOR, fg='#6B5C3E', font=('Arial', 9, 'bold')).pack(side='left', padx=(10, 8))
        self.lang_switch = SlideSwitch(lang_container, get_lang(), self._on_language_switch)
        self.lang_switch.pack(side='left')

    def _build_right(self, parent):
        self._preview_frame = tk.Frame(parent, bg=BG_COLOR)
        self._preview_frame.pack(fill='both', expand=True)
        tk.Label(self._preview_frame, text=tr('請在左側選擇資料夾，然後按「載入預覽」'), bg=BG_COLOR, fg='#94A3B8', font=('Arial', 10)).pack(expand=True)

    def _clear_input(self):
        for w in self._input_frame.winfo_children(): w.destroy()

    def _clear_preview(self):
        for w in self._preview_frame.winfo_children(): w.destroy()
        tk.Label(self._preview_frame, text=tr('請在左側選擇資料夾，然後按「載入預覽」'), bg=BG_COLOR, fg='#94A3B8', font=('Arial', 10)).pack(expand=True)
        self._preview = None
        self._update_undo_button_state()

    def _restart_app(self):
        self._clear_preview()
        self._undo_stack = []
        if hasattr(self, '_src_dir_cache'):
            try:
                del self._src_dir_cache
            except AttributeError:
                pass
        if hasattr(self, '_excel_var'):
            self._excel_var.set('')
        if hasattr(self, '_mkdir_names') and self._mkdir_names.winfo_exists():
            self._mkdir_names.delete('1.0', 'end')
            placeholder = "HK1\\lesson1\\game\nHK1\\lesson1\\sound\nHK1\\lesson2\\video\nHK2\\backup"
            self._mkdir_names.insert('1.0', placeholder)
            self._mkdir_names.config(fg='#94A3B8')
        if hasattr(self, '_del_ext_var'):
            self._del_ext_var.set('')
        if hasattr(self, '_del_kw_var'):
            self._del_kw_var.set('')
        if hasattr(self, '_global_kw_var'):
            self._global_kw_var.set('')
        if hasattr(self, '_exclude_kw_var'):
            self._exclude_kw_var.set('')
        self._log_msg(tr("已重置預覽與相關設定。"))

    def _path_row(self, parent, label, attr):
        tk.Label(parent, text=label, bg=BG_COLOR).pack(anchor='w')
        row = tk.Frame(parent, bg=BG_COLOR)
        row.pack(fill='x')
        var = tk.StringVar()
        setattr(self, attr, var)
        e = tk.Entry(row, textvariable=var, width=26, font=('Arial', 10))
        e.pack(side='left', fill='x', expand=True, ipady=4)
        self._bind_drop(e, var)
        tk.Button(row, text=tr('瀏覽'), command=lambda v=var: self._browse_dir(v), bg=BTN_COLOR, relief='flat', pady=2).pack(side='left', padx=2)
        return var

    def _build_input(self):
        self._clear_input()
        f      = self._input_frame
        mode   = self._mode_var.get()

        if mode == MODE_TEMPLATE_COPY:
            self._path_row(f, tr('🗂️ 批次範本來源目錄：'), '_src_dir_var')
        else:
            self._path_row(f, tr('來源資料夾：'), '_src_dir_var')

        if mode == MODE_SMART_RENAME:
            self._only_dir_var = tk.BooleanVar(value=False)
            tk.Checkbutton(f, text=tr('📁 預覽只載入資料夾 (排除檔案)'), variable=self._only_dir_var, bg=BG_COLOR, fg='#2563EB', font=('Arial', 9, 'bold')).pack(anchor='w', pady=(4,0))

        if mode == MODE_MKDIR:
            def set_text_hint(widget, text):
                widget.insert('1.0', text)
                widget.config(fg='#94A3B8')
                widget.bind('<FocusIn>', lambda e: widget.delete('1.0', 'end') or widget.config(fg='#000000') if widget.get('1.0', 'end-1c') == text else None)
                widget.bind('<FocusOut>', lambda e: widget.insert('1.0', text) or widget.config(fg='#94A3B8') if not widget.get('1.0', 'end-1c').strip() else None)

            tk.Label(f, text=tr('預計建立的相對路徑（支援多行、多層級）：'), bg=BG_COLOR).pack(anchor='w', pady=(6,0))
            tk.Button(f, text=tr('🛠️ 巢狀結構與 AI 智慧生成器'), command=self._open_mkdir_generator, bg='#e7edaf', font=('Arial', 9, 'bold'), relief='flat', pady=4).pack(anchor='w', fill='x', pady=(2,4))
            self._mkdir_names = tk.Text(f, height=10, width=28)
            self._mkdir_names.pack(anchor='w')
            placeholder = "HK1\\lesson1\\game\nHK1\\lesson1\\sound\nHK1\\lesson2\\video\nHK2\\backup"
            set_text_hint(self._mkdir_names, placeholder)

            pad_row = tk.Frame(f, bg=BG_COLOR)
            pad_row.pack(anchor='w', pady=(4,0))
            self._pad_var = tk.BooleanVar(value=False)
            tk.Checkbutton(pad_row, text=tr('最後一層數字補零，位數：'), variable=self._pad_var, bg=BG_COLOR).pack(side='left')
            self._pad_width = tk.StringVar(value='2')
            tk.Entry(pad_row, textvariable=self._pad_width, width=4).pack(side='left')

        if mode == MODE_EXCEL:
            tk.Label(f, text=tr('Excel 檔案 (.xlsx / .xlsm)：'), bg=BG_COLOR).pack(anchor='w')
            row = tk.Frame(f, bg=BG_COLOR)
            row.pack(fill='x')
            self._excel_var = tk.StringVar()
            e = tk.Entry(row, textvariable=self._excel_var, width=26, font=('Arial', 10))
            e.pack(side='left', fill='x', expand=True, ipady=4)
            self._bind_drop(e, self._excel_var)
            tk.Button(row, text=tr('瀏覽'), command=self._browse_excel, bg=BTN_COLOR, relief='flat', pady=2).pack(side='left', padx=2)

        if mode == MODE_DELETE_FILTER:
            tk.Label(f, text=tr('🔍 篩選副檔名（如 .bak，空代表不限）：'), bg=BG_COLOR).pack(anchor='w', pady=(4,0))
            self._del_ext_var = tk.StringVar()
            tk.Entry(f, textvariable=self._del_ext_var, width=24, font=('Arial', 10)).pack(anchor='w', ipady=3)
            tk.Label(f, text=tr('📝 檔名包含關鍵字（空代表不限）：'), bg=BG_COLOR).pack(anchor='w', pady=(4,0))
            self._del_kw_var = tk.StringVar()
            tk.Entry(f, textvariable=self._del_kw_var, width=24, font=('Arial', 10)).pack(anchor='w', ipady=3)
            tk.Label(f, text=tr('⚠️ 警告：執行後檔案將移入隱藏暫存區！'), fg='#EF4444', bg=BG_COLOR, font=('Arial', 9, 'bold')).pack(anchor='w', pady=(6,0))
            tk.Button(f, text=tr('🧹 清理暫存區 (丟至回收桶)'), command=self._clean_trash_backup, bg='#FEE2E2', fg='#EF4444', font=('Arial', 9, 'bold'), relief='flat', pady=4).pack(anchor='w', fill='x', pady=(6,0))

        btn_row = tk.Frame(f, bg=BG_COLOR)
        btn_row.pack(anchor='w', fill='x', pady=(10,0))
        tk.Button(btn_row, text=tr('載入預覽'), bg='#2563EB', fg='white', relief='flat', padx=10, pady=4, command=self._load_preview).pack(side='left')
        tk.Button(btn_row, text=tr('重新開始'), bg='#64748B', fg='white', relief='flat', padx=10, pady=4, command=self._restart_app).pack(side='left', padx=6)

    def _open_mkdir_generator(self):
        from mkdir_generator import MkdirGeneratorDialog
        def on_apply(text):
            self._mkdir_names.delete('1.0', 'end')
            self._mkdir_names.config(fg='#000000')
            self._mkdir_names.insert('1.0', text)
            self._load_preview()
        MkdirGeneratorDialog(self, on_apply)

    def _on_mode_change(self):
        self._build_input()

    def _load_preview(self):
        mode = self._mode_var.get()

        if mode == MODE_EXCEL:
            self._load_excel()
            return

        src = normalize(getattr(self, '_src_dir_var', tk.StringVar()).get())
        if not src or not os.path.isdir(src):
            messagebox.showerror(tr('錯誤'), tr('請選擇有效的來源資料夾'))
            return

        kw_filter      = self._global_kw_var.get().strip()
        exclude_raw    = self._exclude_kw_var.get().strip()
        import re
        exclude_kws = [k.strip() for k in re.split(r'[,，]', exclude_raw) if k.strip()][:5]
        filter_type    = self._filter_type_var.get()
        case_sensitive = self._case_sensitive_var.get()

        def should_keep(name, is_directory):
            if kw_filter and not match_keyword(name, kw_filter, case_sensitive): return False
            for ex_kw in exclude_kws:
                if match_keyword(name, ex_kw, case_sensitive): return False
            if filter_type == 'file' and is_directory: return False
            if filter_type == 'dir' and not is_directory: return False
            return True

        if mode == MODE_SMART_RENAME:
            entries = []
            only_dir = getattr(self, '_only_dir_var', tk.BooleanVar()).get()
            
            for root, dirs, files in os.walk(src):
                if not only_dir:
                    for f in files:
                        rel_file = os.path.relpath(os.path.join(root, f), src)
                        if should_keep(f, is_directory=False): entries.append(rel_file)
                for d in dirs:
                    rel_dir = os.path.relpath(os.path.join(root, d), src)
                    if should_keep(d, is_directory=True): entries.append(rel_dir)
            label = '項目'

        elif mode == MODE_TEMPLATE_COPY:
            entries = []
            only_dir = getattr(self, '_only_dir_var', tk.BooleanVar()).get()
            
            for root, dirs, files in os.walk(src):
                if not only_dir:
                    for f in files:
                        if should_keep(f, is_directory=False):
                            entries.append(os.path.relpath(os.path.join(root, f), src))
                for d in dirs:
                    if should_keep(d, is_directory=True):
                        entries.append(os.path.relpath(os.path.join(root, d), src))
            if not entries:
                messagebox.showerror(tr('錯誤'), tr('符合過濾條件的範本內沒有任何項目'))
                self._clear_preview()
                return
            self._src_dir_cache = src
            items = [(os.path.join(src, e), os.path.join("目標客戶路徑", e)) for e in entries]
            self._refresh_preview(items)
            return

        elif mode == MODE_MKDIR:
            raw = self._mkdir_names.get('1.0', 'end').strip()
            is_placeholder = (self._mkdir_names.cget('fg') == '#94A3B8' or self._mkdir_names.cget('fg') == '#94a3b8')
            if is_placeholder:
                raw = ""
            names = [n.strip() for n in raw.splitlines() if n.strip()]
            if not names:
                messagebox.showerror(tr('錯誤'), tr('請填入預計建立的相對路徑'))
                self._clear_preview()
                return
            if self._pad_var.get():
                try:
                    padded_names = []
                    for name in names:
                        parts = name.split(os.sep)
                        if parts:
                            parts[-1] = batch_pad([parts[-1]], int(self._pad_width.get()))[0]
                            padded_names.append(os.sep.join(parts))
                        else:
                            padded_names.append(name)
                    names = padded_names
                except ValueError:
                    messagebox.showerror(tr('錯誤'), tr('補零位數請填數字'))
                    return
            items = []
            for name in names:
                last_part = os.path.basename(name)
                if should_keep(last_part, is_directory=True):
                    full_p = os.path.normpath(os.path.join(src, name))
                    items.append((full_p, ''))
            self._src_dir_cache  = src
            self._refresh_preview(items)
            return

        elif mode == MODE_DELETE_FILTER:
            ext_target = self._del_ext_var.get().strip().lower()
            kw_target  = self._del_kw_var.get().strip()
            if not ext_target and not kw_target:
                messagebox.showwarning(tr('提示'), tr('請填入副檔名或關鍵字其中一項篩選條件'))
                return
            items = []
            for root, dirs, files in os.walk(src):
                for f_name in files:
                    if ext_target and not f_name.lower().endswith(ext_target): continue
                    if kw_target and not match_keyword(f_name, kw_target, case_sensitive): continue
                    if not should_keep(f_name, is_directory=False): continue
                    full_path = os.path.join(root, f_name)
                    items.append((full_path, os.path.join(root, "【即將刪除】" + f_name)))
            if not items:
                messagebox.showinfo(tr('提示'), tr('找不到符合篩選條件的檔案'))
                self._clear_preview()
                return
            self._src_dir_cache = src
            self._refresh_preview(items)
            return

        if not entries:
            messagebox.showinfo(tr('提示'), tr('找不到符合過濾條件的項目'))
            self._clear_preview()
            return

        items = [(os.path.join(src, e), os.path.join(src, e)) for e in entries]
        self._src_dir_cache = src
        
        if self._preview and self._preview.winfo_exists() and getattr(self._preview, '_mode', None) == mode:
            only_dir = False
            if mode == MODE_SMART_RENAME: only_dir = getattr(self, '_only_dir_var', tk.BooleanVar()).get()
            self._preview.load_items(items, has_key=self._has_key(), is_only_dir=only_dir)
            self._update_undo_button_state()
        else:
            self._refresh_preview(items)

    def _load_excel(self):
        path = normalize(getattr(self, '_excel_var', tk.StringVar()).get())
        if not path or not os.path.isfile(path):
            messagebox.showerror(tr('錯誤'), tr('請選擇有效的 Excel 檔案'))
            return
        try:
            import pandas as pd
            from fm_config import COL_FILE, COL_NEW_NAME
            df    = pd.read_excel(path, dtype=str).fillna('')
            items = []
            kw_filter = self._global_kw_var.get().strip()
            exclude_raw = self._exclude_kw_var.get().strip()
            import re
            exclude_kws = [k.strip() for k in re.split(r'[,，]', exclude_raw) if k.strip()][:5]
            case_sensitive = self._case_sensitive_var.get()
            cols = list(df.columns)

            has_cn_path = '原始路徑' in cols
            cn_src_name_col = None
            cn_dst_name_col = None
            for c in cols:
                if c in ('原始檔名', '原始資料夾名稱'):
                    cn_src_name_col = c
                if c in ('修改後檔名', '修改後資料夾名稱'):
                    cn_dst_name_col = c

            use_cn_format = has_cn_path and cn_src_name_col is not None

            for _, row in df.iterrows():
                if use_cn_format:
                    s_path = str(row.get('原始路徑', '')).strip()
                    s_name = str(row.get(cn_src_name_col, '')).strip()
                    d_path = str(row.get('修改後路徑', '')).strip()
                    d_name = str(row.get(cn_dst_name_col, '')).strip() if cn_dst_name_col else ''

                    if not s_name and not s_path:
                        continue
                    old = os.path.join(s_path, s_name) if s_path else s_name
                    new = os.path.join(d_path, d_name) if d_path else d_name
                    if not new:
                        new = old
                else:
                    old = str(row.get(COL_FILE, '')).strip()
                    new = str(row.get(COL_NEW_NAME, '')).strip()

                if old:
                    if kw_filter and not match_keyword(old, kw_filter, case_sensitive): continue
                    is_excluded = False
                    for ex_kw in exclude_kws:
                        if match_keyword(old, ex_kw, case_sensitive):
                            is_excluded = True
                            break
                    if is_excluded: continue
                    items.append((old, new if new else old))
            if not items:
                messagebox.showinfo(tr('提示'), tr('Excel 內沒有符合過濾條件的資料'))
                self._clear_preview()
                return
            self._refresh_preview(items)
        except Exception as e:
            messagebox.showerror(tr('錯誤'), tr('讀取 Excel 失敗：{e}', e=e))

    def _refresh_preview(self, items):
        only_dir = False
        if self._mode_var.get() == MODE_SMART_RENAME:
            only_dir = getattr(self, '_only_dir_var', tk.BooleanVar()).get()
        for w in self._preview_frame.winfo_children(): w.destroy()
        self._preview = PreviewPanel(
            self._preview_frame, items, mode=self._mode_var.get(),
            on_predict_cb=self._do_predict, on_execute_cb=self._do_execute,
            on_undo_cb=self._do_undo, has_key=self._has_key(), is_only_dir=only_dir,
            selected_llm_cb=lambda: self._llm_var.get()
        )
        self._preview.pack(fill='both', expand=True)
        self._update_undo_button_state()

    def _do_predict(self, confirmed, targets, callback, log_info=None):
        llm = self._llm_var.get()
        key = self._key_entry.get().strip()
        if not key: return
        if self._save_key.get(): self._persist_current_key()

        current_mode = self._mode_var.get()
        
        print(f"\n=================== [發送 AI 聯動請求 (僅後端除錯看得到)] ===================")
        if log_info:
            print(f"【變更欄位】：{log_info.get('type', '未知')}")
            print(f"   ● 修改項目：{log_info.get('name', '檔案')}")
            print(f"   ● 變更內容：{log_info.get('detail', '')}")
        else:
            print(f"【變更狀態】：已獲取參考範本共 {len(confirmed)} 筆")

        out_prompt = build_prompt(confirmed, targets, current_mode, log_info)
        print(f"【傳送給 AI 的完整規律 Prompt】：\n{out_prompt}")
        print(f"======================================================================\n")

        predict_type = "目錄路徑" if current_mode == MODE_TEMPLATE_COPY or (log_info and log_info.get('is_path')) else "檔案名稱"
        self._log_msg(f"🤖 [AI 智能連動]：正在根據您的手動範例規律，預測剩餘的 {count} 筆【{predict_type}】...', count=len(targets), predict_type=predict_type")

        def run():
            try:
                ok, result = predict(llm, key, confirmed, targets, current_mode, log_info)
                if ok:
                    print(f"✨ [AI 聯動預測成功對照清單]")
                    if current_mode == MODE_TEMPLATE_COPY or (log_info and log_info.get('is_path')):
                        for tgt, res_p in zip(targets, result): print(f"   [路徑推導] {tgt} ──> {res_p}")
                    else:
                        for tgt, res_n in zip(targets, result): print(f"   [檔名推導] {tgt} ──> {res_n}")
                    print("======================================================================\n")

                    self.after(0, lambda: self._log_msg(tr("✨ [AI 聯動成功]：已自動為其餘 {count} 筆項目代入預測結果。", count=len(targets))))
                    self.after(0, lambda: callback(targets, result))
                else:
                    print(f"❌ [AI 回傳錯誤]：{result}")
                    self.after(0, lambda: self._log_msg(tr("❌ [AI 預測失敗]：連線或解析異常。")))
                    
                    def handle_error(err_msg):
                        msg = tr("AI 預測失敗，錯誤原因如下：\n{err_msg}\n\n", err_msg=err_msg)
                        if "額度" in err_msg or "429" in err_msg or "limit" in err_msg.lower():
                            msg += "偵測到 API 額度可能已達上限或超出頻率限制。\n\n"
                        msg += "請問您是否要將目前面板暫時切換為「手動操作模式」？\n（此操作將清除目前輸入的 API Key，讓您接下來以手動方式處理，且已修改/預測好的內容均會為您保留）"
                        
                        ans = messagebox.askyesno(tr("AI 預測失敗 - 是否切換為手動模式？"), msg)
                        if ans:
                            self._key_entry.delete(0, 'end')
                            self._on_key_entry_change()
                            self._log_msg("ℹ️ 已自動切換為手動操作模式。")
                            
                    self.after(0, lambda: handle_error(result))
            except Exception as ex:
                print(f"💥 [連線異常崩潰]：{ex}")
                self.after(0, lambda: self._log_msg(tr("💥 [連線異常]：無法與 AI 伺服器建立通訊。")))
                
        threading.Thread(target=run, daemon=True).start()

    def _do_execute(self, checked_items):
        mode       = self._mode_var.get()
        results    = []
        undo_batch = []

        batch_path_action = None
        if mode == MODE_SMART_RENAME or mode == MODE_EXCEL:
            changed_items = []
            for src_path, src_name, dst_path, dst_name in checked_items:
                if normalize(dst_path) != normalize(src_path):
                    changed_items.append(src_name)
            
            if len(changed_items) > 0:
                ans = messagebox.askyesnocancel(
                    tr('批次路徑變更確認'),
                    tr(
                        '偵測到有 {count} 筆項目的「目標資料夾路徑」已被變更。\n\n請問您要如何批次處理這些項目？\n\n[是 (Yes)]：批次移動檔案（搬移歸檔至新資料夾）\n[否 (No)]：批次複製檔案（原地保留，複製副本至新資料夾）\n[取消 (Cancel)]：取消本次執行',
                        count=len(changed_items)
                    )
                )
                if ans is None:
                    self._log_msg("ℹ️ 使用者已取消批次執行。")
                    return
                batch_path_action = ans

        for src_path, src_name, dst_path, dst_name in checked_items:
            r        = None
            src_full = os.path.join(src_path, src_name) if src_name else src_path
            
            is_dir_op = os.path.isdir(src_full)

            if mode == MODE_SMART_RENAME or mode == MODE_EXCEL:
                if normalize(dst_path) != normalize(src_path):
                    if batch_path_action is True:
                        if is_dir_op:
                            r = move_folder(src_full, os.path.join(dst_path, dst_name), rename=True)
                        else:
                            r = move_file(src_full, dst_path, os.path.splitext(dst_name)[0])
                    elif batch_path_action is False:
                        if is_dir_op:
                            r = copy_folder(src_full, os.path.join(dst_path, dst_name), rename=True)
                        else:
                            r = copy_file(src_full, dst_path, os.path.splitext(dst_name)[0])
                else:
                    if is_dir_op:
                        r = rename_folder(src_full, dst_name)
                    else:
                        r = rename_file(src_path, src_name, os.path.splitext(dst_name)[0])

            elif mode == MODE_TEMPLATE_COPY:
                if is_dir_op:
                    r = copy_folder(src_full, os.path.join(dst_path, dst_name), rename=True)
                else:
                    r = copy_file(src_full, dst_path, os.path.splitext(dst_name)[0])

            elif mode == MODE_MKDIR:
                try:
                    if os.path.exists(dst_path):
                        r = OpResult(False, f'已存在: {dst_path}')
                    else:
                        os.makedirs(dst_path)
                        r = OpResult(True, f'建立: {dst_path}', undo_info={'op': 'mkdir', 'path': dst_path})
                except Exception as e:
                    r = OpResult(False, f'建立失敗 {dst_path}: {e}')

            elif mode == MODE_DELETE_FILTER:
                if "【即將刪除】" in dst_name:
                    try:
                        trash_dir = os.path.join(getattr(self, '_src_dir_cache', src_path), '.trash_backup')
                        os.makedirs(trash_dir, exist_ok=True)
                        backup_dst = os.path.join(trash_dir, src_name)
                        if os.path.exists(backup_dst): os.remove(backup_dst)
                        shutil.move(src_full, backup_dst)
                        r = OpResult(True, f'已刪除 (已暫存): {src_name}', undo_info={'op': 'restore_deleted', 'src': backup_dst, 'dst': src_full})
                    except Exception as e:
                        r = OpResult(False, f'刪除失敗: {e}')
                else:
                    continue

            if r:
                results.append(r)
                if r.success and r.undo_info: undo_batch.append(r.undo_info)
                self._log_msg(str(r))
                if r.success:
                    is_move_op = (mode in (MODE_SMART_RENAME, MODE_EXCEL) and normalize(dst_path) != normalize(src_path) and batch_path_action is True)
                    is_delete_op = (mode == MODE_DELETE_FILTER and "【即將刪除】" in dst_name)
                    if is_move_op or is_delete_op:
                        limit = getattr(self, '_src_dir_cache', None)
                        if limit:
                            clean_empty_parent_dirs(os.path.dirname(src_full), limit)

        if undo_batch: self._undo_stack.append(undo_batch)
        self._update_undo_button_state()
        success = sum(1 for r in results if r.success)
        fail    = len(results) - success
        messagebox.showinfo(tr('完成'), tr('成功 {success} 筆，失敗 {fail} 筆', success=success, fail=fail))

    def _do_undo(self):
        if not self._undo_stack:
            messagebox.showinfo(tr('提示'), tr('沒有可復原的操作'))
            return
        batch = self._undo_stack.pop()
        ok_count = 0
        for info in reversed(batch):
            if info.get('op') == 'restore_deleted':
                src = info['src']
                dst = info['dst']
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.move(src, dst)
                    self._log_msg(f'[OK] 復原刪除: {dst}')
                    ok_count += 1
                except Exception as e:
                    self._log_msg(f'[FAIL] 復原刪除失敗: {e}')
            else:
                r = undo(info)
                self._log_msg(str(r))
                if r.success: ok_count += 1
        self._update_undo_button_state()
        messagebox.showinfo(tr('復原'), tr('復原 {ok_count} / {len_batch} 筆', ok_count=ok_count, len_batch=len(batch)))

    def _on_llm_change(self, *_):
        self._fill_key()

    def _on_key_entry_change(self, _=None):
        if self._preview: self._preview.update_has_key(self._has_key())

    def _fill_key(self):
        llm = self._llm_var.get()
        self._key_entry.delete(0, 'end')
        if llm in self._api_keys: self._key_entry.insert(0, self._api_keys[llm])

    def _on_save_key_toggle(self):
        if self._save_key.get(): self._persist_current_key()
        else:
            delete_keys()
            self._api_keys = {}
            self._log_msg(tr('已清除本機儲存的 API Key'))

    def _persist_current_key(self):
        llm = self._llm_var.get()
        key = self._key_entry.get().strip()
        if key:
            self._api_keys[llm] = key
            ok, msg = save_keys(self._api_keys)
            self._log_msg(tr('Key 儲存：{msg}', msg=msg))

    def _clear_keys(self):
        ok, msg = delete_keys()
        self._api_keys = {}
        self._key_entry.delete(0, 'end')
        self._save_key.set(False)
        self._log_msg(tr('清除 Key：{msg}', msg=msg))

    def _log_msg(self, msg):
        print(msg)

    def _update_undo_button_state(self):
        if self._preview and self._preview.winfo_exists():
            has_undo = bool(self._undo_stack)
            self._preview.set_undo_state(has_undo)

    def _on_language_switch(self, new_lang):
        set_lang(new_lang)
        self.should_restart = True
        self.destroy()

    def _toggle_language(self):
        new_lang = 'zh' if get_lang() == 'en' else 'en'
        set_lang(new_lang)
        self.should_restart = True
        self.destroy()

    def _clean_trash_backup(self):
        src = normalize(getattr(self, '_src_dir_var', tk.StringVar()).get())
        if not src or not os.path.isdir(src):
            messagebox.showerror(tr('錯誤'), tr('請選擇有效的來源資料夾'))
            return
            
        trash_dir = os.path.join(src, '.trash_backup')
        if not os.path.exists(trash_dir):
            messagebox.showinfo(tr('提示'), tr('目前來源目錄下沒有暫存區 (.trash_backup)'))
            return
            
        ans = messagebox.askyesno(
            tr('確認清理暫存區'), 
            tr('確定要將暫存資料夾 (.trash_backup) 移至系統資源回收桶嗎？\n\n（移至回收桶後，主介面的「復原」按鈕將無法自動還原在此之前被篩選刪除的檔案）')
        )
        if ans:
            success = send_to_recycle_bin(trash_dir)
            if success:
                new_undo_stack = []
                for batch in self._undo_stack:
                    new_batch = [op for op in batch if op.get('op') != 'restore_deleted']
                    if new_batch:
                        new_undo_stack.append(new_batch)
                self._undo_stack = new_undo_stack
                self._update_undo_button_state()
                
                messagebox.showinfo(tr('完成'), tr('已將暫存區資料夾 (.trash_backup) 移至資源回收桶！'))
                self._log_msg("🧹 已成功將 .trash_backup 移至資源回收桶，並重置相關復原佇列。")
            else:
                messagebox.showerror(tr('錯誤'), tr('移至資源回收桶失敗，資料夾可能正被其他程式佔用。'))

    def _browse_dir(self, var):
        d = filedialog.askdirectory()
        if d: var.set(d)

    def _browse_excel(self):
        path = filedialog.askopenfilename(filetypes=[('Excel', '*.xlsx *.xlsm'), ('All', '*.*')])
        if path: self._excel_var.set(path)

    def _apply_drop_support(self):
        self._dnd_files = DND_FILES if HAS_DND else None

    def _bind_drop(self, widget, var):
        if not self._dnd_files: return
        try:
            widget.drop_target_register(self._dnd_files)
            widget.dnd_bind('<<Drop>>', lambda e: var.set(e.data.strip('{}').strip()))
        except Exception: pass

    def _section(self, parent, title):
        tk.Label(parent, text=title, font=('Arial', 10, 'bold'), bg=BG_COLOR, fg='#2563EB').pack(anchor='w', pady=(6,2))
        f = tk.Frame(parent, bg=BG_COLOR)
        f.pack(fill='x')
        return f

if __name__ == '__main__':
    while True:
        app = App()
        app.mainloop()
        if not getattr(app, 'should_restart', False):
            break