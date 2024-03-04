// socket.service.ts
import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Observable } from 'rxjs';
import { Message } from './message.interface';

@Injectable({
  providedIn: 'root'
})

export class SocketService {

  constructor(private socket: Socket) { }

  connexion_request(username: string, clientId: string): Observable<any> {
    return new Observable<any>(observer => {
      this.socket.emit('connexion_request', { username, clientId });
      this.socket.on('response_to_connexion_request', (data: any) => {
        observer.next(data);
      });
      this.socket.on('message', (data: any) => {
        observer.next(data);
      });
    });
  }

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

  joinConversation(conversationId: string): void {
    this.socket.emit('join_conversation', { conversation_id: conversationId });
  }

  sendMessage(conversationId: string, message: Message): void {
    const data = {
      conversation_id: conversationId,
      message: message
    };
    this.socket.emit('send_message', data);
  }

  
  receiveMessage(): Observable<{ conversation_id: string, message: Message }> {
    return new Observable<{ conversation_id: string, message: Message }>(observer => {
      this.socket.on('new_message_to_receive', (data: { conversation_id: string, message: Message }) => {
        observer.next(data);
      });
    });
  }
}
