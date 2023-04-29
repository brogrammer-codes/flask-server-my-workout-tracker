from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from utils  import get_token
import os
from model.TaskManager import TaskManager

app = Flask(__name__)
CORS(app)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
task_manager = TaskManager(url, key)
@app.route('/')
def hello_world():
    return jsonify({
        'greeting': 'Welcome to my habit tracker!',
        'body':"Our website is here to help you achieve your goals and get in shape. Whether you're just starting out or are a fitness pro, we've got the tools you need to succeed."
    })

@app.route('/user')
def user():
    token = get_token(request)
    try:
        return jsonify({
            'user': task_manager.get_user(token),
        })
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/user/profile', methods=['PATCH', 'GET'])
def patch_user_profile():
    try:
        if(request.method == 'PATCH'):
            token = get_token(request)
            data = request.get_json()
            return jsonify({
                'profile': task_manager.update_profile(token, data),
            })
        elif (request.method == 'GET'):
            user_id = request.args.get('user_id')
            return jsonify({
                'profile': task_manager.get_profile(user_id),
            })
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/profiles')
def fetch_all_profiles():
    try:
        return jsonify({
            'profiles': task_manager.get_profiles(),
        })
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/login',  methods=['POST'])
def login():
    data = request.get_json()
    try:
        email = data.get('email')
        if(email):
            return jsonify({
                'session': task_manager.login_user(email),
            }, 201)
        return Response('''{"message": "No username or password"}''', status=400, mimetype='application/json')
    except Exception as e:
        return Response('''{"message": "Email Sent"}''', status=201, mimetype='application/json')


@app.route('/task', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def addOrUpdateTask():
    data = request.get_json()
    token = get_token(request)
    task_id = data.get('task_id')
    task_get_id = request.args.get('task_id')
    try:
        if(request.method == 'POST'):
            return jsonify({
                'task': task_manager.create_task(token, data),
            }, 201)
        elif(request.method == 'PATCH'):
            return jsonify({
                'task': task_manager.update_task(token, data),
            }, 201)
        elif(request.method == 'DELETE'):
            return jsonify({
                'task': task_manager.delete_task(token, task_id),
            }, 201)
        elif(request.method == 'GET'):
            return jsonify({
                'task': task_manager.get_task(token, task_get_id),
            }, 201)
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/task/type')
def getActivity():
    token = get_token(request)
    keyword = request.args.get('keyword')
    type = request.args.get('type')
    try:
        return jsonify({
            'task': task_manager.search_task_by_type(token, type, keyword),
        }, 201)
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/task/clone', methods=['POST'])
def cloneTask():
    data = request.get_json()
    token = get_token(request)
    task_id = data.get('task_id')
    parent_id = data.get('parent_id')
    try:
        return jsonify({
            'task': task_manager.duplicate_task(token, task_id, parent_id),
        }, 201)
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')
    
@app.route('/task/complete', methods=['POST'])
def completeTask():
    data = request.get_json()
    token = get_token(request)
    print(data)
    try:
        return jsonify({
            'task': task_manager.complete_task(token, data),
        }, 201)
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/tasks')
def getTasks():
    token = get_token(request)
    task_id = request.args.get('task_id')

    try:
        return jsonify({
            'task_tree': task_manager.get_tasks(token, task_id),
        })
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)