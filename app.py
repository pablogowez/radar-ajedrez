import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="Radar Diagnóstico", layout="centered")

JUGADORES_TEST = {"Faustino Oro": "20000197"} # Probamos solo con uno para no saturar

st.title("🕵️ Radar 4.0: El Investigador")

if st.button("EJECUTAR DIAGNÓSTICO", type="primary"):
    url = f"https://chess-results.com/SpielerSuche.aspx?lan=2&id=20000197"
    
    # Cabeceras "Discretas"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9'
    }

    try:
        session = requests.Session()
        r = session.get(url, headers=headers, timeout=10)
        
        st.write(f"**Estado de Conexión:** {r.status_code}")
        
        # AQUÍ ESTÁ LA CLAVE: ¿Qué página nos devolvieron?
        soup = BeautifulSoup(r.content, 'html.parser')
        titulo = soup.title.string if soup.title else "Sin Título"
        st.info(f"Título de la página recibida: '{titulo}'")
        
        # Intentamos leer tablas a la fuerza con Pandas
        try:
            dfs = pd.read_html(r.text)
            st.success(f"¡Se encontraron {len(dfs)} tablas en la página!")
            if len(dfs) > 0:
                st.write("Vista previa de la primera tabla encontrada:")
                st.dataframe(dfs[0].head())
        except Exception as e:
            st.error(f"Pandas no pudo leer tablas: {e}")
            st.text("Contenido parcial del HTML (para analizar):")
            st.code(r.text[:500]) # Nos muestra los primeros 500 caracteres

    except Exception as e:
        st.error(f"Error fatal: {e}")
