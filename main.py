import pickle
import pandas as pd
import streamlit as st
from supabase import create_client
import io
import json
import datetime
import uuid

# Configuración de Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"
BUCKET_NAME = "modelos"
MODEL_FILE = "xgboost_multioutput.pkl"
TABLE_NAME = "suelo_registros"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Descargar modelo desde Supabase Storage con manejo de errores
try:
    response = supabase.storage.from_(BUCKET_NAME).download(MODEL_FILE)
    model_bytes = io.BytesIO(response)  # Convertir a objeto BytesIO
    model = pickle.load(model_bytes)  # Cargar modelo con pickle
    print(f"Modelo cargado exitosamente, tipo: {type(model)}")
    st.write(f"Modelo cargado exitosamente, tipo: {type(model)}")
except Exception as e:
    st.error(f"Error al cargar el modelo: {e}")
    st.stop()

st.title("Registro y Predicción de Suelos")

# Formulario para ingreso de datos
tipo_suelo = st.number_input("Tipo de suelo", min_value=0, step=1)
pH = st.number_input("pH del suelo", min_value=0.0, step=0.1)
materia_organica = st.number_input("Materia orgánica", min_value=0.0, step=0.1)
conductividad = st.number_input("Conductividad eléctrica", min_value=0.0, step=0.1)
nitrogeno = st.number_input("Nivel de Nitrógeno", min_value=0.0, step=0.1)
fósforo = st.number_input("Nivel de Fósforo", min_value=0.0, step=0.1)
potasio = st.number_input("Nivel de Potasio", min_value=0.0, step=0.1)
humedad = st.number_input("Humedad", min_value=0.0, step=0.1)
densidad = st.number_input("Densidad", min_value=0.0, step=0.1)
altitud = st.number_input("Altitud", min_value=0.0, step=0.1)

if st.button("Registrar y Predecir"):
    # Crear dataframe temporal para predicción
    input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fósforo, potasio, humedad, densidad, altitud]],
                               columns=["tipo_suelo", "pH", "materia_organica", "conductividad", "nitrogeno", "fósforo", "potasio", "humedad", "densidad", "altitud"])
    
    # Hacer predicción
    try:
        st.write(f"Tipo de modelo antes de predecir: {type(model)}")
        prediction = model.predict(input_data)
        predicted_fertilidad, predicted_cultivo = int(prediction[0, 0]), str(prediction[0, 1])
    except Exception as e:
        st.error(f"Error en la predicción: {e}")
        st.stop()
    
    # Generar valores de id y fecha_registro
    record_id = str(uuid.uuid4())
    fecha_registro = datetime.datetime.utcnow().isoformat()
    
    # Insertar nuevo registro en Supabase con predicciones
    new_record = {
        "id": record_id,
        "fecha_registro": fecha_registro,
        "tipo_suelo": tipo_suelo,
        "pH": pH,
        "materia_organica": materia_organica,
        "conductividad": conductividad,
        "nitrogeno": nitrogeno,
        "fosforo": fósforo,
        "potasio": potasio,
        "humedad": humedad,
        "densidad": densidad,
        "altitud": altitud,
        "fertilidad": predicted_fertilidad,
        "cultivo": predicted_cultivo
    }
    response = supabase.table(TABLE_NAME).insert(new_record).execute()
    
    if response.data:
        st.success("Registro y predicción guardados correctamente.")
        st.success(f"Predicción de fertilidad: {predicted_fertilidad}")
        st.success(f"Predicción de cultivo: {predicted_cultivo}")
    else:
        st.error("Error al guardar los datos en Supabase.")
