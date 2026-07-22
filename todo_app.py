import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date

# ==========================================
# Entity Classes (エンティティクラス)
# ==========================================

class Task:
    """課題情報を保持するエンティティクラス"""
    def __init__(self, task_content: str, due_date: date):
        self.task_content = task_content
        self.due_date = due_date
        self.is_completed = False

    def set_completed(self, status: bool):
        self.is_completed = status


class TaskList:
    """課題の一覧および検証・追加等のドメインロジックを担うエンティティクラス"""
    def __init__(self):
        self.max_contents_length = 20  # 仕様書・詳細設計：最大文字数20字[cite: 1, 4]
        self.tasks = []

    def check_contents_length(self, contents: str) -> bool:
        """文字数制限(20文字以内)をチェックする[cite: 1, 4]"""
        return len(contents) <= self.max_contents_length

    def add_task(self, new_task: Task):
        """課題を追加する[cite: 1, 4]"""
        self.tasks.append(new_task)


# ==========================================
# Control Class (コントロールクラス)
# ==========================================

class CreateTaskControl:
    """ユースケースの制御および画面とエンティティの仲介を担うコントロールクラス[cite: 4]"""
    def __init__(self):
        self.task_list = TaskList()

    def validate_task(self, task_content: str, due_date_str: str) -> bool:
        """入力データのバリデーション（文字数制限、日付形式チェック）[cite: 3, 4]"""
        if not self.task_list.check_contents_length(task_content):
            return False
        try:
            # 日付フォーマットの検証 (MM/DD または YYYY/MM/DD 等)
            parts = due_date_str.split('/')
            if len(parts) == 2:
                current_year = date.today().year
                month, day = map(int, parts)
                date(current_year, month, day)
            elif len(parts) == 3:
                year, month, day = map(int, parts)
                date(year, month, day)
            else:
                return False
            return True
        except ValueError:
            return False

    def parse_date(self, due_date_str: str) -> date:
        """文字列からdateオブジェクトを生成[cite: 1]"""
        parts = list(map(int, due_date_str.split('/')))
        if len(parts) == 2:
            return date(date.today().year, parts[0], parts[1])
        return date(parts[0], parts[1], parts[2])

    def register_task(self, task_content: str, due_date_str: str):
        """課題を新規登録する[cite: 3, 4]"""
        due_date = self.parse_date(due_date_str)
        new_task = Task(task_content, due_date)
        self.task_list.add_task(new_task)

    def delete_task(self, task: Task):
        """課題を削除する[cite: 3, 4]"""
        if task in self.task_list.tasks:
            self.task_list.tasks.remove(task)

    def sort_tasks(self):
        """課題を締切日の昇順に並べ替える[cite: 1, 3, 4]"""
        self.task_list.tasks.sort(key=lambda x: x.due_date)

    def update_task_status(self, task: Task, status: bool):
        """課題の完了・未完了状態を更新する[cite: 1, 3, 4]"""
        task.set_completed(status)


# ==========================================
# Boundary Classes (バウンダリ/画面クラス)
# ==========================================

class TaskInputScreen(tk.Toplevel):
    """課題内容入力画面[cite: 3, 4]"""
    def __init__(self, parent, control: CreateTaskControl, initial_content="", initial_date=""):
        super().__init__(parent)
        self.title("課題内容入力")
        self.geometry("350x200")
        self.control = control
        self.result = None

        tk.Label(self, text="課題名 (20字以内):").pack(anchor="w", padx=10, pady=(10,0))
        self.entry_content = tk.Entry(self, width=30)
        self.entry_content.insert(0, initial_content)
        self.entry_content.pack(padx=10, pady=5)

        tk.Label(self, text="締切日 (月/日 例: 7/24):").pack(anchor="w", padx=10, pady=(5,0))
        self.entry_date = tk.Entry(self, width=30)
        self.entry_date.insert(0, initial_date)
        self.entry_date.pack(padx=10, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="確認へ", command=self.enter_task_content).pack(side="left", padx=5)
        tk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(side="left", padx=5)

    def enter_task_content(self):
        content = self.entry_content.get().strip()
        due_date_str = self.entry_date.get().strip()

        if not content or not due_date_str:
            messagebox.showwarning("警告", "すべての項目を入力してください。")
            return

        if not self.control.validate_task(content, due_date_str):
            messagebox.showerror("エラー", "入力内容に誤りがあります。\n※課題名は20文字以内、日付は正しい形式(月/日)で入力してください。")
            return

        self.result = (content, due_date_str)
        self.destroy()


class TaskConfirmScreen(tk.Toplevel):
    """課題内容確認画面[cite: 3, 4]"""
    def __init__(self, parent, content: str, due_date_str: str):
        super().__init__(parent)
        self.title("課題内容確認")
        self.geometry("300x180")
        self.confirmed = False
        self.action = None  # 'confirm', 'modify', 'cancel'

        tk.Label(self, text="【以下の内容で登録しますか？】", font=("", 10, "bold")).pack(pady=10)
        tk.Label(self, text=f"課題名: {content}").pack(anchor="w", padx=20)
        tk.Label(self, text=f"締切日: {due_date_str}").pack(anchor="w", padx=20)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="確定", command=self.confirm_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="修正", command=self.modify_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="取消", command=self.cancel_task).pack(side="left", padx=5)

    def confirm_task(self):
        self.action = 'confirm'
        self.destroy()

    def modify_task(self):
        self.action = 'modify'
        self.destroy()

    def cancel_task(self):
        self.action = 'cancel'
        self.destroy()


