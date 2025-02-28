import pandas as pd
import streamlit as st
from supabase import create_client
import datetime
import xgboost as xgb

# Configuración de Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"
TABLE_NAME = "suelo_registros"
BUCKET_NAME = "modelos"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Descargar modelos desde Supabase
try:
    response_fert = supabase.storage.from_(BUCKET_NAME).download("fertilidad_model.json")
    response_cult = supabase.storage.from_(BUCKET_NAME).download("cultivo_model.json")
    
    with open("fertilidad_model.json", "wb") as f:
        f.write(response_fert)
    with open("cultivo_model.json", "wb") as f:
        f.write(response_cult)
    
    fertilidad_model = xgb.XGBClassifier()
    fertilidad_model.load_model("fertilidad_model.json")
    
    cultivo_model = xgb.XGBClassifier()
    cultivo_model.load_model("cultivo_model.json")
    
    st.success("Modelos cargados exitosamente desde Supabase")
except Exception as e:
    st.error(f"Error al cargar los modelos: {e}")
    st.stop()

st.title("Gestión de Registros de Suelos")

# 📌 Crear Pestañas
menu = st.sidebar.radio("Selecciona una opción", ["Agregar Registro", "Editar Registro", "Eliminar Registro"])

if menu == "Agregar Registro":
    st.subheader("📌 Agregar un Nuevo Registro")
    tipo_suelo = st.selectbox("Tipo de suelo", options=[1, 2, 3, 4], format_func=lambda x: {1: 'Arcilloso', 2: 'Arenoso', 3: 'Limoso', 4: 'Franco'}.get(x, 'Desconocido'))
    pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, step=0.1)
    materia_organica = st.number_input("Materia orgánica", min_value=0.0, max_value=10.0, step=0.1)
    conductividad = st.number_input("Conductividad eléctrica", min_value=0.0, max_value=5.0, step=0.1)
    nitrogeno = st.number_input("Nivel de Nitrógeno", min_value=0.0, max_value=5.0, step=0.1)
    fosforo = st.number_input("Nivel de Fósforo", min_value=0.0, max_value=500.0, step=0.1)
    potasio = st.number_input("Nivel de Potasio", min_value=0.0, step=0.1)
    humedad = st.number_input("Humedad", min_value=0.0, step=0.1)
    densidad = st.number_input("Densidad", min_value=0.0, step=0.1)
    altitud = st.number_input("Altitud", min_value=0.0, step=0.1)
    
    if st.button("Predecir Fertilidad y Cultivo"):
        if 'fertilidad_pred' not in st.session_state:
            st.session_state.fertilidad_pred = None
        if 'cultivo_pred' not in st.session_state:
            st.session_state.cultivo_pred = None
        try:
            input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, humedad, densidad, altitud]],
                                      columns=["tipo_suelo", "pH", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "humedad", "densidad", "altitud"])
            st.session_state.fertilidad_pred = int(fertilidad_model.predict(input_data)[0])
            st.session_state.cultivo_pred = "Maíz" if st.session_state.fertilidad_pred == 1 else "Ninguno"
            
            st.write(f"Fertilidad predicha: {'Fértil' if st.session_state.fertilidad_pred == 1 else 'Infértil'}")
            if st.session_state.fertilidad_pred == 1:
                st.write(f"Cultivo recomendado: {st.session_state.cultivo_pred}")
        except Exception as e:
            st.error(f"Error en la predicción: {e}")
    
    if st.button("Registrar Nuevo Suelo"):
        if 'fertilidad_pred' not in st.session_state or st.session_state.fertilidad_pred is None:
            st.error("⚠️ Primero debes predecir la fertilidad y el cultivo antes de registrar.")
            st.stop() 
        fecha_registro = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        new_record = {
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
            "fertilidad": st.session_state.fertilidad_pred,
            "cultivo": st.session_state.cultivo_pred
        }
        try:
            response = supabase.table(TABLE_NAME).insert(new_record).execute()
            if response and response.data:
                st.success("Registro agregado correctamente.")
            else:
                st.error("Error: No se pudo insertar el registro. Verifica los datos.")
        except Exception as e:
            st.error(f"Error en la inserción a Supabase: {e}")
