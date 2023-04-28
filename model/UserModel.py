import json

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
        response = self.supabase.table('profiles').select('username, full_name, website').eq('id', profile_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data'][0]
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
        