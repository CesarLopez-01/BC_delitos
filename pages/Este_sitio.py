import streamlit as st 

st.markdown("""
### 💼 Una aplicacion como esta para tu negocio

¿Quieres implementar modelos de inteligencia aritificial para predecir **ventas**, **produccion**, **inventario** o realizar otras actividades?  
Contactame para desarrollar soluciones personalizadas basadas especificamente en tu negocio.
""")

st.markdown("""
Manda un correo a lopezrca01@gmail.com 
""")

st.markdown("---")

st.markdown("""
### 🗃️ Fuente de datos

Los datos fueron obtenidos del portal oficial de la [Secretaría de Seguridad Ciudadana de Baja California](https://www.seguridadbc.gob.mx/contenidos/estadisticas5.php).  
Esta fuente incluye una selección de delitos clasificados como de **alto y mediano impacto**, los cuales afectan la vida,
integridad y patrimonio de las personas.  
La información comprende el periodo de **2014 a 2024**.

- *San Quintín solo cuenta con datos del 2021 al 2024.*  
- *San Felipe solo cuenta con datos del 2022 al 2024.*

Durante el procesamiento de los datos, se eliminaron registros debido a las siguientes razones:
\nRenglones vacíos  
Fechas no válidas  
Horas no válidas  
Datos con la etiqueta `#REF`

Puedes descargar los datos procesados en la pestaña "Crimen Niviel Estado" con el boton "DESCARGAR DATOS"
""")


st.markdown("---")

st.markdown("""
### 🗺️ Fuente cartográfica

El mapa fue obtenido del portal del **Consejo Nacional de Población (CONAPO)**, específicamente de la sección:

🔗 [Índices de Marginación 2020](https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372)  
**Cartografía digital (shp) del índice de marginación urbana por colonia 2020.**

""")

st.markdown("""
La cartografía permite visualizar aproximadamente **400,000 registros de delitos** de un total de **510,000**.  
Esta diferencia se explica principalmente por dos razones:

1. **Inconsistencias en los nombres de colonias** entre la base de datos de la SSC y el archivo de CONAPO.
2. **Ausencia de algunas localidades** en el shapefile de CONAPO, ya que no todas han sido integradas en la cartografía urbana 2020.
""")

st.markdown("---")

st.markdown("""
⚠️ *Esta aplicación no está afiliada al gobierno ni representa una fuente oficial de 
información de la Secretaría de Seguridad Ciudadana de Baja California.*
""")




