import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from prophet import Prophet

st.title('PRONOSTICO DE CRIMENES EN BAJA CALIFORNIA')


@st.cache_data
def cargarDatos():
    df = pd.read_csv('data/DELITOS_BC.csv')
    return df

df = cargarDatos()
df['FECHA DEL HECHO DEL DELITO'] = pd.to_datetime(df['FECHA DEL HECHO DEL DELITO'], format="%d/%m/%Y")


freq= {
    'Diaria': 'D',
    'Semanal': 'W',
    'Mensual': 'ME',
}


st.markdown(f'### Escoge la frecuencia de la serie de Tiempo')
frecuencia_select = st.selectbox(
    ' ',
    ('Diaria','Semanal','Mensual'), index = 1
)

frecuencia = freq[frecuencia_select]

serie = df.groupby(pd.Grouper(key='FECHA DEL HECHO DEL DELITO', freq=frecuencia)).size().reset_index(name='delitos')
serie_mun = df.groupby(['MUNICIPIO',pd.Grouper(key='FECHA DEL HECHO DEL DELITO', freq=frecuencia)]).size().reset_index(name='delitos')

df_prophet = serie.copy()
df_prophet.rename(columns={'FECHA DEL HECHO DEL DELITO':'ds','delitos':'y'}, inplace=True)


chart = alt.Chart(serie).mark_line().encode(
    x='FECHA DEL HECHO DEL DELITO:T',
    y='delitos:Q',
    tooltip=['FECHA DEL HECHO DEL DELITO:T', 'delitos:Q']
).properties(
    title='Serie de Delitos',
    width=800,
    height=400
).interactive()
st.altair_chart(chart, use_container_width=True)


years = st.slider('Indica la cantidad de años a predecir:', min_value=1, max_value=25, value=5)


if st.button("GENERARA PRONOSTICO"):
    with st.spinner("Generando pronósticos, por favor espera..."):
        st.subheader("Pronostico del Estado")
        # Modelo general
        m = Prophet()
        m.fit(df_prophet)

        future = m.make_future_dataframe(periods=93 + 365*years, freq='D')
        forecast = m.predict(future)

        fig1 = m.plot(forecast)
        fig1.set_size_inches(18, 4)
        ax = fig1.gca()
        inicio_forecast = df_prophet['ds'].max()
        ax.set_title('PRONOSTICO DE DELITOS EN BAJA CALIFORNIA', fontsize=18)
        ax.axvline(x=inicio_forecast, color='black', linestyle='--', label='Inicio del pronóstico')
        ax.legend()
        st.pyplot(fig1)

        # -----------------------------------
        # Pronósticos por municipio
        # -----------------------------------
        st.subheader("Pronostico por Municipio")
        
        modelos = {}
        predicciones = {}

        municipios = serie_mun['MUNICIPIO'].unique()
        col1, col2 = st.columns(2)

        for i, municipio in enumerate(municipios):
            df_mun = serie_mun[serie_mun['MUNICIPIO'] == municipio][['FECHA DEL HECHO DEL DELITO', 'delitos']]
            df_mun = df_mun.rename(columns={'FECHA DEL HECHO DEL DELITO': 'ds', 'delitos': 'y'})

            m_mun = Prophet()
            m_mun.fit(df_mun)

            future_mun = m_mun.make_future_dataframe(periods=93 + 365*years, freq='D')
            forecast_mun = m_mun.predict(future_mun)

            modelos[municipio] = m_mun
            predicciones[municipio] = forecast_mun

            fig = m_mun.plot(forecast_mun)
            fig.set_size_inches(8, 3)
            ax = fig.gca()
            ax.set_title(f"{municipio}", fontsize=12)
            ax.axvline(x=inicio_forecast, color='black', linestyle='--', label='Inicio del pronostico')
            ax.legend()

            if i % 2 == 0:
                col1.pyplot(fig)
            else:
                col2.pyplot(fig)

    st.success("Pronósticos generados con exito")
    st.markdown("---")

    st.markdown("""
    ### 💼 Una aplicacion como esta para tu negocio

    ¿Quieres implementar modelos de inteligencia aritificial para predecir **ventas**, **produccion**, **inventario** o realizar otras actividades?  
    Contactame para desarrollar soluciones personalizadas basadas especificamente en tu negocio.
    """)

    st.markdown("""
    Manda un correo a lopezrca01@gmail.com 
    """)









