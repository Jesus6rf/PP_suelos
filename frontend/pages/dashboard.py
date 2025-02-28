import streamlit as st
import pandas as pd
from backend.database import get_all_records

st.title("Visualización de Registros")

try:
    data = get_all_records()
    df = pd.DataFrame(data)
    st.dataframe(df)
except Exception as e:
    st.error(f"Error al obtener los datos: {e}")
