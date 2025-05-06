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


st.title('CRIMENES EN BAJA CALIFORNIA')


st.markdown("""
Los datos fueron obtenidos del portal oficial de la [Secretaría de Seguridad Ciudadana de Baja California](https://www.seguridadbc.gob.mx/contenidos/estadisticas5.php).  
Esta fuente incluye una selección de delitos clasificados como de **alto y mediano impacto**, los cuales afectan la vida,
integridad y patrimonio de las personas.  
La información comprende el periodo de **2014 a 2024**.

- *San Quintín solo cuenta con datos del 2021 al 2024.*  
- *San Felipe solo cuenta con datos del 2022 al 2024.*
""")

st.write('')


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
csv = df.drop(columns=['NO', 'CLASIFICACION','X','Y'], errors='ignore')
csv = csv.to_csv(index=False).encode('utf-8')
gdf = cargarMapa()


# -------------------------- PROCESAMIENTO DE DATOS ---------------------------
df_horas = df[df['HORA DEL HECHO DEL DELITO'].str.strip() != '00:00'].copy()

df = procesar_datos(df)
df_horas = procesar_datos(df_horas)

años = df['Año'].unique()


# ----------------------------- SELECCIONAR AÑOS ------------------------------
st.markdown(f'### SELECTOR DE AÑOS')

fecha = st.slider(
    ' ',
    min_value=min(años),
    max_value=max(años),
    value=(min(años), max(años))
)

st.download_button(
    label="DESCARGAR DATOS",
    data=csv,
    file_name='DELITOS_BAJA_CALIFORNIA.csv',
    mime='text/csv'
)

st.divider()
#----------------------------------------------------------------------------------

#FILTRAR EL DATAFRAME SEGUN AÑOS SELECCIONADOS
df = df[(df['Año'] >= fecha[0]) & (df['Año'] <= fecha[1])]
df_horas = df_horas[(df_horas['Año'] >= fecha[0]) & (df_horas['Año'] <= fecha[1])]


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


# -------------------------- TARJETAS DE MUNICIPIOS ---------------------------
delitos_por_municipio = df['MUNICIPIO'].value_counts()

st.title("DELITOS POR MUNICIPIO")

st.write("")

cols = st.columns(len(delitos_por_municipio))

for idx, (col, (municipio, total)) in enumerate(zip(cols, delitos_por_municipio.items())):
    with col:
        border_style = "border-right: 1px solid #ccc;" if idx < len(delitos_por_municipio) - 1 else ""
        
        st.markdown(
            f"""
            <div style="{border_style} padding: 5px; text-align: center; height: 100%;">
                <h3 style="margin-bottom: 5px;">{municipio}</h3>
                <h2 style="color: #f43535;">{total:,}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
st.write("")
st.write("")
st.write("")


# -------------------------- LINEA DE TIEMPO DELITOS --------------------------
chart = graficar_linea_tiempo(df)


# -------------------------- DONUT CHART MUNICIPIO ----------------------
delitos_municipio = df['MUNICIPIO'].value_counts().reset_index()
delitos_municipio.columns = ['municipio', 'total']

delitos_municipio['porcentaje'] = (delitos_municipio['total'] / delitos_municipio['total'].sum()) * 100

donut_chart = alt.Chart(delitos_municipio).mark_arc(innerRadius=70, outerRadius=120).encode(
    theta=alt.Theta(field="total", type="quantitative"),
    color=alt.Color(field="municipio", type="nominal", legend=alt.Legend(title="Municipio")),
    tooltip=[
        alt.Tooltip('municipio:N', title='Municipio'),
        alt.Tooltip('total:Q', title='Delitos'),
        alt.Tooltip('porcentaje:Q', format=".2f", title='Porcentaje del Total')
    ]
).properties(
    width=400,
    height=400
).configure_title(
    fontSize=24,
    fontWeight='bold'
)


# -------------------------- MOSTRAR EN DOS COLUMNAS --------------------------
col1, col2 = st.columns(2)

#COLUMNA 1 - LINEA DE TIEMPO
with col1:
    st.markdown(f'### REGISTROS DE DELITOS EN BAJA CALIFORNIA')
    st.altair_chart(chart, use_container_width=True)

#COLUMNA 2 - DONUT
with col2:
    st.markdown(f'### MUNICIPIOS CON MAS REGISTROS EN BAJA CALIFORNA')
    st.altair_chart(donut_chart, use_container_width=True)

st.divider()


# -------------------------- GRAFICAR BARRAS DE TIEMPO  -----------------------
#TITULO
st.title('TOTAL DE DELITOS POR TIEMPO')

st.write('')

col1, col2 = st.columns(2)

#COLUMNA 1 - AÑO Y DIA
with col1:
    st.markdown(f'### DELITOS POR AÑO EN BAJA CALIFORNIA')
    chart_años = graficar_barras('Año', df, '', 'AÑO', 'CANTIDAD DE DELITOS', 'blues')
    st.altair_chart(chart_años, use_container_width=True)
    
    
    st.markdown(f'### DELITOS POR DIA EN BAJA CALIFORNIA')
    chart_dias = graficar_barras('Dia', df, '', 'DIA', 'CANTIDAD DE DELITOS', 'oranges')
    st.altair_chart(chart_dias, use_container_width=True)
    
#COLUMNA 2 - MES Y HORA
with col2:
    st.markdown(f'### DELITOS POR MES EN BAJA CALIFORNIA')
    chart_meses = graficar_barras('Mes', df, '', 'MES', 'CANTIDAD DE DELITOS', 'reds')
    st.altair_chart(chart_meses, use_container_width=True)
    
    
    st.markdown(f'### DELITOS POR HORA EN BAJA CALIFORNIA')
    chart_horas = graficar_barras('HORA DEL HECHO DEL DELITO', df_horas, '', 'HORA', 'CANTIDAD DE DELITOS', 'purples')
    st.altair_chart(chart_horas, use_container_width=True)


st.divider()


# -------------------------- TENDENCIA DE DELITOS ---------------------------
final_chart2 = tendencia_delitos(df_horas)


# -------------------------- CLASIFICACION DE DELITOS -----------------------
final_chart = clasificacion_delitos(df)


# ----------------- MOSTRAR TENDENCIA Y CLASIFICACION EN STREAMLIT ----------
st.title('COMPORTAMIENTO DE LOS DELITOS')
st.write('')

col1, col2 = st.columns(2)

#COLUMNA 1 - TENDENCIA DELITOS
with col1:
    st.markdown(f'### TENDENCIA DE LOS DELITOS DURANTE EL DIA EN BC')
    st.altair_chart(final_chart2, use_container_width=True)

#COLUMNA 2 - CALSIFICACION DELITOS
with col2:
    st.markdown(f'### TOTAL POR CLASIFICACION DEL DELITO EN BC')
    st.altair_chart(final_chart, use_container_width=True)

st.divider()

# -------------------------- MAPA FOLIUM ---------------------------
st.title('MAPA DE DELITOS EN BAJA CALIFORNIA')

st.write('')



st.markdown(f'### DELITO DE ENFASIS')
delitos = ['TOTAL'] + sorted(df['CLASIFICACION DEL DELITO'].unique())
columna = st.selectbox(
    ' ',
    delitos
)


gdf = gdf.merge(tabla_dinamica[columnas_existentes], on='NO', how='left')
gdf = gdf.drop(columns=['NO', 'CLASIF', 'X', 'Y'])
m = graficar_mapa(gdf,columna)
st_folium(m, width=1500, height=850, returned_objects=[])

