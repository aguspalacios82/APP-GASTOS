import streamlit as st
import pandas as pd
import os
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Mis Gastos", page_icon="💸")

# Título
st.title("💸 Control de Gastos")

# Nombre del archivo donde guardaremos los datos (por ahora)
ARCHIVO_GASTOS = 'gastos.csv'

# Función para cargar datos
def cargar_datos():
    if os.path.exists(ARCHIVO_GASTOS):
        return pd.read_csv(ARCHIVO_GASTOS)
    else:
        return pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Nota"])

# Cargar los datos existentes
df = cargar_datos()

# --- FORMULARIO DE INGRESO ---
st.subheader("Nuevo Gasto")
with st.form("form_gasto", clear_on_submit=True):
    col1, col2 = st.columns(2)
    fecha = col1.date_input("Fecha", date.today())
    categoria = col2.selectbox("Categoría", ["Comida", "Transporte", "Casa", "Ocio", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.0, step=100.0, format="%.2f")
    nota = st.text_input("Nota (opcional)")
    
    guardar = st.form_submit_button("Cargar Gasto")
    
    if guardar:
        nuevo_gasto = pd.DataFrame([{
            "Fecha": fecha,
            "Categoría": categoria,
            "Monto": monto,
            "Nota": nota
        }])
        # Guardar en el archivo CSV
        df = pd.concat([df, nuevo_gasto], ignore_index=True)
        df.to_csv(ARCHIVO_GASTOS, index=False)
        st.success("¡Gasto guardado!")
        st.rerun() # Recarga la página para mostrar el nuevo dato

# --- MOSTRAR DATOS ---
st.divider()
st.subheader("Historial")

if not df.empty:
    # Métricas rápidas
    total = df["Monto"].sum()
    st.metric("Total Gastado", f"${total:,.2f}")
    
    # Mostrar tabla (ordenada por fecha reciente primero)
    df = df.sort_values(by="Fecha", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Aún no hay gastos cargados.")


