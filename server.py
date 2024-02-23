from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, send


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Route pour la page de connexion
@app.route('/connexion')
def connexion():
    if 'pseudo' in request.cookies:
        return redirect(url_for('messagerie'))
    
    return render_template('connexion.html')

 
# Route pour la page principale de messagerie
@app.route('/messagerie')
def messagerie():
    if 'pseudo' not in request.cookies:
        return redirect(url_for('connexion'))
    
    return render_template('messagerie.html')


# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('connexion'))  # Redirigez l'utilisateur vers la page de connexion après déconnexion


# Gérer la demande de connexion
@socketio.on('connexion_request')
def handle_connexion_request(data):
    try:
        pseudo = data.get('pseudo', '')

        if pseudo == 'test' or pseudo == 'test1':
            response = {'success': True, 'error': 'Pseudo non valide'}
        else:
            response = {'success': False, 'error': 'Pseudo non valide'}

        # Envoye une réponse au client
        emit('connexion_response', response)

    except Exception as e:
        print('Erreur lors de la connexion:', str(e))
        response = {'success': False, 'error': 'Erreur lors de la connexion'}
        emit('connexion_response', response)


# Recevoir le pseudo de la session socket de messagerie :
@socketio.on('inform_server_of_session_data')
def set_session(data):
    try:
        pseudo = data.get('pseudo')
        session['pseudo'] = pseudo
        join_room(pseudo)  # Rejoindre la salle avec le pseudo comme nom

        print(f'inform_server_session_data called: {session}')

    except Exception as e:
        print('Erreur lors du passage des infos de la session:', str(e))




# Gérer un message envoyé
@socketio.on('send_message')
def handle_send_message(data):
    recipient_pseudo = data.get('recipient', 'default_recipient')
    message = data.get('message', '')
    sender_pseudo = session.get('pseudo')
    print(f"Message de {sender_pseudo} à {recipient_pseudo}: {message}")
        
    # Utilisez 'room' pour envoyer à un utilisateur spécifique
    room = recipient_pseudo
    send(f"De {sender_pseudo}: {message}", room=room)

    response = {'success': True, 'sent_message': message}  # Ajoutez plus d'informations si nécessaire
    
    # Envoyez une réponse au client
    emit('message_sent_response_server', response)

if __name__ == '__main__':
    socketio.run(app, debug=True)
