import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Radar Ajedrez ARG", page_icon="🇦🇷", layout="centered")

# --- LISTA DE JUGADORES ---
JUGADORES = {
    "Faustino Oro": "20000197",
    "Ilán Schnaider": "169013",
    "Joaquín Fiorito": "180173",
    "Francisco Fiorito": "180165",
    "Sandro Mareco": "112275",
    "Fernando Peralta": "105309",
    "Diego Flores": "108049",
    "Candela Francisco": "160911",
    "Ernestina Adam": "165883"
}

def buscar_historial(nombre, fide_id):
    # Buscamos TODO, sin filtrar por fecha al principio
    url = f"https://chess-results.com/SpielerSuche.aspx?lan=2&id={fide_id}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        tabla = soup.find('table', {'class': 'CRs1'})
        if not tabla: return []

        filas = tabla.find_all('tr')[1:]
        data = []
        
        # Tomamos hasta los primeros 10 resultados que aparezcan (suelen ser los más nuevos)
        for fila in filas[:10]:
            cols = fila.find_all('td')
            if len(cols) > 5:
                torneo = cols[0].text.strip()
                link = "https://chess-results.com/" + cols[0].find('a')['href']
                lugar = cols[1].text.strip()
                fecha_texto = cols[5].text.strip() # Guardamos el texto original por si falla la fecha
                
                # Intentamos convertir fecha, si falla, guardamos None
                fecha_obj = None
                for fmt in ["%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y"]:
                    try:
                        fecha_obj = datetime.strptime(fecha_texto, fmt)
                        break
                    except: continue
                
                data.append({
                    "Jugador": nombre,
                    "Torneo": torneo,
                    "Lugar": lugar,
                    "FechaTexto": fecha_texto, # Mostramos esto si no hay fecha real
                    "FechaObj": fecha_obj,
                    "Link": link
                })
        return data
    except Exception as e:
        return []

# --- PANTALLA PRINCIPAL ---
st.title("♟️ Radar: Modo Diagnóstico")
st.warning("Mostrando los últimos torneos detectados (incluyendo recientes/pasados) para verificar conexión.")

if st.button("🔄 ESCANEAR HISTORIAL", type="primary"):
    barra = st.progress(0)
    resultados = []
    
    total = len(JUGADORES)
    for i, (nom, id_fide) in enumerate(JUGADORES.items()):
        found = buscar_historial(nom, id_fide)
        if found: resultados.extend(found)
        barra.progress((i + 1) / total)
        time.sleep(0.1)
    
    barra.empty()
    
    if resultados:
        df = pd.DataFrame(resultados)
        
        # Ordenamos: Los que tienen fecha futura primero, luego los recientes
        # (Truco: Rellenamos fechas vacías con fecha muy vieja para que vayan al fondo)
        df['SortDate'] = df['FechaObj'].fillna(datetime(2000, 1, 1))
        df = df.sort_values(by='SortDate', ascending=False)
        
        st.success(f"Se encontraron {len(df)} registros en total.")
        
        for _, row in df.iterrows():
            with st.container():
                # Icono según fecha
                icono = "✅" # Pasado
                hoy = datetime.now()
                if row['FechaObj'] and row['FechaObj'] >= hoy:
                    icono = "🔜 FUTURO"
                elif row['FechaObj'] and (hoy - row['FechaObj']).days < 30:
                    icono = "🔥 RECIENTE"
                
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{row['Jugador']}**")
                c1.caption(f"{icono} | {row['Torneo']}")
                c1.text(f"📍 {row['Lugar']} | 📅 {row['FechaTexto']}")
                c2.link_button("Abrir", row['Link'])
                st.divider()
    else:
        st.error("⚠️ Error crítico: No se encontró NADA. Chess-Results podría estar bloqueando o cambió su web.")
