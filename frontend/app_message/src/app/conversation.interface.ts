// conversation.interface.ts
import {Message} from './message.interface'

export interface Conversation {
    _id: string;
    nom: string;
    messages: Message[];
  }