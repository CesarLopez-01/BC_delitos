import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd


#***************************************************************
# -------------------------- LEER DATOS ------------------------
#***************************************************************
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

# Carga de datos
df_horas = df[df['HORA DEL HECHO DEL DELITO'].str.strip() != '00:00'].copy()
df_horas['HORA DEL HECHO DEL DELITO'] = pd.to_datetime(df_horas['HORA DEL HECHO DEL DELITO'], format="%H:%M").dt.hour


#******************************************************************************
# -------------------------- PROCESAMIENTO DE DATOS ---------------------------
#******************************************************************************
# Limpieza de datos
def procesar_datos(df):
    
    df['HORA DEL HECHO DEL DELITO'] = pd.to_datetime(df['HORA DEL HECHO DEL DELITO'], format="%H:%M").dt.hour
    df['FECHA DE REGISTRO DEL DELITO'] = pd.to_datetime(df['FECHA DE REGISTRO DEL DELITO'], format="%d/%m/%Y")
    df['FECHA DEL HECHO DEL DELITO'] = pd.to_datetime(df['FECHA DEL HECHO DEL DELITO'], format="%d/%m/%Y")

    # Nuevas columnas de tiempo
    df['AñoRegistro'] = df['FECHA DE REGISTRO DEL DELITO'].dt.year
    df['MesRegistro'] = df['FECHA DE REGISTRO DEL DELITO'].dt.month
    df['SemanaRegistro'] = df['FECHA DE REGISTRO DEL DELITO'].dt.isocalendar().week
    df['DiaRegistro'] = df['FECHA DE REGISTRO DEL DELITO'].dt.day_name()
    df['AñoHecho'] = df['FECHA DEL HECHO DEL DELITO'].dt.year
    df['MesHecho'] = df['FECHA DEL HECHO DEL DELITO'].dt.month
    df['SemanaHecho'] = df['FECHA DEL HECHO DEL DELITO'].dt.isocalendar().week
    df['DiaHecho'] = df['FECHA DEL HECHO DEL DELITO'].dt.day_name()
    
    dias_es = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    df['DiaRegistro'] = df['DiaRegistro'].map(dias_es)
    df['DiaHecho'] = df['DiaHecho'].map(dias_es)


    return df

#*******************************************************************
# -------------------------- MAPA FOLIUM ---------------------------
#*******************************************************************

def procesar_mapa(gdf):

    # Renombrar columnas
    gdf = gdf.rename(columns={
        'HOMICIDIO_': 'HOMICIDIO CALIFICADO (FEMINICIDIO)',
        'HOMICIDIO2': 'HOMICIDIO CALIFICADO (VIOLENTO)',
        'LESIONES_C': 'LESIONES CULPOSAS',
        'LESIONES_D': 'LESIONES DOLOSAS',
        'OTROS_ROBO': 'OTROS ROBOS CON VIOLENCIA',
        'OTROS_ROB2': 'OTROS ROBOS SIN VIOLENCIA',
        'ROBO_A_BAN': 'ROBO A BANCO',
        'ROBO_A_COM': 'ROBO A COMERCIO',
        'ROBO_A_CO2': 'ROBO A COMERCIO CON VIOLENCIA',
        'ROBO_DE_VE': 'ROBO DE VEHICULO',
        'ROBO_DE_V2': 'ROBO DE VEHICULO CON VIOLENCIA',
        'ROBO_EN_CA': 'ROBO EN CASA HABITACION',
        'ROBO_EN_C2': 'ROBO EN CASA HABITACION CON VIOLENCIA',
        'ROBO_CON_V': 'ROBO CON VIOLENCIA (EN VIA PUBLICA)',
        'ROBO_SIMPL': 'ROBO SIMPLE (EN VIA PUBLICA)',
        'SECUESTRO': 'SECUESTRO',
        'TOTAL_GENE': 'TOTAL'
    })

    return gdf



def MapaEnBlanco(gdf):
    gdf = gdf.drop(columns=['HOMICIDIO_',
        'HOMICIDIO2',
        'LESIONES_C',
        'LESIONES_D',
        'OTROS_ROBO',
        'OTROS_ROB2',
        'ROBO_A_BAN',
        'ROBO_A_COM',
        'ROBO_A_CO2',
        'ROBO_DE_VE',
        'ROBO_DE_V2',
        'ROBO_EN_CA',
        'ROBO_EN_C2',
        'ROBO_CON_V',
        'ROBO_SIMPL',
        'SECUESTRO',
        'TOTAL_GENE'
        ])
    return gdf


