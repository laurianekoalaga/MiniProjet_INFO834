import redis
import time
import redis
import time

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.r = redis.Redis(host=host, port=port, db=db)
        except Exception as e:
            print(f'Redis error: {e}')

    def add_connexion(self, username: str, clientId: str):
        try:
            key = f"connexion:{username}:{clientId}"
            self.r.lpush(key, time.time())
        except Exception as e:
            print(f'Redis error: {e}')

    def add_deconnexion(self, username: str, clientId: str):
        try:
            key = f"deconnexion:{username}:{clientId}"
            self.r.lpush(key, time.time())
        except Exception as e:
            print(f'Redis error: {e}')     
