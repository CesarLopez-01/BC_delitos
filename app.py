import streamlit as st 

#streamlit run app.py

st.set_page_config(
    page_title='BC Crimenes',
    layout="wide",
    page_icon=('images/BC_crimen.png')
)


# --- PAGE SETUP ---

Estado = st.Page(
    page='pages/Estado.py',
    title='Crimen Nivel Estado',
    icon=':material/bar_chart:',
    default=True,
    )

Municipio = st.Page(
    page='pages/Municipio.py',
    title='Crimen Nivel Municipio',
    icon=':material/bar_chart:',
    )

Localidad = st.Page(
    page='pages/Localidad.py',
    title='Crimen Nivel Localidad',
    icon=':material/bar_chart:',
    )


Modelo = st.Page(
    page='pages/Modelo.py',
    title='Modelo de Predicciones',
    icon=':material/data_saver_off:',
    )


Este_sitio = st.Page(
    page='pages/Este_sitio.py',
    title='Informacion del sitio',
    icon=':material/info:',
    )

# --- NAVIGATION SETUP [WITH SECTIONS] ---

pg = st.navigation(
    {
        'Estadisticas':[Estado, Municipio, Localidad],
        'Pronosticos':[Modelo],
        'info':[Este_sitio]
    }
)


# --- SHARED ON ALL PAGES ---

st.sidebar.image('images/BC_crimen.png', use_container_width=True)
st.sidebar.text('💼 Hecho por Cesar Lopez')

# --- RUN NAVIGATION ---
pg.run()




