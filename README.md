# MiniProjet_INFO834
  
Pour lancer et tester la messagerie, suivre ces étapes après avoir fait un git clone :  
  
#### MongoDB :  
1. Lancer un serveur Mongod sur le port 27017.
2. Exécuter le fichier <i>apiMongoDB.py<i> afin de créer la base de données nommée par défaut <i>MessagingAppINFO834<i> dans MongoDB et d'y importer les utilisateurs et conversations d'exemples.  
   <b>/!\<b> Si vous aviez déjà une base de données ayant le nom <i>MessagingAppINFO834<i>, elle sera supprimée. Pour éviter 
   cela vous devrez modifier la valeur de <i>database_name<i> dans le constructeur de la classe <i>MongoDBManger<i>.
  
#### Redis :
4. Lancer un serveur Redis sur le port 6379 (base de données 0 par défaut).  
  
#### Serveur Flask :
5. Lancer le serveur Flask en exécutant le fichier <i>app.py<i>.  
   <b>/!\<b> Les librairies nécessaires sont <i>flask<i>, <i>flask_socketio<i> & <i>jwt<i>.  

#### Angular :  
(Prérequis : Node.js et Angular installé).  
6. Se placer dans le répertoire /frontend/app_message dans un invite de commande.  
7. Executer à cet endroit la commande <i>npm install<i> pour installer les dépendances nécessaires.  
8. Executer la commande <i>ng serve<i> toujours au même endroit.  

#### Utilisation :
9. Se rendre à http://localhost:4200/ dans deux ou trois navigateurs différents et se connecter avec les identifiants des comptes fictifs qui servent d'exemple :
    - username = sasha, password = myPwsasha  
    - username = maria, password = myPwmaria  
    - username = paul, password = myPwpaul

10. Tester l'envoi de messages et observer qu'ils s'affichent sur les autres comptes. La conversation "IDU4" est une conversation à trois comptes utilisateurs.
    
11. Observer les nouvelles données dans MongoDB et Redis. Pour Redis saisir <i>KEYS *<i> dans l'invite de commande du client (lancé avec <i>redis-cli<i>), puis par exemple copier une clé de type <i>connexion:username:clientId<i> et utiliser cette clé comme ceci pour voir les timestamps de connexion/deconnexion, comme ici : <i>LRANGE deconnexion:sasha:a42ad3ec-e2a3-4719-8206-283a623f804c 0 -1<i> .
    
