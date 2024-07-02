from flask import Flask, request, jsonify
import pymysql.cursors
from flask_cors import CORS

# Configurar a aplicação Flask
app = Flask(__name__)
CORS(app)

# Configurar a conexão com o banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'db': 'poll_system',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Função para obter a conexão com o banco de dados
def get_db_connection():
    connection = pymysql.connect(**db_config)
    return connection

# Rotas
@app.route('/')
def home():
    return 'API do Sistema de Enquetes'

@app.route('/list_polls', methods=['GET'])
def list_polls():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM polls')
            results = cursor.fetchall()
            return jsonify(results)
    finally:
        connection.close()

@app.route('/v2/user', methods=['GET'])
def get_user_v2():
    poll_id = request.args.get('id')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (poll_id,))
            poll_results = cursor.fetchone()
            if not poll_results:
                return jsonify({'error': 'Enquete não encontrada'}), 404
            
            cursor.execute('SELECT * FROM users WHERE id = %s', (poll_id,))
            option_results = cursor.fetchall()
            poll = {
                'username': poll_results['username'],
                'password': poll_results['password']
            }
            return jsonify(poll)
    finally:
        connection.close()

@app.route('/v1/user', methods=['GET'])
def get_users():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users')
            results = cursor.fetchall()
            return jsonify(results)
    finally:
        connection.close()

@app.route('/create_poll', methods=['POST'])
def create_poll():
    if request.is_json:
        data = request.get_json()
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415

    question = data.get('question')
    options = data.get('options')
    created_by = data.get('id')

    if not question or not options or not created_by:
        return jsonify({'error': 'Missing required fields'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO polls (question, created_by) VALUES (%s, %s)', (question, created_by))
            poll_id = cursor.lastrowid

            options_array = options if isinstance(options, list) else [options]
            for option in options_array:
                cursor.execute('INSERT INTO options (poll_id, option_text) VALUES (%s, %s)', (poll_id, option))

            connection.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()


@app.route('/get_poll', methods=['GET'])
def get_poll():
    poll_id = request.args.get('id')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM polls WHERE id = %s', (poll_id,))
            poll_results = cursor.fetchone()
            if not poll_results:
                return jsonify({'error': 'Enquete não encontrada'}), 404
            
            cursor.execute('SELECT * FROM options WHERE poll_id = %s', (poll_id,))
            option_results = cursor.fetchall()
            poll = {
                'question': poll_results['question'],
                'options': option_results
            }
            return jsonify(poll)
    finally:
        connection.close()

@app.route('/user', methods=['GET'])
def get_user():
    poll_id = request.args.get('id')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (poll_id,))
            user_results = cursor.fetchone()
            if not user_results:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            return jsonify(user_results)
    finally:
        connection.close()

@app.route('/vote', methods=['POST'])
def vote():
    if request.is_json:
        data = request.get_json()
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415

    poll_id = data.get('poll_id')
    option_id = data.get('option_id')
    user_id = data.get('id')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO votes (poll_id, option_id, user_id) VALUES (%s, %s, %s)', (poll_id, option_id, user_id))
            connection.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/get_results', methods=['GET'])
def get_results():
    poll_id = request.args.get('id')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM polls WHERE id = %s', (poll_id,))
            poll_results = cursor.fetchone()
            if not poll_results:
                return jsonify({'error': 'Enquete não encontrada'}), 404
            
            cursor.execute('SELECT options.option_text, COUNT(votes.id) AS votes FROM options LEFT JOIN votes ON options.id = votes.option_id WHERE options.poll_id = %s GROUP BY options.id', (poll_id,))
            result = cursor.fetchall()
            results = {
                'question': poll_results['question'],
                'results': result
            }
            return jsonify(results)
    finally:
        connection.close()

# Iniciar o servidor
if __name__ == '__main__':
    app.run(port=3000, debug=True)
