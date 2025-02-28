import pandas as pd
import streamlit as st
from supabase import create_client
import io
import json
import datetime
import uuid
import xgboost as xgb

# Configuración de Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"
BUCKET_NAME = "modelos"
TABLE_NAME = "suelo_registros"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Descargar modelos desde Supabase
try:
    response_fert = supabase.storage.from_(BUCKET_NAME).download("fertilidad_model.json")
    response_cult = supabase.storage.from_(BUCKET_NAME).download("cultivo_model.json")
    
    # Guardar temporalmente en archivos locales
    with open("fertilidad_model.json", "wb") as f:
        f.write(response_fert)
    with open("cultivo_model.json", "wb") as f:
        f.write(response_cult)
    
    # Cargar modelos
    fertilidad_model = xgb.XGBClassifier()
    fertilidad_model.load_model("fertilidad_model.json")
    
    cultivo_model = xgb.XGBClassifier()
    cultivo_model.load_model("cultivo_model.json")
    
    st.success("Modelos cargados exitosamente desde Supabase")
except Exception as e:
    st.error(f"Error al cargar los modelos: {e}")
    st.stop()

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
    # Crear dataframe con todas las variables
    input_data = pd.DataFrame([[float(tipo_suelo), float(pH), float(materia_organica), float(conductividad), float(nitrogeno), 
                                float(fosforo), float(potasio), float(humedad), float(densidad), float(altitud)]],
                               columns=["tipo_suelo", "pH", "materia_organica", "conductividad", "nitrogeno", 
                                        "fosforo", "potasio", "humedad", "densidad", "altitud"])
    
    # Hacer predicción de fertilidad
    try:
        st.write('Valores de entrada para fertilidad:', input_data)
        predicted_fertilidad = int(fertilidad_model.predict(input_data)[0])
        st.write(f'Predicción cruda de fertilidad: {predicted_fertilidad}')
    except Exception as e:
        st.error(f"Error en la predicción de fertilidad: {e}")
        st.stop()
    
    # Hacer predicción de cultivo
    try:
        st.write('Valores de entrada para cultivo:', input_data)
        predicted_cultivo_encoded = int(cultivo_model.predict(input_data)[0])
        st.write(f'Predicción cruda de cultivo: {predicted_cultivo_encoded}')
    except Exception as e:
        st.error(f"Error en la predicción de cultivo: {e}")
        st.stop()
    
    # Mostrar predicciones antes de enviarlas a la base de datos
    st.write(f"Fertilidad predicha: {predicted_fertilidad}")
    st.write(f"Cultivo predicho: {predicted_cultivo_encoded}")
    
    # Generar valores de id y fecha_registro
    record_id = str(uuid.uuid4())
    fecha_registro = datetime.datetime.utcnow().isoformat()
    
    # Insertar nuevo registro en Supabase con predicciones
    new_record = {
        "id": record_id,
        "fecha_registro": fecha_registro,
        "tipo_suelo": int(tipo_suelo),
        "pH": float(pH),
        "materia_organica": float(materia_organica),
        "conductividad": float(conductividad),
        "nitrogeno": float(nitrogeno),
        "fosforo": float(fosforo),
        "potasio": float(potasio),
        "humedad": float(humedad),
        "densidad": float(densidad),
        "altitud": float(altitud),
        "fertilidad": predicted_fertilidad,
        "cultivo": predicted_cultivo_encoded
    }
    
    try:
        response = supabase.table(TABLE_NAME).insert(new_record).execute()
        st.success("Registro y predicción guardados correctamente.")
    except Exception as e:
        st.error(f"Error en la inserción a Supabase: {e}")
