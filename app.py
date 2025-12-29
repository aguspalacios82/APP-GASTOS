import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mis Gastos", page_icon="💸")
st.title("💸 Control de Gastos (En la Nube)")

# --- CONEXIÓN CON GOOGLE SHEETS ---
# Usamos el truco del bloque de texto JSON
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    # Leemos el texto JSON desde los secretos y lo convertimos a diccionario
    json_info = json.loads(st.secrets["gcp"]["service_account_json"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_info, scope)
    client = gspread.authorize(creds)

    # Abrir la hoja de cálculo
    sheet = client.open("APP-GASTOS").sheet1
    st.success("✅ Conectado a Google Sheets")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- FORMULARIO ---
st.subheader("Nuevo Gasto")
with st.form("form_gasto", clear_on_submit=True):
    col1, col2 = st.columns(2)
    fecha = col1.date_input("Fecha", date.today())
    categoria = col2.selectbox("Categoría", ["Comida", "Supermercado", "Transporte", "Casa", "Ocio", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.0, step=100.0, format="%.2f")
    nota = st.text_input("Nota (opcional)")
    
    enviado = st.form_submit_button("Guardar Gasto")
    
    if enviado:
        # Convertir fecha a texto para Sheets
        fecha_str = fecha.strftime("%Y-%m-%d")
        # Agregar fila a Google Sheets
        try:
            sheet.append_row([fecha_str, categoria, monto, nota])
            st.toast("¡Gasto guardado en la nube! ☁️")
        except Exception as e:
            st.error(f"No se pudo guardar: {e}")

# --- MOSTRAR HISTORIAL ---
st.divider()
st.subheader("Historial (Desde Google Sheets)")

# Leer datos de Sheets
try:
    registros = sheet.get_all_records()
    if registros:
        df = pd.DataFrame(registros)
        
        # Calcular total
        # Aseguramos que la columna Monto sea numérica (a veces Sheets la manda como texto)
        if "Monto" in df.columns:
            df["Monto"] = pd.to_numeric(df["Monto"], errors='coerce').fillna(0)
            total = df["Monto"].sum()
            st.metric("Total Gastado", f"${total:,.2f}")

        # Mostrar tabla ordenada (recientes arriba)
        # (Asumiendo que 'Fecha' existe, si no mostramos tal cual)
        if "Fecha" in df.columns:
            df = df.sort_values(by="Fecha", ascending=False)
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("La hoja está vacía. ¡Carga tu primer gasto!")
except Exception as e:
    st.warning("No se pudieron leer los datos antiguos o la hoja está vacía.")
