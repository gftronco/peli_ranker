
import streamlit as st
import requests
import pandas as pd

# ----- FUNCIONES AUXILIARES -----
def buscar_top_10(genero, tipo, anio):
    """Busca las 10 mejores películas o series según género, tipo y año usando TMDb API."""
    API_KEY_TMDB = "TU_API_KEY_TMDB"
    BASE_URL_TMDB = "https://api.themoviedb.org/3"

    genero_id = {
        "Comedia": 35,
        "Acción": 28,
        "Animación": 16,
        "Anime": 16,  # Consideramos animación para anime
    }.get(genero, None)

    if not genero_id:
        return []

    tipo_endpoint = "movie" if tipo == "Películas" else "tv"
    url = f"{BASE_URL_TMDB}/discover/{tipo_endpoint}?api_key={API_KEY_TMDB}&with_genres={genero_id}&primary_release_year={anio}&sort_by=popularity.desc"
    response = requests.get(url)

    if response.status_code == 200:
        resultados = response.json().get('results', [])
        top_10 = resultados[:10]
        return [
            {
                "titulo": item['title'] if tipo == "Películas" else item['name'],
                "popularidad": item['popularity'],
                "episodios": item.get('number_of_episodes', 1),  # Default to 1 for movies
                "duracion": item.get('runtime', 120) if tipo == "Películas" else item.get('episode_run_time', [30])[0],
                "id": item['id']
            }
            for item in top_10
        ]
    return []

def calcular_tiempo_total_y_orden(lista):
    """Ordena la lista por popularidad y calcula el tiempo total."""
    ordenada = sorted(lista, key=lambda x: x['popularidad'], reverse=True)
    tiempo_total = sum(item['duracion'] * (item['episodios'] if 'episodios' in item else 1) for item in ordenada)
    return ordenada, tiempo_total

# ----- INTERFAZ DE USUARIO -----
st.title("Recomendador de Películas y Series")
st.sidebar.title("Opciones")

# Selección de tipo, género y año
tipo = st.sidebar.radio("¿Qué deseas ver?", ["Películas", "Series"])
genero = st.sidebar.selectbox("Selecciona el género", ["Comedia", "Acción", "Animación", "Anime"])
anio = st.sidebar.number_input("Selecciona el año", min_value=1900, max_value=2025, step=1, value=2023)

# Buscar las 10 mejores películas o series
if st.sidebar.button("Buscar Top 10"):
    top_10 = buscar_top_10(genero, tipo, anio)

    if top_10:
        st.write(f"### Top 10 de {tipo} de {genero} en {anio}")
        seleccionados = []
        for item in top_10:
            if st.checkbox(f"{item['titulo']} (Popularidad: {item['popularidad']})", key=item['id']):
                seleccionados.append(item)

        if seleccionados:
            ordenada, tiempo_total = calcular_tiempo_total_y_orden(seleccionados)

            st.write("### Orden recomendado para ver:")
            for idx, item in enumerate(ordenada, 1):
                total_duracion = item['duracion'] * (item['episodios'] if 'episodios' in item else 1)
                st.write(f"{idx}. {item['titulo']} - Duración total: {total_duracion} minutos")

            st.write(f"### Tiempo total necesario: {tiempo_total} minutos")
        else:
            st.warning("Selecciona al menos una película o serie.")
    else:
        st.error("No se encontraron resultados. Intenta con otro género o año.")
