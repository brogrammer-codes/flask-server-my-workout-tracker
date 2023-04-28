
from supabase import create_client
from typing import List
from model.UserModel import UserModel
from model.TaskModel import TaskModel

class TaskManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self.user_model = UserModel(self.supabase)
        self.task_model = TaskModel(self.supabase)

    def login_user(self, email: str) -> dict:
        return self.user_model.login_user(email)
    
    def get_user(self, token: str) -> dict:
        return self.user_model.get_user(token)

    def create_user(self, email: str, password: str, app_url: str) -> dict:
        return self.user_model.create_user(email, password, app_url)

    def get_profile(self, profile_id: int) -> dict:
        return self.user_model.get_profile(profile_id)

    def update_profile(self, token: str, profile: str) -> dict:
        return self.user_model.update_profile(token, profile)

    def update_password(self, token: str, password: str) -> dict:
        return self.user_model.set_password(token, password)
    
    def get_tasks(self, token:str, task_id=None) -> List[dict]:
        return self.task_model.get_tasks(token, task_id)
    
    def get_task(self, token:str, task_id) -> dict:
        return self.task_model.get_task(token, task_id)
    
    def search_task_by_type(self, token: str, type: str, keyword: str) -> List[dict]:
        return self.task_model.search_task_by_type(token, type, keyword)

    def create_task(self, token: str, task: dict) -> dict:
        return self.task_model.create_task(token, task)

    
    def update_task(self,token: str, task: dict) -> dict:
        return self.task_model.update_task(token, task)


    def delete_task(self, token: str, task_id: int) -> dict:
        return self.task_model.delete_task(token, task_id)

    def duplicate_task(self,token, task_id, parent_id=None):
        return self.task_model.duplicate_task(token, task_id, parent_id)
    
    def complete_task(self, token, task):
        return self.task_model.duplicate_task(token, task)


