import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Radar Ajedrez ARG", page_icon="♟️", layout="centered")

# --- LISTA DE JUGADORES ---
# Usamos el nombre exacto para la búsqueda
JUGADORES = [
    "Faustino Oro",
    "Ilan Schnaider",
    "Joaquin Fiorito",
    "Francisco Fiorito",
    "Sandro Mareco",
    "Fernando Peralta",
    "Diego Flores",
    "Candela Francisco",
    "Ernestina Adam"
]

def buscar_torneos(nombre):
    # TRUCO: Buscamos por nombre para que salga la lista de torneos
    url = f"https://chess-results.com/SpielerSuche.aspx?lan=2&name={nombre}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        # Leemos todas las tablas
        dfs = pd.read_html(r.content)
        
        # Buscamos la tabla que tenga resultados
        df_torneos = None
        for t in dfs:
            # La tabla correcta suele tener estas columnas
            if "Torneo" in t.columns or "Tournament" in t.columns:
                df_torneos = t
                break
        
        if df_torneos is None:
            return []

        resultados = []
        
        # Procesamos la tabla
        for index, row in df_torneos.iterrows():
            try:
                # Intentamos extraer datos clave por posición
                # Col 0: Nombre del Torneo
                # Col 5: Fecha (aprox)
                torneo = row.iloc[0]
                lugar = row.iloc[1]
                fecha_raw = str(row.iloc[5])
                
                # Link del jugador (Chess-Results no da el link directo fácil en esta vista, usamos el de búsqueda)
                link = url 
                
                # Guardamos TODO (sin filtrar fecha por ahora para ver si funciona)
                resultados.append({
                    "Jugador": nombre,
                    "Torneo": torneo,
                    "Lugar": lugar,
                    "FechaTexto": fecha_raw,
                    "Link": link
                })
            except:
                continue
                
        # Devolvemos solo los primeros 5 para no saturar la pantalla
        return resultados[:5]

    except Exception as e:
        return []

# --- PANTALLA ---
st.title("🇦🇷 Radar: Lista Completa")
st.warning("Modo 'Ver Todo': Mostrando los últimos 5 torneos detectados de cualquier fecha.")

if st.button("🔄 ESCANEAR AHORA", type="primary"):
    barra = st.progress(0)
    lista_final = []
    
    total = len(JUGADORES)
    for i, nombre in enumerate(JUGADORES):
        data = buscar_torneos(nombre)
        if data: lista_final.extend(data)
        barra.progress((i + 1) / total)
        time.sleep(0.2)
    
    barra.empty()
    
    if lista_final:
        st.success(f"¡Se encontraron {len(lista_final)} registros!")
        
        for item in lista_final:
            with st.container():
                st.markdown(f"**{item['Jugador']}**")
                st.write(f"🏆 {item['Torneo']}")
                st.caption(f"📍 {item['Lugar']} | 📅 {item['FechaTexto']}")
                st.divider()
    else:
        st.error("Sigue sin aparecer nada. Posible cambio de estructura en la web.")
