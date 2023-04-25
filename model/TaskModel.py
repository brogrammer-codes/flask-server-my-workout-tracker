from utils import get_subtree_helper, reduce_joint_array, flatten_task_details
from typing import List
from model.UserModel import UserModel

import json

class TaskModel:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.user_model = UserModel(supabase_client)

    def get_tasks(self, token:str, task_id=None) -> List[dict]:
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase\
            .table('tasks')\
            .select('id, parent_id, name, task_details(*)')\
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

    def search_task_by_type(self, token: str, type: str, keyword: str):
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase\
            .table('tasks')\
            .select('id, parent_id, name, task_details(*)')\
            .eq('user_id', user_id)\
            .eq('name', type)\
            .execute().json()
        folder = json.loads(response)['data'][0]
        response = self.supabase\
            .table('tasks')\
            .select('id, parent_id, name, task_details(*)')\
            .eq('user_id', user_id)\
            .eq('parent_id', folder.get('id'))\
            .execute().json()
        task_tree_json_data = json.loads(response)['data']

        task_tree_json_data = [data for data in task_tree_json_data if data['task_details'] is not None]
        # task_tree_json_data = [data for data in task_tree_json_data if data['parent_id'] is None]
        if keyword is not None:
            task_tree_json_data = [data for data in task_tree_json_data if keyword.lower() in  data['name'].lower()]
        reduce_joint_array(task_tree_json_data)
        return task_tree_json_data
    
    def create_task(self, token: str, task: dict) -> dict:
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        data = self.supabase\
            .table('tasks')\
            .insert({"parent_id": task.get('parent_id'), "user_id": user_id, "name": task.get('name')})\
            .execute()\
            .json()
        json_data = json.loads(data)['data'][0]
        data = self.supabase\
            .table('task_details')\
            .insert({"id": json_data.get('id'), "complete": task.get('complete'), "type": task.get('type'), "description": task.get('description'), "user_id": user_id, "tag_1": task.get('tag_1'), "tag_2": task.get('tag_2'), "tag_3": task.get('tag_3'), "tag_4": task.get('tag_4'), "tag_5": task.get('tag_5'), "tag_6": task.get('tag_6'), "video_url":  task.get('video_url')})\
            .execute()\
            .json()
        task_details = json.loads(data)['data'][0]
        task_details['parent_id'] = json_data.get('parent_id')
        task_details['name'] = json_data.get('name')
        return task_details
    
    def update_task(self,token: str, task: dict) -> dict:
        task_id = task.get('id')
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        data = self.supabase.table("tasks")\
            .update({"parent_id": task.get('parent_id'), "user_id": user_id, "name": task.get('name')}).eq('user_id', user_id).eq('id', task_id)\
            .execute().json()
        json_data = json.loads(data)['data'][0]
        data = self.supabase.table("task_details")\
            .update({"complete": task.get('complete'), "type": task.get('type'), "description": task.get('description'), "user_id": user_id, "tag_1": task.get('tag_1'), "tag_2": task.get('tag_2'), "tag_3": task.get('tag_3'), "tag_4": task.get('tag_4'), "tag_5": task.get('tag_5'), "tag_6": task.get('tag_6')}).eq('user_id', user_id).eq('id', task_id)\
            .execute().json()
        task_details = json.loads(data)['data'][0]
        task_details['parent_id'] = json_data.get('parent_id')
        task_details['name'] = json_data.get('name')
        return task_details

    def delete_task(self, token: str, task_id: int) -> dict:
        user = self.user_model.get_user(token)
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
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        # Get the task to duplicate
        task_to_duplicate = self.supabase.table('tasks').select('id, name, parent_id, task_details(*)').eq('user_id', user_id).eq('id', task_id).execute().json()
        task_to_duplicate = json.loads(task_to_duplicate)['data'][0]
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
    def get_task(self, token, task_id):
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        current_task = self.supabase.table('tasks')\
            .select('id, name, parent_id, task_details(*)')\
                .eq('id', task_id)\
                    .eq('user_id', user_id)\
                        .execute()\
                            .json()
        print(user_id, task_id)
        current_task = json.loads(current_task)['data'][0]
        flatten_task_details(current_task)
        
        return current_task
    def can_add_note(self, token, task_id, parent_id=None):
        user = self.user_model.get_user(token)
        user_id = user.get('user').get('id')
        task_in_routine = self.recursive_task_complete_helper(user_id, parent_id)
    def recursive_task_complete_helper(self, user_id, parent_id = None):
        if parent_id is None:
            return False
        parent_task = self.supabase.table('tasks')\
                .select('id, name, parent_id, task_details(*)')\
                    .eq('user_id', user_id)\
                        .eq('parent_id', parent_id)\
                            .execute()\
                                .json()
        parent_task = json.loads(parent_task)['data']
        return self