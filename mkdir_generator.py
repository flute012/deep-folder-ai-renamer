from i18n import tr
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import threading
from ai_client import _CALLERS


def _apply_placeholder(widget, placeholder_text):
    """為 Text 元件套用灰字提示（placeholder）效果。"""
    widget.insert('1.0', placeholder_text)
    widget.config(fg='#94A3B8')

    def on_focus_in(e):
        if widget.get('1.0', 'end-1c') == placeholder_text:
            widget.delete('1.0', 'end')
            widget.config(fg='#1e293b')

    def on_focus_out(e):
        if not widget.get('1.0', 'end-1c').strip():
            widget.insert('1.0', placeholder_text)
            widget.config(fg='#94A3B8')

    widget.bind('<FocusIn>',  on_focus_in)
    widget.bind('<FocusOut>', on_focus_out)
    return placeholder_text          # 回傳供呼叫方判斷是否為 placeholder


def _get_real_text(widget, placeholder_text):
    """取得 Text 元件的實際內容（排除 placeholder）。"""
    content = widget.get('1.0', 'end-1c')
    if content == placeholder_text or widget.cget('fg') in ('#94A3B8', '#94a3b8'):
        return ''
    return content


# ────────────────────────────────────────────────────────────────────────────
# 課次 / 序列名稱 AI 生成對話框（專供「第二層」使用）
# ────────────────────────────────────────────────────────────────────────────
class SequenceGeneratorDialog(tk.Toplevel):
    """讓使用者輸入一個命名範例，由 AI 補全後續的序列名稱。"""

    TITLE = tr("🤖 AI 序列名稱產生器")
    WIDTH, HEIGHT = 480, 310

    def __init__(self, parent, apply_callback, llm, api_key):
        super().__init__(parent)
        self.apply_callback = apply_callback
        self.llm     = llm
        self.api_key = api_key

        self.title(self.TITLE)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.configure(bg=parent.cget('bg'))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        bg  = self.cget('bg')
        pad = {'padx': 12, 'pady': 6}

        tk.Label(self, text=tr("命名範例（第一個項目）："),
                 bg=bg, font=('Arial', 9, 'bold')).pack(anchor='w', **pad)
        self.example_entry = tk.Entry(self, font=('Arial', 10), width=50)
        self.example_entry.pack(anchor='w', padx=12)
        self._set_entry_placeholder(
            self.example_entry,
            tr("例：2024年Q1  /  第一季  /  2024-01月份報告")
        )

        tk.Label(self, text=tr("主題 / 背景說明（可選填）："),
                 bg=bg, font=('Arial', 9, 'bold')).pack(anchor='w', **pad)
        self.theme_entry = tk.Entry(self, font=('Arial', 10), width=50)
        self.theme_entry.pack(anchor='w', padx=12)
        self._set_entry_placeholder(
            self.theme_entry,
            tr("例：按季度區分的財務報表資料夾")
        )

        row = tk.Frame(self, bg=bg)
        row.pack(fill='x', padx=12, pady=10)
        tk.Label(row, text=tr("欲生成數量："),
                 bg=bg, font=('Arial', 9, 'bold')).pack(side='left')
        self.count_var = tk.StringVar(value='4')
        tk.Entry(row, textvariable=self.count_var,
                 font=('Arial', 10), width=6).pack(side='left', padx=4)

        self.status_lbl = tk.Label(self, text='', bg=bg,
                                   fg='#2563EB', font=('Arial', 9))
        self.status_lbl.pack(pady=4)

        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(side='bottom', fill='x', pady=12)
        self.gen_btn = tk.Button(
            btn_frame, text=tr('開始生成'),
            command=self._start_generation,
            bg='#2563EB', fg='white', relief='flat', padx=12, pady=4)
        self.gen_btn.pack(side='right', padx=12)
        tk.Button(btn_frame, text=tr('取消'), command=self.destroy,
                  bg='#fff7eb', relief='flat', padx=12, pady=4).pack(side='right', padx=4)

    # ── Entry placeholder helper ──
    @staticmethod
    def _set_entry_placeholder(entry, text):
        entry.insert(0, text)
        entry.config(fg='#94A3B8')

        def fi(e):
            if entry.get() == text:
                entry.delete(0, 'end')
                entry.config(fg='#1e293b')

        def fo(e):
            if not entry.get().strip():
                entry.insert(0, text)
                entry.config(fg='#94A3B8')

        entry.bind('<FocusIn>',  fi)
        entry.bind('<FocusOut>', fo)
        return text

    def _get_entry(self, entry, placeholder):
        v = entry.get().strip()
        return '' if v == placeholder else v

    def _start_generation(self):
        example   = self._get_entry(self.example_entry,
                                    tr("例：2024年Q1  /  第一季  /  2024-01月份報告"))
        theme     = self._get_entry(self.theme_entry,
                                    tr("例：按季度區分的財務報表資料夾"))
        count_str = self.count_var.get().strip()

        if not example:
            messagebox.showwarning(tr('提示'), tr('請輸入命名範例！'))
            return
        try:
            count = int(count_str)
        except ValueError:
            messagebox.showerror(tr('錯誤'), tr('數量請填寫數字！'))
            return
        if not self.api_key:
            messagebox.showerror(tr('錯誤'), tr('請先在主畫面輸入並設定 API Key！'))
            return

        self.gen_btn.config(state='disabled')
        self.status_lbl.config(text=tr('🤖 AI 生成中，請稍候…'))

        def run():
            try:
                prompt = (
                    f"你現在是一個資料夾命名專家。使用者正在為辦公室文件建立資料夾序列。\n"
                    f"已知第一個資料夾的命名範例為：「{example}」\n"
                    f"背景說明：「{theme}」\n"
                    f"請依照範例的命名格式、編號邏輯、語言風格，"
                    f"生成包含範例在內共 {count} 個資料夾名稱。\n"
                    f"若為季度、月份、年度等時間序列，請依序延伸（Q1→Q2→Q3…）。\n"
                    f"請嚴格只回傳一個標準 JSON 陣列，"
                    f"例如 [\"2024年Q1\", \"2024年Q2\"]，"
                    f"不要包含任何 Markdown 標記或說明文字。"
                )
                raw   = _CALLERS[self.llm](self.api_key, prompt)
                clean = (raw.strip()
                         .removeprefix('```json')
                         .removeprefix('```')
                         .removesuffix('```')
                         .strip())
                try:
                    names = json.loads(clean)
                except json.JSONDecodeError:
                    import re
                    matches = list(re.finditer(r'"(?:[^"\\]|\\.)*"', clean))
                    if matches:
                        names = json.loads('[' + ', '.join(m.group(0) for m in matches) + ']')
                    else:
                        raise

                if isinstance(names, list) and names:
                    self.after(0, lambda: self.apply_callback(names))
                    self.after(0, self.destroy)
                else:
                    self.after(0, lambda: messagebox.showerror(tr('錯誤'), tr('AI 回傳格式不正確：{raw}', raw=raw)))
                    self.after(0, lambda: self.gen_btn.config(state='normal'))
                    self.after(0, lambda: self.status_lbl.config(text=''))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(tr('錯誤'), tr('AI 生成失敗：{e}', e=e)))
                self.after(0, lambda: self.gen_btn.config(state='normal'))
                self.after(0, lambda: self.status_lbl.config(text=''))

        threading.Thread(target=run, daemon=True).start()


