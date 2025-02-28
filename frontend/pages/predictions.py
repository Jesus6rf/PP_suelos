import streamlit as st
from backend.database import get_record, update_record

st.title("Actualizar Registros")

id_registro = st.number_input("ID del registro", min_value=1, step=1)

if st.button("Cargar Registro"):
    record = get_record(id_registro)
    if record:
        st.session_state.record_data = record
    else:
        st.warning("Registro no encontrado.")

if "record_data" in st.session_state:
    record = st.session_state.record_data
    pH = st.number_input("pH", value=record.get("pH", 7.0), min_value=0.0, max_value=14.0, step=0.1)
    
    if st.button("Actualizar Registro"):
        update_record(id_registro, {"pH": float(pH)})
        st.success("Registro actualizado")
