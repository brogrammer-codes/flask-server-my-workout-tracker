def get_token(request):
    if(request):
        headers = request.headers
        bearer = headers.get('Authorization')    # Bearer YourTokenHere
        if(bearer):
            token = bearer.split()[1]
            return token
    return ''


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

