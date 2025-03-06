from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health')
def health():
    return jsonify({"status": "ok"})

@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)
    
@api.route('/todos/<int:id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

    
@api.route('/todos', methods=['POST'])
def create_todo():
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

    
@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    
    return jsonify(todo.to_dict())


@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200

# API that marks todo items as completed
@api.route('/todos/<int:todo_id>/complete', methods=['POST'])
def complete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    todo.completed = True
    db.session.commit()
    
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['GET'])
def filter_todos():
    # Get query parameters
    completed = request.args.get('completed')
    window = request.args.get('window', type=int)

    # Start building the query
    query = Todo.query

    # Filter by completion status if specified
    if completed is not None:
        # Convert string 'true' or 'false' to boolean
        is_completed = completed.lower() == 'true'
        query = query.filter(Todo.completed == is_completed)

    # Filter by time window if specified
    if window is not None:
        # Calculate current time and future time
        now = datetime.now()
        future = now + timedelta(days=window)
        # Filter tasks with deadline within the time window
        query = query.filter(Todo.deadline_at <= future)
        query = query.filter(Todo.deadline_at >= now)

    # Execute query and format results
    todos = query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)