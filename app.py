import os
import pymysql
from http import HTTPStatus
from flask_cors import CORS
from flask import Flask, redirect, request, jsonify, url_for, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from db import Database
from config import DevelopmentConfig as devconf


host = os.environ.get('FLASK_SERVER_HOST', devconf.HOST)
port = os.environ.get('FLASK_SERVER_PORT', devconf.PORT)
version = str(devconf.VERSION).lower()
url_prefix = str(devconf.URL_PREFIX).lower()
route_prefix = f"/{url_prefix}/{version}"


def create_app():
    """ Создание экземпляра приложения Flask

    :return: (object) Объект класса Flask
    """
    app = Flask(__name__)
    cors = CORS(app, resources={f"{route_prefix}/*": {"origins": "*"}})
    app.config.from_object(devconf)
    return app


def get_response_msg(data, status_code):
    """ Создание JSON ответов сервера

    :param data: (list of tuples) Данные полученные SQL запросом
    :param status_code: (int) HTTP Статус
    :return: (object) Объект класса Response
    """
    message = {
        'status': status_code,
        'data': data if data else 'No records found'
    }
    response_msg = jsonify(message)
    response_msg.status_code = status_code
    return response_msg


app = create_app()
wsgi_app = app.wsgi_app
db = Database(devconf)
auth = HTTPBasicAuth()
app.config['SECRET_KEY'] = 'secret key here'

users = {
    "admin": generate_password_hash("admin")
}


def sql_query(query):
    """ Выполнение SQL запроса на выборку записей

    :param query: (str) SQL запрос
    :return: (object) Объект класса Response
    """
    try:
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


