import json

class UserModel:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def login_user(self, email: str, password: str) -> dict:
        session = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
        response_data = session.json()
        json_data = json.loads(response_data)
        self.supabase.postgrest.auth(session.session.access_token)
        return json_data

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
        json_data = json.loads(response_data)['data']
        return json_data

    def create_user(self, email: str, password: str, app_url: str) -> dict:
        session = self.supabase.auth.sign_up({"email": email, "password": password, "options":{"email_redirect_to": app_url}})
        response_data = session.json()
        json_data = json.loads(response_data)
        return json_data

    def update_profile(self, token: str, profile: str) -> dict:
        user = self.get_user(token)
        user_id = user.get('user').get('id')
        response = self.supabase.table('profiles').update(profile).eq('id', user_id).execute()
        response_data = response.json()
        json_data = json.loads(response_data)['data']
        return json_data