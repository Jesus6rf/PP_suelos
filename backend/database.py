from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("https://kuztdsenxrumlvwygzdn.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc")
TABLE_NAME = "suelo_registros"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_record(data):
    """Inserta un nuevo registro en Supabase."""
    return supabase.table(TABLE_NAME).insert(data).execute()

def update_record(id, data):
    """Actualiza un registro en Supabase."""
    return supabase.table(TABLE_NAME).update(data).eq("id", id).execute()

def get_record(id):
    """Obtiene un registro por ID."""
    response = supabase.table(TABLE_NAME).select("*").eq("id", id).execute()
    return response.data[0] if response.data else None

def get_all_records():
    """Obtiene todos los registros."""
    return supabase.table(TABLE_NAME).select("*").execute().data

def delete_record(id):
    """Elimina un registro por ID."""
    return supabase.table(TABLE_NAME).delete().eq("id", id).execute()
