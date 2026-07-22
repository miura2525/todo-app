"""
<<boundary>> HomeScreen
アプリケーションのメインウィンドウモジュール
"""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date, datetime

from task import Task, TaskList
from create_task_control import CreateTaskControl
from sub_screens import TaskConfirmScreen, TaskDeleteConfirmScreen, TaskStatusConfirmScreen

class HomeScreen:
    """メイン画面クラス"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("課題管理(ToDo) アプリケーション")
        self.root.geometry("680x560")

        self.task_list = TaskList()
        self.controller = CreateTaskControl()

        self._create_input_frame()
        self._create_control_frame()
        self._create_list_frame()
        self._create_action_frame()

    def _create_input_frame(self):
        """入力フォーム"""
        input_frame = tk.LabelFrame(self.root, text="新規課題の追加", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="課題名 (20字以内):").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = tk.Entry(input_frame, width=35)
        self.title_entry.grid(row=0, column=1, columnspan=2, sticky="w", pady=2)

        tk.Label(input_frame, text="締切日 (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=2)
        self.due_entry = tk.Entry(input_frame, width=18)
        self.due_entry.grid(row=1, column=1, sticky="w", pady=2)
        self.due_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        tk.Label(input_frame, text="課題内容:").grid(row=2, column=0, sticky="nw", pady=2)
        self.desc_text = tk.Text(input_frame, width=40, height=3)
        self.desc_text.grid(row=2, column=1, sticky="w", pady=2)

        add_btn = tk.Button(input_frame, text="追加", command=self.request_task_registration, bg="#4CAF50", fg="white", font=("", 9, "bold"), width=8)
        add_btn.grid(row=2, column=2, sticky="se", padx=5, pady=2)

    def _create_control_frame(self):
        """ソート・凡例"""
        ctrl_frame = tk.Frame(self.root, padx=10)
        ctrl_frame.pack(fill="x", padx=10, pady=2)

        sort_btn = tk.Button(ctrl_frame, text="締切日の昇順で並べ替え", command=self.request_task_sorting)
        sort_btn.pack(side="left")

        legend_lbl = tk.Label(ctrl_frame, text="※ 背景色ピンク: 締切2日以内(未完了)", fg="#d32f2f", font=("", 8))
        legend_lbl.pack(side="right")

    def _create_list_frame(self):
        """課題一覧 (Treeview)"""
        list_frame = tk.Frame(self.root, padx=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("title", "due_date", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("title", text="課題名")
        self.tree.heading("due_date", text="締切日")
        self.tree.heading("status", text="状態")

        self.tree.column("title", width=280)
        self.tree.column("due_date", width=120, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("urgent", background="#FFEBEE", foreground="#C62828")

    def _create_action_frame(self):
        """下部操作ボタン"""
        btn_frame = tk.Frame(self.root, padx=10, pady=10)
        btn_frame.pack(fill="x")

        view_btn = tk.Button(btn_frame, text="詳細を確認", command=self.request_task_check)
        view_btn.pack(side="left", padx=5)

        toggle_btn = tk.Button(btn_frame, text="完了 / 未完了 に変更", command=self.request_task_status_update)
        toggle_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(btn_frame, text="削除", command=self.request_task_deletion, bg="#f44336", fg="white")
        delete_btn.pack(side="right", padx=5)

    def request_task_registration(self):
        """課題登録リクエスト"""
        title = self.title_entry.get()
        due_date = self.due_entry.get()
        description = self.desc_text.get("1.0", tk.END).strip()

        is_valid, msg = self.controller.validate_task(title, due_date, self.task_list)
        if not is_valid:
            messagebox.showwarning("入力エラー", msg)
            return

        new_task = Task(title.strip(), description, due_date.strip())
        self.task_list.add_task(new_task)

        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)

        self.update_display()
        messagebox.showinfo("完了", f"課題 '{new_task.title}' を登録しました。")

    def update_display(self):
        """画面表示の更新 (残り2日以内の強調表示含む)"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        today = date.today()

        for idx, task in enumerate(self.task_list.tasks):
            status_text = "完了" if task.completed else "未完了"
            tags = ()

            if not task.completed:
                try:
                    due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if (due - today).days <= 2:
                        tags = ("urgent",)
                except ValueError:
                    pass

            self.tree.insert("", "end", iid=str(idx), values=(task.title, task.due_date, status_text), tags=tags)

    def request_task_check(self):
        """詳細確認リクエスト"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "確認したい課題を選択してください。")
            return

        idx = int(selected[0])
        task = self.task_list.tasks[idx]
        TaskConfirmScreen(self.root, task)

    def request_task_status_update(self):
        """状態変更リクエスト"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "状態を変更する課題を選択してください。")
            return

        idx = int(selected[0])
        task = self.task_list.tasks[idx]

        if TaskStatusConfirmScreen.confirm(task.completed):
            task.completed = not task.completed
            self.update_display()

    def request_task_deletion(self):
        """削除リクエスト"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "削除する課題を選択してください。")
            return

        idx = int(selected[0])
        task = self.task_list.tasks[idx]

        if TaskDeleteConfirmScreen.confirm(task.title):
            del self.task_list.tasks[idx]
            self.update_display()

    def request_task_sorting(self):
        """並べ替えリクエスト"""
        self.controller.sort_tasks(self.task_list)
        self.update_display()