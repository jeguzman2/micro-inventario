from bson import ObjectId
import re

class ValidationError(Exception):
    pass

class InputSanitizer:

    @staticmethod
    def validate_object_id(id: str):
        if not ObjectId.is_valid(id):
            raise ValidationError("ID inválido o malformado.")

    @staticmethod
    def validate_stock(stock):
        if not isinstance(stock, int):
            raise ValidationError("El stock debe ser un número entero.")
        if stock < 0 or stock > 1_000_000:
            raise ValidationError("El stock está fuera de rango permitido (0-1,000,000).")

    @staticmethod
    def validate_nombre(nombre: str):
        if nombre is None or nombre.strip() == "":
            raise ValidationError("El nombre no puede estar vacío.")
        
        # Evitar regex injection
        if re.search(r"[^\w\sáéíóúÁÉÍÓÚñÑ-]", nombre):
            raise ValidationError("El nombre contiene caracteres no permitidos.")
