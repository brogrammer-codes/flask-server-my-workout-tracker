
from supabase import create_client, Client
import json
from utils import get_subtree_helper, reduce_joint_array, flatten_task_details
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
            .select('id, parent_id, name, task_details(type, complete, description)')\
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
            .insert({"parent_id": task.get('parent_id'), "user_id": user_id, "name": task.get('name')})\
            .execute()\
            .json()
        json_data = json.loads(data)['data'][0]
        data = self.supabase\
            .table('task_details')\
            .insert({"id": json_data.get('id'), "complete": task.get('complete'), "type": task.get('type'), "description": task.get('description'), "user_id": user_id})\
            .execute()\
            .json()
        task_details = json.loads(data)['data'][0]
        task_details['parent_id'] = json_data.get('parent_id')
        return task_details
    
    def update_task(self,token: str, task_id: str, complete: str) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase.table("tasks")\
            .update({"complete": complete}).eq('user_id', user_id).eq('id', task_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data']
        return json_data

    def delete_task(self, token: str, task_id: int) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        # Delete corresponding entries in task_details table
        self.supabase.table('task_details').delete().eq('user_id', user_id).eq('id', task_id).execute()

        # Delete children tasks recursively
        child_tasks = self.supabase.table('tasks').select('id').eq('parent_id', task_id).execute().json()
        child_tasks = json.loads(child_tasks)['data']
        for child_task in child_tasks:
            self.delete_task(token, child_task.get('id'))
        # Delete the task itself
        self.supabase.table('tasks').delete().eq('id', task_id).execute()
    def duplicate_task(self,token, task_id, parent_id=None):
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        # Get the task to duplicate
        task_to_duplicate = self.supabase.table('tasks').select('id, name, parent_id, task_details(type, complete, description)').eq('user_id', user_id).eq('id', task_id).execute().json()
        task_to_duplicate = json.loads(task_to_duplicate)['data'][0]
        # Create a new task with the same data as the task to duplicate, but with a new name

        flatten_task_details(task_to_duplicate)
        if(parent_id):
            task_to_duplicate['parent_id'] = parent_id
        else:
            task_to_duplicate['name'] = task_to_duplicate['name'] + ' (copy)'
        task_to_duplicate.pop('id')
        new_task = self.create_task(token, task_to_duplicate)
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
