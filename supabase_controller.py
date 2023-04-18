
from supabase import create_client, Client
import json
from utils import get_subtree_helper, reduce_joint_array
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
        response = self.supabase\
            .table('tasks')\
            .select('id, parent_id, task_details(name, type, complete, description)')\
            .eq('user_id', user_id)\
            .execute().json()
        task_tree_json_data = json.loads(response)['data']
        reduce_joint_array(task_tree_json_data)
        # think of a better way to do this
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
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        data = self.supabase\
            .table('tasks')\
            .insert({"parent_id": task.get('parent_id'), "user_id": user_id})\
            .execute()\
            .json()
        json_data = json.loads(data)['data'][0]
        data = self.supabase\
            .table('task_details')\
            .insert({"id": json_data.get('id'), "name": task.get('name'), "complete": task.get('complete'), "type": task.get('type'), "description": task.get('description'), "user_id": user_id})\
            .execute()\
            .json()
        task_details = json.loads(data)['data'][0]
        return {"task": json_data, "details": task_details}
    
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
    def duplicate_task(self,token, task_id, parent_id=None):
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        # Get the task to duplicate
        task_to_duplicate = self.supabase.table('tasks').select('id, name, parent_id, complete').eq('user_id', user_id).eq('id', task_id).execute().json()
        task_to_duplicate = json.loads(task_to_duplicate)['data'][0]

        # Create a new task with the same data as the task to duplicate, but with a new name
        new_task = {
            "name": task_to_duplicate['name'] + ' (copy)' if parent_id is None else task_to_duplicate['name'],
            "parent_id": task_to_duplicate['parent_id'] if parent_id is None else parent_id,
            "complete": task_to_duplicate['complete'],

        }
        new_task_name = task_to_duplicate['name'] + ' (copy)'
        new_task_parent_id = task_to_duplicate['parent_id'] if parent_id is None else parent_id
        new_task = self.supabase.table('tasks')\
            .insert({'name': new_task_name, 'parent_id': new_task_parent_id, 'complete': task_to_duplicate['complete'], "user_id": user_id})\
            .execute().json()
        new_task = json.loads(new_task)['data'][0]
        # Duplicate the sub-tasks of the task to duplicate
        sub_tasks = self.supabase.table('tasks').select('id').eq('parent_id', task_id).execute().json()
        sub_tasks = json.loads(sub_tasks)['data']
        for sub_task in sub_tasks:
            self.duplicate_task(token, sub_task['id'], new_task['id'])
        return new_task

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