def update(query):
    """ Выполнение SQL запроса на изменение записей

    :param query: (str) SQL запрос
    :return: (object) Объект класса Response
    """
    try:
        db.run_query(query=query)
        response = get_response_msg('Updated successfully', HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


## ==============================================[ Routes - Start ]
@auth.verify_password
def verify_password(username, password):
    """ Верификация пользователя API сервера

    :param username: (str) Логин пользователя
    :param password: (str) Пароль пользователя
    :return: (str) Логин пользователя
    """
    if username in users and check_password_hash(users.get(username), password):
        return username


## GET
## /api/v1/get_user?email=NULL
@app.route(f"{route_prefix}/get_user", methods=['GET'])
@auth.login_required
def get_user():
    """ GET API запрос на получение данных пользователя по email
    \nПример: /api/v1/get_user?email=example@mail.com

    :return: (object) Объект класса Response
    """
    email = request.args.get('email', default='NULL', type=str)
    query = f"select * from Users where email ='{email}'"
    return sql_query(query)


## /api/v1/get_user_bio?user_id=NULL
@app.route(f"{route_prefix}/get_user_bio", methods=['GET'])
@auth.login_required
def get_user_bio():
    """ GET API запрос на получение данных пользователя по id
    \nПример: /api/v1/get_user_bio?user_id=1

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    query = f"select * from Users where user_id ='{userid}'"
    return sql_query(query)


## /api/v1/get_settings?user_id=NULL
@app.route(f"{route_prefix}/get_settings", methods=['GET'])
@auth.login_required
def get_user_settings():
    """ GET API запрос на получение выбранных параметров пользователем по его id
    \nПример: /api/v1/get_settings?user_id=2

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    query = f"select * from Settings where user_id ='{userid}'"
    return sql_query(query)


## /api/v1/get_sessions?user_id=NULL
@app.route(f"{route_prefix}/get_sessions", methods=['GET'])
@auth.login_required
def get_user_sessions():
    """ GET API запрос на получение информации о сессиях пользователя по его id
    \nПример: /api/v1/get_sessions?user_id=1

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    query = f"select * from Sessions where user_id ='{userid}'"
    return sql_query(query)


## /api/v1/get_last_session?user_id=NULL
@app.route(f"{route_prefix}/get_last_session", methods=['GET'])
@auth.login_required
def get_user_last_session():
    """ GET API запрос на получение информации о последней сессии пользователя по его id
    \nПример: /api/v1/get_last_session?user_id=1

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    query = f"select * from Sessions where user_id ='{userid}'order by last_log desc limit 1"
    return sql_query(query)


## /api/v1/get_tasks?user_id=NULL
@app.route(f"{route_prefix}/get_tasks", methods=['GET'])
@auth.login_required
def get_user_tasks():
    """ GET API запрос на получение информации о имеющихся задачах пользователя по его id
    \nПример: /api/v1/get_tasks?user_id=1

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    query = f"select * from Tasks where user_id ='{userid}'"
    return sql_query(query)


## /api/v1/get_categories?user_id=NULL
@app.route(f"{route_prefix}/get_categories", methods=['GET'])
@auth.login_required
def get_user_categories():
    """ GET API запрос на получение информации о существующих категориях пользователя по его id
    \nПример: /api/v1/get_categories?user_id=1

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    query = f"select * from Categories where user_id ='{userid}'"
    return sql_query(query)


## /api/v1/get_tags
@app.route(f"{route_prefix}/get_tags", methods=['GET'])
@auth.login_required
def get_tags():
    """ GET API запрос на получение имеющихся тегов
    \nПример: /api/v1/get_tags

    :return: (object) Объект класса Response
    """
    query = f"select * from Tags"
    return sql_query(query)


## POST
## /api/v1/add_user
@app.route(f"{route_prefix}/add_user", methods=['POST'])
@auth.login_required
def insert_user():
    """ POST API запрос на добавление пользователя
    \nПример: /api/v1/add_user

    :return: (object) Объект класса Response
    """
    data = request.json
    email = data['email']
    passw = data['password']
    created_at = data['created_at']
    total_session = data['total_session']
    total_tasks = data['total_tasks']
    total_categories = data['total_categories']
    query = f"insert into Users values (NULL, '{email}', '{passw}', '{created_at}', " \
            f"{total_session}, {total_tasks}, {total_categories})"
    return update(query)


## /api/v1/add_task?user_id=NULL
@app.route(f"{route_prefix}/add_task", methods=['POST'])
@auth.login_required
def add_task():
    """ POST API запрос на добавление новой задачи пользователю по его id
    \nПример: /api/v1/add_task?user_id=1

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    task_name = data['task_name']
    created_at = data['created_at']
    task_desc = data['task_desc']
    completed_at = data['completed_at']
    tag_id = data['tag_id']
    today_tag = data['today_tag']
    repeat_f = data['repeat_f']
    repeat_interval = data['repeat_interval']
    category_id = data['category_id']
    query = f"insert into Tasks values (NULL, {userid}, '{task_name}', '{created_at}', " \
            f"'{task_desc}', '{completed_at}', {tag_id}, {today_tag}, {repeat_f}, {repeat_interval}, {category_id})"
    return update(query)


## /api/v1/add_category?user_id=NULL
@app.route(f"{route_prefix}/add_category", methods=['POST'])
@auth.login_required
def add_category():
    """ POST API запрос на добавление новой категории пользователю по его id
    \nПример: /api/v1/add_category?user_id=1

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    category = data['category']
    created_at = data['created_at']
    total_tasks = data['total_tasks']
    colour = data['colour']
    path_to_cover = data['path_to_cover']
    emoji = data['emoji']
    query = f"insert into Categories values (NULL, {userid}, '{category}', '{created_at}', " \
            f"{total_tasks}, '{colour}', '{path_to_cover}', '{emoji}')"
    return update(query)


## /api/v1/set_settings?user_id=NULL
@app.route(f"{route_prefix}/set_settings", methods=['POST'])
@auth.login_required
def set_settings():
    """ POST API запрос на сохранение настроек пользователя по его id
    \nПример: /api/v1/set_settings?user_id=1

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    first_day_week = data['first_day_week']
    lang = data['lang']
    theme = data['theme']
    sort_by = data['sort_by']
    query = f"insert into Settings values (NULL, {userid}, '{first_day_week}', '{lang}', " \
            f"'{theme}', '{sort_by}')"
    return update(query)


## /api/v1/add_session?user_id=NULL
@app.route(f"{route_prefix}/add_session", methods=['POST'])
@auth.login_required
def add_session():
    """ POST API запрос на сохранение новой сессии пользователя по его id
    \nПример: /api/v1/add_session?user_id=1

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    device = data['device']
    last_log = data['last_log']
    ip_address = data['ip_address']
    query = f"insert into Sessions values (NULL, {userid}, '{device}', '{last_log}', " \
            f"'{ip_address}')"
    return update(query)


## PUT
## /api/v1/update_user?user_id=NULL
@app.route(f"{route_prefix}/update_user", methods=['PUT'])
@auth.login_required
def update_user():
    """ PUT API запрос на обновление данных пользователя по его id
    \nПример: /api/v1/update_user?user_id=1

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    email = data['email']
    passw = data['password']
    created_at = data['created_at']
    total_session = data['total_session']
    total_tasks = data['total_tasks']
    total_categories = data['total_categories']
    query = f"update Users set email = '{email}', passw = '{passw}', created_at = '{created_at}', " \
            f"total_session = {total_session}, total_tasks = {total_tasks}, total_categories = {total_categories}" \
            f"where user_id = {userid}"
    return update(query)


## /api/v1/update_task?user_id=NULL&task_id=NULL
@app.route(f"{route_prefix}/update_task", methods=['PUT'])
@auth.login_required
def update_task():
    """ PUT API запрос на обновление задачи по id задачи, и по id пользователя
    \nПример: /api/v1/update_task?user_id=1&task_id=5

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    taskid = request.args.get('task_id', default='NULL', type=int)
    task_name = data['task_name']
    created_at = data['created_at']
    task_desc = data['task_desc']
    completed_at = data['completed_at']
    tag_id = data['tag_id']
    today_tag = data['today_tag']
    repeat_f = data['repeat_f']
    repeat_interval = data['repeat_interval']
    category_id = data['category_id']
    query = f"update Tasks set task_name = '{task_name}', created_at = '{created_at}', " \
            f"task_desc = '{task_desc}', completed_at = '{completed_at}', tag_id = {tag_id}, today_tag = {today_tag}," \
            f"repeat_f = {repeat_f}, repeat_interval = {repeat_interval}, category_id = {category_id}" \
            f"where user_id = {userid} and task_id = {taskid}"
    return update(query)


## /api/v1/update_category?user_id=NULL&category_id=NULL
@app.route(f"{route_prefix}/update_category", methods=['PUT'])
@auth.login_required
def update_category():
    """ PUT API запрос на обновление категории по id категории, и по id пользователя
    \nПример: /api/v1/update_category?user_id=2&category_id=4

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    categoryid = request.args.get('category_id', default='NULL', type=int)
    category = data['category']
    created_at = data['created_at']
    total_tasks = data['total_tasks']
    colour = data['colour']
    path_to_cover = data['path_to_cover']
    emoji = data['emoji']
    query = f"update Categories set category = '{category}', created_at = '{created_at}', " \
            f"total_tasks = {total_tasks}, colour = '{colour}', path_to_cover = '{path_to_cover}', emoji = '{emoji}'" \
            f"where user_id = {userid} and category_id = {categoryid}"
    return update(query)


## /api/v1/update_settings?user_id=NULL
@app.route(f"{route_prefix}/update_settings", methods=['PUT'])
@auth.login_required
def update_settings():
    """ PUT API запрос на обновление параметров пользователя по его id
    \nПример: /api/v1/update_settings?user_id=1

    :return: (object) Объект класса Response
    """
    data = request.json
    userid = request.args.get('user_id', default='NULL', type=int)
    first_day_week = data['first_day_week']
    lang = data['lang']
    theme = data['theme']
    sort_by = data['sort_by']
    query = f"update Settings set first_day_week = '{first_day_week}', lang = '{lang}', " \
            f"theme = '{theme}', sort_by = '{sort_by}' where user_id = {userid}"
    return update(query)


## DELETE
## /api/v1/delete_task?user_id=NULL&task_id=NULL
@app.route(f"{route_prefix}/delete_task", methods=['DELETE'])
@auth.login_required
def delete_task():
    """ DELETE API запрос на удаление задачи по id задачи, и по id пользователя
    \nПример: /api/v1/delete_task?user_id=1&task_id=3

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    taskid = request.args.get('task_id', default='NULL', type=int)
    query = f"delete from Tasks where user_id = {userid} and task_id ={taskid}"
    return update(query)


## /api/v1/delete_category?user_id=NULL&category_id=NULL
@app.route(f"{route_prefix}/delete_category", methods=['DELETE'])
@auth.login_required
def delete_category():
    """ DELETE API запрос на удаление категории по id категории, и по id пользователя
    \nПример: /api/v1/delete_category?user_id=2&category_id=1

    :return: (object) Объект класса Response
    """
    userid = request.args.get('user_id', default='NULL', type=int)
    categoryid = request.args.get('category_id', default='NULL', type=int)
    query = f"delete from Categories where user_id = {userid} and category_id = {categoryid}"
    return update(query)


## /api/v1/health
@app.route(f"{route_prefix}/health", methods=['GET'])
@auth.login_required
def health():
    """ GET API запрос на получение статуса базы данных
    \nПример: /api/v1/health

    :return: (object) Объект класса Response
    """
    try:
        db_status = "Connected to DB" if db.db_connection_status else "Not connected to DB"
        response = get_response_msg("Online " + db_status, HTTPStatus.OK)
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


## /
@app.route('/', methods=['GET'])
@auth.login_required
def home():
    """ GET API запрос перенаправляющий на /api/v1/health

    :return: (object) Объект класса Response
    """
    return redirect(url_for('health'))

## =================================================[ Routes - End ]

## ================================[ Error Handler Defined - Start ]
## Unauthorized
@auth.error_handler
def unauthorized():
    """ Обработка ошибки: Не пройдена верификация

    :return: (object) Объект класса Response
    """
    return get_response_msg(data='Unauthorized access', status_code=HTTPStatus.UNAUTHORIZED)


## HTTP 404 error handler
@app.errorhandler(HTTPStatus.NOT_FOUND)
@auth.login_required
def page_not_found(e):
    """ Обработка ошибки: Страницы не существует

    :return: (object) Объект класса Response
    """
    return get_response_msg(data=str(e), status_code=HTTPStatus.NOT_FOUND)


## HTTP 400 error handler
@app.errorhandler(HTTPStatus.BAD_REQUEST)
@auth.login_required
def bad_request(e):
    """ Обработка ошибки: Плохой запрос

    :return: (object) Объект класса Response
    """
    return get_response_msg(str(e), HTTPStatus.BAD_REQUEST)


## HTTP 500 error handler
@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
@auth.login_required
def internal_server_error(e):
    """ Обработка ошибки: Внутренняя ошибка сервера

    :return: (object) Объект класса Response
    """
    return get_response_msg(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
## ==================================[ Error Handler Defined - End ]


if __name__ == '__main__':
    ## Launch the application
    app.run(host=host, port=port)
