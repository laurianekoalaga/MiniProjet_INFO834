// src/app/login/login.component.ts
import { Component } from '@angular/core';
import { SocketService } from '../socket.service';
import { v4 as uuidv4 } from 'uuid';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {

  username: string = '';
  clientId: string = '';
  isFormInvalid: boolean = true;
  messageConnexionFailed: string = '';

  constructor(private socketService: SocketService, private router: Router) {
    // Vérifiez si clientId existe déjà dans le localStorage
    const storedClientId = localStorage.getItem('clientId');
    this.clientId = storedClientId || uuidv4(); // Utilisez le clientId existant ou générez un nouveau
    // Stocker l'identifiant dans le stockage local
    localStorage.setItem('clientId', this.clientId);
  }

  ngOnInit(): void {
    // Vérifier si un token existe dans le localStorage
    const storedToken = localStorage.getItem('authToken');
    console.log("storedTocken from login.component.ts ngOnInit :", storedToken)
    console.log("clientId from login.component.ts ngOnInit :", localStorage.getItem('clientId'))          

    if (storedToken) {
      // Si un token existe, émettre une demande d'accès à la messagerie
      this.socketService.access_messaging_request(storedToken).subscribe(
        (data) => {
          if (data.response_code == 1) {
            this.router.navigate(['/messaging']);
          } else {
            console.log(data.response_message);  // Gérer le cas où l'accès est refusé
          }
        }
      );
    }
  }

  onSubmit(): void {
    this.socketService.connexion_request(this.username, this.clientId).subscribe(
      (data) => {
        if (data.response_code == 1) {
          // Enregistrez le token dans le localStorage
          localStorage.setItem('authToken', data.authToken);
          console.log(localStorage.getItem('authToken'))
          console.log(localStorage.getItem('clientId'))          
          
          // Envoyez la demande d'accès à la messagerie avec le token
          this.socketService.access_messaging_request(data.authToken);
  
          // Naviguez vers la page de messagerie
          this.router.navigate(['/messaging']);
        } else {
          this.messageConnexionFailed = data.response_message;
          console.log("clientId from login.component.ts onSubmit :", localStorage.getItem('authToken'))          
          console.log("clientId from login.component.ts onSubmit :", localStorage.getItem('clientId'))          
        }
     });
  }


  onUsernameChange(): void {
    this.isFormInvalid = this.username.trim() === '';
    this.messageConnexionFailed = '';
  }
}

