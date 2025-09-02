from flask import Flask, abort
from flask_smorest import Api, Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields
from uuid import uuid4
from datetime import datetime, timezone
import enum

server = Flask(__name__)

# Configuration object
class APIConfig:
    API_TITLE = 'TODO APP'
    API_VERSION = 'v1'
    # Automatic REST API documentation in machine readable format
    OPENAPI_VERSION = '3.0.3'
    # Give base url for generated docs - in this case /docs but if we said /api it would be /api/docs for example
    OPENAPI_URL_PREFIX = '/'
    # Where the docs are available. Swagger UI displays the docs as an interactive webpage
    OPENAPI_SWAGGER_UI_PATH = '/docs'
    # Content Delivery Network - don't have to install / server files ourselves
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    # If ReDoc interface preferred OPENAPI specs shown at http://localhost:5000/redoc (or whatever server url is/redoc)
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_REDOC_UI_URL = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'

# Load configuration
server.config.from_object(APIConfig)

# Extends server
api = Api(server)

# Blueprints: set of url paths that belong together in a part of your app - domain organisation: allows separate config/access requirements for groups
todo = Blueprint('todo blueprint', 'todo', url_prefix='/todo', description='TODO API') # /todo group

# Normally in database not hardcoded
tasks = [
    {
        'id': uuid4(),
        'created': datetime.now(timezone.utc), 
        'completed': False,
        'task': 'Create Flask API'
    }
]

# Marshmallow models. These classes act like interface in TypeScript + allow control over which fields allowed / needed for each
# USING PASCAL CASE FOR CLASSNAMES FOR FRONTEND COMPATABILITY|
class CreateTask(Schema):
    task = fields.String()

class UpdateTask(CreateTask): # Inherits from CreateTask - has task property and what we add
    completed = fields.Bool()

class Task(UpdateTask): # Inherits task and completed
    id = fields.UUID()
    created = fields.DateTime()

class ListTasks(Schema):
    tasks = fields.List(fields.Nested(Task))

class SortByEnum(enum.Enum):
    task = 'task'
    created = 'created'

class SortDirectionEnum(enum.Enum):
    asc = 'asc'
    desc = 'desc'

class ListTasksParameters(Schema):
    order_by = fields.Enum(SortByEnum, load_default=SortByEnum.created)
    order = fields.Enum(SortDirectionEnum, load_default=SortDirectionEnum.asc)



# Classes allow grouping by url with various HTTP methods
# MethodView = flask class that allows urls as classes
@todo.route('/tasks') # todo blueprint (which uses todo as url prefix) with /tasks path -> todo/tasks
class TodoCollection(MethodView): # Collection vs singleton
    @todo.arguments(ListTasksParameters, location='query')
    @todo.response(status_code=200, schema=ListTasks)
    def get(self, parameters):
        return {
            'tasks': sorted(tasks, # from ListTasks. Use hard values rather than .get etc as we gave default values so is fallback.
            key=lambda task: task[parameters['order_by'].value], # Order_by is limited to the values we have given it and so prevents SQL injection as well as making API more predictable
            reverse=parameters['order'] == SortDirectionEnum.desc)

            }

    # ANY INPUT = ARGUMENT
    @todo.arguments(CreateTask) # As defined above
    @todo.response(status_code=201, schema=Task) # Resource created code
    def post(self, task):
        task['id'] = uuid4()
        task['created'] = datetime.now(timezone.utc)
        task['completed'] = False
        tasks.append(task)
        return task
    
# Singleton endpoint   
@todo.route('/tasks/<uuid:task_id>') # Search by specific id (uuid type)
class  TodoTask(MethodView):
    @todo.response(status_code=200, schema=Task)
    def get(self, task_id):
        for task in tasks:
            if task['id'] == task_id:
                return task
        abort(404, f'Task with ID {task_id} not found.')    

    @todo.arguments(UpdateTask)
    @todo.response(status_code=200, schema=Task)
    def put(self, payload, task_id): # Parameter order does matter
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = payload['completed']
                task['task'] = payload['task']
                return task
        abort(404, f'Task with ID {task_id} not found.')

    @todo.response(status_code=204) # Empty response
    def delete(self, task_id):
        for index, task in enumerate(tasks):
            if task['id'] == task_id:
                tasks.pop(index)
                return 
        abort(404, f'Task with ID {task_id} not found.')

# Registering blueprint needs to go at the bottom of the file below the routes because all routes in one file here
api.register_blueprint(todo)