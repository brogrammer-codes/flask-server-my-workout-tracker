from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from supabase_controller import create_user, login_user, get_user, add_task, get_tasks, update_task
from utils  import get_token
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return jsonify({
        'greeting': 'Welcome to my habit tracker!',
        'body':"Our website is here to help you achieve your goals and get in shape. Whether you're just starting out or are a fitness pro, we've got the tools you need to succeed."
    })

@app.route('/user')
def user():
    token = get_token(request)
    user_id = request.args.get('user_id')
    try:
        return jsonify({
            'user': get_user(token, user_id),
        })
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/sign-up',  methods=['POST'])
def signUp():
    data = request.get_json()
    try:
        email = data.get('email')
        password = data.get('password')
        app_url = data.get('app_url')
        if(email and password):
            return jsonify({
                'session': create_user(email, password, app_url),
            }, 201)
        return Response('''{"message": "No username or password"}''', status=400, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/login',  methods=['POST'])
def login():
    data = request.get_json()
    try:
        email = data.get('email')
        password = data.get('password')
        if(email and password):
            return jsonify({
                'session': login_user(email, password),
            }, 201)
        return Response('''{"message": "No username or password"}''', status=400, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/task', methods=['POST', 'PATCH'])
def addOrUpdateTask():
    data = request.get_json()
    token = get_token(request)
    parent_id = data.get('parent_id')
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    name = data.get('name')
    complete = data.get('complete')
    try:
        if(request.method == 'POST'):
            return jsonify({
                'task': add_task(token, parent_id, user_id, name),
            }, 201)
        elif(request.method == 'PATCH'):
            for key in data:
                print(key)
            return jsonify({
                'task': update_task(token, user_id, task_id, complete),
            }, 201)
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

@app.route('/tasks')
def getTasks():
    token = get_token(request)
    user_id = request.args.get('user_id')
    try:
        return jsonify({
            'task_tree': get_tasks(token, user_id),
        })
    except Exception as e:
        print(e)
        return Response('''{"message": "Bad Request"}''', status=400, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)