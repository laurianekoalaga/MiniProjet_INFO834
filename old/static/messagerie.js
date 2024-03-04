const socket = io.connect('http://localhost:5000');

const storedPseudo = getCookie('pseudo');
let currentRecipient = null;

if (storedPseudo) {
    socket.emit('inform_server_of_session_data', { pseudo: storedPseudo });
}

socket.on('message', function(data) {
    var chatHistory = document.querySelector('.chat-history ul');

    var newMessage = document.createElement('li');
    newMessage.className = 'clearfix';
    newMessage.innerHTML = `
        <div class="message-data text-right">
            <span class="message-data-time">${getCurrentTime()}</span>
            <img src="/static/images/avatar_image.jpg" alt="avatar">
        </div>
        <div class="message other-message float-left">${data}</div>
    `;

    chatHistory.appendChild(newMessage);
    chatHistory.scrollTop = chatHistory.scrollHeight;
});

// Dans votre gestionnaire d'événement côté client
socket.on('message_sent_response_server', function(response) {
    if (response.success) {
        console.log('Message envoyé avec succès!');
        
        // Ajoutez le message à la conversation côté expéditeur
        var chatHistory = document.querySelector('.chat-history ul');
        var newMessage = document.createElement('li');
        newMessage.className = 'clearfix';
        newMessage.innerHTML = `
            <div class="message-data text-right">
                <span class="message-data-time">${getCurrentTime()}</span>
                <img src="/static/images/avatar_image.jpg" alt="avatar">
            </div>
            <div class="message my-message float-right">${response.sent_message}</div>
        `;

        chatHistory.appendChild(newMessage);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    } else {
        console.error('Erreur lors de l\'envoi du message.');

        var chatHistory = document.querySelector('.chat-history ul');
        var newMessage = document.createElement('li');
        newMessage.className = 'clearfix';
        newMessage.innerHTML = `
            <div class="message-data text-right">
                <span class="message-data-time">${getCurrentTime()}</span>
                <img src="/static/images/avatar_image.jpg" alt="avatar">
            </div>
            <div class="message my-message float-right">Erreur lors de l'envoi du message.</div>
        `;

        chatHistory.appendChild(newMessage);
        chatHistory.scrollTop = chatHistory.scrollHeight;    }
});


// Fonction pour envoyer des messages
function sendMessageToUser() {
    var messageInput = document.getElementById('messageInput');
    var message = messageInput.value;
    messageInput.value = '';

    // Obtenez le pseudo du destinataire (temporaire, à personnaliser selon vos besoins)
    var recipientPseudo = 'test1';

    // Envoyez le message au serveur avec le pseudo du destinataire et un callback
    socket.emit('send_message', { 'recipient': recipientPseudo, 'message': message });
}

function logout() {
    // Supprimer le cookie pseudo
    document.cookie = "pseudo=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

    window.location.href = '/logout';  // route '/logout' dans votre application Flask
}

function getCurrentTime() {
    var now = new Date();
    var hours = now.getHours();
    var minutes = now.getMinutes();
    return hours + ':' + (minutes < 10 ? '0' : '') + minutes;
}

function initializeChat(pseudo) {
    // Initialisation de la messagerie avec le pseudo de l'utilisateur
    console.log('Utilisateur connecté:', pseudo);
}

// Fonction pour récupérer la valeur d'un cookie
function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}