# shortcut to run server in dev mode rather than FLASK_APP=app:server flask run --reload
# ./run.sh in terminal
# Find server variable in file app (server = Flask())
export FLASK_APP=app:server
export FLASK_ENV=development
flask run --reload