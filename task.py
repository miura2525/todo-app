"""
<<entity>> Task, TaskList
課題データおよび課題リストを管理するモジュール
"""

class Task:
    """課題単体のエンティティ"""
    def __init__(self, title: str, description: str, due_date: str):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = False

class TaskList:
    """課題群を管理するコレクションエンティティ"""
    def __init__(self, max_contents_length: int = 20):
        self.max_contents_length = max_contents_length
        self.tasks: list[Task] = []

    def check_contents_length(self, contents: str) -> bool:
        """課題名の文字数チェック (20字以内)"""
        return len(contents.strip()) <= self.max_contents_length

    def add_task(self, new_task: Task) -> None:
        """課題の追加"""
        self.tasks.append(new_task)