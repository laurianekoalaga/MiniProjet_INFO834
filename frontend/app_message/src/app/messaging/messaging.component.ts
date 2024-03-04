// messaging.component.ts
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { SocketService } from '../socket.service';

@Component({
  selector: 'app-messaging',
  templateUrl: './messaging.component.html',
  styleUrls: ['./messaging.component.css']
})
export class MessagingComponent implements OnInit {

  conversations = [
    { id: 'conversation_1', name: 'Vincent Porter', avatar: './assets/images/avatar_image.jpg', lastSeen: 7 },
    { id: 'conversation_2', name: 'Rosine Soro', avatar: './assets/images/avatar_image.jpg', lastSeen: 2 },
  ];

  selectedConversationId: string | null = null;
  selectedConversationName: string | null = null;
  selectedConversationLastSeen: number | null = null;

  messages = [
    { content: 'Votre message ici', timestamp: new Date(), isMine: true },
    { content: 'Message reçu ici', timestamp: new Date(), isMine: false },
    // Ajoutez d'autres messages fictifs au besoin
  ];

  newMessage: string = '';
  constructor(private router: Router, private socketService: SocketService) {}

  ngOnInit(): void {
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
      // Rediriger vers la page de connexion si le token n'est pas présent
      this.router.navigate(['/login']);
      return;
    } else {

      // Vérifier l'accès à la messagerie via le service socket
      this.socketService.access_messaging_request(authToken).subscribe(
        (data) => {
          if (data.response_code !== 1) {
            // Rediriger vers la page de connexion si l'accès est refusé
            this.router.navigate(['/login']);
          }
        },
        (error) => {
          // Gérer les erreurs, par exemple rediriger vers la page de connexion
          this.router.navigate(['/login']);
        }
      );
    }

    // Initialisation des valeurs par défaut ou chargement des données depuis le serveur
    if (this.conversations.length > 0) {
      this.selectedConversationId + this.conversations[0].id;
    }

  }

  // Méthode appelée lors du clic sur le bouton de déconnexion
  deconnexionRequest(): void {
    // Récupérer le token d'authentification du stockage local
    const authToken = localStorage.getItem('authToken');

    if (authToken) {
      // Émettre une demande de déconnexion au serveur avec l'authToken
      this.socketService.deconnexion_request(authToken);

      // Supprimer le token d'authentification du stockage local
      localStorage.removeItem('authToken');

      // Rediriger vers la page de connexion
      this.router.navigate(['/login']);
    }
  }


  onSelectConversation(conversationId: string): void {
    this.selectedConversationId = conversationId;
    this.socketService.joinConversation(conversationId);

  }

  sendMessage(): void {
    if (this.selectedConversationId && this.newMessage.trim() !== '') {
      const newMessage = {
        content: this.newMessage,
        timestamp: new Date(),
        isMine: true // Assumez que l'utilisateur actuel envoie le message
      };

      this.messages.push(newMessage);
      // Envoyez le message au serveur ou effectuez toute autre logique nécessaire
      // Réinitialisez le champ de saisie après l'envoi du message
      this.newMessage = '';
    }
  }

}
