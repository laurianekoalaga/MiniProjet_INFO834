import redis
from datetime import datetime

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            # Initialisation de la connexion Redis
            self.r = redis.Redis(host=host, port=port, db=db)
        except Exception as e:
            print(f'Redis error: {e}')

    def add_connexion(self, username: str, clientId: str):
        try:
            # Construction de la clé pour stocker la connexion
            key = f"connexion:{username}:{clientId}"
            # Récupération de la date et l'heure actuelle sous forme de chaîne de caractères
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Stockage de la date et l'heure dans Redis
            self.r.lpush(key, timestamp)
        except Exception as e:
            print(f'Redis error: {e}')

    def add_deconnexion(self, username: str, clientId: str):
        try:
            # Construction de la clé pour stocker la déconnexion
            key = f"deconnexion:{username}:{clientId}"
            # Récupération de la date et l'heure actuelle sous forme de chaîne de caractères
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Stockage de la date et l'heure dans Redis
            self.r.lpush(key, timestamp)
        except Exception as e:
            print(f'Redis error: {e}')
