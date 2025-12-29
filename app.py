import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mis Gastos", page_icon="💸")
st.title("💸 Gastos (Google Sheets)")

# --- CONEXIÓN ---
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    # Leemos la credencial desde los secretos
    json_info = json.loads(st.secrets["gcp"]["service_account_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_info, scope)
    client = gspread.authorize(creds)
    
    # AQUI ESTA EL CAMBIO: Usamos el nombre real de tu hoja
    sheet = client.open("APP-GASTOS").sheet1
    st.success("✅ Conectado a Google Sheets")
except Exception as e:
    st.error(f"Error conectando: {e}")
    st.stop()

# --- CARGAR GASTO ---
with st.form("form", clear_on_submit=True):
    fecha = st.date_input("Fecha", date.today())
    categoria = st.selectbox("Categoría", ["Comida", "Supermercado", "Transporte", "Salidas", "Otros"])
    monto = st.number_input("Monto", min_value=0.0, step=100.0)
    nota = st.text_input("Nota")
    
    if st.form_submit_button("Guardar"):
        try:
            # Guardamos: Fecha (texto), Categoria, Monto, Nota
            sheet.append_row([str(fecha), categoria, monto, nota])
            st.toast("¡Guardado en la Nube!")
        except Exception as e:
            st.error(f"Error al guardar: {e}")

# --- VER DATOS ---
st.divider()
try:
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        # Calculamos el total sumando la columna 'Monto'
        if 'Monto' in df.columns:
            total = pd.to_numeric(df['Monto'], errors='coerce').fillna(0).sum()
            st.metric("Total Gastado", f"${total:,.2f}")
    else:
        st.info("Hoja vacía. ¡Carga el primer gasto!")
except:
    st.info("Aún no hay datos cargados.")

