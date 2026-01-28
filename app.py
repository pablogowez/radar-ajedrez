import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Radar X-Ray", layout="centered")

# Probamos con un solo jugador para no saturar
JUGADOR_TEST = "Faustino Oro"

st.title("🩻 Radar: Modo Rayos X")
st.info("Este modo muestra la TABLA CRUDA que recibe el sistema para ver los nombres reales de las columnas.")

if st.button("VER TABLA CRUDA", type="primary"):
    # Usamos lan=1 (Alemán/Original) porque suele ser la más estable
    url = f"https://chess-results.com/SpielerSuche.aspx?lan=1&name={JUGADOR_TEST}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        # Leemos TODAS las tablas
        dfs = pd.read_html(r.content)
        
        st.write(f"📊 Se encontraron {len(dfs)} tablas en la página.")
        
        if len(dfs) > 0:
            # Buscamos la tabla más grande (la que tenga más datos)
            tabla_grande = max(dfs, key=len)
            
            st.write("### 🔎 Esta es la tabla con más datos encontrada:")
            # Mostramos las columnas detectadas
            st.write("**Columnas detectadas:**", list(tabla_grande.columns))
            
            # Mostramos las primeras 5 filas tal cual vienen
            st.dataframe(tabla_grande.head(5))
            
        else:
            st.error("❌ Pandas no encontró ninguna tabla HTML.")

    except Exception as e:
        st.error(f"Error técnico: {e}")
