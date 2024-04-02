// messaging.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { SocketService } from '../socket.service';
import { jwtDecode } from 'jwt-decode';
import { Message } from '../message.interface';
import { Conversation } from '../conversation.interface';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-messaging',
  templateUrl: './messaging.component.html',
  styleUrls: ['./messaging.component.css']
})
export class MessagingComponent implements OnInit, OnDestroy {

  private subscriptions: Subscription[] = [];

  username: string = '';

  conversations: Conversation[] = [];

  selectedConversation: Conversation | null = null
  selectedConversationId: string | null = null;
  selectedConversationName: string | null = null;
  //selectedConversationLastSeen: number | null = null;
  messages: Message[] = [];

  newMessage: string = '';


  constructor(private router: Router, private socketService: SocketService) {}

  ngOnInit(): void {

    // Récupérer le token d'authentification
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
      // Rediriger vers la page de connexion si le token n'est pas présent
      this.router.navigate(['/login']);

    } else {
      // Si token présent, demander l'accès à la messagerie
      const subscription = this.socketService.access_messaging_request(authToken).subscribe(

        (data) => {
          console.log('aaa')
          if (data.response_code != 1) {
            // Rediriger vers la page de connexion si l'accès est refusé (token compromis)
            this.router.navigate(['/login']);

          } else {
            // Sinon accès à la messagerie
            const decodedToken: any = jwtDecode(authToken);
            this.username = decodedToken.username;
            this.conversations = data.response_data
            
            // Sélection par défaut de la première conversation dans la liste
            if (this.conversations.length > 0) {
              this.onSelectConversation(this.conversations[0]);
            }

            // Souscrire à la réception de nouveaux messages
            this.subscriptions.push(
              this.socketService.receiveMessage().subscribe(data => {
                this.handleNewMessage(data);
              })
            );
          }
        },
        (error) => {
          // Si autres erreurs rediriger vers la page de connexion
          this.router.navigate(['/login']);
        }
      );
      this.subscriptions.push(subscription);
    }
  }

  // Méthode poour le désabonnement de tous les observables
  cleanupSubscriptions(): void {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
    //this.subscriptions = [];
  }

  ngOnDestroy(): void {
    this.cleanupSubscriptions();
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
      this.cleanupSubscriptions();
    
      // Rediriger vers la page de connexion
      this.router.navigate(['/login']);
    }
  }

  // Méthode appelée lors du clic sur une conversation
  onSelectConversation(conversation: Conversation): void {
    this.selectedConversation = conversation;
    this.selectedConversationId = conversation._id;
    this.selectedConversationName = conversation.nom;

    // Rejoindre la room socketio associée à la conversation
    this.socketService.joinConversation(conversation._id);

    // Récupération des messages de cette conversation
    this.socketService.getMessages(conversation._id, (messages: Message[]) => {
      this.messages = messages;
      // Descendre aux derniers messages
      this.scrollToBottomOfChatHistory();
    });  
  }

  // Méthode appelée lors de l'envoi d'un message
  sendMessage(): void {
    if (this.selectedConversationId && this.newMessage.trim() !== '') {
      // Création d'un nouvel objet message
      const newMessage: Message = {
        _id: this.messages.length + 1,
        emetteur: this.username,
        contenu: this.newMessage,
        timestamp: new Date()
      };

      console.log('sendMessage in messaging.ts called');

      // Envoi du message
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
      // Faire défiler vers le bas pour afficher le dernier message ajouté
      this.scrollToBottomOfChatHistory();
    }
  }

  // Méthode pour déterminer la classe CSS en fonction de l'émetteur du message
  getMessageClass(message: Message): { messageClass: string, divClass: string } {
    let messageClass = message.emetteur == this.username ? 'my-message float-right' : 'other-message float-left';
    let divClass = message.emetteur == this.username ? 'message-data text-right' : 'message-data text-left';
    return { messageClass, divClass };
  }

  // Méthode pour se placer au niveau des derniers messages dans la conversation
  scrollToBottomOfChatHistory(): void {
    const chatHistory = document.querySelector('.chat-history');
    if (chatHistory) {
        requestAnimationFrame(() => {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        });
    } else {
        console.error('La classe .chat-history n\'a pas été trouvée dans le document.');
    }
}
}
