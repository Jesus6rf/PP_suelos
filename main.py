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
    model_dict = pickle.load(model_bytes)  # Cargar el diccionario con los modelos
    
    # Extraer los modelos y el label encoder
    fertilidad_model = model_dict["fertilidad_model"]
    cultivo_model = model_dict["cultivo_model"]
    label_encoder = model_dict["label_encoder"]
    feature_columns_fert = model_dict["feature_columns_fert"]
    feature_columns_cult = model_dict["feature_columns_cult"]
    
    print("Modelos cargados exitosamente")
    st.write("Modelos cargados exitosamente")
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
fosforo = st.number_input("Nivel de Fósforo", min_value=0.0, step=0.1)
potasio = st.number_input("Nivel de Potasio", min_value=0.0, step=0.1)
humedad = st.number_input("Humedad", min_value=0.0, step=0.1)
densidad = st.number_input("Densidad", min_value=0.0, step=0.1)
altitud = st.number_input("Altitud", min_value=0.0, step=0.1)

if st.button("Registrar y Predecir"):
    # Crear dataframe con todas las variables
    input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica, conductividad, nitrogeno, fosforo, potasio, humedad, densidad, altitud, 0]],
                               columns=feature_columns_cult)
    
    # Separar datos para fertilidad (sin cultivo_encoded)
    input_data_fertilidad = input_data[feature_columns_fert]
    
    # Hacer predicción de fertilidad
    try:
        predicted_fertilidad = int(fertilidad_model.predict(input_data_fertilidad)[0])  # Predicción binaria
        
        # Hacer predicción de cultivo usando input_data con cultivo_encoded
        predicted_cultivo_encoded = int(cultivo_model.predict(input_data)[0])  # Predicción de cultivo
        predicted_cultivo = str(label_encoder.inverse_transform([predicted_cultivo_encoded])[0])  # Convertir a texto
    except Exception as e:
        st.error(f"Error en la predicción: {e}")
        st.stop()
    
    # Mostrar predicciones antes de enviarlas a la base de datos
    st.write(f"Fertilidad predicha: {predicted_fertilidad}")
    st.write(f"Cultivo predicho: {predicted_cultivo}")
    
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
        "fertilidad": int(predicted_fertilidad),
        "cultivo": predicted_cultivo
    }
    
    # Verificar el contenido antes de la inserción
    st.write("Nuevo registro a insertar:", new_record)
    
    try:
        response = supabase.table(TABLE_NAME).insert(new_record).execute()
        st.write("Respuesta de Supabase:", response)
    except Exception as e:
        st.error(f"Error en la inserción a Supabase: {e}")
        st.stop()
    
    if response and response.data:
        st.success("Registro y predicción guardados correctamente.")
        st.success(f"Predicción de fertilidad: {predicted_fertilidad}")
        st.success(f"Predicción de cultivo: {predicted_cultivo}")
    else:
        st.error("Error al guardar los datos en Supabase.")
