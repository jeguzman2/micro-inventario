from fastapi import FastAPI
from pydantic_core import ValidationError
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

from sanitizer import InputSanitizer
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


@app.post("/inventarios/crear")
def crear_producto(body: dict):
    try:
        # Validar nombre
        if "nombre" not in body:
            raise ValidationError("Falta el campo 'nombre'.")
        InputSanitizer.validate_nombre(body["nombre"])

        # Validar stock
        if "stock" not in body:
            raise ValidationError("Falta el campo 'stock'.")
        InputSanitizer.validate_stock(body["stock"])

        # Construir documento
        nuevo = {
            "nombre": body["nombre"],
            "stock": body["stock"]
        }

        # Insertar en Mongo
        result = productos.insert_one(nuevo)

        return {
            "mensaje": "Producto creado",
            "_id": str(result.inserted_id)
        }

    except ValidationError as e:
        return {"error": str(e)}

# Obtener producto por ID
@app.get("/inventarios/detalle/{id}")
def get_producto(id: str):
    try:
        InputSanitizer.validate_object_id(id)

        producto = productos.find_one({"_id": ObjectId(id)})
        if not producto:
            return {"error": "Producto no encontrado"}

        producto["_id"] = str(producto["_id"])
        return producto
    
    except ValidationError as e:
        return {"error": str(e)}


# Actualizar stock
@app.patch("/inventarios/actualizar/{id}/stock")
def update_stock(id: str, body: dict):
    try:
        # Validar ID
        InputSanitizer.validate_object_id(id)

        # Validar campo stock
        if "stock" not in body:
            raise ValidationError("Falta el campo 'stock'.")
        
        InputSanitizer.validate_stock(body["stock"])

        productos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"stock": body["stock"]}}
        )

        return {"mensaje": "Stock actualizado"}
    
    except ValidationError as e:
        return {"error": str(e)}


# Buscar por nombre
@app.get("/inventarios/buscar/nombre")
def buscar(nombre: str):
    try:
        InputSanitizer.validate_nombre(nombre)

        resultados = productos.find({
            "nombre": {"$regex": f".*{nombre}.*", "$options": "i"}
        })

        lista = []
        for prod in resultados:
            prod["_id"] = str(prod["_id"])
            lista.append(prod)

        return lista

    except ValidationError as e:
        return {"error": str(e)}

@app.get("/inventarios")
def get_inventarios():
    inventarios = []

    for prod in productos.find():
        prod["_id"] = str(prod["_id"])  # convertir ObjectId
        inventarios.append(prod)

    return inventarios


#Health check
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready"}
