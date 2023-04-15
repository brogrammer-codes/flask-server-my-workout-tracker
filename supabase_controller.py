
import os
from supabase import create_client, Client
import json

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user(token, user_id):
    user = supabase.auth.get_user(token)
    response_data = user.json()
    json_data = json.loads(response_data)['user']
    if(user_id):
      response = supabase.table('profiles').select('username, full_name, website', count='exact').eq('id', user_id).execute()
      user_profile = response.json()
      user_json_data = json.loads(user_profile)['data']
      return {'profile': user_json_data, 'user': json_data}
    return json_data

def create_user(email, password, app_url):
    session = supabase.auth.sign_up(
        {"email": email, "password": password, "options":{"email_redirect_to": app_url}})
    response_data = session.json()
    json_data = json.loads(response_data)
    # supabase.postgrest.auth(session.session.access_token)
    return json_data

def login_user(email, password):
    session = supabase.auth.sign_in_with_password(
        {"email": email, "password": password})
    response_data = session.json()
    json_data = json.loads(response_data)
    supabase.postgrest.auth(session.session.access_token)
    return json_data

def add_task(token, parent_id, user_id, name):
    # print(token, parent_id, user_id, name)
    supabase.postgrest.auth(token)
    data = supabase\
        .table('tasks')\
        .insert({"parent_id": parent_id, "name": name, "user_id": user_id})\
        .execute()

    response_data = data.json()
    json_data = json.loads(response_data)['data']
    return json_data

def get_tasks(token, user_id):
    supabase.postgrest.auth(token)
    response = supabase.table('tasks').select('id, name, parent_id, complete').eq('user_id', user_id).execute()
    task_tree = response.json()
    task_tree_json_data = json.loads(task_tree)['data']
    return task_tree_json_data

def update_task(token, user_id, task_id, complete):
    supabase.postgrest.auth(token)
    response = supabase.table("tasks")\
        .update({"complete": complete}).eq('user_id', user_id).eq('id', task_id).execute()
    response_data = response.json()
    json_data = json.loads(response_data)['data']
    return json_data