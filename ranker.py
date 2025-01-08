
import streamlit as st
import requests
import pandas as pd
from operator import itemgetter

# ----- CONSTANTES Y VARIABLES GLOBALES -----
API_KEY_TMDB = "TU_API_KEY_TMDB"
BASE_URL_TMDB = "https://api.themoviedb.org/3"
lista_contenido = []

# ----- FUNCIONES AUXILIARES -----
def buscar_pelicula_titulo(titulo):
    """Busca películas o series por título en TMDb."""
    url = f"{BASE_URL_TMDB}/search/movie?api_key={API_KEY_TMDB}&query={titulo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def buscar_plataformas(id_pelicula):
    """Busca plataformas de streaming para una película."""
    url = f"{BASE_URL_TMDB}/movie/{id_pelicula}/watch/providers?api_key={API_KEY_TMDB}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', {}).get('US', {}).get('flatrate', [])
    return []

def calcular_tiempo_total(lista):
    """Calcula el tiempo total para ver las películas no vistas."""
    return sum(item['duracion'] for item in lista if not item['visto'])

# ----- INTERFAZ DE USUARIO -----
st.title("Gestor de Contenido: Películas y Series")
st.sidebar.title("Opciones")

# Opciones del menú
opcion = st.sidebar.selectbox("Selecciona una opción:", ["Gestionar lista", "Buscar información", "Calcular tiempo"])

if opcion == "Gestionar lista":
    st.subheader("Gestionar lista de contenido")
    
    # Agregar contenido
    with st.form("form_agregar_contenido"):
        titulo = st.text_input("Título")
        categoria = st.selectbox("Categoría", ["Comedia", "Acción", "Animación", "Anime"])
        año = st.number_input("Año de emisión", min_value=1900, max_value=2025, step=1)
        duracion = st.number_input("Duración (en minutos)", min_value=1, step=1)
        visto = st.checkbox("¿Ya lo viste?")
        submitted = st.form_submit_button("Agregar a la lista")

        if submitted:
            lista_contenido.append({
                "titulo": titulo,
                "categoria": categoria,
                "año": año,
                "duracion": duracion,
                "visto": visto,
                "prioridad": 0,
                "plataforma": []
            })
            st.success(f"Agregado: {titulo}")

    # Mostrar lista
    if lista_contenido:
        st.write("### Tu lista de contenido")
        df = pd.DataFrame(lista_contenido)
        st.table(df)

if opcion == "Buscar información":
    st.subheader("Buscar información de películas y plataformas")
    
    # Buscar película
    titulo_busqueda = st.text_input("Ingresa el título de la película/serie")
    if st.button("Buscar"):
        resultados = buscar_pelicula_titulo(titulo_busqueda)
        if resultados:
            for item in resultados:
                st.write(f"**{item['title']}** ({item['release_date']}) - Popularidad: {item['popularity']}")
                plataformas = buscar_plataformas(item['id'])
                if plataformas:
                    st.write("Disponible en:")
                    for p in plataformas:
                        st.write(f"- {p['provider_name']}")
                else:
                    st.write("No se encontraron plataformas de streaming.")
        else:
            st.warning("No se encontraron resultados.")

if opcion == "Calcular tiempo":
    st.subheader("Cálculo de tiempo total")
    
    if lista_contenido:
        tiempo_total = calcular_tiempo_total(lista_contenido)
        st.write(f"El tiempo total necesario para ver contenido no visto es: **{tiempo_total} minutos**.")
    else:
        st.warning("La lista está vacía. Por favor, agrega contenido primero.")
