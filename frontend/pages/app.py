import streamlit as st
import pandas as pd
from backend.database import insert_record
from backend.model_loader import load_models
import datetime

st.title("Registro y Predicción de Suelos")

# Cargar modelos
try:
    fertilidad_model, cultivo_model = load_models()
    st.success("Modelos cargados correctamente")
except RuntimeError as e:
    st.error(e)
    st.stop()

# Entrada de datos
tipo_suelo = st.selectbox("Tipo de suelo", [1, 2, 3, 4], 
    format_func=lambda x: {1: 'Arcilloso', 2: 'Arenoso', 3: 'Limoso', 4: 'Franco'}.get(x, 'Desconocido'))
pH = st.number_input("pH del suelo", min_value=0.0, max_value=14.0, step=0.1)
materia_organica = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=10.0, step=0.1)

if st.button("Registrar y Predecir"):
    input_data = pd.DataFrame([[tipo_suelo, pH, materia_organica]], 
                               columns=["tipo_suelo", "pH", "materia_organica"])
    
    try:
        # Predicción
        predicted_fertilidad = int(fertilidad_model.predict(input_data)[0])
        predicted_fertilidad_text = "Fértil" if predicted_fertilidad == 1 else "Infértil"
        predicted_cultivo = "Ninguno"
        
        if predicted_fertilidad == 1:
            cultivos = ["Trigo", "Maíz", "Caña de Azúcar", "Algodón", "Arroz"]
            predicted_cultivo_encoded = int(cultivo_model.predict(input_data)[0])
            predicted_cultivo = cultivos[predicted_cultivo_encoded] if predicted_cultivo_encoded < len(cultivos) else "Desconocido"

        # Guardar en Supabase
        new_record = {
            "tipo_suelo": int(tipo_suelo), "pH": float(pH), "materia_organica": float(materia_organica),
            "fertilidad": predicted_fertilidad, "cultivo": predicted_cultivo,
            "fecha_registro": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        insert_record(new_record)
        
        # Mostrar resultado
        st.write(f"**Fertilidad Predicha:** {predicted_fertilidad_text}")
        st.write(f"**Cultivo Predicho:** {predicted_cultivo}")
        st.success("Registro guardado correctamente")
    
    except Exception as e:
        st.error(f"Error: {e}")

# Aplicar estilos CSS
def apply_styles():
    with open("frontend/assets/style.css", "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

apply_styles()
