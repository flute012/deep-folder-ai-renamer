from i18n import tr
import tkinter as tk

from tkinter import ttk, messagebox

import tkinter.filedialog as fd

import os



from fm_config import (

    MODE_SMART_RENAME, MODE_TEMPLATE_COPY, MODES_EXTENDABLE,

    BATCH_SIZE_OPTIONS, BATCH_SIZE_DEFAULT, AI_EXTEND_DEFAULT,

    MODE_MKDIR

)



class GlowBorder:

    COLORS = ['#F59E0B', '#FCD34D', '#FDE68A', '#FCD34D', '#F59E0B']

    INTERVAL = 120



    def __init__(self, frame):

        self._frame   = frame

        self._step    = 0

        self._running = False

        self._job     = None



    def start(self):

        if self._running: return

        self._running = True

        self._animate()



    def stop(self):

        self._running = False

        if self._job:

            try: self._frame.after_cancel(self._job)

            except Exception: pass

        try: self._frame.config(highlightthickness=0, highlightbackground='#f7f1e4')

        except Exception: pass



    def _animate(self):

        if not self._running: return

        color = self.COLORS[self._step % len(self.COLORS)]

        try:

            self._frame.config(highlightthickness=2, highlightbackground=color)

            self._step += 1

            self._job = self._frame.after(self.INTERVAL, self._animate)

        except Exception:

            self._running = False



