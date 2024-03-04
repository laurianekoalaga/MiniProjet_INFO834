# Importation de la classe MongoClient depuis le module pymongo
from pymongo import MongoClient
from datetime import datetime

# Définition de la classe MongoDBManager
class MongoDBManager:
    
    
    def __init__(self, url):
        # Initialisation des attributs de la classe
        self.client = None
        self.db = None
        self.url = url
        self.database_name = None  

    # Méthode pour se connecter à la base de données
    def connect(self, database_name):
        try:
            # Connexion au client MongoDB avec l'URL spécifiée
            self.client = MongoClient(self.url)
            # Vérification si la base de données spécifiée existe dans la liste des bases de données du client
            if database_name in self.client.list_database_names():
                # Si la base de données existe, assigner son nom à l'attribut database_name
                self.database_name = database_name
                # Sélection explicite de la base de données dans le client
                self.db = self.client[database_name]
                # Affichage d'un message de réussite de la connexion
                print("Connexion a la base de donnee reussie")
                return True
            else:
                # Si la base de données n'existe pas, afficher un message d'erreur
                print("La base de donnees specifiee n existe pas.")
                return False
        except Exception as e:
            # Capture des exceptions et affichage d'un message d'erreur en cas de problème lors de la connexion
            print("Erreur lors de la connexion a la base de donnees :", e)
            return False

    # Méthode pour insérer un utilisateur dans la collection Utilisateurs
    def insert_user(self, document):
        try:
                # Vérification si le username est déjà utilisé
                if self.db["Utilisateurs"].count_documents({"username": document["username"]}) == 0:
                    # Si le username est unique, insertion du document dans la collection avec l'option {'autoIndexId': False}
                    collection = self.db["Utilisateurs"]
                    return collection.insert_one(document, {'autoIndexId': False})
                else:
                    print("Le username", document["username"], "est déjà utilisé.")
                    return False
                
        except Exception as e:
            # Capture des exceptions et affichage d'un message d'erreur en cas de problème lors de l'insertion
            print("Erreur lors de l'insertion du document :", e)
            return False

    # Méthode pour ajouter une conversation pour un utilisateur
    def add_conversation(self, username, conversation):
        try:
            # Vérifier si l'utilisateur existe dans la collection Utilisateurs
            if self.db["Utilisateurs"].count_documents({"username": username}) > 0:
                    # Insérer la conversation dans la collection Conversations
                    conversation_result = self.db["Conversations"].insert_one(conversation)
                    if conversation_result:
                        conversation_id = conversation_result.inserted_id
                        # Ajouter l'ID de la conversation à la liste des conversations de l'utilisateur
                        self.db["Utilisateurs"].update_one({"username": username}, {"$push": {"conversations": conversation_id}})
                        print("Conversation ajoutée avec succès pour l'utilisateur avec le username :", username)
                        return True
                    else:
                        print("Erreur lors de l'insertion de la conversation.")
                        return False
            else:
                print("L'utilisateur avec le username", username, "n'existe pas.")
                return False
        except Exception as e:
            print("Erreur lors de l'ajout de la conversation :", e)
            return False


    # Méthode pour ajouter un message à une conversation
    def add_message(self, conversation_id, message):
        try:
            # Vérifier si la conversation existe dans la collection Conversation
            if self.db["Conversations"].count_documents({"_id": conversation_id}) > 0:
                # Ajouter le message à la conversation
                self.db["Conversations"].update_one({"_id": conversation_id}, {"$push": {"messages": message}})
                print("Message ajouté avec succès à la conversation avec l'ID :", conversation_id)
                return True
            else:
                print("La conversation avec l'ID", conversation_id, "n'existe pas.")
                return False
        except Exception as e:
            print("Erreur lors de l'ajout du message à la conversation :", e)
            return False

    # Méthode pour récupérer toutes les conversations d'un utilisateur
    def get_user_conversations(self, username):
        try:
            # Vérifier si l'utilisateur existe dans la collection Utilisateurs
            if self.db["Utilisateurs"].count_documents({"username": username}) > 0:
                # Récupérer les conversations de l'utilisateur
                utilisateur = self.db["Utilisateurs"].find_one({"username": username})
                conversations_ids = utilisateur.get("conversations", [])
                conversations = []
                for conversation_id in conversations_ids:
                    conversation = self.db["Conversations"].find_one({"_id": conversation_id})
                    if conversation:
                        conversations.append(conversation)
                return conversations
            else:
                print("L'utilisateur avec le username", username, "n'existe pas.")
                return None
        except Exception as e:
            print("Erreur lors de la récupération des conversations de l'utilisateur :", e)
            return None

    
    # Méthode pour récupérer toutes les informations d'un utilisateur sans le mot de passe
    def get_user_info(self, username):
        try:
            # Vérifier si l'utilisateur existe dans la collection Utilisateurs
            user_info = self.db["Utilisateurs"].find_one({"username": username}, {"mot_de_passe": 0})
            if user_info:
                return user_info
            else:
                print("L'utilisateur avec le username", username, "n'existe pas.")
                return None
        except Exception as e:
            print("Erreur lors de la récupération des informations de l'utilisateur :", e)
            return None


    # Méthode pour supprimer un message d'une conversation et une message???
        