# ────────────────────────────────────────────────────────────────────────────
# 主對話框
# ────────────────────────────────────────────────────────────────────────────
class MkdirGeneratorDialog(tk.Toplevel):
    """巢狀結構與 AI 智慧生成器對話框。"""

    # ── placeholder 文字常數（改一個地方就全改） ──
    _PH_LVL1 = (
        "會議記錄\n"
        "合約文件\n"
        "財務報表\n"
        "人事資料\n"
        "專案管理"
    )
    _PH_LVL2 = (
        "2024年Q1\n"
        "2024年Q2\n"
        "2024年Q3\n"
        "2024年Q4"
    )
    _PH_LVL3 = (
        "草稿\n"
        "審核中\n"
        "定稿"
    )
    _PH_AI_PROMPT = (
        "例：幫我建立「人事」、「財務」、「行政」三個大目錄，"
        "每個底下各有 2024 和 2025 兩個年份子目錄，"
        "2024 底下再建「上半年」、「下半年」。"
    )

    def __init__(self, parent, apply_callback):
        super().__init__(parent)
        self.parent          = parent
        self.apply_callback  = apply_callback

        self.title(tr('🛠️ 巢狀結構與 AI 智慧生成器'))
        self.geometry('980x680')
        self.configure(bg=parent.cget('bg'))
        self.minsize(820, 560)
        self.transient(parent)
        self.grab_set()

        self.llm     = parent._llm_var.get()
        self.api_key = parent._key_entry.get().strip()

        self._build_ui()

    # ──────────────────────────────────────────────────
    # 版面建置
    # ──────────────────────────────────────────────────
    def _build_ui(self):
        bg = self.cget('bg')

        main_pane = tk.Frame(self, bg=bg)
        main_pane.pack(fill='both', expand=True, padx=12, pady=12)

        # 左側：輸入區
        left_panel = tk.Frame(main_pane, bg=bg)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 6))

        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(fill='both', expand=True)

        tab_combo = tk.Frame(self.notebook, bg=bg)
        tab_ai    = tk.Frame(self.notebook, bg=bg)
        self.notebook.add(tab_combo, text=tr(' ⚡ 巢狀交叉組合 '))
        self.notebook.add(tab_ai,    text=tr(' 🤖 AI 智慧生成結構 '))

        self._build_combo_tab(tab_combo)
        self._build_ai_tab(tab_ai)

        # 右側：預覽與手動編輯
        right_panel = tk.Frame(main_pane, bg=bg)
        right_panel.pack(side='left', fill='both', expand=True, padx=(6, 0))

        tk.Label(right_panel,
                 text=tr('📋 相對路徑預覽列表（可在此手動新增、刪除、調整）：'),
                 bg=bg, font=('Arial', 10, 'bold'), fg='#2563EB'
                 ).pack(anchor='w', pady=(0, 4))

        preview_wrap = tk.Frame(right_panel, bg=bg)
        preview_wrap.pack(fill='both', expand=True)

        self.preview_text = tk.Text(preview_wrap, font=('Consolas', 10),
                                    wrap='none', relief='flat',
                                    borderwidth=1, highlightthickness=1,
                                    highlightbackground='#CBD5E1')
        self.preview_text.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(preview_wrap, orient='vertical',
                           command=self.preview_text.yview)
        sb.pack(side='right', fill='y')
        self.preview_text.config(yscrollcommand=sb.set)

        # 統計標籤
        self.count_lbl = tk.Label(right_panel, text='', bg=bg,
                                   fg='#64748B', font=('Arial', 8))
        self.count_lbl.pack(anchor='e', padx=4, pady=2)
        self.preview_text.bind('<KeyRelease>', self._update_count)

        # 底部按鈕
        bottom_bar = tk.Frame(self, bg=bg)
        bottom_bar.pack(side='bottom', fill='x', padx=12, pady=10)

        tk.Button(bottom_bar, text=tr('✔ 確定帶入主視窗'),
                  command=self._apply_and_close,
                  bg='#22C55E', fg='white', relief='flat',
                  font=('Arial', 10, 'bold'), padx=16, pady=6
                  ).pack(side='right', padx=4)
        tk.Button(bottom_bar, text=tr('取消'), command=self.destroy,
                  bg='#fff7eb', relief='flat',
                  font=('Arial', 10), padx=16, pady=6
                  ).pack(side='right', padx=4)

        # 快速說明
        tk.Label(bottom_bar,
                 text=tr('💡 右側框內可直接手動編輯，每行代表一個要建立的相對路徑（支援多層，用 \\ 分隔）'),
                 bg=bg, fg='#64748B', font=('Arial', 8), justify='left'
                 ).pack(side='left', padx=4)

    # ──────────────────────────────────────────────────
    # 頁籤一：巢狀交叉組合
    # ──────────────────────────────────────────────────
    def _build_combo_tab(self, tab):
        bg  = tab.cget('bg')
        pad = {'padx': 8, 'pady': 3}

        # 第一層
        row1 = tk.Frame(tab, bg=bg)
        row1.pack(fill='x', **pad)
        tk.Label(row1, text=tr('第一層：主分類（每行一個）'),
                 bg=bg, font=('Arial', 9, 'bold')).pack(side='left')
        tk.Label(row1, text=tr('必填'), bg=bg, fg='#EF4444',
                 font=('Arial', 8)).pack(side='left', padx=4)

        self.lvl1_text = tk.Text(tab, height=5, font=('Arial', 9),
                                 relief='flat', borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground='#CBD5E1')
        self.lvl1_text.pack(fill='x', padx=8, pady=(0, 6))
        self._ph_lvl1 = _apply_placeholder(self.lvl1_text, tr(self._PH_LVL1))

        # 第二層
        row2 = tk.Frame(tab, bg=bg)
        row2.pack(fill='x', **pad)
        tk.Label(row2, text=tr('第二層：子目錄（每行一個）'),
                 bg=bg, font=('Arial', 9, 'bold')).pack(side='left')
        tk.Label(row2, text=tr('選填'), bg=bg, fg='#64748B',
                 font=('Arial', 8)).pack(side='left', padx=4)

        ai_seq_btn = tk.Button(row2, text=tr('🤖 AI 生成序列'),
                               command=self._open_seq_generator,
                               bg='#fff7eb', relief='flat',
                               font=('Arial', 8, 'bold'), fg='#2563EB')
        ai_seq_btn.pack(side='right')

        self.lvl2_text = tk.Text(tab, height=5, font=('Arial', 9),
                                 relief='flat', borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground='#CBD5E1')
        self.lvl2_text.pack(fill='x', padx=8, pady=(0, 6))
        self._ph_lvl2 = _apply_placeholder(self.lvl2_text, tr(self._PH_LVL2))

        # 第三層（選填）
        row3 = tk.Frame(tab, bg=bg)
        row3.pack(fill='x', **pad)
        self.use_lvl3_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row3,
                       text=tr('啟用第三層：子子目錄（選填，如草稿/定稿）'),
                       variable=self.use_lvl3_var,
                       bg=bg, font=('Arial', 9, 'bold'),
                       command=self._toggle_lvl3).pack(side='left')

        self.lvl3_text = tk.Text(tab, height=3, font=('Arial', 9),
                                 relief='flat', borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground='#CBD5E1',
                                 state='disabled', bg='#f0f0f0')
        self.lvl3_text.pack(fill='x', padx=8, pady=(0, 6))

        # 組合按鈕
        tk.Button(tab, text=tr('⚡ 產生交叉路徑組合'),
                  command=self._generate_combinations,
                  bg='#2563EB', fg='white', relief='flat',
                  font=('Arial', 10, 'bold'), pady=6
                  ).pack(fill='x', padx=8, pady=8)

    # ──────────────────────────────────────────────────
    # 頁籤二：AI 智慧生成結構
    # ──────────────────────────────────────────────────
    def _build_ai_tab(self, tab):
        bg  = tab.cget('bg')
        pad = {'padx': 8, 'pady': 4}

        tk.Label(tab, text=tr('請用白話文描述您想建立的目錄結構：'),
                 bg=bg, font=('Arial', 10, 'bold')).pack(anchor='w', **pad)

        hint = tk.Label(tab,
                        text=(
                            '💡 提示：越詳細越準確。例如：\n'
                            '「建立專案管理、合約文件兩個主目錄，\n'
                            '  每個底下各有 2024、2025 年份子目錄，\n'
                            '  2024 底下再分草稿、審核中、定稿三個資料夾。」'
                        ),
                        bg=bg, fg='#64748B', justify='left',
                        font=('Arial', 9))
        hint.pack(anchor='w', padx=8, pady=(0, 4))

        self.ai_prompt_text = tk.Text(tab, height=9, font=('Arial', 10),
                                      relief='flat', borderwidth=1,
                                      highlightthickness=1,
                                      highlightbackground='#CBD5E1')
        self.ai_prompt_text.pack(fill='both', expand=True, padx=8, pady=4)
        self._ph_ai = _apply_placeholder(self.ai_prompt_text, tr(self._PH_AI_PROMPT))

        self.ai_status_lbl = tk.Label(tab, text='', bg=bg,
                                       fg='#2563EB', font=('Arial', 9))
        self.ai_status_lbl.pack(pady=2)

        self.ai_gen_btn = tk.Button(tab, text=tr('🤖 AI 智慧生成結構'),
                                    command=self._generate_ai_structure,
                                    bg='#2563EB', fg='white', relief='flat',
                                    font=('Arial', 10, 'bold'), pady=6)
        self.ai_gen_btn.pack(fill='x', padx=8, pady=8)

    # ──────────────────────────────────────────────────
    # 事件處理
    # ──────────────────────────────────────────────────
    def _toggle_lvl3(self):
        if self.use_lvl3_var.get():
            self.lvl3_text.config(state='normal', bg='white')
            _apply_placeholder(self.lvl3_text, tr(self._PH_LVL3))
        else:
            self.lvl3_text.delete('1.0', 'end')
            self.lvl3_text.config(state='disabled', bg='#f0f0f0')

    def _open_seq_generator(self):
        if not self.api_key:
            messagebox.showwarning(tr('提示'), tr('請先在主視窗設定 API Key，才能使用 AI 功能！'))
            return

        def apply_names(names):
            self.lvl2_text.delete('1.0', 'end')
            self.lvl2_text.config(fg='#1e293b')
            self.lvl2_text.insert('1.0', '\n'.join(names))

        SequenceGeneratorDialog(self, apply_names, self.llm, self.api_key)

    def _get_lvl_lines(self, widget, placeholder):
        """取得 Text 內容，自動排除 placeholder 後，回傳非空行列表。"""
        raw = _get_real_text(widget, placeholder)
        return [l.strip() for l in raw.splitlines() if l.strip()]

    def _generate_combinations(self):
        lvl1 = self._get_lvl_lines(self.lvl1_text, self._PH_LVL1)
        lvl2 = self._get_lvl_lines(self.lvl2_text, self._PH_LVL2)

        if not lvl1:
            messagebox.showwarning(tr('提示'), tr('請輸入第一層目錄！'))
            return

        use_lvl3 = self.use_lvl3_var.get()
        lvl3 = []
        if use_lvl3:
            lvl3 = self._get_lvl_lines(self.lvl3_text, self._PH_LVL3)

        paths = []
        if lvl2 and use_lvl3 and lvl3:
            for a in lvl1:
                for b in lvl2:
                    for c in lvl3:
                        paths.append(os.path.join(a, b, c))
        elif lvl2:
            for a in lvl1:
                for b in lvl2:
                    paths.append(os.path.join(a, b))
        else:
            # 只有第一層
            for a in lvl1:
                paths.append(a)

        self._set_preview('\n'.join(paths))

    def _generate_ai_structure(self):
        user_prompt = _get_real_text(self.ai_prompt_text, self._PH_AI_PROMPT)
        if not user_prompt:
            messagebox.showwarning(tr('提示'), tr('請輸入目錄結構需求描述！'))
            return
        if not self.api_key:
            messagebox.showerror(tr('錯誤'), tr('請先在主畫面輸入並設定 API Key！'))
            return

        self.ai_gen_btn.config(state='disabled')
        self.ai_status_lbl.config(text=tr('🤖 AI 正在規劃目錄結構，請稍候…'))

        def run():
            try:
                prompt = (
                    f"你現在是一個高階資料夾結構管理專家，專門服務辦公室文件管理需求。\n"
                    f"使用者的需求描述如下：\n"
                    f"「{user_prompt}」\n\n"
                    f"任務需求：\n"
                    f"請根據上述需求，推導出所有需要建立的相對資料夾路徑列表。\n"
                    f"注意事項：\n"
                    f"1. 使用 Windows 路徑格式（以反斜線 \\ 分隔層級）。\n"
                    f"2. 輸出「相對路徑」列表，每一項代表一個要建立的資料夾；\n"
                    f"   若包含子目錄，直接輸出子目錄完整相對路徑即可，系統會自動建立父目錄。\n"
                    f"3. 資料夾命名請貼近台灣辦公室常見習慣（繁體中文或英文皆可）。\n"
                    f"4. 輸出格式必須是 JSON 陣列，例如：\n"
                    f"   [\"合約文件\\\\2024\\\\\草稿\", \"合約文件\\\\2024\\\\定稿\"]\n"
                    f"   （JSON 中反斜線須寫成雙反斜線 \\\\）\n"
                    f"請嚴格只回傳 JSON 陣列，不要包含任何 Markdown 標記或說明文字。"
                )
                raw   = _CALLERS[self.llm](self.api_key, prompt)
                clean = (raw.strip()
                         .removeprefix('```json')
                         .removeprefix('```')
                         .removesuffix('```')
                         .strip())
                try:
                    paths = json.loads(clean)
                except json.JSONDecodeError:
                    import re
                    matches = list(re.finditer(r'"(?:[^"\\]|\\.)*"', clean))
                    if matches:
                        paths = json.loads('[' + ', '.join(m.group(0) for m in matches) + ']')
                    else:
                        raise

                if isinstance(paths, list):
                    normalized = [os.path.normpath(p) for p in paths]
                    self.after(0, lambda: self._set_preview('\n'.join(normalized)))
                else:
                    self.after(0, lambda: messagebox.showerror(
                        '錯誤', f'AI 回傳格式不符（非 JSON 陣列）：{raw}'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(tr('錯誤'), tr('AI 生成失敗：{e}', e=e)))
            finally:
                self.after(0, lambda: self.ai_gen_btn.config(state='normal'))
                self.after(0, lambda: self.ai_status_lbl.config(text=''))

        threading.Thread(target=run, daemon=True).start()

    def _set_preview(self, text):
        self.preview_text.delete('1.0', 'end')
        self.preview_text.insert('1.0', text)
        self._update_count()

    def _update_count(self, _=None):
        lines = [l for l in self.preview_text.get('1.0', 'end-1c').splitlines() if l.strip()]
        self.count_lbl.config(text=tr('共 {count} 條路徑', count=len(lines)))

    def _apply_and_close(self):
        text = self.preview_text.get('1.0', 'end-1c').strip()
        if not text:
            messagebox.showwarning(tr('提示'), tr('目前尚無任何路徑，請先使用左側工具生成，或手動輸入。'))
            return
        self.apply_callback(text)
        self.destroy()
