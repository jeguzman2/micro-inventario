from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
# Crea la app FastAPI
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
app = FastAPI()


# ================================
#  CONEXIÓN A MONGO (Atlas o Local)
# ================================
# Si estás local → pon tu propia URL:
# MONGO_URL = "mongodb://localhost:27017/"



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
@app.get("/inventarios/buscar/nombre")
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

#Health check
@app.get("/health")
def health():
    return {"status": "ok"}

