"""
<<boundary>> 各種確認・入力画面
ポップアップダイアログを提供するモジュール
"""
import tkinter as tk
from tkinter import messagebox
from task import Task

class TaskConfirmScreen:
    """<<boundary>> TaskConfirmScreen: 課題内容確認画面"""
    def __init__(self, parent: tk.Tk, task: Task):
        self.win = tk.Toplevel(parent)
        self.win.title(f"課題詳細: {task.title}")
        self.win.geometry("420x320")

        tk.Label(self.win, text=f"【課題名】 {task.title}", font=("", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        tk.Label(self.win, text=f"【締切日】 {task.due_date}").pack(anchor="w", padx=10, pady=2)
        tk.Label(self.win, text=f"【状 態】 {'完了' if task.completed else '未完了'}").pack(anchor="w", padx=10, pady=2)

        tk.Label(self.win, text="【課題内容】", font=("", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 2))

        desc_box = tk.Text(self.win, wrap="word", height=8)
        desc_box.pack(fill="both", expand=True, padx=10, pady=5)
        desc_box.insert("1.0", task.description if task.description else "（詳細なし）")
        desc_box.config(state="disabled")

class TaskDeleteConfirmScreen:
    """<<boundary>> TaskDeleteConfirmScreen: 削除確認"""
    @staticmethod
    def confirm(task_title: str) -> bool:
        return messagebox.askyesno("削除確認", f"課題 '{task_title}' を削除してもよろしいですか？")

class TaskStatusConfirmScreen:
    """<<boundary>> TaskStatusConfirmScreen: 状態変更確認"""
    @staticmethod
    def confirm(current_status: bool) -> bool:
        next_status = "未完了" if current_status else "完了"
        return messagebox.askyesno("状態変更確認", f"課題の状態を '{next_status}' に変更しますか？")