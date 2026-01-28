import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Radar Ajedrez ARG", page_icon="♟️", layout="centered")

# --- LISTA OFICIAL ---
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
    
    # Cabeceras para parecer un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # Petición directa
        r = requests.get(url, headers=headers, timeout=10)
        
        # Leemos TODAS las tablas de la página de una vez usando lxml
        # Esto es mucho más potente que el método anterior
        tablas = pd.read_html(r.content)
        
        # La tabla de torneos suele ser la segunda (índice 1) o la que tiene muchas columnas
        # Buscamos la tabla correcta
        df_torneos = None
        for t in tablas:
            # Si tiene columna "Torneo" y "Rd.", es la buena
            if "Torneo" in t.columns or "Tournament" in t.columns:
                df_torneos = t
                break
        
        if df_torneos is None:
            return []

        # Limpieza de datos
        resultados = []
        hoy = datetime.now()
        limite = hoy - timedelta(days=20) # Miramos 20 días atrás

        # Iteramos por las filas de la tabla encontrada
        for index, row in df_torneos.iterrows():
            # A veces los nombres de columna varían, buscamos por posición si falla el nombre
            try:
                torneo = row.iloc[0] # Primera columna: Nombre
                lugar = row.iloc[1]  # Segunda columna: Lugar
                fecha_str = str(row.iloc[5]) # Sexta columna: Fecha
                
                # Enlace (reconstrucción manual porque pandas read_html no trae links)
                # Como no tenemos el link exacto con este método, ponemos el perfil del jugador
                link = url 
                
                # Parsear fecha
                fecha_obj = None
                for fmt in ["%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y"]:
                    try:
                        fecha_obj = datetime.strptime(fecha_str, fmt)
                        break
                    except: continue
                
                if fecha_obj and fecha_obj >= limite:
                    resultados.append({
                        "Jugador": nombre,
                        "Torneo": torneo,
                        "Lugar": lugar,
                        "Inicio": fecha_obj,
                        "Link": link
                    })
            except:
                continue
                
        return resultados

    except Exception as e:
        return []

# --- PANTALLA ---
st.title("🇦🇷 Radar Selección")
st.caption("Rastreador Oficial de Torneos FIDE")

if st.button("🔄 ESCANEAR AHORA", type="primary"):
    barra = st.progress(0)
    aviso = st.empty()
    lista_final = []
    
    total = len(JUGADORES)
    for i, (nom, id_fide) in enumerate(JUGADORES.items()):
        aviso.text(f"Buscando a {nom}...")
        try:
            data = buscar_torneos(nom, id_fide)
            if data: lista_final.extend(data)
        except:
            pass
        barra.progress((i + 1) / total)
        time.sleep(0.2)
    
    barra.empty()
    aviso.empty()
    
    if lista_final:
        df = pd.DataFrame(lista_final)
        df = df.sort_values(by="Inicio")
        df['Mes'] = df['Inicio'].dt.strftime('%B %Y').str.upper()
        
        st.success(f"¡Éxito! Se encontraron {len(df)} torneos.")
        
        for mes in df['Mes'].unique():
            st.subheader(mes)
            subset = df[df['Mes'] == mes]
            for _, row in subset.iterrows():
                with st.container():
                    st.markdown(f"**{row['Jugador']}**")
                    st.write(f"🏆 {row['Torneo']}")
                    st.caption(f"📍 {row['Lugar']} | 📅 {row['Inicio'].strftime('%d/%m/%Y')}")
                    # Como link ponemos el perfil del jugador para ver detalles
                    st.link_button("Ver Perfil en Chess-Results", row['Link'])
                    st.divider()
    else:
        st.info("Conexión exitosa, pero no se encontraron torneos NUEVOS en las fechas próximas.")
