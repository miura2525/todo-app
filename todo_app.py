import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date

class Task:
    """課題オブジェクト"""
    def __init__(self, title: str, description: str, due_date: str):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = False

class CreateTaskController:
    """【Control】"""
    @staticmethod
    def validate_title(title: str) -> tuple[bool, str]:
        """課題名の文字数バリデーション（20文字以内）"""
        if not title.strip():
            return False, "課題名を入力してください。"
        if len(title.strip()) > 20:
            return False, "課題名は20文字以内で入力してください。"
        return True, ""

    @staticmethod
    def validate_date(date_str: str) -> tuple[bool, str]:
        """締切日の形式チェック (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "締切日は YYYY-MM-DD 形式で入力してください。"

class ToDoApp:
    """【Boundary】GUIメイン画面 (HomeScreen)"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("課題管理(ToDo) アプリケーション")
        self.root.geometry("680x560")

        self.tasks: list[Task] = []
        self.controller = CreateTaskController()

        # UI構築
        self._create_input_frame()
        self._create_control_frame()
        self._create_list_frame()
        self._create_action_frame()

    def _create_input_frame(self):
        """1. 新規課題の入力フォーム"""
        input_frame = tk.LabelFrame(self.root, text="新規課題の追加", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # 課題名 (最大20字)
        tk.Label(input_frame, text="課題名 (20字以内):").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = tk.Entry(input_frame, width=35)
        self.title_entry.grid(row=0, column=1, columnspan=2, sticky="w", pady=2)

        # 締切日
        tk.Label(input_frame, text="締切日 (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=2)
        self.due_entry = tk.Entry(input_frame, width=18)
        self.due_entry.grid(row=1, column=1, sticky="w", pady=2)
        self.due_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        # 課題内容
        tk.Label(input_frame, text="課題内容:").grid(row=2, column=0, sticky="nw", pady=2)
        self.desc_text = tk.Text(input_frame, width=40, height=3)
        self.desc_text.grid(row=2, column=1, sticky="w", pady=2)

        # 追加ボタン
        add_btn = tk.Button(input_frame, text="追加", command=self.add_task, bg="#4CAF50", fg="white", font=("", 9, "bold"), width=8)
        add_btn.grid(row=2, column=2, sticky="se", padx=5, pady=2)

    def _create_control_frame(self):
        """2. 並べ替えボタンフレーム"""
        ctrl_frame = tk.Frame(self.root, padx=10)
        ctrl_frame.pack(fill="x", padx=10, pady=2)

        sort_btn = tk.Button(ctrl_frame, text="締切日の昇順で並べ替え", command=self.sort_tasks)
        sort_btn.pack(side="left")

        # 強調表示の凡例
        legend_lbl = tk.Label(ctrl_frame, text="※ 背景色ピンク: 締切2日以内(未完了)", fg="#d32f2f", font=("", 8))
        legend_lbl.pack(side="right")

    def _create_list_frame(self):
        """3. 課題一覧表示 (Treeview)"""
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

        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 強調表示タグの設定（残り2日以内）
        self.tree.tag_configure("urgent", background="#FFEBEE", foreground="#C62828")

    def _create_action_frame(self):
        """4. 操作ボタン（詳細確認・状態変更・削除）"""
        btn_frame = tk.Frame(self.root, padx=10, pady=10)
        btn_frame.pack(fill="x")

        view_btn = tk.Button(btn_frame, text="詳細を確認", command=self.view_detail)
        view_btn.pack(side="left", padx=5)

        toggle_btn = tk.Button(btn_frame, text="完了 / 未完了 に変更", command=self.toggle_status)
        toggle_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(btn_frame, text="削除", command=self.delete_task, bg="#f44336", fg="white")
        delete_btn.pack(side="right", padx=5)

    def add_task(self):
        """課題内容を登録する"""
        title = self.title_entry.get()
        due_date = self.due_entry.get()
        description = self.desc_text.get("1.0", tk.END).strip()

        # 入力検証
        valid_title, msg_title = self.controller.validate_title(title)
        if not valid_title:
            messagebox.showwarning("入力エラー", msg_title)
            return

        valid_date, msg_date = self.controller.validate_date(due_date)
        if not valid_date:
            messagebox.showwarning("入力エラー", msg_date)
            return

        # 登録処理
        new_task = Task(title.strip(), description, due_date.strip())
        self.tasks.append(new_task)

        # フォーム初期化
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)

        self.update_list()
        messagebox.showinfo("完了", f"課題 '{new_task.title}' を登録しました。")

    def update_list(self):
        """画面一覧の再描画（残り2日以内の強調表示判定を含む）"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        today = date.today()

        for idx, task in enumerate(self.tasks):
            status_text = "完了" if task.completed else "未完了"
            tags = ()

            # 6. 残り2日以内の強調表示判定
            if not task.completed:
                try:
                    due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    days_left = (due - today).days
                    if days_left <= 2:
                        tags = ("urgent",)
                except ValueError:
                    pass

            self.tree.insert("", "end", iid=str(idx), values=(task.title, task.due_date, status_text), tags=tags)

    def view_detail(self):
        """課題内容を確認する"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "確認したい課題を選択してください。")
            return

        idx = int(selected[0])
        task = self.tasks[idx]

        # 詳細画面ポップアップ (TaskConfirmScreen/TaskInputScreen役割)
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"課題詳細: {task.title}")
        detail_win.geometry("420x320")

        tk.Label(detail_win, text=f"【課題名】 {task.title}", font=("", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        tk.Label(detail_win, text=f"【締切日】 {task.due_date}").pack(anchor="w", padx=10, pady=2)
        tk.Label(detail_win, text=f"【状 態】 {'完了' if task.completed else '未完了'}").pack(anchor="w", padx=10, pady=2)

        tk.Label(detail_win, text="【課題内容】", font=("", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 2))

        desc_box = tk.Text(detail_win, wrap="word", height=8)
        desc_box.pack(fill="both", expand=True, padx=10, pady=5)
        desc_box.insert("1.0", task.description if task.description else "（詳細なし）")
        desc_box.config(state="disabled")

    def toggle_status(self):
        """完了/未完了状態に変更する"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "状態を変更する課題を選択してください。")
            return

        idx = int(selected[0])
        self.tasks[idx].completed = not self.tasks[idx].completed
        self.update_list()

    def delete_task(self):
        """課題を削除する"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("選択エラー", "削除する課題を選択してください。")
            return

        idx = int(selected[0])
        task = self.tasks[idx]

        if messagebox.askyesno("削除確認", f"課題 '{task.title}' を削除してもよろしいですか？"):
            del self.tasks[idx]
            self.update_list()

    def sort_tasks(self):
        """課題を並べ替える（締切日の昇順）"""
        self.tasks.sort(key=lambda x: x.due_date)
        self.update_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()