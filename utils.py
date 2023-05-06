from enums.task import TaskTypes

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
  

def create_task_payload(array, key='task_details'):
    for item in array:
        flatten_task_details(item, key)
        item['can_complete'] = can_complete(array, item)

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
    create_task_payload(data['shared_tasks'])
        
def can_complete(tasktree, task = None):
    if task is None or task.get('complete') == True:
        return False
    parent_id = task.get('parent_id')
    while parent_id is not None:
        parent = next((t for t in tasktree if t.get('id') == parent_id), None)
        if parent is None:
            return False
        # Some tasks in the array are flattened, others still have the `task_details` so we need the extra check
        # TODO: Clean this up at some point
        if parent.get('task_details'):
            if parent.get('task_details').get('type') == TaskTypes.ROUTINE.value:
                return True
        else:
            if parent.get('type') == TaskTypes.ROUTINE.value:
                return True
        
        parent_id = parent.get('parent_id')

    return False