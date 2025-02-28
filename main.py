import pickle
import pandas as pd
import streamlit as st
from supabase import create_client
import io
import json

# Configuración de Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"
BUCKET_NAME = "modelos"
MODEL_FILE = "xgboost_multioutput.pkl"
TABLE_NAME = "suelo_registros"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Descargar modelo desde Supabase Storage
response = supabase.storage.from_(BUCKET_NAME).download(MODEL_FILE)
model = pickle.load(io.BytesIO(response))
print("Modelo cargado exitosamente")

st.title("Registro y Predicción de Suelos")

# Formulario para ingreso de datos
tipo_suelo = st.number_input("Tipo de suelo", min_value=0, step=1)
pH = st.number_input("pH del suelo", min_value=0.0, step=0.1)
materia_organica = st.number_input("Materia orgánica", min_value=0.0, step=0.1)
conductividad = st.number_input("Conductividad eléctrica", min_value=0.0, step=0.1)
nitrogeno = st.number_input("Nivel de Nitrógeno", min_value=0.0, step=0.1)
fosforo = st.number_input("Nivel de Fósforo", min_value=0.0, step=0.1)
potasio = st.number_input("Nivel de Potasio", min_value=0.0, step=0.1)
humedad = st.number_input("Humedad", min_value=0.0, step=0.1)
densidad = st.number_input("Densidad", min_value=0.0, step=0.1)
altitud = st.number_input("Altitud", min_value=0.0, step=0.1)

if st.button("Registrar y Predecir"):
    # Insertar nuevo registro en Supabase
    new_record = {
        "tipo_suelo": tipo_suelo,
        "pH": pH,
        "materia_organica": materia_organica,
        "conductividad": conductividad,
        "nitrogeno": nitrogeno,
        "fosforo": fosforo,
        "potasio": potasio,
        "humedad": humedad,
        "densidad": densidad,
        "altitud": altitud
    }
    response = supabase.table(TABLE_NAME).insert(new_record).execute()
    st.success("Registro guardado en la base de datos.")
    
    # Obtener el ID del nuevo registro
    data_response = supabase.table(TABLE_NAME).select("id, tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, humedad, densidad, altitud").order("fecha_registro", desc=True).limit(1).execute()
    data = pd.DataFrame(data_response.data)
    
    if not data.empty:
        X = data[['tipo_suelo', 'pH', 'materia_organica', 'conductividad', 'nitrogeno', 'fosforo', 'potasio', 'humedad', 'densidad', 'altitud']]
        prediction = model.predict(X)
        predicted_fertilidad, predicted_cultivo = prediction[:, 0], prediction[:, 1]
        
        # Actualizar la tabla con las predicciones
        supabase.table(TABLE_NAME).update({"fertilidad": int(predicted_fertilidad[0]), "cultivo": str(predicted_cultivo[0])}).eq("id", data["id"].iloc[0]).execute()
        st.success(f"Predicción de fertilidad almacenada: {int(predicted_fertilidad[0])}")
        st.success(f"Predicción de cultivo almacenada: {str(predicted_cultivo[0])}")
