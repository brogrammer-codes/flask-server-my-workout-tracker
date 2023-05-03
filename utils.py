def get_token(request):
    if(request):
        headers = request.headers
        bearer = headers.get('Authorization')    # Bearer YourTokenHere
        if(bearer):
            token = bearer.split()[1]
            return token
    return None


def get_subtree_helper(task_tree, task_id, subtree):
    for task in task_tree:
        if task['parent_id'] == task_id:
            subtree.append(task)
            get_subtree_helper(task_tree, task['id'], subtree)

def reduce_joint_array(array, key='task_details'):
    for item in array:
        flatten_task_details(item, key)

def flatten_task_details(task_to_update, key='task_details'):
    item_details = task_to_update.get(key)
    if(item_details):
        task_to_update.update(item_details)
        task_to_update.pop(key)

def merge_shared_tasks_to_profile(data):
    shared_tasks = []
    for task in data['shared_tasks']:
        task_details = [task_detail for task_detail in data['shared_task_details'] if task_detail['id'] == task['id']]
        task['task_details'] = task_details[0] if task_details else {}
        shared_tasks.append(task)
    data['shared_tasks'] = shared_tasks
    data.pop('shared_task_details')
    reduce_joint_array(data['shared_tasks'])