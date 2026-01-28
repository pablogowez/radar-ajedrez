import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Radar Ajedrez ARG", page_icon="♟️", layout="mobile")

# --- LISTA OFICIAL (IDs verificados) ---
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

def buscar_torneos(nombre, fide_id):
    url = f"https://chess-results.com/SpielerSuche.aspx?lan=2&id={fide_id}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        tabla = soup.find('table', {'class': 'CRs1'})
        if not tabla: return []

        filas = tabla.find_all('tr')[1:]
        data = []
        hoy = datetime.now()
        # Buscamos torneos desde hace 20 días (activos) hasta el futuro infinito
        limite = hoy - timedelta(days=20)

        for fila in filas:
            cols = fila.find_all('td')
            if len(cols) > 5:
                torneo = cols[0].text.strip()
                link = "https://chess-results.com/" + cols[0].find('a')['href']
                lugar = cols[1].text.strip()
                fecha_str = cols[5].text.strip()
                
                fecha_obj = None
                for fmt in ["%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y"]:
                    try:
                        fecha_obj = datetime.strptime(fecha_str, fmt)
                        break
                    except: continue
                
                if fecha_obj and fecha_obj >= limite:
                    data.append({
                        "Jugador": nombre,
                        "Torneo": torneo,
                        "Lugar": lugar,
                        "Inicio": fecha_obj,
                        "Link": link
                    })
        return data
    except: return []

# --- PANTALLA ---
st.title("♟️ Radar Selección ARG")
st.write("Rastreador de torneos oficiales en Chess-Results.")

if st.button("🔄 ESCANEAR AHORA", type="primary"):
    barra = st.progress(0)
    aviso = st.empty()
    resultados = []
    
    total = len(JUGADORES)
    for i, (nom, id_fide) in enumerate(JUGADORES.items()):
        aviso.text(f"Buscando a {nom}...")
        found = buscar_torneos(nom, id_fide)
        if found: resultados.extend(found)
        barra.progress((i + 1) / total)
        time.sleep(0.1)
    
    barra.empty()
    aviso.empty()
    
    if resultados:
        df = pd.DataFrame(resultados)
        df = df.sort_values(by="Inicio")
        df['Mes'] = df['Inicio'].dt.strftime('%B %Y').str.upper()
        
        st.success(f"¡Encontré {len(df)} torneos!")
        
        for mes in df['Mes'].unique():
            st.header(mes)
            subset = df[df['Mes'] == mes]
            for _, row in subset.iterrows():
                st.markdown(f"**{row['Jugador']}**")
                st.write(f"🏆 {row['Torneo']}")
                st.write(f"📍 {row['Lugar']} | 📅 {row['Inicio'].strftime('%d/%m')}")
                st.link_button("Ver Torneo", row['Link'])
                st.divider()
    else:
        st.info("No hay torneos nuevos cargados por el momento.")
