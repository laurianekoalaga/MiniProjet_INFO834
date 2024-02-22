# Importation de la classe MongoClient depuis le module pymongo
from pymongo import MongoClient

# Définition de la classe MongoDBManager
class MongoDBManager:
    
    # Méthode d'initialisation de la classe avec les paramètres url et database_name
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

    # Méthode pour insérer un document dans une collection
    def insert_one(self, collection_name, document):
        try:
            # Vérification si la collection existe dans la base de données
            if collection_name in self.db.list_collection_names():
                # Si la collection existe, insertion du document dans la collection avec l'option {'autoIndexId': False}
                collection = self.db[collection_name]
                return collection.insert_one(document, {'autoIndexId': False})
            else:
                # Si la collection n'existe pas, afficher un message d'erreur
                print("La collection specifiee n existe pas.")
                return None
        except Exception as e:
            # Capture des exceptions et affichage d'un message d'erreur en cas de problème lors de l'insertion
            print("Erreur lors de l insertion du document :", e)
            return None

    # Méthode pour afficher tous les documents d'une collection
    def find_all(self, collection_name):
        try:
            # Sélection de la collection dans la base de données
            collection = self.db[collection_name]
            # Récupération de tous les documents de la collection
            return collection.find()
        except Exception as e:
            # Capture des exceptions et affichage d'un message d'erreur en cas de problème lors de la récupération des documents
            print("Erreur lors de la recuperation des documents :", e)
            return None


# Exemple d'utilisation :
if __name__ == "__main__":
    # Création d'une instance de MongoDBManager avec l'URL de la base de données MongoDB
    db_manager = MongoDBManager("mongodb://localhost:27017/")
    
    # Connexion à la base de données spécifiée (dans cet exemple, "ProjInfo834")
    if db_manager.connect("ProjInfo834"):
        # Si la connexion est réussie, un nouvel utilisateur est inséré 
        utilisateur = {"pseudo": "utilisateur_testPython", "mot_de_passe": "mdp"}
        insertion_result = db_manager.insert_one("Utilisateurs", utilisateur)
        if insertion_result:
            print("\nDocument insere avec l ID :", insertion_result.inserted_id)


        # Récupération de tous les documents de la collection "Utilisateurs"
        utilisateurs = db_manager.find_all("Utilisateurs")
        print("\nutilisateurs existants:\n")
        for utilisateur in utilisateurs:
            print(utilisateur)
    else:
        # Si la connexion échoue, afficher un message d'erreur
        print("Impossible de se connecter a la base de donnees.")
