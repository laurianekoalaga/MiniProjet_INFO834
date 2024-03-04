// app.module.ts 
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { FormsModule } from '@angular/forms';
import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';
import { MessagingComponent } from './messaging/messaging.component';
import { SocketService } from './socket.service';

const config: SocketIoConfig = { url: 'http://localhost:5000', options: {} };

@NgModule({ 
  declarations: [
    AppComponent,
    LoginComponent,
    MessagingComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    SocketIoModule.forRoot(config)
  ],
  providers: [SocketService],
  bootstrap: [AppComponent]
})
export class AppModule { }