# Exemple d'utilisation :
if __name__ == "__main__":
    # Création d'une instance de MongoDBManager avec l'URL de la base de données MongoDB
    db_manager = MongoDBManager("mongodb://localhost:27017/")
    
    # Connexion à la base de données spécifiée (dans cet exemple, "ProjInfo834")
    if db_manager.connect("ProjInfo834"):
        # Si la connexion est réussie, un nouvel utilisateur est inséré 
        utilisateur = {"username": "utilisateur_testPython", "mot_de_passe": "mdp"}
        insertion_result = db_manager.insert_user(utilisateur) 
        if insertion_result:
            print("\nDocument insere avec l ID :", insertion_result.inserted_id)


        # Récupération de tous les documents de la collection "Utilisateurs"
        '''
        utilisateurs = db_manager.find_all("Utilisateurs")
        print("\nutilisateurs existants:\n")
        for utilisateur in utilisateurs:
            print(utilisateur)
        '''

        # Tester l'ajout d'une conversation pour un utilisateur
        conversation = {"nom": "conversation_test", "messages": []}
        conversation_id = None  # Initialisation de la variable pour stocker l'ID de la conversation
        if db_manager.add_conversation("utilisateur_testPython", conversation):
            print("Conversation ajoutée avec succès.")
            conversation_id = db_manager.get_user_conversations("utilisateur_testPython")[-1]["_id"]
        else:
            print("Erreur lors de l'ajout de la conversation.")

        message_id=0
        # Tester l'ajout d'un message à une conversation
        if conversation_id:
            message_id+=1
            message = {"_id": message_id,"emetteur": "utilisateur_testPython", "contenu": "Ceci est un message de test", "timestamp":datetime.now()}
            if db_manager.add_message(conversation_id, message):
                print("Message ajouté avec succès à la conversation.")
            else:
                print("Erreur lors de l'ajout du message à la conversation.")
        else:
            print("Impossible de tester l'ajout de message car l'ID de la conversation n'a pas été récupéré.")


        # Tester la récupération de toutes les informations d'une conversation
        user_conversations = db_manager.get_user_conversations("utilisateur_testPython")
        if user_conversations:
            print("Conversations de l'utilisateur :")
            for conversation in user_conversations:
                print(conversation)
        else:
            print("Aucune conversation trouvée pour cet utilisateur.")

        #Tester la récupération de toutes les informations d'un utilisateur 
        user_info = db_manager.get_user_info("utilisateur_testPython")
        if user_info:
            print("Informations de l'utilisateur :", user_info)
        else:
            print("Utilisateur non trouvé.")


    else:
        # Si la connexion échoue, afficher un message d'erreur
        print("Impossible de se connecter a la base de donnees.")
