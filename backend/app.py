# app.py (côté serveur Flask)
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import jwt 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
SECRET_KEY = 'mysecretkey'

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
    username = data['username']
    clientId = data['clientId']

    # Vérifier si l'identifiant unique est déjà connecté
    if clientId not in connected_clients.keys():
        if username == 'andrei':
            print(f'{username} just connected with client id: ({clientId}).')

            authToken = generate_authToken(username, clientId)
            connected_clients[clientId] = {'username':username, 'authToken': authToken}

            response = {
                'response_code': 1,
                'response_message': f'Connexion accepted for username {username}.',
                'authToken': authToken
            }

        else:
            response = {
                'response_code': 300,
                'response_message': 'Server refused connexion: invalid logins.'
            }
    else:
        response = {
            'response_code': 301,
            'response_message': 'Server refused connexion: clientID already used.'
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
        print(f"Compte déconnecté pour username {username}. Client ID {clientId} free to use.")

        response = {
            'response_code': 1,
            'response_message': 'Deconnexion réussie côté serveur.'
        }

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

        # charger les données du username en question

        # Chargez les données associées au clientId, par exemple depuis une base de données
        # Puis, émettez une réponse appropriée vers le client

        response = {
            'response_code': 1,
            'response_message': f'Authentification authToken accepted, access to messaging ok for user {username} (client ID : {clientId})'
            #'response_user_data': les données à envoyer pour la messagerie de l'utilisateur
        }

    else:
        # Le authToken est invalide ou expiré, émettez une réponse d'erreur vers le client
        response = {
            'response_code': 500,
            'response_message': f'Authentification authToken rejected, access to messaging not accepted for user {username} (client ID : {clientId})'
        }
        print("authToken not accepted in access_messaging_request call")


    emit('response_to_access_messaging_request', response)

@socketio.on('join_conversation')
def handle_join_conversation(data):
    conversation_id = data.get('conversation_id')
    room = f'conversation_{conversation_id}'
    join_room(room)


@socketio.on('send_message')
def handle_send_message(data):
    conversation_id = data.get('conversation_id')
    message_content = data.get('content')
    room = f'conversation_{conversation_id}'
    emit('receive_message', {'content': message_content}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
