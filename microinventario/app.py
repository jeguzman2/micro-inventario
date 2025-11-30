from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os

# Crea la app FastAPI
app = FastAPI()


# ================================
#  CONEXIÓN A MONGO (Atlas o Local)
# ================================
# Si estás local → pon tu propia URL:
# MONGO_URL = "mongodb://localhost:27017/"

MONGO_URL = "mongodb+srv://provesi_user:123@cluster0.oj30l9o.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URL)
db = client["provesi"]
productos = db["productos"]




# -----------------------------
#     ENDPOINTS DEL SERVICIO
# -----------------------------



@app.get("/")
def home():
    return {"mensaje": "Inventario funcionando correctamente"}


# Obtener producto por ID
@app.get("/inventarios/detalle/{id}")
def get_producto(id: str):
    try:
        producto = productos.find_one({"_id": ObjectId(id)})
        if not producto:
            return {"error": "Producto no encontrado"}
        
        # Convertir ObjectId a string
        producto["_id"] = str(producto["_id"])
        return producto

    except:
        return {"error": "ID inválido"}


# Actualizar stock
@app.patch("/inventarios/actualizar/{id}/stock")
def update_stock(id: str, body: dict):
    if "stock" not in body:
        return {"error": "Falta el campo 'stock'"}

    try:
        productos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"stock": body["stock"]}}
        )
        return {"mensaje": "Stock actualizado"}
    except:
        return {"error": "ID inválido"}


# Buscar por nombre
@app.get("/inventarios/buscar")
def buscar(nombre: str):
    print(nombre)
    resultados = productos.find({
        "nombre": {"$regex": f".*{nombre}.*", "$options": "i"}
    })

    lista = []
    
    for prod in resultados:
        prod["_id"] = str(prod["_id"])
        lista.append(prod)

    return lista

