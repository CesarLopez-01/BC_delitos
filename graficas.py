import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import folium
from folium import Element
import ProcesarDatos


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


df=cargarDatos()

df_horas = df[df['HORA DEL HECHO DEL DELITO'].str.strip() != '00:00'].copy()
df_horas['HORA DEL HECHO DEL DELITO'] = pd.to_datetime(df_horas['HORA DEL HECHO DEL DELITO'], format="%H:%M").dt.hour


#******************************************************************************
# -------------------------- LINEA DE TIEMPO DELITOS --------------------------
#******************************************************************************

def graficar_linea_tiempo(df):

    df_time_serie = df.groupby('FECHA DEL HECHO DEL DELITO').size().reset_index(name='delitos')
    df_time_serie.columns = ['fecha', 'delitos']
    
    zoom_x = alt.selection_interval(bind='scales', encodings=['x']) 
    
    chart = alt.Chart(df_time_serie).mark_line(
        color='#f43535',
        strokeWidth=2
    ).encode(
        x=alt.X('fecha:T', title='FECHA'),
        y=alt.Y('delitos:Q', title='CANTIDAD DE DELITOS'),
        tooltip=[
            alt.Tooltip('fecha:T', title='Fecha'),
            alt.Tooltip('delitos:Q', title='Delitos')
        ]
    ).properties(
        width=400,
        height=400
    ).add_params(
        zoom_x
    ).configure_title(
        fontSize=24,
        fontWeight='bold'
    )
    
    return chart

chart = graficar_linea_tiempo(df)


#************************************************************************
# -------------------------- BARRAS DE TIEMPO ---------------------------
#************************************************************************

def graficar_barras(x, data, title, xlabel, ylabel, palette='reds'):
    conteo = data[x].value_counts()

    if x in ['DiaHecho', 'DiaRegistro']:
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        conteo = conteo.reindex(orden_dias).fillna(0)
    else:
        conteo = conteo.sort_index()

    df_conteo = pd.DataFrame({
        x: conteo.index,
        'Cantidad': conteo.values
    })

    if x in ['DiaHecho', 'DiaRegistro']:
        x_axis = alt.X(f'{x}:O', title=xlabel, sort=orden_dias)
    else:
        x_axis = alt.X(f'{x}:O', title=xlabel)

    chart = alt.Chart(df_conteo).mark_bar().encode(
        x=x_axis,
        y=alt.Y('Cantidad:Q', title=ylabel),
        color=alt.Color('Cantidad:Q', scale=alt.Scale(scheme=palette), legend=None),
        tooltip=[x, 'Cantidad']
    ).properties(
        title=title,
        width=700,
        height=400
    ).configure_axis(
        labelFontSize=16,
        titleFontSize=16
    ).configure_axisX(
        labelAngle=0
    ).configure_title(
        fontSize=24,
        fontWeight='bold'
    )

    return chart


#****************************************************************************
# -------------------------- TENDENCIA DE DELITOS ---------------------------
#****************************************************************************

