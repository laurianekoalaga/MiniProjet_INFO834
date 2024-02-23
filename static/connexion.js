document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour récupérer la valeur d'un cookie
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }

    const storedPseudo = getCookie('pseudo');
    console.log(storedPseudo)

    const socket = io.connect('http://localhost:5000');
    const connexionForm = document.getElementById('connexionForm');

    connexionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const pseudoInput = document.getElementById('pseudo');
        const pseudo = pseudoInput.value;

        // Envoyer les données de connexion au serveur via Socket.IO
        socket.emit('connexion_request', { pseudo });

        // Écouter la réponse du serveur
        socket.on('connexion_response', function(data) {
            // Rediriger vers la page de messagerie en cas de succès
            if (data.success) {
                document.cookie = `pseudo=${pseudo}`;  // Enregistre le pseudo dans un cookie
                window.location.href = '/messagerie';
            } else {
                alert('Erreur de connexion. Veuillez réessayer.');
            }
        });
    });
});