class TaskDeleteConfirmScreen(tk.Toplevel):
    """課題削除確認画面[cite: 3, 4]"""
    def __init__(self, parent, task: Task):
        super().__init__(parent)
        self.title("削除確認")
        self.geometry("300x150")
        self.confirmed = False

        tk.Label(self, text="本当にこの課題を削除しますか？", font=("", 10)).pack(pady=15)
        tk.Label(self, text=f"課題名: {task.task_content}").pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="削除実行", command=self.confirm_task_deletion).pack(side="left", padx=10)
        tk.Button(btn_frame, text="中止", command=self.destroy).pack(side="left", padx=10)

    def confirm_task_deletion(self):
        self.confirmed = True
        self.destroy()


class TaskStatusConfirmScreen(tk.Toplevel):
    """状態変更確認画面[cite: 3, 4]"""
    def __init__(self, parent, task: Task, target_status: bool):
        super().__init__(parent)
        self.title("状態変更確認")
        self.geometry("300x150")
        self.confirmed = False
        
        status_str = "完了" if target_status else "未完了"
        tk.Label(self, text=f"課題の状態を「{status_str}」に変更しますか？", font=("", 10)).pack(pady=15)
        tk.Label(self, text=f"課題名: {task.task_content}").pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="変更実行", command=self.confirm_task_status_update).pack(side="left", padx=10)
        tk.Button(btn_frame, text="中止", command=self.destroy).pack(side="left", padx=10)

    def confirm_task_status_update(self):
        self.confirmed = True
        self.destroy()


class HomeScreen(tk.Tk):
    """メイン画面（ホーム画面）[cite: 3, 4]"""
    def __init__(self):
        super().__init__()
        self.title("課題管理(ToDo) アプリケーション")
        self.geometry("600x450")
        self.control = CreateTaskControl()

        # ヘッダー操作エリア
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(header_frame, text="新規課題追加", command=self.request_task_registration, bg="#e1f5fe").pack(side="left", padx=5)
        tk.Button(header_frame, text="締切日順に並べ替え", command=self.request_task_sorting, bg="#fff3e0").pack(side="left", padx=5)

        # 課題一覧表示エリア
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh_task_list()

    def refresh_task_list(self):
        """画面の一覧表示を再描画する[cite: 1]"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        tasks = self.control.task_list.tasks

        if not tasks:
            tk.Label(self.list_frame, text="登録されている課題はありません。", fg="gray").pack(pady=20)
            return

        today = date.today()

        for idx, task in enumerate(tasks):
            task_frame = tk.Frame(self.list_frame, relief="ridge", bd=1)
            task_frame.pack(fill="x", pady=3, ipady=3)

            # 強調表示判定（締切日まで残り2日以内）[cite: 1]
            days_remaining = (task.due_date - today).days
            is_urgent = (0 <= days_remaining <= 2) and not task.is_completed

            # テキスト色の決定[cite: 1]
            if task.is_completed:
                fg_color = "gray"
                status_text = "[完了]"
            elif is_urgent:
                fg_color = "red"
                status_text = "[! 締切間近 !]"
            else:
                fg_color = "black"
                status_text = "[未完了]"

            display_text = f"{status_text} {task.task_content} (締切: {task.due_date.strftime('%m/%d')})"
            label = tk.Label(task_frame, text=display_text, fg=fg_color, font=("", 10, "bold" if is_urgent else "normal"))
            label.pack(side="left", padx=10)

            # 操作ボタン群[cite: 1]
            btn_box = tk.Frame(task_frame)
            btn_box.pack(side="right", padx=5)

            if task.is_completed:
                tk.Button(btn_box, text="未完了に戻す", command=lambda t=task: self.request_task_status_update(t, False)).pack(side="left", padx=2)
            else:
                tk.Button(btn_box, text="完了", command=lambda t=task: self.request_task_status_update(t, True)).pack(side="left", padx=2)

            tk.Button(btn_box, text="削除", command=lambda t=task: self.request_task_deletion(t)).pack(side="left", padx=2)

    def request_task_registration(self):
        """課題登録要求イベント処理[cite: 3, 4]"""
        content, date_str = "", ""
        while True:
            input_screen = TaskInputScreen(self, self.control, content, date_str)
            self.wait_window(input_screen)

            if not input_screen.result:
                break  # キャンセル時[cite: 3]

            content, date_str = input_screen.result

            confirm_screen = TaskConfirmScreen(self, content, date_str)
            self.wait_window(confirm_screen)

            if confirm_screen.action == 'confirm':
                self.control.register_task(content, date_str)
                self.refresh_task_list()
                break
            elif confirm_screen.action == 'modify':
                continue  # 修正のため入力画面へ戻る[cite: 3]
            else:
                break  # 取消[cite: 3]

    def request_task_deletion(self, task: Task):
        """課題削除要求イベント処理[cite: 3, 4]"""
        delete_screen = TaskDeleteConfirmScreen(self, task)
        self.wait_window(delete_screen)

        if delete_screen.confirmed:
            self.control.delete_task(task)
            self.refresh_task_list()

    def request_task_status_update(self, task: Task, target_status: bool):
        """課題状態変更要求イベント処理[cite: 3, 4]"""
        status_screen = TaskStatusConfirmScreen(self, task, target_status)
        self.wait_window(status_screen)

        if status_screen.confirmed:
            self.control.update_task_status(task, target_status)
            self.refresh_task_list()

    def request_task_sorting(self):
        """課題並べ替え要求イベント処理[cite: 3, 4]"""
        self.control.sort_tasks()
        self.refresh_task_list()


if __name__ == "__main__":
    app = HomeScreen()
    app.mainloop()