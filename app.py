import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Radar Final", layout="centered")

# Probamos con un solo nombre para calibrar
JUGADOR_TEST = "Faustino Oro"

st.title("🎯 Radar: Protocolo de Cortesía")
st.info("Intentando conectar simulando una visita humana completa (Home -> Búsqueda).")

if st.button("INICIAR PROTOCOLO", type="primary"):
    
    # 1. Configuración de camuflaje
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    session = requests.Session()
    session.headers.update(headers)

    try:
        # 2. PASO CLAVE: Visitamos la Home primero para obtener Cookies
        st.write("1️⃣ Entrando a la Home para obtener credenciales...")
        home = session.get("https://chess-results.com/?lan=2", timeout=10)
        st.write(f"   *Status Home:* {home.status_code}")
        
        # Pausa dramática para parecer humano
        time.sleep(1.5)
        
        # 3. Hacemos la búsqueda usando la MISMA sesión
        st.write(f"2️⃣ Buscando a **{JUGADOR_TEST}**...")
        url_busqueda = f"https://chess-results.com/SpielerSuche.aspx?lan=2&name={JUGADOR_TEST}"
        response = session.get(url_busqueda, timeout=10)
        
        # 4. Análisis de resultados
        dfs = pd.read_html(response.content)
        st.success(f"✅ Se encontraron {len(dfs)} tablas en la respuesta.")
        
        # Mostramos TODAS las tablas (resumidas) para encontrar la buena
        for i, tabla in enumerate(dfs):
            with st.expander(f"📂 Tabla #{i} (Filas: {len(tabla)}) - Clic para ver"):
                st.dataframe(tabla.head(3)) # Mostramos solo las primeras 3 filas
                
                # Chequeo inteligente: ¿Parece una lista de torneos?
                columnas_str = " ".join([str(c) for c in tabla.columns]).lower()
                datos_str = str(tabla.iloc[0].values).lower() if len(tabla) > 0 else ""
                
                if "torne" in columnas_str or "tourn" in columnas_str or "oro" in datos_str:
                    st.toast(f"¡La Tabla #{i} parece ser la correcta!", icon="🎉")
                    st.write("### 🔥 ¡ESTA ES LA TABLA DE RESULTADOS!")
                    st.dataframe(tabla)

    except Exception as e:
        st.error(f"Error: {e}")
