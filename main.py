"""
エントリーポイント（プログラム実行ファイル）
"""
import tkinter as tk
from main_screen import HomeScreen

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeScreen(root)
    root.mainloop()