# app.py (côté serveur Flask)
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import jwt 
from apiMongoDB import MongoDBManager
from apiRedis import RedisManager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
SECRET_KEY = 'sk2'
mongodb_manager = MongoDBManager("mongodb://localhost:27017/")
mongodb_manager.connect("ProjInfo834")
redis_manager = RedisManager()
connected_clients = {}

def generate_authToken(username, clientId):
    payload = {
        'username': username,
        'clientId': clientId
    }
    authToken = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return authToken


def validate_authToken(authToken):
    try:
        payload = jwt.decode(authToken, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Le authToken a expiré
    except jwt.InvalidTokenError:
        return None  # Le authToken est invalide


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected with request_sid : {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected with request_sid : {request.sid}")

@socketio.on('connexion_request')
def handle_connexion_request(data):
    username = data.get('username')
    clientId = data.get('clientId')     
    hashedPassword = data.get('hashedPassword')

    # Vérifier si l'identifiant unique est déjà connecté
    try:
        if clientId not in connected_clients.keys():
            response_from_db = mongodb_manager.verify_user_credentials(username, hashedPassword)
            print(response_from_db)
            if response_from_db.get('response_code') == 1:
                print(f'{username} just connected with client id: ({clientId}).')
                authToken = generate_authToken(username, clientId)
                connected_clients[clientId] = {'username':username, 'authToken': authToken}
                response = {
                    'response_code': 1,
                    'response_message': f'Connexion accepted for username {username}.',
                    'authToken': authToken
                }
                redis_manager.add_connexion(username, clientId)

            else:
                response = {
                    'response_code': 1000,
                    'response_message': response_from_db.get('response_message')
                }
        else:
            response = {
                'response_code': 301,
                'response_message': 'Server refused connexion: clientID already used.'
            }
    except Exception as e:
        response = {
            'response_code': 1000,
            'response_message': e
            }
        
    emit('response_to_connexion_request', response)


@socketio.on('deconnexion_request')
def handle_deconnexion_request(data):
    authToken = data.get('authToken')
    
    payload = validate_authToken(authToken)
    if payload != None:
        clientId = payload.get('clientId')
        username = payload.get('username')

        del connected_clients[clientId]
        print(f"Account {username} deconnected. Client ID {clientId} free.")

        response = {
            'response_code': 1,
            'response_message': 'Deconnexion réussie côté serveur.'
        }
        redis_manager.add_deconnexion(username, clientId)


    else :
        response = {
            'response_code': 100,
            'response_message': 'Compromised authToken at deconnexion tentative.'
        }
    # Envoyer une confirmation de déconnexion au client
    emit('response_to_deconnexion_request', response)

@socketio.on('access_messaging_request')
def handle_access_messaging_request(authToken):
    payload = validate_authToken(authToken)
    print("access_messaging_request called")
    if payload != None:
        # Le authToken est valide, vous pouvez accéder aux informations du payload
        username = payload.get('username')
        clientId = payload.get('clientId')
        print("authToken accepted in access_messaging_request call")

        response_from_db = mongodb_manager.get_user_conversations_without_msg(username)
        if response_from_db.get('response_code') == 1:
            response = {
                'response_code': 1,
                'response_message': f'Authentification authToken accepted, access to messaging ok for user {username} (client ID : {clientId})',
                'response_data': response_from_db.get('response_data')
            }
        else:
            response = {
                'response_code': 1000,
                'response_message': response_from_db.get('response_message'),
                'response_data': response_from_db.get('response_data')
            }
    else:
        # Le authToken est invalide ou expiré, émettez une réponse d'erreur vers le client
        response = {
            'response_code': 501,
            'response_message': f'Authentification authToken rejected, access to messaging not accepted for user {username} (client ID : {clientId})'
        }
        print("authToken not accepted in access_messaging_request call")


    emit('response_to_access_messaging_request', response)

@socketio.on('join_conversation')
def handle_join_conversation(data):
    conversation_id = data.get('conversation_id')
    print(f"handle_join_conversation called for conversation id {conversation_id}")
    join_room(conversation_id)
   

@socketio.on('get_messages')
def handle_get_messages(data):
    try :
        conversation_id = data.get('conversation_id')
        print(f"handle_get_messages called for conversation id {conversation_id}")
        response_from_db = mongodb_manager.get_messages_for_conversation(conversation_id)
        if response_from_db.get('response_code') == 1:
            response = {
                'response_code': 1,
                'response_message': "Success",
                'response_data': response_from_db.get('response_data')
            }
        else:
            response = {
                'response_code': 1000,
                'response_message': response_from_db.get('response_message'),
                'response_data': response_from_db.get('response_data')
            }
    except Exception as e:
        response = {
            'response_code': 1000,
            'response_message': e
        }
    emit('messages_for_conversation', response)

@socketio.on('send_message')
def handle_send_message(data):
    conversation_id = data.get('conversation_id')
    message = data.get('message')

    print(f"send_message called for conversation id : {conversation_id}, message data : {message}\n")
    mongodb_manager.add_message(conversation_id=conversation_id, message=message)
    emit('new_message_to_receive', data, room=conversation_id)


if __name__ == '__main__':
    socketio.run(app, debug=True)
