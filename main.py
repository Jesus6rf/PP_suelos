import pandas as pd
import streamlit as st
from supabase import create_client
import datetime
import xgboost as xgb

# Configuración de Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"
TABLE_NAME = "suelo_registros"

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Gestión de Registros de Suelos")

# 📌 Crear Pestañas
menu = st.sidebar.radio("Selecciona una opción", ["Ver Registros", "Agregar Registro", "Editar Registro", "Eliminar Registro", "Predecir Suelo"])

if menu == "Ver Registros":
    st.subheader("📌 Registros Existentes")
    def fetch_data():
        response = supabase.table(TABLE_NAME).select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    
    data = fetch_data()
    if not data.empty:
        st.dataframe(data)
    else:
        st.write("No hay registros disponibles.")

elif menu == "Agregar Registro" or menu == "Predecir Suelo":
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
        # Aquí se podría agregar la lógica de predicción antes del registro
        st.write("(Aquí se mostrará la predicción antes de registrar el suelo)")

    if st.button("Registrar Nuevo Suelo"): 
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
            "altitud": float(altitud)
        }
        try:
            supabase.table(TABLE_NAME).insert(new_record).execute()
            st.success("Registro agregado correctamente.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error al insertar registro: {e}")

elif menu == "Editar Registro":
    st.subheader("📌 Editar Registro Existente")
    id_to_update = st.number_input("ID del registro a editar", min_value=1, step=1)
    updated_ph = st.number_input("Nuevo pH del suelo", min_value=0.0, max_value=14.0, step=0.1)
    updated_humedad = st.number_input("Nueva Humedad", min_value=0.0, step=0.1)
    
    if st.button("Actualizar Registro"):
        try:
            supabase.table(TABLE_NAME).update({"pH": updated_ph, "humedad": updated_humedad}).eq("id", id_to_update).execute()
            st.success("Registro actualizado correctamente.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error al actualizar el registro: {e}")

elif menu == "Eliminar Registro":
    st.subheader("📌 Eliminar Registro")
    id_to_delete = st.number_input("ID del registro a eliminar", min_value=1, step=1)
    if st.button("Eliminar Registro"):
        try:
            supabase.table(TABLE_NAME).delete().eq("id", id_to_delete).execute()
            st.success("Registro eliminado correctamente.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error al eliminar el registro: {e}")

elif menu == "Predecir Suelo":
    st.subheader("📌 Predicción de Fertilidad y Cultivo")
    st.write("(Funcionalidad en desarrollo)")
