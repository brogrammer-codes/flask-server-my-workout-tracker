
from supabase import create_client, Client
import json
from utils import get_subtree_helper
from typing import List

class TaskManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)

    def login_user(self, email: str, password: str) -> dict:
        session = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
        response_data = session.json()
        json_data = json.loads(response_data)
        self.supabase.postgrest.auth(session.session.access_token)
        return json_data
    
    def get_tasks(self, token:str, task_id=None) -> List[dict]:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase.table('tasks').select('id, name, parent_id, complete').eq('user_id', user_id).execute()
        task_tree = response.json()
        task_tree_json_data = json.loads(task_tree)['data']
        if(task_id is not None):
            subtree = []
            for task in task_tree_json_data:
                if task['id'] == task_id:
                    subtree.append(task)
                    get_subtree_helper(task_tree_json_data, task_id, subtree)
                    break
            return subtree
        return task_tree_json_data

    def create_task(self, token: str, task: dict) -> dict:
        parent_id = task.get('parent_id')
        name = task.get('name')
        # task_id = task.get('task_id')
        # complete = data.get('complete')
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        data = self.supabase\
            .table('tasks')\
            .insert({"parent_id": parent_id, "name": name, "user_id": user_id})\
            .execute()
        response_data = data.json()
        json_data = json.loads(response_data)['data']
        return json_data
    
    def update_task(self,token: str, task_id: str, complete: str) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase.table("tasks")\
            .update({"complete": complete}).eq('user_id', user_id).eq('id', task_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data']
        return json_data

    def delete_task(self, token: str, task_id: int) -> dict:
        # implementation of delete_task function
        pass

    def create_user(self, email: str, password: str, app_url: str) -> dict:
        session = self.supabase.auth.sign_up({"email": email, "password": password, "options":{"email_redirect_to": app_url}})
        response_data = session.json()
        json_data = json.loads(response_data)
        return json_data

    def get_user(self, token: str, user_id=None) -> dict:
        self.supabase.postgrest.auth(token)
        user = self.supabase.auth.get_user(token)
        response_data = user.json()
        json_data = json.loads(response_data)['user']
        if(user_id is not None):
            response = self.supabase.table('profiles').select('id, username, full_name, website', count='exact').eq('id', user_id).execute()
            user_profile = response.json()
            user_json_data = json.loads(user_profile)['data']
            return {'profile': user_json_data, 'user': json_data}
        else:
            token_user_id = json_data.get('id')
            response = self.supabase.table('profiles').select('id, username, full_name, website', count='exact').eq('id', token_user_id).execute()
            user_profile = response.json()
            user_json_data = json.loads(user_profile)['data']
            return {'profile': user_json_data, 'user': json_data}

    def get_profile(self, profile_id: int) -> dict:
        response = self.supabase.table('profiles').select('username, full_name, website').eq('id', profile_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data']
        return json_data

    def update_profile(self, token: str, profile: str) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase.table('profiles').update(profile).eq('id', user_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data']
        return json_data
