import requests
import pickle
import os
from io import BytesIO

# 📌 Configuración de Supabase Storage
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"
BUCKET_NAME = "modelos"  # Nombre del storage en Supabase
MODEL_FILE = "xgboost_multioutput.pkl"  # Nombre del archivo en el storage


def obtener_modelo():
    """Devuelve la URL pública del modelo almacenado en Supabase Storage."""
    url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{MODEL_FILE}"
    return url

# 📌 Obtener la URL del modelo al importar el módulo
modelo_url = obtener_modelo()

if modelo_url:
    print(f"✅ Modelo disponible en: {modelo_url}")
else:
    print("❌ No se pudo acceder al modelo en Supabase.")
