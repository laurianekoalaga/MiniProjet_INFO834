// socket.service.ts
import { Injectable, EventEmitter } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Observable } from 'rxjs';
import { Message } from './message.interface';

@Injectable({
  providedIn: 'root'
})

export class SocketService {

  newMessageReceived: EventEmitter<any> = new EventEmitter<any>();

  constructor(private socket: Socket) { }

  // Émettre une demande de connexion au serveur
  connexion_request(username: string, clientId: string, hashedPassword: string): Observable<any> {
    return new Observable<any>(observer => {
      this.socket.emit('connexion_request', { username, clientId, hashedPassword });
      this.socket.on('response_to_connexion_request', (data: any) => {
        observer.next(data);
      });
      this.socket.on('message', (data: any) => {
        observer.next(data);
      }); 
    });
  }

  // Émettre une demande d'accès à la page de messagerie au serveur
  access_messaging_request(authToken: string): Observable<any> {
    return new Observable<any>(observer => {
      this.socket.emit('access_messaging_request', authToken);
      this.socket.on('response_to_access_messaging_request', (data: any) => {
        observer.next(data);
      });
    });
  }

  // Émettre une demande de déconnexion au serveur
  deconnexion_request(authToken: string): void {
    this.socket.emit('deconnexion_request', { authToken });
  }

  // Rejoindre une room socketio (i.e. une conversation)
  joinConversation(conversationId: string): void {
    this.socket.emit('join_conversation', { conversation_id: conversationId });
  }

  // Demande des messages d'une conversation donnée au serveur
  getMessages(conversationId: string, callback: (messages: Message[]) => void): void {
    this.socket.emit('get_messages', { conversation_id: conversationId });
    this.socket.on('messages_for_conversation', (data: any) => {
      callback(data.response_data);
    });
  }

  // Envoi d'un nouveau message au serveur
  sendMessage(conversationId: string, message: Message): void {
    const data = {
      conversation_id: conversationId,
      message: message
    };
    this.socket.emit('send_message', data);
    console.log('senfMessage in socket.ts called')
  }
  
  // Traitement lors de la réception d'un nouveau message venant du serveur
  receiveMessage(): Observable<{ conversation_id: string, message: Message }> {
    return new Observable<{ conversation_id: string, message: Message }>(observer => {
      this.socket.on('new_message_to_receive', (data: { conversation_id: string, message: Message }) => {
        console.log(data)
        observer.next(data);
      });
    });
  }
}
