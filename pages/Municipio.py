#IMPORTAR LIBRERIAS
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import folium
from streamlit_folium import st_folium 
from ProcesarDatos import procesar_datos, procesar_mapa, MapaEnBlanco
from graficas import (graficar_linea_tiempo, 
                      graficar_barras, 
                      tendencia_delitos, 
                      clasificacion_delitos, 
                      graficar_mapa)


st.title('CRIMENES POR MUNICIPIO')

# -------------------------- LEER DATOS ------------------------
@st.cache_data
def cargarDatos():
    df = pd.read_csv('data/DELITOS_BC.csv')
    return df

@st.cache_data
def cargarMapa():
    gdf = gpd.read_file('data/mapa/BC.shp', engine='pyogrio')
    return gdf

df = cargarDatos()
gdf = cargarMapa()



# -------------------------- SELECCIONAR MUNICIPIO ---------------------------
municipio = st.selectbox(
    'Selecciona un Municipio',
    sorted(df['MUNICIPIO'].unique())
)

df = df[df['MUNICIPIO'] == municipio]



# -------------------------- PROCESAMIENTO DE DATOS ---------------------------
df_horas = df[df['HORA DEL HECHO DEL DELITO'].str.strip() != '00:00'].copy()

df = procesar_datos(df)
df_horas = procesar_datos(df_horas)

años = df['AñoHecho'].unique()



# ----------------------------- SELECCIONAR AÑOS ------------------------------
st.markdown(f'### SELECTOR DE AÑOS')

fecha = st.slider(
    ' ',
    min_value=min(años),
    max_value=max(años),
    value=(min(años), max(años))
)
st.divider()


df = df[(df['AñoHecho'] >= fecha[0]) & (df['AñoHecho'] <= fecha[1])]
df_horas = df_horas[(df_horas['AñoHecho'] >= fecha[0]) & (df_horas['AñoHecho'] <= fecha[1])]

#TABLA DINAMICA PARA OBTENER LA SUMA DE CADA TIPO DE DELITO
tabla_dinamica = pd.pivot_table(
    df,
    index='NO',
    columns='CLASIFICACION DEL DELITO',
    aggfunc='size',
    fill_value=0
).reset_index()

#SUMAR EL RENGLON EXCEPTO LA COLUMNA 'NO'
tabla_dinamica['TOTAL'] = tabla_dinamica.iloc[:, 1:].sum(axis=1)

#BORRAR COLUMNAS PARA CONCATENAR CON TABLA DINAMICA
gdf = MapaEnBlanco(gdf)

columnas = [
    'HOMICIDIO CALIFICADO (FEMINICIDIO)',
    'HOMICIDIO CALIFICADO (VIOLENTO)',
    'LESIONES CULPOSAS',
    'LESIONES DOLOSAS',
    'OTROS ROBOS CON VIOLENCIA',
    'OTROS ROBOS SIN VIOLENCIA',
    'ROBO A BANCO',
    'ROBO A COMERCIO',
    'ROBO A COMERCIO CON VIOLENCIA',
    'ROBO DE VEHICULO',
    'ROBO DE VEHICULO CON VIOLENCIA',
    'ROBO EN CASA HABITACION',
    'ROBO EN CASA HABITACION CON VIOLENCIA',
    'ROBO CON VIOLENCIA (EN VIA PUBLICA)',
    'ROBO SIMPLE (EN VIA PUBLICA)',
    'SECUESTRO',
    'TOTAL'
]

columnas_existentes = ['NO'] + [col for col in columnas if col in tabla_dinamica.columns]

#COMBINAR
gdf = gdf.merge(tabla_dinamica[columnas_existentes], on='NO', how='left')


# -------------------------- LINEA DE TIEMPO DELITOS --------------------------
chart = graficar_linea_tiempo(df)



# -------------------------- DONUT CHART LOCALIDADES ----------------------
localidades_delitos = (
    gdf[['COLONIA', 'TOTAL']]
    .sort_values(by='TOTAL', ascending=False)
    .head(5)
    .reset_index(drop=True)
    .rename(columns={'TOTAL': 'DELITOS'})
)

localidades_delitos['PORCENTAJE'] = (
    localidades_delitos['DELITOS'] / localidades_delitos['DELITOS'].sum() * 100
).round(2)

