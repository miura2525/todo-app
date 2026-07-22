"""
<<control>> CreateTaskControl
ビジネスロジック・入力検証を行うコントローラーモジュール
"""
from datetime import datetime
from task import TaskList

class CreateTaskControl:
    """各種操作のバリデーションと制御を行うクラス"""
    
    @staticmethod
    def validate_task(task_content: str, due_date: str, task_list: TaskList) -> tuple[bool, str]:
        """入力された課題内容および締切日の検証"""
        if not task_content.strip():
            return False, "課題名を入力してください。"
        
        if not task_list.check_contents_length(task_content):
            return False, f"課題名は{task_list.max_contents_length}文字以内で入力してください。"
            
        try:
            datetime.strptime(due_date.strip(), "%Y-%m-%d")
        except ValueError:
            return False, "締切日は YYYY-MM-DD 形式で入力してください。"
            
        return True, ""

    @staticmethod
    def sort_tasks(task_list: TaskList) -> None:
        """締切日の昇順で並べ替え"""
        task_list.tasks.sort(key=lambda x: x.due_date)