# Importation de la classe MongoClient depuis le module pymongo
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import bcrypt

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
                
                response = {
                    'response_code': 1,
                    'response_message': f"Connexion to DB {database_name} succeeded."
                }
                print(f"Une connexion à la BD {database_name} a eu lieu.")
                return response
            else:
                # Si la base de données n'existe pas, message d'erreur
                response = {
                    'response_code': 300,
                    'response_message': f"DB {database_name} doesn't exist."
                }
                return response
            
        except Exception as e:
            # Capture des exceptions et affichage d'un message d'erreur en cas de problème lors de la connexion
            response = {
                'response_code': 1000,
                'response_message': str(e)
            }
            return response
        

    # Méthode pour vérifier qu'un utilisateur existe dans la base de données lors d'une tentative de connexion
    def verify_user_credentials(self, username, password):
        try:
            user = self.db["Utilisateurs"].find_one({"username": username, "mot_de_passe": password})
            if user:
                print("Informations de connexion valides pour l'utilisateur :", user)
                response = {
                    'response_code': 1,
                    'response_message': f'Verification of credentials OK for user {username}'
                }
                return response
            else:
                print("Nom d'utilisateur ou mot de passe incorrect.")
                response = {
                    'response_code': 401,
                    'response_message': f'Incorrect username or password'
                }
                return response        
        except Exception as e:
            print("Erreur lors de la vérification des informations de connexion de l'utilisateur :", e)
            response = {
                'response_code': 1000,
                'response_message': str(e)
            }
            return response  

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

    # Méthode pour ajouter une conversation pour plusieurs utilisateurs
    def add_conversation_for_users(self, usernames, conversation):
        try:
            # Vérifier si les utilisateurs existent dans la collection Utilisateurs
            users_exist = self.db["Utilisateurs"].count_documents({"username": {"$in": usernames}}) == len(usernames)
            if users_exist:
                # Insérer la conversation dans la collection Conversations
                conversation_result = self.db["Conversations"].insert_one(conversation)
                if conversation_result:
                    conversation_id = conversation_result.inserted_id
                    # Ajouter l'ID de la conversation à la liste des conversations de chaque utilisateur
                    self.db["Utilisateurs"].update_many({"username": {"$in": usernames}}, {"$push": {"conversations": conversation_id}})
                    print("Conversation ajoutée avec succès pour les utilisateurs :", usernames)
                    return True
                else:
                    print("Erreur lors de l'insertion de la conversation.")
                    return False
            else:
                print("Certains utilisateurs de la liste n'existent pas.")
                return False
        except Exception as e:
            print("Erreur lors de l'ajout de la conversation :", e)
            return False


    # Méthode pour ajouter un message à une conversation
    def add_message(self, conversation_id, message):
        try:
            conversation_id = ObjectId(conversation_id)
            # Vérifier si la conversation existe dans la collection Conversation
            if self.db["Conversations"].count_documents({"_id": conversation_id}) > 0:
                # Ajouter le message à la conversation
                self.db["Conversations"].update_one({"_id": conversation_id}, {"$push": {"messages": message}})
                print("Message ajouté avec succès à la conversation avec l'ID :", conversation_id)
                response = {
                    'response_code': 1,
                    'reponse_message': f'Message added in conversation {conversation_id} with success.'
                }
                return response
            else:
                print("La conversation avec l'ID", conversation_id, "n'existe pas.")
                response = {
                    'response_code': 501,
                    'reponse_message': f'Could not add message as conversation {conversation_id} does not exist.'
                }    
                return response      
        except Exception as e:
                response = {
                    'response_code': 1000,
                    'reponse_message': str(e)
                }
                return response

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
                        conversation['_id'] = str(conversation['_id'])
                        conversations.append(conversation)
                response = {
                    'response_code': 1,
                    'reponse_message': f'Success',
                    'response_data': conversations
                }
                return response
            
            else:
                print("L'utilisateur avec le username", username, "n'existe pas.")
                response = {
                    'response_code': 601,
                    'reponse_message': f'Username {username} does not exist. Could not get conversations.',
                }
                return response   
                     
        except Exception as e:
            print("Erreur lors de la récupération des conversations de l'utilisateur :", e)
            response = {
                'response_code': 1000,
                'reponse_message': str(e)
            }
            return response
    

    # Méthode pour récupérer toutes les conversations d'un utilisateur sans les messages
    def get_user_conversations_without_msg(self, username):
        try:
            # Vérifier si l'utilisateur existe dans la collection Utilisateurs
            if self.db["Utilisateurs"].count_documents({"username": username}) > 0:
                # Récupérer les conversations de l'utilisateur
                utilisateur = self.db["Utilisateurs"].find_one({"username": username})
                conversations_ids = utilisateur.get("conversations", [])
                conversations = []
                for conversation_id in conversations_ids:
                    conversation = self.db["Conversations"].find_one({"_id": conversation_id}, {"messages": 0})  # Exclure les messages
                    if conversation:
                        conversation['_id'] = str(conversation['_id'])
                        conversations.append(conversation)
                response = {
                    'response_code': 1,
                    'reponse_message': f'Success',
                    'response_data': conversations
                }
                return response
            
            else:
                print("L'utilisateur avec le username", username, "n'existe pas.")
                response = {
                    'response_code': 601,
                    'reponse_message': f'Username {username} does not exist. Could not get conversations.',
                }
                return response    
                    
        except Exception as e:
            print("Erreur lors de la récupération des conversations de l'utilisateur :", e)
            response = {
                'response_code': 1000,
                'reponse_message': str(e)
            }
            return response
        
    # Méthode pour récupérer la liste des messages pour un ID de conversation donné
    def get_messages_for_conversation(self, conversation_id):
        try:
            conversation_id = ObjectId(conversation_id)
            # Vérifier si la conversation existe dans la collection Conversations
            conversation = self.db["Conversations"].find_one({"_id": conversation_id})
            if conversation:
                messages = conversation.get("messages", [])
                response = {
                    'response_code': 1,
                    'reponse_message': f'Success',
                    'response_data': messages
                }
                return response
            else:
                print("La conversation avec l'ID", conversation_id, "n'existe pas.")
                response = {
                    'response_code': 602,
                    'reponse_message': f'Conversation with ID {conversation_id} does not exist.',
                }
                return response
        except Exception as e:
            print("Erreur lors de la récupération des messages de la conversation :", e)
            response = {
                'response_code': 1000,
                'reponse_message': str(e)
            }
            return response
    
    # Méthode pour récupérer toutes les informations d'un utilisateur sans le mot de passe
    def get_user_info(self, username):
        try:
            # Vérifier si l'utilisateur existe dans la collection Utilisateurs
            user_info = self.db["Utilisateurs"].find_one({"username": username}, {"mot_de_passe": 0})
            if user_info:
                response = {
                    'response_code': 1,
                    'reponse_message': f'Success',
                    'response_data': user_info
                }
                return response            
            else:
                print("L'utilisateur avec le username", username, "n'existe pas.")
                response = {
                    'response_code': 701,
                    'reponse_message': f'Username {username} does not exist.',
                }
                return response            
        except Exception as e:
            print("Erreur lors de la récupération des informations de l'utilisateur :", e)
            response = {
                'response_code': 1000,
                'reponse_message': str(e),
            }
            return response


    def delete_all_users(self):
        try:
            result = self.db["Utilisateurs"].delete_many({})
            print(f"{result.deleted_count} documents supprimés de la collection Utilisateurs.")
            return True
        except Exception as e:
            print("Erreur lors de la suppression des documents de la collection Utilisateurs :", e)
            return False
        

    def delete_all_conversations(self):
        try:
            result = self.db["Conversations"].delete_many({})
            print(f"{result.deleted_count} documents supprimés de la collection Conversations.")
            return True
        except Exception as e:
            print("Erreur lors de la suppression des documents de la collection Conversations :", e)
            return False