class PreviewRow:

    COL_WIDTHS = [220, 180, 220, 180]



    def __init__(self, parent, idx, src_path, src_name, dst_path, dst_name,
                 on_edit_cb, on_check_cb, on_remove_cb, col_widths_ref, mode=None, on_check_click_cb=None):
        self.idx          = idx
        self.src_path_orig = src_path
        self.src_name_orig = src_name
        self._on_edit     = on_edit_cb
        self._on_check    = on_check_cb
        self._on_remove   = on_remove_cb
        self._col_widths  = col_widths_ref
        self._editing     = False
        self._glow        = None
        self._mode        = mode
        self._on_check_click = on_check_click_cb



        self.checked      = tk.BooleanVar(value=True)

        self.src_path_var = tk.StringVar(value=src_path)

        self.src_name_var = tk.StringVar(value=src_name)

        

        if self._mode == MODE_MKDIR:

            if src_path or src_name:

                self._last_dst_path = os.path.join(src_path, src_name)

            else:

                self._last_dst_path = os.path.join(dst_path, dst_name) if (dst_path and dst_name) else (dst_path or dst_name)

            self._last_dst_name = ""

        else:

            self._last_dst_path = dst_path if dst_path else src_path

            self._last_dst_name = dst_name if dst_name else src_name

        

        self._backup_path   = self._last_dst_path

        self._backup_name   = self._last_dst_name

        

        self.dst_path_var = tk.StringVar(value=self._last_dst_path)

        self.dst_name_var = tk.StringVar(value=self._last_dst_name)



        bg = '#f0f4ff' if idx % 2 == 0 else '#ffffff'

        self.bg = bg



        self.frame = tk.Frame(parent, bg=bg, bd=0)

        self.frame.pack(fill='x', padx=4, pady=1)



        self._build(bg)



    def _build(self, bg):
        self._cb = tk.Checkbutton(
            self.frame, variable=self.checked, bg=bg,
            command=lambda: self._on_check(self.idx, self.checked.get())
        )
        self._cb.grid(row=0, column=0, padx=(2,0))
        if self._on_check_click:
            self._cb.bind('<Button-1>', lambda e: self._on_check_click(e, self.idx))



        RO_BG = '#e8e8e8'

        RO_FG = '#888888'



        if self._mode == MODE_MKDIR:

            # 建立資料夾模式路徑顯示

            tot_w = sum(self._col_widths)

            self._dst_path_entry = tk.Entry(

                self.frame, textvariable=self.dst_path_var,

                width=tot_w // 7, font=('Arial', 9), relief='flat', bg=bg

            )

            self._dst_path_entry.grid(row=0, column=1, columnspan=5, padx=2, sticky='ew')

            self._dst_path_entry.bind('<FocusIn>',  self._on_focus_in)

            self._dst_path_entry.bind('<FocusOut>', self._on_focus_out)

            self._dst_path_entry.bind('<Return>',   self._on_focus_out)

            self._entries = [self._dst_path_entry]

        else:

            self._src_path_lbl = tk.Label(

                self.frame, textvariable=self.src_path_var,

                anchor='w', bg=RO_BG, fg=RO_FG, font=('Arial', 9),

                width=self._col_widths[0] // 7

            )

            self._src_path_lbl.grid(row=0, column=1, padx=2, sticky='ew')



            self._src_name_lbl = tk.Label(

                self.frame, textvariable=self.src_name_var,

                anchor='w', bg=RO_BG, fg=RO_FG, font=('Arial', 9),

                width=self._col_widths[1] // 7

            )

            self._src_name_lbl.grid(row=0, column=2, padx=2, sticky='ew')



            tk.Label(self.frame, text='→', bg=bg, fg='#2563EB', font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=2)



            self._dst_path_entry = tk.Entry(

                self.frame, textvariable=self.dst_path_var,

                width=self._col_widths[2] // 7, font=('Arial', 9), relief='flat', bg=bg

            )

            self._dst_path_entry.grid(row=0, column=4, padx=2, sticky='ew')

            self._dst_path_entry.bind('<FocusIn>',  self._on_focus_in)

            self._dst_path_entry.bind('<FocusOut>', self._on_focus_out)

            self._dst_path_entry.bind('<Return>',   self._on_focus_out)



            self._dst_name_entry = tk.Entry(

                self.frame, textvariable=self.dst_name_var,

                width=self._col_widths[3] // 7, font=('Arial', 9), relief='flat', bg=bg

            )

            self._dst_name_entry.grid(row=0, column=5, padx=2, sticky='ew')

            self._dst_name_entry.bind('<FocusIn>',  self._on_focus_in)

            self._dst_name_entry.bind('<FocusOut>', self._on_focus_out)

            self._dst_name_entry.bind('<Return>',   self._on_focus_out)

            self._entries = [

                self._src_path_lbl,

                self._src_name_lbl,

                self._dst_path_entry,

                self._dst_name_entry

            ]



        self.ai_dot = tk.Label(self.frame, text='●', bg=bg, fg='#CBD5E1', font=('Arial', 8))

        self.ai_dot.grid(row=0, column=6, padx=2)

        if self._mode != MODE_MKDIR and self.dst_name_var.get() and self.dst_name_var.get() != self.src_name_var.get():

            self.ai_dot.config(fg='#F59E0B')



        self.accept_ai_btn = tk.Button(

            self.frame, text=tr('✔ 接受預測'), bg='#D1FAE5', fg='#059669',

            relief='flat', font=('Arial', 8), padx=4, pady=0,

            command=self._on_accept_ai_prediction

        )



        self.cancel_ai_btn = tk.Button(

            self.frame, text=tr('↩ 撤銷預測'), bg='#FEE2E2', fg='#EF4444',

            relief='flat', font=('Arial', 8), padx=4, pady=0,

            command=self._on_cancel_ai_prediction

        )



        self.remove_btn = tk.Button(

            self.frame, text='✕', bg=bg, fg='#EF4444',

            relief='flat', font=('Arial', 8, 'bold'), padx=3,

            command=lambda: self._on_remove(self.idx)

        )

        self.remove_btn.grid(row=0, column=9, padx=(0, 4))



        self._hint_count = 0

        if self.idx == 0:

            self._run_hint_anim()



    def _run_hint_anim(self):

        if self._mode == MODE_MKDIR: return

        BLINK_MS  = 1800

        MAX_BLINK = 3

        orig_path = self.dst_path_var.get()

        orig_name = self.dst_name_var.get()

        hint_path = "D:\\新專案\\目標資料夾"

        hint_name = orig_name



        def _show_hint():

            if not self.frame.winfo_exists(): return

            self.dst_path_var.set(hint_path)

            self.dst_name_var.set(hint_name)

            self._dst_path_entry.config(fg='#2563EB')

            self._dst_name_entry.config(fg='#2563EB')

            self.frame.after(BLINK_MS // 2, _show_orig)



        def _show_orig():

            if not self.frame.winfo_exists(): return

            self.dst_path_var.set(orig_path)

            self.dst_name_var.set(orig_name)

            self._dst_path_entry.config(fg='#000000')

            self._dst_name_entry.config(fg='#000000')

            self._hint_count += 1

            if self._hint_count < MAX_BLINK:

                self.frame.after(BLINK_MS // 2, _show_hint)



        self.frame.after(300, _show_hint)



    def start_glow(self):

        if not self._glow: self._glow = GlowBorder(self.frame)

        self._glow.start()

        self.accept_ai_btn.grid(row=0, column=7, padx=2)

        self.cancel_ai_btn.grid(row=0, column=8, padx=2)



    def stop_glow(self):

        if self._glow: self._glow.stop()

        self.accept_ai_btn.grid_forget()

        self.cancel_ai_btn.grid_forget()

        self.set_confirmed()



    def _on_cancel_ai_prediction(self):

        if self._glow: self._glow.stop()

        self.accept_ai_btn.grid_forget()

        self.cancel_ai_btn.grid_forget()

        self.dst_path_var.set(self._backup_path)

        self.dst_name_var.set(self._backup_name)

        self._last_dst_path = self._backup_path

        self._last_dst_name = self._backup_name

        self.ai_dot.config(text='●', fg='#CBD5E1')

        self._dst_path_entry.config(bg=self.bg, fg='#000000')

        self._dst_name_entry.config(bg=self.bg, fg='#000000')



    def _on_accept_ai_prediction(self):

        if self._glow: self._glow.stop()

        self.accept_ai_btn.grid_forget()

        self.cancel_ai_btn.grid_forget()

        self.set_confirmed()

        

        curr_path = self.dst_path_var.get().strip()

        curr_name = self.dst_name_var.get().strip()

        self._last_dst_path = curr_path

        self._last_dst_name = curr_name

        self._backup_path = curr_path

        self._backup_name = curr_name

        

        log_payload = {

            "is_path": curr_path != self.src_path_orig,

            "is_name": curr_name != self.src_name_orig,

            "type": "接受預測",

            "name": self.src_name_orig,

            "detail": tr("點擊接受預測，將預測結果轉為確認狀態"),

            "skip_auto_predict": True

        }

        self._on_edit(self.idx, self.get_values(), log_payload)



    def set_confirmed(self):

        if self.frame.winfo_exists():

            self.ai_dot.config(text='●', fg='#22C55E')

            self._dst_path_entry.config(bg='#ECFDF5', fg='#065F46')

            self._dst_name_entry.config(bg='#ECFDF5', fg='#065F46')



    def set_prediction(self, dst_path, dst_name):

        self._backup_path = self.dst_path_var.get().strip()

        self._backup_name = self.dst_name_var.get().strip()

        self.dst_path_var.set(dst_path)

        self.dst_name_var.set(dst_name)

        self._last_dst_path = dst_path

        self._last_dst_name = dst_name

        self.ai_dot.config(text='●', fg='#F59E0B')

        self._dst_path_entry.config(bg='#FEF3C7', fg='#92400E')

        self._dst_name_entry.config(bg='#FEF3C7', fg='#92400E')

        self.start_glow()



    def set_row_bg(self, idx):

        bg = '#f0f4ff' if idx % 2 == 0 else '#ffffff'

        self.bg = bg

        self.frame.config(bg=bg)

        for w in self.frame.winfo_children():

            try: w.config(bg=bg)

            except Exception: pass



    def get_values(self):

        return (

            self.src_path_var.get().strip(),

            self.src_name_var.get().strip(),

            self.dst_path_var.get().strip(),

            self.dst_name_var.get().strip(),

        )



    def is_checked(self):

        return self.checked.get()



    def _on_focus_in(self, _=None):

        self._editing = True



    def _on_focus_out(self, _=None):

        if self._editing:

            self._editing = False

            if self._glow: self._glow.stop()

            self.accept_ai_btn.grid_forget()

            self.cancel_ai_btn.grid_forget()

            

            curr_path = self.dst_path_var.get().strip()

            curr_name = self.dst_name_var.get().strip()

            

            log_payload = {"is_path": False, "is_name": False, "type": "無變更", "name": self.src_name_orig, "detail": ""}

            

            if curr_path != self._last_dst_path:

                log_payload.update({

                    "is_path": True,

                    "type": "目標資料夾路徑 (Path)",

                    "detail": tr("手動修改新路徑：{curr_path}", curr_path=curr_path)

                })

                self._last_dst_path = curr_path

                self._backup_path = curr_path

            elif curr_name != self._last_dst_name:

                log_payload.update({

                    "is_name": True,

                    "type": "目標檔案名稱 (Name)",

                    "detail": tr("手動修改新檔名：{curr_name}", curr_name=curr_name)

                })

                self._last_dst_name = curr_name

                self._backup_name = curr_name

            else:

                return



            self._on_edit(self.idx, self.get_values(), log_payload)



    def update_widths(self):

        if self._mode == MODE_MKDIR:

            tot = sum(self._col_widths)

            self._dst_path_entry.config(width=max(5, tot // 7))

        else:

            for i, e in enumerate(self._entries):

                e.config(width=max(5, self._col_widths[i] // 7))



class ColResizer(tk.Frame):

    def __init__(self, parent, col_idx, col_widths, on_resize_cb):

        super().__init__(parent, width=5, bg='#CBD5E1', cursor='sb_h_double_arrow')

        self._col_idx   = col_idx

        self._col_widths = col_widths

        self._on_resize = on_resize_cb

        self._drag_x    = None

        self.bind('<ButtonPress-1>',  self._start)

        self.bind('<B1-Motion>',      self._drag)

        self.bind('<ButtonRelease-1>', self._end)



    def _start(self, e): self._drag_x = e.x_root



    def _drag(self, e):

        if self._drag_x is None: return

        delta = e.x_root - self._drag_x

        self._drag_x = e.x_root

        self._col_widths[self._col_idx] = max(60, self._col_widths[self._col_idx] + delta)

        self._on_resize()



    def _end(self, _): self._drag_x = None



class ExtendGroup(tk.Frame):

    def __init__(self, parent, group_idx, mode, on_predict_cb, on_remove_cb, has_key):

        super().__init__(parent, bg='#fff7eb', relief='groove', bd=1)

        self._group_idx  = group_idx

        self._mode       = mode

        self._on_predict = on_predict_cb

        self._on_remove  = on_remove_cb

        self._has_key    = has_key

        self._count_var  = tk.StringVar(value=str(AI_EXTEND_DEFAULT))

        self._build()



    def _build(self):

        top = tk.Frame(self, bg='#fff7eb')

        top.pack(fill='x', padx=6, pady=(4,2))



        if self._mode == MODE_TEMPLATE_COPY:

            title_text = f'📂 目標路徑組 {self._group_idx + 1}：'

            hint_text = "請在此貼上或輸入目標派發路徑（例如：D:\\新教材\\客戶A 或是 B班級）\n支援輸入多行派發給多個資料夾"

        else:

            title_text = f'組 {self._group_idx + 1} 範例：'

            hint_text = "01_第一單元\n02_第二單元"



        tk.Label(top, text=title_text, bg='#fff7eb', font=('Arial', 9, 'bold')).pack(side='left')

        tk.Button(top, text='✕', command=lambda: self._on_remove(self._group_idx), bg='#fff7eb', relief='flat', fg='#94A3B8', font=('Arial', 8)).pack(side='right')



        self._example = tk.Text(self, height=2, width=40, font=('Arial', 9))

        self._example.pack(padx=6, pady=2, fill='x')

        

        self._example.insert('1.0', hint_text)

        self._example.config(fg='#94A3B8')

        self._example.bind('<FocusIn>', lambda e: self._example.delete('1.0', 'end') or self._example.config(fg='#000000') if self._example.get('1.0', 'end-1c') == hint_text else None)



        bot = tk.Frame(self, bg='#fff7eb')

        bot.pack(fill='x', padx=6, pady=(2,4))



        if self._mode == MODE_TEMPLATE_COPY:

            self._btn = tk.Button(bot, text=tr('🔗 套用此目標路徑'), command=self._trigger_distribution, bg='#2563EB', fg='white', relief='flat', padx=8)

            self._btn.pack(side='left', padx=4)

        else:

            tk.Label(bot, text=tr('預測筆數：'), bg='#fff7eb', font=('Arial', 9)).pack(side='left')

            tk.Entry(bot, textvariable=self._count_var, width=5, font=('Arial', 9)).pack(side='left', padx=4)

            self._btn = tk.Button(bot, text=tr('AI 生成'), command=self._trigger, bg='#2563EB' if self._has_key else '#CBD5E1', fg='white', relief='flat', padx=8, state='normal' if self._has_key else 'disabled')

            self._btn.pack(side='left', padx=4)



        self._status = tk.Label(bot, text='', bg='#fff7eb', fg='#64748B', font=('Arial', 8))

        self._status.pack(side='left', padx=4)



    def _trigger_distribution(self):

        raw_text = self._example.get('1.0', 'end-1c').strip()

        if not raw_text or "請在此貼上或輸入目標派發路徑" in raw_text:

            messagebox.showwarning('提示', '請先輸入目標派發路徑')

            return

        paths = [p.strip() for p in raw_text.splitlines() if p.strip()]

        self._on_predict(self._group_idx, "DISTRIBUTE_MODE", paths, self._on_result)



    def _trigger(self):

        example_text = self._example.get('1.0', 'end').strip()

        if not example_text or "01_第一單元" in example_text:

            messagebox.showwarning('提示', '請填入至少一筆範例')

            return

        try: count = int(self._count_var.get())

        except ValueError:

            messagebox.showerror('錯誤', '筆數請填數字')

            return

        self._btn.config(state='disabled', text='生成中…')

        self._status.config(text='')

        self._on_predict(self._group_idx, example_text, count, self._on_result)



    def _on_result(self, names, count):

        self._btn.config(state='normal', text=tr('🔗 套用此目標路徑') if self._mode == MODE_TEMPLATE_COPY else 'AI 生成')

        self._status.config(text=f'已套用' if self._mode == MODE_TEMPLATE_COPY else f'已生成 {len(names)} 筆')



    def set_has_key(self, has_key):

        if self._mode == MODE_TEMPLATE_COPY: return

        self._has_key = has_key

        self._btn.config(bg='#2563EB' if has_key else '#CBD5E1', state='normal' if has_key else 'disabled')



class PreviewPanel(tk.Frame):

    def __init__(self, parent, items, mode, on_predict_cb, on_execute_cb, on_undo_cb, has_key=False, is_only_dir=False, selected_llm_cb=None):

        super().__init__(parent, bg='#f7f1e4')

        self._items        = list(items)

        self._mode         = mode

        self._on_predict   = on_predict_cb

        self._on_execute   = on_execute_cb

        self._on_undo      = on_undo_cb

        self._has_key      = has_key

        self._is_only_dir  = is_only_dir

        self._selected_llm_cb = selected_llm_cb

        self._rows         = []

        self._confirmed    = {}

        self._edit_history = []  # 累積所有使用者手動修改的歷史記錄 [(src, dst), ...]

        self._batch_size   = int(BATCH_SIZE_DEFAULT)

        self._sort_asc     = True

        self._extend_groups = []

        self._col_widths = [220, 180, 220, 180]
        
        self._last_clicked_idx = None

        

        # ── 分頁狀態 ──

        self._current_page = 0

        self._page_size = 150

        self._total_pages = 1



        self._build()

    def set_undo_state(self, has_undo):
        if hasattr(self, '_undo_btn') and self._undo_btn.winfo_exists():
            if has_undo:
                self._undo_btn.config(
                    state='normal',
                    bg='#F59E0B',
                    fg='white',
                    activebackground='#D97706',
                    activeforeground='white'
                )
            else:
                self._undo_btn.config(
                    state='disabled',
                    bg='#CBD5E1',
                    fg='white',
                    disabledforeground='white'
                )

    def _build(self):

        bar = tk.Frame(self, bg='#f7f1e4')

        bar.pack(fill='x', padx=8, pady=(8,4))

        tk.Label(bar, text='預覽變更', font=('Arial', 11, 'bold'), bg='#f7f1e4', fg='#2563EB').pack(side='left')



        self._batch_label = tk.Label(bar, text='', bg='#f7f1e4', fg='#64748B', font=('Arial', 9))

        self._batch_label.pack(side='left', padx=10)



        self._ai_status = tk.Label(bar, text='（無 API Key，純手動模式）' if not self._has_key else '', bg='#f7f1e4', fg='#F59E0B', font=('Arial', 8))

        self._ai_status.pack(side='left')



        tk.Label(bar, text=tr('批次：'), bg='#f7f1e4', fg='#64748B', font=('Arial', 9)).pack(side='left', padx=(10,0))

        self._batch_var = tk.StringVar(value=BATCH_SIZE_DEFAULT)

        self._batch_menu = ttk.Combobox(bar, textvariable=self._batch_var, values=BATCH_SIZE_OPTIONS, width=5, state='readonly' if self._has_key else 'disabled')

        self._batch_menu.pack(side='left', padx=2)

        self._batch_menu.bind('<<ComboboxSelected>>', self._on_batch_change)



        self._sort_btn = tk.Button(bar, text=tr('排序 A→Z'), command=self._toggle_sort, bg='#fff7eb', relief='flat', padx=6)

        self._sort_btn.pack(side='left', padx=(4,2))



        # AI 預測按鈕

        self._continue_ai_btn = tk.Button(

            bar, text=tr('🤖 請 AI 繼續預測'), command=self._trigger_continue_ai,

            bg='#e7edaf', fg='#474747', relief='flat', font=('Arial', 9, 'bold'), padx=8,

            state='normal' if self._has_key else 'disabled'

        )

        self._continue_ai_btn.pack(side='left', padx=6)

        check_bar = tk.Frame(self, bg='#f7f1e4')

        check_bar.pack(fill='x', padx=8, pady=(2, 2))

        tk.Button(check_bar, text=tr('☑ 全選'), command=self._check_all, bg='#fff7eb', relief='flat', font=('Arial', 9), padx=6).pack(side='left', padx=(2, 4))
        tk.Button(check_bar, text=tr('☒ 取消全選'), command=self._uncheck_all, bg='#fff7eb', relief='flat', font=('Arial', 9), padx=6).pack(side='left')
        tk.Button(check_bar, text=tr('✔ 接受本頁所有預測'), command=self._accept_all_predictions, bg='#D1FAE5', fg='#059669', relief='flat', font=('Arial', 9, 'bold'), padx=8).pack(side='left', padx=6)
        tk.Button(check_bar, text=tr('🗑 列表移除已勾選'), command=self._remove_checked_rows, bg='#FEE2E2', fg='#EF4444', relief='flat', font=('Arial', 9, 'bold'), padx=8).pack(side='left', padx=6)
        tk.Button(check_bar, text=tr('🗑 列表移除未勾選'), command=self._remove_unchecked_rows, bg='#FEF3C7', fg='#D97706', relief='flat', font=('Arial', 9, 'bold'), padx=8).pack(side='left', padx=6)



        # ─── [ 分頁控制列 ] ───

        self._page_frame = tk.Frame(self, bg='#f7f1e4')

        self._page_frame.pack(fill='x', padx=8, pady=(2, 4))

        

        self._prev_page_btn = tk.Button(self._page_frame, text=tr('◀ 上一頁'), command=self._prev_page, bg='#fff7eb', relief='flat', font=('Arial', 9), padx=6)

        self._prev_page_btn.pack(side='left', padx=2)

        

        self._page_lbl = tk.Label(self._page_frame, text=tr('第 1 / 1 頁  (共 0 筆項目)'), bg='#f7f1e4', font=('Arial', 9, 'bold'), fg='#2563EB')

        self._page_lbl.pack(side='left', padx=10)

        

        self._next_page_btn = tk.Button(self._page_frame, text=tr('下一頁 ▶'), command=self._next_page, bg='#fff7eb', relief='flat', font=('Arial', 9), padx=6)

        self._next_page_btn.pack(side='left', padx=2)



        self._header_frame = tk.Frame(self, bg='#e2e8f0')

        self._header_frame.pack(fill='x', padx=8, pady=(2,0))

        self._build_header()



        container = tk.Frame(self, bg='#f7f1e4')

        container.pack(fill='both', expand=True, padx=8)



        self._canvas = tk.Canvas(container, bg='#f7f1e4', highlightthickness=0)

        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self._canvas.yview)

        self._scroll_frame = tk.Frame(self._canvas, bg='#f7f1e4')

        self._scroll_frame.bind('<Configure>', lambda e: self._canvas.configure(scrollregion=self._canvas.bbox('all')))

        self._canvas.create_window((0,0), window=self._scroll_frame, anchor='nw')

        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side='left', fill='both', expand=True)

        scrollbar.pack(side='right', fill='y')

        self._canvas.bind_all('<MouseWheel>', lambda e: self._canvas.yview_scroll(-1*(e.delta//120), 'units'))



        if self._mode in MODES_EXTENDABLE:

            self._extend_frame = tk.Frame(self, bg='#f7f1e4')

            self._extend_frame.pack(fill='x', padx=8, pady=(4,0))

            self._build_extend_area()



        btn_bar = tk.Frame(self, bg='#f7f1e4')

        btn_bar.pack(fill='x', padx=8, pady=8)



        legend = tk.Frame(btn_bar, bg='#f7f1e4')

        legend.pack(side='left', padx=(0,12))

        for color, label in [('#F59E0B','AI 預測'), ('#22C55E','已確認'), ('#CBD5E1','未填')]:

            tk.Label(legend, text='●', fg=color, bg='#f7f1e4', font=('Arial', 10)).pack(side='left')

            tk.Label(legend, text=label, bg='#f7f1e4', font=('Arial', 8), fg='#64748B').pack(side='left', padx=(0,6))



        tk.Button(btn_bar, text='✔ 執行勾選項目', command=self._trigger_execute, bg='#22C55E', fg='white', relief='flat', padx=10).pack(side='left', padx=4)

        self._undo_btn = tk.Button(btn_bar, text=tr('【復原上一步】'), command=self._on_undo, bg='#F59E0B', fg='white', relief='flat', padx=10)
        self._undo_btn.pack(side='left', padx=4)

        tk.Button(btn_bar, text=tr('【匯出對照表至 Excel】'), command=self._export_to_excel, bg='#6366F1', fg='white', relief='flat', padx=10).pack(side='right', padx=4)



        self._render_current_page()



    def _build_header(self):

        for w in self._header_frame.winfo_children(): w.destroy()

        self._header_labels = []

        

        tk.Label(self._header_frame, text='  ✔', bg='#e2e8f0', width=3, font=('Arial', 9, 'bold')).pack(side='left')

        if self._mode == MODE_MKDIR:

            tot_w = sum(self._col_widths)

            lbl = tk.Label(self._header_frame, text=tr('預計新建的完整資料夾路徑'), bg='#e2e8f0', font=('Arial', 9, 'bold'), width=tot_w // 7, anchor='w')

            lbl.pack(side='left', fill='x', expand=True, padx=2)

            self._header_labels.append(lbl)

        else:

            name_label = '來源資料夾名稱' if self._is_only_dir else '來源檔名'

            target_label = '目標資料夾名稱' if self._is_only_dir else '目標檔名'

            labels = ['來源路徑', name_label, '目標路徑', target_label]

            for i, label in enumerate(labels):

                lbl = tk.Label(self._header_frame, text=label, bg='#e2e8f0', font=('Arial', 9, 'bold'), width=self._col_widths[i] // 7, anchor='w')

                lbl.pack(side='left', padx=2)

                self._header_labels.append(lbl)

                if i == 1: tk.Label(self._header_frame, text='→', bg='#e2e8f0', font=('Arial', 9, 'bold')).pack(side='left', padx=2)

                if i < 3: ColResizer(self._header_frame, i, self._col_widths, self._on_col_resize).pack(side='left', fill='y')



    def _build_extend_area(self):

        if self._mode == MODE_TEMPLATE_COPY:

            self._build_dispatch_panel()

        else:

            top = tk.Frame(self._extend_frame, bg='#f7f1e4')

            top.pack(fill='x', pady=(4,2))

            title = 'AI 延伸新增'

            btn_txt = '＋ 新增一組'

            tk.Label(top, text=title, font=('Arial', 10, 'bold'), bg='#f7f1e4', fg='#2563EB').pack(side='left')

            tk.Button(top, text=btn_txt, command=self._add_extend_group, bg='#fff7eb', relief='flat', padx=8).pack(side='left', padx=8)

            self._groups_frame = tk.Frame(self._extend_frame, bg='#f7f1e4')

            self._groups_frame.pack(fill='x')

            self._add_extend_group()



    def _build_dispatch_panel(self):

        # 建立派發目的地面板

        panel = tk.Frame(self._extend_frame, bg='#fff7eb', relief='groove', bd=1)

        panel.pack(fill='x', pady=4, padx=2)

        

        # 標題

        top = tk.Frame(panel, bg='#fff7eb')

        top.pack(fill='x', padx=8, pady=(6,2))

        tk.Label(top, text=tr('📂 選擇一對多派發目的地'), font=('Arial', 10, 'bold'), bg='#fff7eb', fg='#2563EB').pack(side='left')

        tk.Label(top, text=tr('（支援從檔案總管拖曳多個資料夾至下方輸入框，可手動加上子資料夾階層）'), font=('Arial', 8), bg='#fff7eb', fg='#64748B').pack(side='left', padx=10)

        

        # 多行目的地輸入框

        mid = tk.Frame(panel, bg='#fff7eb')

        mid.pack(fill='x', padx=8, pady=2)

        

        self.dispatch_text = tk.Text(mid, height=4, width=50, font=('Arial', 9))

        self.dispatch_text.pack(side='left', fill='x', expand=True, padx=(0,6))

        

        # 設置預覽預設文字

        placeholder = (

            "D:\\資訊\\HK2\n"

            "D:\\檔案室\\HK3\n"

            "E:\\收發室\\HK4"

        )

        self.dispatch_text.insert('1.0', placeholder)

        self.dispatch_text.config(fg='#94A3B8')

        

        def on_focus_in(e):

            if self.dispatch_text.get('1.0', 'end-1c').strip() == placeholder.strip():

                self.dispatch_text.delete('1.0', 'end')

                self.dispatch_text.config(fg='#000000')

                

        def on_focus_out(e):

            if not self.dispatch_text.get('1.0', 'end-1c').strip():

                self.dispatch_text.insert('1.0', placeholder)

                self.dispatch_text.config(fg='#94A3B8')

                

        self.dispatch_text.bind('<FocusIn>', on_focus_in)

        self.dispatch_text.bind('<FocusOut>', on_focus_out)

        

        # 註冊拖曳

        # 來源於 ui_main.py App 的 _dnd_files

        master_app = self.winfo_toplevel()

        if hasattr(master_app, '_dnd_files') and master_app._dnd_files:

            try:

                self.dispatch_text.drop_target_register(master_app._dnd_files)

                self.dispatch_text.dnd_bind('<<Drop>>', self._on_dispatch_dnd_drop)

            except Exception: pass

            

        # 2. 按鈕區

        bot = tk.Frame(panel, bg='#fff7eb')

        bot.pack(fill='x', padx=8, pady=(2,6))

        

        self.dispatch_btn = tk.Button(

            bot, text=tr('📊 生成一對多派發預覽'), command=self._generate_dispatch_preview,

            bg='#2563EB', fg='white', relief='flat', font=('Arial', 9, 'bold'), padx=12

        )

        self.dispatch_btn.pack(side='right', padx=4)



    def _on_dispatch_dnd_drop(self, event):

        raw = event.data.strip()

        import re

        paths = []

        for part in re.findall(r'{([^}]+)}|([^\s]+)', raw):

            p = part[0] if part[0] else part[1]

            if p: paths.append(os.path.normpath(p))

            

        placeholder = (

            "D:\\辦公室測試資料夾\\HK2\n"

            "D:\\辦公室測試資料夾\\HK3\n"

            "D:\\辦公室測試資料夾\\HK4"

        )

        

        existing = self.dispatch_text.get('1.0', 'end-1c').strip()

        if existing == placeholder.strip():

            existing = ""

            self.dispatch_text.config(fg='#000000')

            

        new_text = '\n'.join(paths)

        if existing:

            self.dispatch_text.delete('1.0', 'end')

            self.dispatch_text.insert('1.0', existing + '\n' + new_text)

        else:

            self.dispatch_text.delete('1.0', 'end')

            self.dispatch_text.insert('1.0', new_text)



    def _generate_dispatch_preview(self):

        target_raw = self.dispatch_text.get('1.0', 'end-1c').strip()

        

        placeholder = (

            "D:\\辦公室測試資料夾\\HK2\n"

            "D:\\辦公室測試資料夾\\HK3\n"

            "D:\\辦公室測試資料夾\\HK4"

        )

        

        if not target_raw or target_raw == placeholder.strip():

            messagebox.showwarning(tr('提示'), tr('請先輸入或拖入目標派發資料夾路徑！'))

            return

        

        target_parents = [os.path.normpath(p.strip()) for p in target_raw.splitlines() if p.strip()]

        if not target_parents:

            messagebox.showwarning(tr('提示'), tr('請輸入有效的目標派發資料夾路徑！'))

            return

            

        if not hasattr(self, '_original_dispatch_sources') or not self._original_dispatch_sources:

            self._original_dispatch_sources = [old for old, _ in self._items if old]

            

        if not self._original_dispatch_sources:

            messagebox.showwarning(tr('提示'), tr('請先載入來源項目！'))

            return

            

        new_items = []

        for p_dir in target_parents:

            final_dst_dir = os.path.normpath(p_dir)

            

            for src_abs in self._original_dispatch_sources:

                src_name = os.path.basename(src_abs)

                dst_abs = os.path.join(final_dst_dir, src_name)

                new_items.append((src_abs, dst_abs))

                

        self._items = new_items

        self._confirmed.clear()

        self._current_page = 0

        self._render_current_page()

        

        messagebox.showinfo(tr('成功'), tr('已成功為 {sources} 筆來源項目與 {targets} 筆目標路徑，生成 {dispatches} 筆笛卡兒派發對照！', sources=len(self._original_dispatch_sources), targets=len(target_parents), dispatches=len(new_items)))



    def _add_extend_group(self):

        idx = len(self._extend_groups)

        g = ExtendGroup(self._groups_frame, idx, self._mode, on_predict_cb=self._on_extend_predict, on_remove_cb=self._remove_extend_group, has_key=self._has_key)

        g.pack(fill='x', pady=2)

        self._extend_groups.append(g)



    def _remove_extend_group(self, group_idx):

        if len(self._extend_groups) <= 1:

            messagebox.showinfo(tr('提示'), tr('至少保留一組'))

            return

        self._extend_groups.pop(group_idx).destroy()

        for i, grp in enumerate(self._extend_groups): grp._group_idx = i



    def _on_extend_predict(self, group_idx, example_text, count_or_paths, result_cb, log_payload=None):

        if example_text == "DISTRIBUTE_MODE":

            target_dirs = count_or_paths

            new_items = []

            for d_dir in target_dirs:

                for src_full, rel_p in self._items:

                    new_items.append((src_full, os.path.normpath(os.path.join(d_dir, os.path.basename(src_full)))))

            

            for row in self._rows: row.frame.destroy()

            self._rows.clear()

            

            for i, (old, new) in enumerate(new_items):

                self._add_row(i, old, new)

            self._update_batch_label()

            result_cb([], 0)

            return



        if self._mode == MODE_MKDIR:

            lines = [l.strip() for l in example_text.splitlines() if l.strip()]

            examples = []

            for l in lines:

                if '->' in l:

                    examples.append(l.split('->', 1)[0].strip())

                else:

                    examples.append(l)

            if not examples:

                examples = [os.path.basename(row.dst_path_var.get().strip()) for row in self._rows if row.is_checked()]

                examples = [e for e in examples if e]

                

            log_payload = log_payload or {}

            log_payload['mkdir_extend_mode'] = True

            log_payload['count'] = count_or_paths

            

            confirmed_pairs = [(e, e) for e in examples]

            targets = [f'__extend_{group_idx}_{i}__' for i in range(count_or_paths)]

            

            def _cb(t, names):

                result_cb(names, count_or_paths)

                src_dir = getattr(self, '_src_dir_cache', '')

                full_paths = []

                for name in names:

                    full_paths.append(os.path.normpath(os.path.join(src_dir, name)))

                self._append_rows(full_paths)

                

            self._on_predict(confirmed_pairs, targets, _cb, log_payload)

            return



        confirmed = [(row.src_name_orig, row.dst_name_var.get()) for row in self._rows if row.idx in self._confirmed]

        lines = [l.strip() for l in example_text.splitlines() if '->' in l]

        examples = [(a.strip(), b.strip()) for a, b in (l.split('->', 1) for l in lines)] if lines else []

        if not examples: examples = confirmed

        targets = [f'__extend_{group_idx}_{i}__' for i in range(count_or_paths)]

        def _cb(t, names):

            result_cb(names, count_or_paths)

            self._append_rows(names)

        self._on_predict(examples, targets, _cb, log_payload)



    def _append_rows(self, names):

        start_idx = len(self._rows)

        for i, name in enumerate(names):

            idx = start_idx + i

            self._items.append(( '', name))

            self._add_row(idx, '', name)

        self._update_batch_label()



    def _add_row(self, idx, old_full, new_full):
        src_path, src_name = self._split_path(old_full)
        dst_path, dst_name = self._split_path(new_full)
        row = PreviewRow(
            self._scroll_frame, idx, src_path, src_name, dst_path, dst_name,
            on_edit_cb=self._on_row_edit, on_check_cb=self._on_row_check,
            on_remove_cb=self._on_row_remove, col_widths_ref=self._col_widths,
            mode=self._mode, on_check_click_cb=self._on_row_check_click
        )
        self._rows.append(row)
        return row

    def _de_duplicate_predictions(self, targets_map, res_map, is_path_mode):
        used_paths = set()
        
        # 1. 蒐集當前頁面所有「不在本次預測目標中」的行目前顯示的目標路徑
        start_idx = self._current_page * self._page_size
        for r in self._rows:
            global_idx = start_idx + r.idx
            if global_idx < len(self._items):
                old_full = self._items[global_idx][0]
                if old_full not in targets_map:
                    full_p = os.path.join(r.dst_path_var.get().strip(), r.dst_name_var.get().strip())
                    used_paths.add(os.path.normpath(full_p).lower())
                    
        # 2. 蒐集非當前頁面所有項目的目標路徑
        for idx, (old_full, new_full) in enumerate(self._items):
            if idx < start_idx or idx >= start_idx + len(self._rows):
                if old_full not in targets_map and new_full:
                    used_paths.add(os.path.normpath(new_full).lower())

        # 3. 依序為預測目標進行去重處理並套用
        for old_full, row in targets_map.items():
            if old_full not in res_map:
                continue
                
            pred_val = res_map[old_full]
            if is_path_mode:
                dst_path = pred_val
                dst_name = row.dst_name_var.get().strip()
            else:
                dst_path = row.dst_path_var.get().strip()
                dst_name = pred_val
                
            full_path = os.path.join(dst_path, dst_name)
            normalized_full = os.path.normpath(full_path).lower()
            
            if normalized_full in used_paths:
                base, ext = os.path.splitext(dst_name)
                counter = 1
                while True:
                    new_name = f"{base}_{counter}{ext}"
                    new_full_path = os.path.join(dst_path, new_name)
                    new_normalized = os.path.normpath(new_full_path).lower()
                    if new_normalized not in used_paths:
                        dst_name = new_name
                        normalized_full = new_normalized
                        break
                    counter += 1
                    
            used_paths.add(normalized_full)
            row.set_prediction(dst_path, dst_name)



    def _on_row_remove(self, local_idx):

        target_row = None

        for r in self._rows:

            if r.idx == local_idx:

                target_row = r

                break

        if target_row:

            target_row.stop_glow()

            target_row.frame.destroy()

            self._rows.remove(target_row)

            global_idx = self._current_page * self._page_size + local_idx

            if global_idx in self._confirmed: del self._confirmed[global_idx]

            

            # 同步自全域清單中移除

            if global_idx < len(self._items):

                self._items.pop(global_idx)

                

            self._render_current_page()



    @staticmethod

    def _split_path(full):

        if not full: return '', ''

        normalized_f = full.replace('\\', '/').replace('//', '/')

        if '/' in normalized_f:

            parts = normalized_f.rsplit('/', 1)

            dir_part = parts[0].replace('/', os.sep)

            base_part = parts[1]

            return dir_part, base_part

        return '', full



    def _on_col_resize(self):

        if hasattr(self, '_header_labels') and len(self._header_labels) == 4:

            for i, lbl in enumerate(self._header_labels):

                try: lbl.config(width=max(5, self._col_widths[i] // 7))

                except Exception: pass

        for row in self._rows: row.update_widths()



    def _toggle_sort(self):

        self._sort_asc = not self._sort_asc

        self._sort_btn.config(text=tr('排序 A→Z') if self._sort_asc else '排序 Z→A')

        self._items.sort(key=lambda item: self._split_path(item[0])[1].lower(), reverse=not self._sort_asc)

        self._render_current_page()



    def _on_row_edit(self, local_idx, values, log_payload=None):

        global_idx = self._current_page * self._page_size + local_idx

        self._confirmed[global_idx] = values

        

        # 更新 self._items 中對應的目標完整路徑，讓翻頁切換後修改能保存

        src_path, src_name, dst_path, dst_name = values

        self._items[global_idx] = (self._items[global_idx][0], os.path.join(dst_path, dst_name))

        

        # 累積歷史修改記錄

        is_path_change = log_payload and log_payload.get('is_path')
        history_key = os.path.join(src_path, src_name)
        if is_path_change:
            history_val = dst_path
        else:
            history_val = dst_name
            
        # 去除重複紀錄並更新
        self._edit_history = [
            (k, v, p) for k, v, p in self._edit_history 
            if not (k == history_key and p == is_path_change)
        ]
        self._edit_history.append((history_key, history_val, is_path_change))

        

        self._rows[local_idx].set_confirmed()

        self._update_batch_label()

        if self._has_key and not (log_payload and log_payload.get('skip_auto_predict')):

            self._auto_predict(local_idx, log_payload)



    def _on_row_check(self, local_idx, checked):
        self._last_clicked_idx = local_idx

    def _on_row_check_click(self, event, local_idx):
        is_shift = (event.state & 0x0001) != 0
        if is_shift and self._last_clicked_idx is not None:
            start = min(self._last_clicked_idx, local_idx)
            end = max(self._last_clicked_idx, local_idx)
            target_val = not self._rows[local_idx].checked.get()
            self.after(20, lambda: self._apply_shift_selection(start, end, target_val))
        else:
            self._last_clicked_idx = local_idx

    def _apply_shift_selection(self, start, end, target_val):
        for idx in range(start, end + 1):
            if idx < len(self._rows):
                self._rows[idx].checked.set(target_val)

    def _remove_checked_rows(self):
        start_idx = self._current_page * self._page_size
        to_remove = []
        for i, row in enumerate(self._rows):
            if row.is_checked():
                to_remove.append(start_idx + i)
        if not to_remove:
            messagebox.showinfo(tr('提示'), tr('請先勾選想要從列表中移除的項目'))
            return
        
        # 倒序刪除並移位已確認字典
        for g_idx in sorted(to_remove, reverse=True):
            if g_idx < len(self._items):
                self._items.pop(g_idx)
            new_confirmed = {}
            for k, v in self._confirmed.items():
                if k < g_idx:
                    new_confirmed[k] = v
                elif k > g_idx:
                    new_confirmed[k - 1] = v
            self._confirmed = new_confirmed
            
        self._render_current_page()
        messagebox.showinfo(tr('成功'), tr('已從預覽列表中批次移除 {count} 筆勾選項目', count=len(to_remove)))

    def _remove_unchecked_rows(self):
        start_idx = self._current_page * self._page_size
        to_remove = []
        for i, row in enumerate(self._rows):
            if not row.is_checked():
                to_remove.append(start_idx + i)
        if not to_remove:
            messagebox.showinfo(tr('提示'), tr('當前頁面所有項目皆已被勾選'))
            return
        
        # 倒序刪除並移位已確認字典
        for g_idx in sorted(to_remove, reverse=True):
            if g_idx < len(self._items):
                self._items.pop(g_idx)
            new_confirmed = {}
            for k, v in self._confirmed.items():
                if k < g_idx:
                    new_confirmed[k] = v
                elif k > g_idx:
                    new_confirmed[k - 1] = v
            self._confirmed = new_confirmed
            
        self._render_current_page()
        messagebox.showinfo(tr('成功'), tr('已從預覽列表中批次移除 {count} 筆未勾選項目', count=len(to_remove)))



    def _render_current_page(self):

        # 1. 銷毀當前頁面的所有行

        for row in self._rows:

            try:

                row.stop_glow()

                row.frame.destroy()

            except Exception: pass

        self._rows.clear()

        

        # 2. 計算分頁邊界

        total_items = len(self._items)

        self._total_pages = max(1, (total_items + self._page_size - 1) // self._page_size)

        

        # 邊界保護

        if self._current_page >= self._total_pages:

            self._current_page = self._total_pages - 1

        if self._current_page < 0:

            self._current_page = 0

            

        start_idx = self._current_page * self._page_size

        end_idx = min(total_items, start_idx + self._page_size)

        

        # 3. 渲染行

        display_items = self._items[start_idx:end_idx]

        for i, (old, new) in enumerate(display_items):

            # 這裡傳入 local_idx (也就是 i)

            row = self._add_row(i, old, new)

            # 已確認狀態設定

            global_idx = start_idx + i

            if global_idx in self._confirmed:

                row.dst_path_var.set(self._confirmed[global_idx][2])

                row.dst_name_var.set(self._confirmed[global_idx][3])

                row.set_confirmed()

                    

        # 4. 更新分頁按鈕與標籤狀態

        self._page_lbl.config(text=tr('第 1 / 1 頁  (共 0 筆項目)', page=self._current_page + 1, total=self._total_pages, count=total_items))

        

        if self._current_page == 0:

            self._prev_page_btn.config(state='disabled', bg='#CBD5E1')

        else:

            self._prev_page_btn.config(state='normal', bg='#fff7eb')

            

        if self._current_page >= self._total_pages - 1:

            self._next_page_btn.config(state='disabled', bg='#CBD5E1')

        else:

            self._next_page_btn.config(state='normal', bg='#fff7eb')

            

        self._update_batch_label()



    def _prev_page(self):

        if self._current_page > 0:

            self._current_page -= 1

            self._render_current_page()

            

    def _next_page(self):

        if self._current_page < self._total_pages - 1:

            self._current_page += 1

            self._render_current_page()



    # 觸發 AI 預測

    def _trigger_continue_ai(self):

        # 蒐集已確認與預測範例

        confirmed_dict = {}

        start_idx = self._current_page * self._page_size

        

        # 蒐集分頁範本

        for local_i, row in enumerate(self._rows):

            global_i = start_idx + local_i

            curr_path = row.dst_path_var.get().strip()

            curr_name = row.dst_name_var.get().strip()

            

            # 優先採用已確認或已有變更的結果

            if global_i in self._confirmed:

                confirmed_dict[global_i] = self._confirmed[global_i]

            elif curr_path != row.src_path_orig or curr_name != row.src_name_orig:

                # 臨時參考範本

                confirmed_dict[global_i] = (row.src_path_orig, row.src_name_orig, curr_path, curr_name)



        # 合併其他分頁已確認項目

        for global_i in self._confirmed:

            if global_i not in confirmed_dict:

                confirmed_dict[global_i] = self._confirmed[global_i]



        # 判斷是否可繼續預測

        # 歷史紀錄合併由滑動預測處理

        if not confirmed_dict and not self._edit_history:

            messagebox.showwarning(tr('提示'), tr('請至少先手動修改並確認一筆資料，讓 AI 有規律可以學習！'))

            return



        # 尋找未預測起始行

        first_unpredicted_local_idx = None

        for local_i, row in enumerate(self._rows):

            global_i = start_idx + local_i

            curr_path = row.dst_path_var.get().strip()

            curr_name = row.dst_name_var.get().strip()

            

            # 尋找未處理的行

            if global_i not in confirmed_dict and curr_path == row.src_path_orig and curr_name == row.src_name_orig:

                first_unpredicted_local_idx = local_i

                break



        if first_unpredicted_local_idx is None:

            messagebox.showinfo(tr('提示'), tr('當前頁面所有項目皆已完成預測與修改！'))

            return



        # 判斷預測模式

        # 尋找最近一筆被修改的範本

        last_edited_global_idx = max(confirmed_dict.keys())

        is_path_change = self._is_only_dir

        val = confirmed_dict[last_edited_global_idx]

        if val[2] != val[0]: # dst_path != src_path

            is_path_change = True



        sim_payload = {"is_path": is_path_change, "type": "手動點擊繼續預測調用"}

        

        # 呼叫滑動預測

        self._auto_predict_sliding(first_unpredicted_local_idx, confirmed_dict, sim_payload)



    def _auto_predict_sliding(self, start_local_idx, confirmed_dict, log_payload=None):

        total = len(self._rows)

        # 向後預測一個批次的行

        start = start_local_idx

        end   = min(total, start + self._batch_size)



        estimated_chars = 0

        for global_i in confirmed_dict:

            # 估算字數

            estimated_chars += len(str(confirmed_dict[global_i]))



        for local_i in range(start, end):

            estimated_chars += len(self._rows[local_i].src_name_orig)

                

        llm_name, char_limit, llm_desc = self._get_llm_limits()

        if estimated_chars > char_limit:

            proceed = messagebox.askyesno(

                f'⚠️ {llm_name} 字數超限警告 (防爆機制)',

                f'目前累計的參考範本與批次預測目標過多，\n'

                f'預估發送 Prompt 長度為 {estimated_chars} 字（已超過 {char_limit} 字安全建議上限）。\n\n'

                f'【模型資訊】：{llm_desc}\n\n'

                f'這可能導致 API 請求過慢、連線逾時或回傳解析失敗。\n'

                f'建議您可以將左側「批次」選單調小（例如改為 9 或 15 筆）。\n\n'

                f'請問您是否堅持要繼續發送請求？'

            )

            if not proceed: return



        # 執行預測

        if self._mode == MODE_TEMPLATE_COPY or (log_payload and log_payload.get('is_path')):
            confirmed_list = []
            confirmed_path_dict = {}
            # 加入歷史修改路徑
            for hist_src, hist_dst, is_p in self._edit_history:
                if is_p:
                    confirmed_path_dict[hist_src] = hist_dst
            for global_i in sorted(confirmed_dict):
                src_full = os.path.join(confirmed_dict[global_i][0], confirmed_dict[global_i][1])
                confirmed_path_dict[src_full] = confirmed_dict[global_i][2]
            confirmed_list = list(confirmed_path_dict.items())
            
            targets_map = {}
            for local_i in range(start, end):
                src_full = os.path.join(self._rows[local_i].src_path_orig, self._rows[local_i].src_name_orig)
                targets_map[src_full] = self._rows[local_i]

            if not targets_map: return
            targets = list(targets_map.keys())

            def _cb_path(t, results):
                res_map = dict(zip(t, results))
                self._de_duplicate_predictions(targets_map, res_map, is_path_mode=True)
                        
            if log_payload: log_payload['pure_path_mode'] = True
            self._on_predict(confirmed_list, targets, _cb_path, log_payload)
            
        else:
            confirmed_list = []
            # 加入歷史修改檔名
            history_src_set = set()
            for hist_src, hist_dst, is_p in self._edit_history:
                if not is_p:
                    confirmed_list.append((hist_src, hist_dst))
                    history_src_set.add(hist_src)

            for global_i in sorted(confirmed_dict):
                src_full = os.path.join(confirmed_dict[global_i][0], confirmed_dict[global_i][1])
                dst_name_val = confirmed_dict[global_i][3]

                # 避免重複
                if src_full not in history_src_set:
                    confirmed_list.append((src_full, dst_name_val)) # src_full -> dst_name

            targets_map = {}
            for local_i in range(start, end):
                src_full = os.path.join(self._rows[local_i].src_path_orig, self._rows[local_i].src_name_orig)
                targets_map[src_full] = self._rows[local_i]

            if not targets_map: return
            targets = list(targets_map.keys())

            def _cb_name(t, results):
                res_map = dict(zip(t, results))
                self._de_duplicate_predictions(targets_map, res_map, is_path_mode=False)

            self._on_predict(confirmed_list, targets, _cb_name, log_payload)



    # AI 批次預測

    def _auto_predict(self, edited_local_idx, log_payload=None):

        total = len(self._rows)

        half  = self._batch_size // 2

        start = max(0, edited_local_idx - half)

        end   = min(total, edited_local_idx + half + 1)

        if end - start < self._batch_size:

            if start == 0: end = min(total, self._batch_size)

            else: start = max(0, end - self._batch_size)



        # 估算 Prompt 字數

        estimated_chars = 0

        # 統計已確認範本字數

        for global_i in self._confirmed:

            # 優先讀取當前分頁即時數值

            start_idx = self._current_page * self._page_size

            local_i = global_i - start_idx

            if 0 <= local_i < len(self._rows):

                estimated_chars += len(str(self._rows[local_i].get_values()))

            else:

                estimated_chars += len(str(self._confirmed[global_i]))



        # 統計預測目標字數

        for local_i in range(start, end):

            global_i = self._current_page * self._page_size + local_i

            if global_i not in self._confirmed:

                estimated_chars += len(self._rows[local_i].src_name_orig)

                

        llm_name, char_limit, llm_desc = self._get_llm_limits()

        if estimated_chars > char_limit:

            proceed = messagebox.askyesno(

                f'⚠️ {llm_name} 字數超限警告 (防爆機制)',

                f'目前累計的參考範本與批次預測目標過多，\n'

                f'預估發送 Prompt 長度為 {estimated_chars} 字（已超過 {char_limit} 字安全建議上限）。\n\n'

                f'【模型資訊】：{llm_desc}\n\n'

                f'這極可能導致 AI 額度超限、連線逾時或回傳解析失敗。\n'

                f'建議您可以將左側「批次」選單調小（例如改為 9 或 15 筆）。\n\n'

                f'請問您是否堅持要繼續發送請求？'

            )

            if not proceed: return # 取消操作



        # 執行預測

        if self._mode == MODE_TEMPLATE_COPY or (log_payload and log_payload.get('is_path')):
            confirmed_dict = {}
            # 加入歷史修改路徑
            for hist_src, hist_dst, is_p in self._edit_history:
                if is_p:
                    confirmed_dict[hist_src] = hist_dst
            for global_i in sorted(self._confirmed):
                # 取得來源與目標路徑
                start_idx = self._current_page * self._page_size
                local_i = global_i - start_idx
                if 0 <= local_i < len(self._rows):
                    src_full = os.path.join(self._rows[local_i].src_path_orig, self._rows[local_i].src_name_orig)
                    confirmed_dict[src_full] = self._confirmed[global_i][2]
                else:
                    # 處理非當前頁面項目
                    s_path, s_name = self._split_path(self._items[global_i][0])
                    src_full = os.path.join(s_path, s_name)
                    confirmed_dict[src_full] = self._confirmed[global_i][2]
            confirmed_list = list(confirmed_dict.items())
            
            targets_map = {}
            for local_i in range(start, end):
                global_i = self._current_page * self._page_size + local_i
                if global_i not in self._confirmed and local_i != edited_local_idx:
                    src_full = os.path.join(self._rows[local_i].src_path_orig, self._rows[local_i].src_name_orig)
                    targets_map[src_full] = self._rows[local_i]

            if not targets_map: return
            targets = list(targets_map.keys())

            def _cb_path(t, results):
                res_map = dict(zip(t, results))
                self._de_duplicate_predictions(targets_map, res_map, is_path_mode=True)
                        
            if log_payload: log_payload['pure_path_mode'] = True
            self._on_predict(confirmed_list, targets, _cb_path, log_payload)
            
        else:
            confirmed_list = []
            # 加入歷史修改檔名
            history_src_set = set()
            for hist_src, hist_dst, is_p in self._edit_history:
                if not is_p:
                    confirmed_list.append((hist_src, hist_dst))
                    history_src_set.add(hist_src)

            for global_i in sorted(self._confirmed):
                start_idx = self._current_page * self._page_size
                local_i = global_i - start_idx
                if 0 <= local_i < len(self._rows):
                    src_full = os.path.join(self._rows[local_i].src_path_orig, self._rows[local_i].src_name_orig)
                    if src_full not in history_src_set:
                        confirmed_list.append((src_full, self._confirmed[global_i][3]))
                else:
                    src_full = self._items[global_i][0]
                    if src_full not in history_src_set:
                        confirmed_list.append((src_full, self._confirmed[global_i][3]))
            
            targets_map = {}
            for local_i in range(start, end):
                global_i = self._current_page * self._page_size + local_i
                if global_i not in self._confirmed and local_i != edited_local_idx:
                    src_full = os.path.join(self._rows[local_i].src_path_orig, self._rows[local_i].src_name_orig)
                    targets_map[src_full] = self._rows[local_i]
            
            if not targets_map: return
            targets = list(targets_map.keys())

            def _cb_name(t, results):
                res_map = dict(zip(t, results))
                self._de_duplicate_predictions(targets_map, res_map, is_path_mode=False)

            self._on_predict(confirmed_list, targets, _cb_name, log_payload)



    def _on_batch_change(self, _=None):

        val = self._batch_var.get()

        self._batch_size = len(self._rows) if val == '全部' else int(val)



    def _trigger_execute(self):

        checked = [row.get_values() for row in self._rows if row.is_checked()]

        if not checked:

            messagebox.showwarning(tr('提示'), tr('請至少勾選一個項目'))

            return

        empty = [v for v in checked if not v[3]]

        if empty and self._mode != MODE_SMART_RENAME:

            proceed = messagebox.askyesno(tr('警告'), tr('有 {count} 筆未填入目標名稱，繼續會略過。是否繼續？', count=len(empty)))

            if not proceed: return

            checked = [v for v in checked if v[3]]

        self._on_execute(checked)



    def _check_all(self):

        for row in self._rows: row.checked.set(True)



    def _uncheck_all(self):

        for row in self._rows: row.checked.set(False)



    def _accept_all_predictions(self):

        count = 0

        for row in self._rows:

            if row._glow and row._glow._running:

                row._on_accept_ai_prediction()

                count += 1

        if count > 0:

            messagebox.showinfo(tr('提示'), tr('已成功接受本頁共 {count} 筆 AI 預測結果！', count=count))

        else:

            messagebox.showinfo(tr('提示'), tr('目前本頁沒有任何待處理的 AI 預測。'))



    def _update_batch_label(self):

        txt = tr('已確認 {confirmed} / {total} 筆', confirmed=len(self._confirmed), total=len(self._rows))

        if len(self._items) > 150:

            txt += tr(' (⚠️ 項目過多，僅顯示前 150 筆 / 共 {total} 筆，建議使用左側過濾器)', total=len(self._items))

            self._batch_label.config(fg='#EF4444')

        else:

            self._batch_label.config(fg='#64748B')

        self._batch_label.config(text=txt)



    def _get_llm_limits(self):

        llm = self._selected_llm_cb() if self._selected_llm_cb else "Mistral"

        if llm == "Gemini":

            return llm, 200000, "Gemini 具備高達 100 萬 Token 的超大上下文視窗，幾乎不受字數限制。"

        elif llm == "Mistral":

            return llm, 80000, "Mistral AI 具備高達 32,000 Token 的超大上下文視窗，免費額度十分寬裕。"

        else: # Groq / Default

            return llm, 25000, "Groq 具備約 8,000 Token 上下文視窗限制。"



    def update_has_key(self, has_key):

        self._has_key = has_key

        self._ai_status.config(text='' if has_key else tr('（無 API Key，純手動模式）'))

        self._batch_menu.config(state='readonly' if has_key else 'disabled')

        self._continue_ai_btn.config(state='normal' if has_key else 'disabled') # 按鈕狀態同步

        for g in self._extend_groups: g.set_has_key(has_key)

        if not has_key:

            for row in self._rows:

                if row._glow:

                    try: row._glow.stop()

                    except Exception: pass



    def load_items(self, items, has_key=None, is_only_dir=False):

        if has_key is not None: self._has_key = has_key

        self._is_only_dir = is_only_dir

        self._confirmed.clear()

        self._edit_history.clear()  # 載入新項目時清空歷史修改記錄

        self._items    = list(items)

        

        # 派發模式備份原始來源路徑

        if self._mode == MODE_TEMPLATE_COPY:

            self._original_dispatch_sources = [old for old, _ in items if old]

            

        self._sort_asc = True

        self._current_page = 0

        self._build_header()

        self._render_current_page()



    def _export_to_excel(self):

        try: import pandas as pd

        except ImportError:

            messagebox.showerror(tr('錯誤'), tr('請先安裝 pandas 套件：\npip install pandas openpyxl'))

            return

        if not self._rows:

            messagebox.showwarning(tr('提示'), tr('目前無任何資料可供匯出'))

            return

        save_path = fd.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel 活頁簿', '*.xlsx')], title=tr('儲存修改對照表'))

        if not save_path: return

        # 根據模式動態決定標頭名稱

        if self._is_only_dir:

            col_src_name = '原始資料夾名稱'

            col_dst_name = '修改後資料夾名稱'

        else:

            col_src_name = '原始檔名'

            col_dst_name = '修改後檔名'



        data = []

        for global_i, (old_full, new_full) in enumerate(self._items):

            s_path, s_name = self._split_path(old_full)

            d_path, d_name = self._split_path(new_full)

            

            data.append({

                tr('原始路徑'): s_path,

                col_src_name: s_name,

                tr('修改後路徑'): d_path,

                col_dst_name: d_name

            })

        try:

            pd.DataFrame(data).to_excel(save_path, index=False)

            messagebox.showinfo(tr('成功'), tr('修改對照表已匯出至：\n{save_path}', save_path=save_path))

        except Exception as e:

            messagebox.showerror(tr('錯誤'), tr('匯出 Excel 失敗：{e}', e=e))