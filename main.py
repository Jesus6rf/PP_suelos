import streamlit as st
import pandas as pd
import supabase
import xgboost as xgb
import numpy as np
import tempfile
from io import StringIO

# Configuración de Supabase
SUPABASE_URL = "https://kuztdsenxrumlvwygzdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1enRkc2VueHJ1bWx2d3lnemRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2OTI0NjksImV4cCI6MjA1NjI2ODQ2OX0.PhGg9A5k-UUoIc83LhLdETIl1WbUErRMBnzQwkRjlPc"

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Cargar modelo desde Supabase Storage
def load_model():
    response = supabase_client.storage.from_("modelos").download("xgboost_multioutput.json")
    
    # Guardar el modelo en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(response)
        temp_path = temp_file.name  # Obtener la ruta del archivo
    
    # Cargar el modelo desde el archivo temporal
    model = xgb.Booster()
    model.load_model(temp_path)
    
    return model

model = load_model()

# Función para cargar datos desde Supabase
def get_data():
    response = supabase_client.table("suelo_registros").select("*").execute()
    return pd.DataFrame(response.data)

# Función para insertar un nuevo registro
def insert_record(data):
    response = supabase_client.table("suelo_registros").insert(data).execute()
    return response

# Función de predicción
def predict(data):
    input_data = np.array(data).reshape(1, -1)
    dmatrix = xgb.DMatrix(input_data)
    prediction = model.predict(dmatrix)
    return prediction[0]

# Interfaz Streamlit
st.title("Gestión de Suelos - Predicciones y Registro")

menu = ["Visualizar Datos", "Agregar Registro", "Hacer Predicción"]
choice = st.sidebar.selectbox("Selecciona una opción", menu)

if choice == "Visualizar Datos":
    st.subheader("Datos actuales en la base de datos")
    df = get_data()
    st.dataframe(df)

elif choice == "Agregar Registro":
    st.subheader("Agregar un nuevo registro")
    tipo_suelo = st.number_input("Tipo de Suelo", min_value=1, max_value=10)
    pH = st.number_input("pH del suelo")
    materia_organica = st.number_input("Materia Orgánica (%)")
    conductividad = st.number_input("Conductividad eléctrica")
    nitrogeno = st.number_input("Nitrógeno (mg/kg)")
    fosforo = st.number_input("Fósforo (mg/kg)")
    potasio = st.number_input("Potasio (mg/kg)")
    humedad = st.number_input("Humedad (%)")
    densidad = st.number_input("Densidad aparente (g/cm³)")
    altitud = st.number_input("Altitud (m)")
    fertilidad = st.selectbox("Fertilidad", [0, 1], format_func=lambda x: "Fértil" if x == 1 else "No Fértil")
    cultivo = st.text_input("Cultivo asociado")
    
    if st.button("Guardar Registro"):
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
            "altitud": altitud,
            "fertilidad": fertilidad,
            "cultivo": cultivo
        }
        insert_record(new_record)
        st.success("Registro guardado exitosamente")

elif choice == "Hacer Predicción":
    st.subheader("Realizar predicción con el modelo")
    input_values = []
    for param in ["pH", "Materia Orgánica", "Conductividad", "Nitrógeno", "Fósforo", "Potasio", "Humedad", "Densidad", "Altitud"]:
        value = st.number_input(f"{param}")
        input_values.append(value)
    
    if st.button("Predecir"):
        result = predict(input_values)
        st.write("Predicción del modelo:", result)