#IMPORTAR LIBRERIAS
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import folium
from streamlit_folium import st_folium 
from ProcesarDatos import procesar_datos, procesar_mapa,  MapaEnBlanco
from graficas import (graficar_linea_tiempo, 
                      graficar_barras, 
                      tendencia_delitos, 
                      clasificacion_delitos, 
                      graficar_mapa)


#TITULO
st.title('CRIMENES POR LOCALIDAD')


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


#JOIN o BUSCARV
df = df.merge(
    gdf[['NO', 'COLONIA','POBLACION']],
    on='NO',                 
    how='left'
)


# ----------------------- SELECCIONAR MUNICIPIO Y LOCALIDAD--------------------
municipio = st.selectbox(
    'Selecciona un Municipio',
    sorted(df['MUNICIPIO'].unique())
)


gdf_municipio = gdf[gdf['MUNICIPIO'] == municipio]
localidades_validas = gdf_municipio[gdf_municipio['TOTAL_GENE'] > 0]['COLONIA'].dropna().unique()


localidad = st.selectbox(
    'Selecciona una Localidad',
    sorted(localidades_validas)
)


df = df[(df['MUNICIPIO'] == municipio) & (df['COLONIA'] == localidad)]



# -------------------------- PROCESAMIENTO DE DATOS ---------------------------
df_horas = df[df['HORA DEL HECHO DEL DELITO'].str.strip() != '00:00'].copy()

df = procesar_datos(df)
df_horas = procesar_datos(df_horas)

años = df['AñoHecho'].unique()


# ----------------------------- SELECCIONAR AÑOS ------------------------------
st.markdown(f'### SELECTOR DE AÑOS')


if len(años) > 1:
    fecha = st.slider(
        ' ',
        min_value=min(años),
        max_value=max(años),
        value=(min(años), max(años))
    )

    df = df[(df['AñoHecho'] >= fecha[0]) & (df['AñoHecho'] <= fecha[1])]
    df_horas = df_horas[(df_horas['AñoHecho'] >= fecha[0]) & (df_horas['AñoHecho'] <= fecha[1])]
    

else:
    st.info(f"SOLO HAY DATOS DEL AÑO {años[0]}")
    fecha = (años[0], años[0])

    df = df[df['AñoHecho'] == años[0]]
    df_horas = df_horas[df_horas['AñoHecho'] == años[0]]



st.divider()


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



# -------------------------- GRAFICAR BARRAS DE TIEMPO  -----------------------
st.title('TOTAL DE DELITOS POR TIEMPO')
st.write('')

col1, col2 = st.columns(2)

#COLUMNA 1 - AÑO Y DIA
with col1:
    st.markdown(f'### DELITOS POR AÑO EN {localidad.upper()}')
    chart_años = graficar_barras('AñoHecho', df, '', 'AÑO', 'CANTIDAD DE DELITOS', 'blues')
    st.altair_chart(chart_años, use_container_width=True)
    
    
    st.markdown(f'### DELITOS POR DIA EN {localidad.upper()}')
    chart_dias = graficar_barras('DiaHecho', df, '', 'DIA', 'CANTIDAD DE DELITOS', 'oranges')
    st.altair_chart(chart_dias, use_container_width=True)
    
#COLUMNA 2 - MES Y HORA
with col2:
    st.markdown(f'### DELITOS POR MES EN {localidad.upper()}')
    chart_meses = graficar_barras('MesHecho', df, '', 'MES', 'CANTIDAD DE DELITOS', 'reds')
    st.altair_chart(chart_meses, use_container_width=True)
    
    
    st.markdown(f'### DELITOS POR HORA EN {localidad.upper()}')
    chart_horas = graficar_barras('HORA DEL HECHO DEL DELITO', df_horas, '', 'HORA', 'CANTIDAD DE DELITOS', 'purples')
    st.altair_chart(chart_horas, use_container_width=True)

st.divider()



# -------------------------- TENDENCIA DE DELITOS ---------------------------
#USAR FUNCION DE graficas
final_chart2 = tendencia_delitos(df_horas)


# ------------------------- CLASIFICACION DE DELITOS -----------------------
#USAR FUNCION de graficas
final_chart = clasificacion_delitos(df)



# -------------------------- MOSTRAR EN STREAMLIT ---------------------------
st.title('COMPORTAMIENTO DE LOS DELITOS')

st.write('')


col1, col2 = st.columns(2)

#COLUMNA 1 - TENDENCIA DELITOS
with col1:
    st.markdown(f'### TENDENCIA DE DELITOS DURANTE EL DIA EN {localidad.upper()}')
    st.altair_chart(final_chart2, use_container_width=True)

#COLUMNA 2 - CALSIFICACION DELITOS
with col2:
    st.markdown(f'### TOTAL POR CLASIFICACION DE DELITOS EN {localidad.upper()}')
    st.altair_chart(final_chart, use_container_width=True)

st.divider()


# -------------------------- MAPA FOLIUM ---------------------------
st.markdown(f'# MAPA DE DELITOS EN {localidad.upper()}')

st.write('')

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

#COMBINAR SOLO SI EXISTE LA COLUMNA (ALGUN TIPO DE DELITO) EN ESE AÑO
columnas_existentes = ['NO'] + [col for col in columnas if col in tabla_dinamica.columns]

#COMBINAR
gdf = gdf.merge(tabla_dinamica[columnas_existentes], on='NO', how='left')

gdf = gdf.drop(columns=['NO', 'CLASIF', 'X', 'Y'])

gdf  = gdf[gdf['MUNICIPIO'] == municipio]
gdf  = gdf[gdf['COLONIA'] == localidad]

m = gdf.explore(tiles=None, name='Delitos')

folium.TileLayer('CartoDB positron', name='Blanco').add_to(m)
folium.TileLayer('CartoDB dark_matter', name='Negro').add_to(m)
folium.TileLayer('OpenStreetMap', name='Default').add_to(m)
folium.LayerControl(collapsed=False).add_to(m)
    
    
st_folium(m, width=1000, height=800, returned_objects=[])