def tendencia_delitos(df_horas):
    delitos = df_horas['CLASIFICACION DEL DELITO'].value_counts().head(5).index
    df_delitos = df_horas[df_horas['CLASIFICACION DEL DELITO'].isin(delitos)]
    df_delitos_hr = df_delitos.groupby(['HORA DEL HECHO DEL DELITO', 'CLASIFICACION DEL DELITO']).size().reset_index(name='CONTEO')


    df_delitos_hr['HORA DEL HECHO DEL DELITO'] = pd.to_numeric(df_delitos_hr['HORA DEL HECHO DEL DELITO'], errors='coerce')

    selection = alt.selection_point(fields=['CLASIFICACION DEL DELITO'])

    # Línea base
    line = alt.Chart(df_delitos_hr).mark_line().encode(
        x=alt.X('HORA DEL HECHO DEL DELITO:O', axis=alt.Axis(title='HORA DEL DÍA', labelAngle=0)),
        y=alt.Y('CONTEO:Q', axis=alt.Axis(title='NÚMERO DE DELITOS')),
        color=alt.Color('CLASIFICACION DEL DELITO:N', scale=alt.Scale(scheme='set1'), title='CLASIFICACIÓN DEL DELITO',
                        legend=alt.Legend(orient='bottom',titleFontSize=13, labelFontSize=12)),  
        tooltip=['CLASIFICACION DEL DELITO:N', 'HORA DEL HECHO DEL DELITO:O', 'CONTEO:Q'],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
    ).add_params(selection)

    # Puntos grandes
    points = alt.Chart(df_delitos_hr).mark_point(size=100, filled=True).encode(
        x='HORA DEL HECHO DEL DELITO:O',
        y='CONTEO:Q',
        color=alt.Color('CLASIFICACION DEL DELITO:N', scale=alt.Scale(scheme='set1')),
        tooltip=['CLASIFICACION DEL DELITO:N', 'HORA DEL HECHO DEL DELITO:O', 'CONTEO:Q'],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
    )

    # Combinar line - points
    final_chart2 = (line + points).properties(
        width=500,
        height=600
    ).configure_title(
        fontSize=24,
        fontWeight='bold'
    )
    
    return final_chart2

final_chart2 = tendencia_delitos(df_horas)


#****************************************************************************
# -------------------------- CLASIFICACION DE DELITOS -----------------------
#****************************************************************************

def clasificacion_delitos(df):
    
    delitos_total = df['CLASIFICACION DEL DELITO'].value_counts().reset_index()
    delitos_total.columns = ['CLASIFICACION DEL DELITO', 'TOTAL']

    orden_clasificaciones = delitos_total.sort_values('TOTAL', ascending=False)['CLASIFICACION DEL DELITO'].tolist()

    # Gráfico de barras
    chart = alt.Chart(delitos_total).mark_bar().encode(
        x=alt.X('TOTAL:Q', title='CANTIDAD DE DELITOS'),
        y=alt.Y('CLASIFICACION DEL DELITO:N',
                sort=orden_clasificaciones,
                title='CLASIFICACIÓN DEL DELITO',
                axis=alt.Axis(labelLimit=300)),
        color=alt.Color('CLASIFICACION DEL DELITO:N',
                        sort=orden_clasificaciones,
                        scale=alt.Scale(scheme='reds', reverse=True),
                        legend=None),
        tooltip=['CLASIFICACION DEL DELITO', 'TOTAL']
    ).properties(
        width=500,
        height=600
    )

    # Texto con etiquetas
    text = alt.Chart(delitos_total).mark_text(
        align='left',
        baseline='middle',
        dx=3,
        fontSize=12
    ).encode(
        x='TOTAL:Q',
        y=alt.Y('CLASIFICACION DEL DELITO:N', sort=orden_clasificaciones),
        text='TOTAL:Q'
    )

    # Combinación final
    final_chart = (chart + text).configure_title(fontSize=24, fontWeight='bold')
    
    return final_chart


#***************************************************************************
# ----------------------------- GRAFICAR MAPA ------------------------------
#***************************************************************************

def graficar_mapa(gdf, columna):
    num_valores = gdf[columna].nunique()
    usar_scheme = num_valores > 1
    scheme = 'fisherjenks' if usar_scheme else None
    k = min(5, num_valores)

    m = gdf.explore(
        column=columna,
        legend=True,
        scheme=scheme,
        k=k if usar_scheme else None,
        name='Localidades',
        style_kwds={'fillOpacity': 0.58},
        tiles=None,
        cmap='Spectral_r',
        popup=True,
        tooltip=False,
        popup_kwds={'max_width': 800}
    )

    # Agregar diferentes tiles
    folium.TileLayer('CartoDB positron', name='Blanco').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Negro').add_to(m)
    folium.TileLayer('OpenStreetMap', name='Default').add_to(m)

    # Control de capas
    folium.LayerControl(collapsed=False).add_to(m)

    return m