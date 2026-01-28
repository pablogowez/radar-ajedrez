import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Radar Ajedrez ARG", page_icon="♟️", layout="centered")

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

def obtener_datos(nombre, fide_id):
    # URL de búsqueda por ID
    url = f"https://chess-results.com/SpielerSuche.aspx?lan=2&id={fide_id}"
    
    # CABECERAS "HUMANAS" (El disfraz)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://chess-results.com/',
        'Connection': 'keep-alive'
    }

    try:
        # Usamos Session para mantener cookies como un navegador real
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        # DEBUG: Si la página nos bloquea, mostramos el código de error
        if response.status_code != 200:
            return [{"Error": f"Bloqueo {response.status_code}"}]

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscamos la tabla de resultados
        tabla = soup.find('table', {'class': 'CRs1'})
        if not tabla:
            # Si no hay tabla, puede ser que no haya torneos O que la estructura cambió
            return []

        filas = tabla.find_all('tr')[1:] # Saltamos encabezado
        data = []
        
        # Tomamos los primeros 5 resultados que aparezcan
        for fila in filas[:5]:
            cols = fila.find_all('td')
            if len(cols) > 5:
                torneo = cols[0].text.strip()
                link = "https://chess-results.com/" + cols[0].find('a')['href']
                lugar = cols[1].text.strip()
                fecha_txt = cols[5].text.strip()
                
                data.append({
                    "Jugador": nombre,
                    "Torneo": torneo,
                    "Lugar": lugar,
                    "Fecha": fecha_txt,
                    "Link": link
                })
        return data

    except Exception as e:
        return [{"Error": str(e)}]

# --- PANTALLA ---
st.title("♟️ Radar 3.0: Anti-Bloqueo")

if st.button("🔄 INTENTAR CONEXIÓN", type="primary"):
    barra = st.progress(0)
    resultados = []
    errores = []
    
    total = len(JUGADORES)
    for i, (nom, id_fide) in enumerate(JUGADORES.items()):
        datos = obtener_datos(nom, id_fide)
        
        # Procesamos si vino con error o con datos
        if datos and "Error" in datos[0]:
            errores.append(f"{nom}: {datos[0]['Error']}")
        elif datos:
            resultados.extend(datos)
            
        barra.progress((i + 1) / total)
        time.sleep(0.5) # Pausa más larga para parecer humano
    
    barra.empty()
    
    if resultados:
        df = pd.DataFrame(resultados)
        st.success(f"¡Conexión exitosa! Se encontraron {len(df)} registros.")
        
        for _, row in df.iterrows():
            with st.container():
                st.markdown(f"**{row['Jugador']}**")
                st.write(f"🏆 {row['Torneo']}")
                st.caption(f"📍 {row['Lugar']} | 📅 {row['Fecha']}")
                st.link_button("Ver Torneo", row['Link'])
                st.divider()
    
    elif errores:
        st.error("⚠️ Seguimos bloqueados. Detalles del error:")
        for e in errores:
            st.write(e)
    else:
        st.warning("Conexión OK (Código 200), pero no se encontraron tablas de torneos. Es posible que Chess-Results esté vacío para estos IDs o haya cambiado su diseño.")