# Exemple d'utilisation :
if __name__ == "__main__":
    # Création d'une instance de MongoDBManager avec l'URL de la base de données MongoDB
    db_manager = MongoDBManager("mongodb://localhost:27017/")
    
    # Connexion à la base de données spécifiée (dans cet exemple, "ProjInfo834")
    if db_manager.connect("ProjInfo834"):

        db_manager.delete_all_conversations()
        db_manager.delete_all_conversations()

        users = [
            {"username": "paul", "mot_de_passe": bcrypt.hashpw("myPwpaul".encode(), bcrypt.gensalt()), "conversations": []},
            {"username": "sasha", "mot_de_passe": bcrypt.hashpw("myPwsasha".encode(), bcrypt.gensalt()), "conversations": []},
            {"username": "maria", "mot_de_passe": bcrypt.hashpw("myPwmaria".encode(), bcrypt.gensalt()), "conversations": []}
        ]

        for user in users:
            db_manager.insert_user(user)

        conversations_sasha_maria = [
            {"nom": "Rendu INFO834", "messages": [
                {"_id": 1, "emetteur": "sasha", "contenu": "Salut, tu sais s'il faut rendre un rapport ou juste le code?", "timestamp": str(datetime.now())},
                {"_id": 2, "emetteur": "maria", "contenu": "Aucune idee", "timestamp": str(datetime.now())},
            ]},
            {"nom": "Soirée", "messages": [
            ]},
        ]

        conversation_sasha_maria_paul =  [
            {"nom": "IDU4", "messages": [
            ]}
        ]

        for conv in conversations_sasha_maria:
            db_manager.add_conversation_for_users(['sasha', 'maria'], conv)

        for conv in conversation_sasha_maria_paul:
            db_manager.add_conversation_for_users(['sasha', 'maria', 'paul'], conv)

    else:
        print("Impossible de se connecter a la base de donnees.")