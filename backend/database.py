import os
from supabase import create_client, Client
import pickle
import requests
from io import BytesIO

# Configuración de la conexión a Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Función para obtener datos de la tabla "suelo_registros"
def obtener_registros():
    response = supabase_client.table("suelo_registros").select("*").execute()
    return response.data if response.data else []

# Función para insertar un nuevo registro
def insertar_registro(datos):
    response = supabase_client.table("suelo_registros").insert(datos).execute()
    return response.data if response.data else None

# Función para leer el modelo directamente desde Supabase Storage sin descargarlo
def leer_modelo():
    bucket_name = "modelos"
    file_name = "xgboost_multioutput.pkl"
    
    response = supabase_client.storage.from_(bucket_name).download(file_name)
    if response:
        return pickle.load(BytesIO(response))
    else:
        raise Exception("No se pudo leer el modelo desde Supabase.")
