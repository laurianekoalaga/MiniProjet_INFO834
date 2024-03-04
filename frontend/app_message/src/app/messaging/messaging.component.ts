// messaging.component.ts
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { SocketService } from '../socket.service';
import { jwtDecode } from 'jwt-decode';
import { Message } from '../message.interface';
import { Conversation } from '../conversation.interface';

@Component({
  selector: 'app-messaging',
  templateUrl: './messaging.component.html',
  styleUrls: ['./messaging.component.css']
})
export class MessagingComponent implements OnInit {

  username: string = '';

  conversations: Conversation[] = [
    {
      _id: '14564',
      nom: 'Rosine',
      messages: []
    }
  ];

  selectedConversationId: string | null = null;
  selectedConversationName: string | null = null;
  selectedConversationLastSeen: number | null = null;

  messages: Message[] = [
    {
      _id: 1,
      emetteur: 'utilisateur1',
      contenu: 'Bonjour, comment ça va ?',
      timestamp: new Date('2024-02-22T12:00:00Z')
    },
    {
      _id: 2,
      emetteur: 'utilisateur2',
      contenu: 'Salut ! Ça va bien, et toi ?',
      timestamp: new Date('2024-02-22T12:05:00Z')
    },
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
          } else {
            const decodedToken: any = jwtDecode(authToken);
            this.username = decodedToken.username;

            // Initialisation des valeurs par défaut ou chargement des données depuis le serveur
            if (this.conversations.length > 0) {
              this.onSelectConversation(this.conversations[0]._id);
            }

            // Souscrire à la réception de nouveaux messages
            this.socketService.receiveMessage().subscribe(data => {
              this.handleNewMessage(data);
            });
          }
        },
        (error) => {
          // Gérer les erreurs, par exemple rediriger vers la page de connexion
          this.router.navigate(['/login']);
        }
      );
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
      const newMessage: Message = {
        _id: this.messages.length + 1,
        emetteur: this.username,
        contenu: this.newMessage,
        timestamp: new Date()
      };
  
      this.socketService.sendMessage(this.selectedConversationId, newMessage)
      this.newMessage = '';

    }
  }
  

  // Méthode pour traiter les nouveaux messages
  handleNewMessage(data: { conversation_id: string, message: any }): void {
    const { conversation_id, message } = data;
    // Vérifier si la conversation du message correspond à celle actuellement sélectionnée
    if (this.selectedConversationId === conversation_id) {
      // Ajouter le message à la liste des messages
      this.messages.push(message);
    }
  }

  // Méthode pour déterminer la classe CSS en fonction de l'émetteur du message
  getMessageClass(message: Message): { messageClass: string, divClass: string } {
    let messageClass = message.emetteur == this.username ? 'my-message float-right' : 'other-message float-left';
    let divClass = message.emetteur == this.username ? 'message-data text-right' : 'message-data text-left';
    return { messageClass, divClass };
  }

}
