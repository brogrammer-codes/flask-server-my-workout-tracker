import json
from utils import  merge_shared_tasks_to_profile, reduce_joint_array

class UserModel:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def login_user(self, email: str) -> dict:
        self.supabase.auth.sign_in_with_otp({'email': email})

    def get_user(self, token: str) -> dict:
        self.supabase.postgrest.auth(token)
        user = self.supabase.auth.get_user(token).json()
        json_data = json.loads(user)['user']
        token_user_id = json_data.get('id')
        profile = self.get_profile(token_user_id)
        return {'profile': profile, 'user': json_data}
    
    def get_profile(self, profile_id: int) -> dict:
        
        response = self.supabase.table('profiles').select('*, shared_tasks(*), shared_task_details(*)').eq('id', profile_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data'][0]
        merge_shared_tasks_to_profile(json_data)
        complete_task = self.supabase.table('tasks')\
            .select('id, name, parent_id, task_details(*)')\
                .eq('user_id', profile_id)\
                    .eq('task_details.complete', True)\
                        .execute()\
                            .json()
        complete_task_data = json.loads(complete_task)['data']
        complete_task_data = [data for data in complete_task_data if data['task_details'] is not None]
        json_data['complete_tasks'] = complete_task_data
        return json_data

    def get_profiles(self) -> dict:
        profiles_response = self.supabase.table('profiles').select('id, username, website, favorite_activity, shared_tasks(*), shared_task_details(*)').execute()
        response_data = profiles_response.json()
        json_data = json.loads(response_data)['data']
        json_data = [data for data in json_data if data['username'] is not None]
        for data in json_data:
            shared_tasks = []
            for task in data['shared_tasks']:
                task_details = [task_detail for task_detail in data['shared_task_details'] if task_detail['id'] == task['id']]
                task['task_details'] = task_details[0] if task_details else {}
                shared_tasks.append(task)
            data['shared_tasks'] = shared_tasks
            data.pop('shared_task_details')
            reduce_joint_array(data['shared_tasks'])
        return json_data

    def update_profile(self, token: str, profile: dict) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase.table('profiles').update(profile).eq('id', user_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data']
        return json_data
    
    def set_password(self, token: str, password: str) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        self.supabase.auth.sign_in_with_otp({'email': password})
        return self.get_user(token)
        