# GRAFICA DE DONUT
donut_chart = alt.Chart(localidades_delitos).mark_arc(innerRadius=60, outerRadius=120).encode(
    theta=alt.Theta(field='DELITOS', type='quantitative'),
    color=alt.Color(field='COLONIA', type='nominal', legend=alt.Legend(title="Colonia")),
    tooltip=[
        alt.Tooltip('COLONIA:N', title='Colonia'),
        alt.Tooltip('DELITOS:Q', title='Número de Delitos'),
        alt.Tooltip('PORCENTAJE:Q', format=".2f", title='Porcentaje del Total')
    ]
).properties(
    width=400,
    height=400
).configure_title(
    fontSize=20,
    fontWeight='bold'
)


# -------------------------- GRAFICAR LINEA Y DONUT ----------------------
col1, col2 = st.columns(2)

#COLUMNA 1 - LINEA DE TIEMPO
with col1:
    st.markdown(f'### REGISTROS DE DELITOS EN {municipio.upper()}')
    st.altair_chart(chart, use_container_width=True)

#COLUMNA 2 - DONUT
with col2:
    st.markdown(f'### LOCALIDES CON MAS REGISTROS EN {municipio.upper()}')
    st.altair_chart(donut_chart, use_container_width=True)



# -------------------------- GRAFICAR BARRAS DE TIEMPO  -----------------------


st.title('TOTAL DE DELITOS POR TIEMPO')
st.write('')

col1, col2 = st.columns(2)

with col1:
    st.markdown(f'### DELITOS POR AÑO EN {municipio.upper()}')
    chart_años = graficar_barras('AñoHecho', df, '', 'AÑO', 'CANTIDAD DE DELITOS', 'blues')
    st.altair_chart(chart_años, use_container_width=True)
    
    
    st.markdown(f'### DELITOS POR DIA EN {municipio.upper()}')
    chart_dias = graficar_barras('DiaHecho', df, '', 'DIA', 'CANTIDAD DE DELITOS', 'oranges')
    st.altair_chart(chart_dias, use_container_width=True)
    
#COLUMNA 2 - MES Y HORA
with col2:
    st.markdown(f'### DELITOS POR MES EN {municipio.upper()}')
    chart_meses = graficar_barras('MesHecho', df, '', 'MES', 'CANTIDAD DE DELITOS', 'reds')
    st.altair_chart(chart_meses, use_container_width=True)
    
    
    st.markdown(f'### DELITOS POR HORA EN {municipio.upper()}')
    chart_horas = graficar_barras('HORA DEL HECHO DEL DELITO', df_horas, '', 'HORA', 'CANTIDAD DE DELITOS', 'purples')
    st.altair_chart(chart_horas, use_container_width=True)


st.divider()



# -------------------------- TENDENCIA DE DELITOS ---------------------------
final_chart2 = tendencia_delitos(df_horas)


# -------------------------- CLASIFICACION DE DELITOS -----------------------
#USAR FUNCION de graficas
final_chart = clasificacion_delitos(df)



# -------------------------- MOSTRAR EN STREAMLIT ---------------------------
st.title('COMPORTAMIENTO DE LOS DELITOS')
st.write('')

col1, col2 = st.columns(2)

#COLUMNA 1 - TENDENCIA DELITO
with col1:
    st.markdown(f'### TENDENCIA DE DELITOS DURANTE EL DIA EN {municipio.upper()}') 
    st.altair_chart(final_chart2, use_container_width=True)

with col2:
    st.markdown(f'### TOTAL POR CLASIFICACION DE DELITOS EN {municipio.upper()}')
    st.altair_chart(final_chart, use_container_width=True)

st.divider()


#-------------------------- MAPA FOLIUM ---------------------------
st.markdown(f'# MAPA DE DELITOS EN {municipio.upper()}')

st.markdown(f'### DELITO DE ENFASIS')
delitos = ['TOTAL'] + sorted(df['CLASIFICACION DEL DELITO'].unique())
columna = st.selectbox(
    ' ',
    delitos
)

st.write('')

gdf = gdf.drop(columns=['NO', 'CLASIF', 'X', 'Y'])
gdf  = gdf[gdf['MUNICIPIO'] == municipio]
m = graficar_mapa(gdf,columna)
st_folium(m, width=1500, height=850, returned_objects=[])

