def get_token(request):
    if(request):
        headers = request.headers
        bearer = headers.get('Authorization')    # Bearer YourTokenHere
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
        item_details = item.get(key)
        if(item_details):
            item.update(item_details)
            item.pop(key)