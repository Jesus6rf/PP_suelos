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
menu = st.sidebar.radio("Selecciona una opción", ["Agregar Registro", "Actualizar Registro", "Eliminar Registro", "Ver Registros"])

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
        try:
            input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, humedad, densidad, altitud]],
                                      columns=["tipo_suelo", "pH", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "humedad", "densidad", "altitud"])
            fertilidad_pred = int(fertilidad_model.predict(input_data)[0])
            cultivo_pred = "Maíz" if fertilidad_pred == 1 else "Ninguno"
            
            st.write(f"Fertilidad predicha: {'Fértil' if fertilidad_pred == 1 else 'Infértil'}")
            if fertilidad_pred == 1:
                st.write(f"Cultivo recomendado: {cultivo_pred}")
        except Exception as e:
            st.error(f"Error en la predicción: {e}")

elif menu == "Actualizar Registro":
    st.subheader("🔄 Actualizar Registro")
    registros = supabase.table(TABLE_NAME).select("*").execute()
    if registros.data:
        registro_id = st.selectbox("Selecciona un registro para actualizar", [r["id"] for r in registros.data])
        datos = next(r for r in registros.data if r["id"] == registro_id)
        
        tipo_suelo = st.selectbox("Tipo de suelo", options=[1, 2, 3, 4], index=[1, 2, 3, 4].index(datos["tipo_suelo"]))
        input_data = {key: st.number_input(f"{key}", value=datos[key]) for key in ["pH", "materia_organica", "conductividad", "nitrogeno", "fosforo", "potasio", "humedad", "densidad", "altitud"]}
        
        if st.button("Predecir y Actualizar Registro"):
            input_df = pd.DataFrame([list(input_data.values())], columns=input_data.keys())
            fertilidad_pred = int(fertilidad_model.predict(input_df)[0])
            cultivo_pred = "Maíz" if fertilidad_pred == 1 else "Ninguno"
            input_data.update({"fertilidad": fertilidad_pred, "cultivo": cultivo_pred})
            
            supabase.table(TABLE_NAME).update(input_data).eq("id", registro_id).execute()
            st.success("Registro actualizado correctamente.")
            
            st.write(f"Fertilidad predicha: {'Fértil' if fertilidad_pred == 1 else 'Infértil'}")
            if fertilidad_pred == 1:
                st.write(f"Cultivo recomendado: {cultivo_pred}")

elif menu == "Ver Registros":
    st.subheader("📋 Ver Registros")
    registros = supabase.table(TABLE_NAME).select("*").execute()
    if registros.data:
        df = pd.DataFrame(registros.data)
        st.dataframe(df)
    else:
        st.write("No hay registros disponibles.")

elif menu == "Eliminar Registro":
    st.subheader("🗑️ Eliminar Registro")
    registros = supabase.table(TABLE_NAME).select("id").execute()
    if registros.data:
        registro_id = st.selectbox("Selecciona un registro para eliminar", [r["id"] for r in registros.data])
        if st.button("Eliminar"):
            supabase.table(TABLE_NAME).delete().eq("id", registro_id).execute()
            st.success("Registro eliminado correctamente.")
    else:
        st.write("No hay registros disponibles.")
