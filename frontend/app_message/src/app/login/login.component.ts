// src/app/login/login.component.ts
import { Component } from '@angular/core';
import { SocketService } from '../socket.service';
import { v4 as uuidv4 } from 'uuid';
import { Router } from '@angular/router';
//import * as bcrypt from 'bcryptjs';
import { sha256 } from 'js-sha256';
import { Subscription } from 'rxjs';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {

  username: string = '';
  password: string = '';
  clientId: string = '';
  isFormInvalid: boolean = true;
  messageConnexionFailed: string = '';
  private subscriptions: Subscription[] = [];


  constructor(private socketService: SocketService, private router: Router) {
    // Vérifiez si clientId existe déjà dans le localStorage
    const storedClientId = localStorage.getItem('clientId');
    this.clientId = storedClientId || uuidv4(); // Utilisez le clientId existant ou générez un nouveau
    // Stocker l'identifiant dans le stockage local
    localStorage.setItem('clientId', this.clientId);
  }

  // Méthode poour le désabonnement de tous les observables
  cleanupSubscriptions(): void {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
  }


  ngOnInit(): void {
    // Vérifier si un token d'authentification existe dans le localStorage
    const storedToken = localStorage.getItem('authToken');
    console.log("storedTocken from login.component.ts ngOnInit :", storedToken)
    console.log("clientId from login.component.ts ngOnInit :", localStorage.getItem('clientId'))          

    if (storedToken) {
      // Si un token existe accéder à la page de messagerie
      this.router.navigate(['/messaging']);
    }
  }

  ngOnDestroy(): void {
    console.log("on destroy")
    this.cleanupSubscriptions();
  }

  onSubmit(): void {
    // Hasher le mot de passe avec bcrypt avant de l'envoyer au serveur
    const hashedPassword = sha256(this.password)

    const subscription = this.socketService.connexion_request(this.username, this.clientId, hashedPassword).subscribe(
      (data) => {
        if (data.response_code == 1) {
          // Enregistrez le token dans le localStorage
          localStorage.setItem('authToken', data.authToken);

          // Naviguez vers la page de messagerie
          this.router.navigate(['/messaging']);
        } else {
          this.messageConnexionFailed = data.response_message;
        }
     });
     this.subscriptions.push(subscription);
     this.password = '';
  }

  // Méthode pour vérifier si le username dans le formulaire est conforme
  onUsernameChange(): void {
    this.isFormInvalid = this.username.trim() === '' || this.password.trim() === '';
    this.messageConnexionFailed = '';
  }

  // Méthode pour vérifier si le password dans le formulaire est conforme
  onPasswordChange(): void {
    this.isFormInvalid = this.username.trim() === '' || this.password.trim() === '';
    this.messageConnexionFailed = '';
  }

}

