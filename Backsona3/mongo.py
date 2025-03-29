from pymongo import MongoClient

uri = "mongodb+srv://BrianG:MikuNK0505@hydrai.o08spkh.mongodb.net/"
client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Conectado a MongoDB exitosamente")
except Exception as e:
    print(f"Error al conectar: {e}")
