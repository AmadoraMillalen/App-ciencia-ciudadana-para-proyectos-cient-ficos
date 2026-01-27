import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import yaml


def page_style():
    #st.set_page_config(initial_sidebar_state="auto")
    #st.set_page_config(page_title='Vapor de agua',layout = 'centered',initial_sidebar_state="collapsed")

    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
    background-image: url("https://images.unsplash.com/photo-1507377288073-bb59c819bdb4");
    
    background-size:  cover;
    background-position: top center;
    background-repeat:  no-repeat;
    background-attachment: local; 
    }}

    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}

    [data-testid="stToolbar"] {{
    right: 2rem;
    }}

    div[data-testid="InputInstructions"] > span:nth-child(1) {{
    visibility: hidden;
    }}

    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)

    hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
    st.markdown(hide_default_format, unsafe_allow_html=True)

    return

def redirect_button(url: str, text: str= None, color="#F63366"):
    st.markdown(
    f'''
    <a href="{url}" target="_self">
        <div style="
            display: inline-block;
            padding: 0.5em 0.75em;
            color: #FFFFFF;
            background-color: {color};
            border-radius: 3px;
            text-decoration: none;">
            {text}
        </div>
    </a>
    ''',
    unsafe_allow_html=True)


def entry_date():

    return day, month, year 

    

def cat_stats(catalog, variables_config=None):	
    
    catalog = catalog.copy()
    # Procesar fechas si existen las columnas necesarias
    if 'fecha' in catalog.columns and 'hora' in catalog.columns:
        catalog['fechahora'] = pd.to_datetime(
                catalog['fecha'].astype(str) + ' ' + catalog['hora'].astype(str),
                format='%Y-%m-%d %H:%M:%S',
                errors='coerce'
            )
        catalog = catalog.sort_values(by='fechahora')
    
    catalog = catalog.reset_index()
    cols = catalog.columns
    
    # Si no se pasa variables_config, usar todas las columnas numéricas
    if variables_config is None:
        # Obtener columnas de metadata para excluir
        metadata_cols = ['n', 'usuario', 'id_loc', 'fecharegistro', 'fecha', 'hora', 
                        'latitud', 'longitud', 'index', 'fechahora']
        # Tomar todas las columnas que no sean metadata
        columnas_analisis = [col for col in cols if col not in metadata_cols]
        # Usar las primeras 5 columnas como principales para mover al inicio
        move_cols = columnas_analisis[:5] if len(columnas_analisis) >= 5 else columnas_analisis
    else:
        # Usar variables configuradas
        columnas_analisis = [var_id for var_id in variables_config.keys() if var_id in catalog.columns]
        move_cols = columnas_analisis
    
    # Reorganizar columnas (variables principales primero)
    if move_cols:
        catalog = catalog[move_cols + [x for x in cols if x not in move_cols and x in catalog.columns]]
    
    # Eliminar columnas de metadata que no queremos mostrar
    deletecols = ['n', 'usuario', 'id_loc', 'fecharegistro', 'index']
    catalog = catalog.drop(columns=deletecols, errors='ignore')
    
    st.markdown(
        f"""
        ### 📊 Estadística del catálogo
        #### 📋 Información general
        ###### - Número de filas (mediciones): {len(catalog)}
        ###### - Número de columnas: {len(catalog.columns)}
        ###### - Mira algunas columnas y sus datos:
        """
    )		
    
    st.write(catalog.head())
    st.write("#### 📈 Estadística de las columnas")
    st.write(catalog.describe())
    
    # Crear histogramas para cada variable numérica o de selección
    if variables_config:
        for var_id, var_config in variables_config.items():
            if var_id in catalog.columns and var_config['tipo'] in ['number', 'select']:
                # Obtener nombre y unidad para mostrar
                nombre_var = var_config['nombre']
                unidad_var = var_config.get('unidad', '')
                
                # Convertir a numérico si es posible
                catalog[var_id] = pd.to_numeric(catalog[var_id], errors='coerce')
                
                # Filtrar valores no nulos
                datos_var = catalog[var_id].dropna()
                
                if len(datos_var) > 0:
                    st.markdown(f"#### 📊 Distribución de {nombre_var}")
                    
                    # Estadísticas básicas
                    st.markdown(f"""
                    ###### - Rango: {np.nanmin(datos_var):.2f} - {np.nanmax(datos_var):.2f} {unidad_var}
                    ###### - Media: {np.nanmean(datos_var):.2f} {unidad_var}
                    ###### - Desviación estándar: {np.nanstd(datos_var):.2f} {unidad_var}
                    """)
                    
                    # Crear histograma
                    if var_config['tipo'] == 'number':
                        fig = px.histogram(
                            x=datos_var,
                            nbins=30,
                            title=f'Distribución de {nombre_var}'
                        )
                    else:  # Para variables select
                        fig = px.histogram(
                            x=datos_var,
                            title=f'Distribución de {nombre_var}'
                        )
                    
                    # Configurar etiquetas
                    eje_x = f"{nombre_var}"
                    if unidad_var:
                        eje_x += f" ({unidad_var})"
                    
                    fig.update_layout(
                        xaxis_title_text=eje_x,
                        yaxis_title_text='Frecuencia',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    else:
        # Si no hay variables_config, crear histogramas para todas las columnas numéricas
        numeric_cols = catalog.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Mostrar solo las primeras 3
            if col in catalog.columns and catalog[col].notna().sum() > 0:
                st.markdown(f"#### 📊 Distribución de {col}")
                
                datos_var = catalog[col].dropna()
                st.markdown(f"""
                ###### - Rango: {np.nanmin(datos_var):.2f} - {np.nanmax(datos_var):.2f}
                ###### - Media: {np.nanmean(datos_var):.2f}
                ###### - Desviación estándar: {np.nanstd(datos_var):.2f}
                """)
                
                fig = px.histogram(x=datos_var, nbins=30, title=f'Distribución de {col}')
                fig.update_layout(
                    xaxis_title_text=col,
                    yaxis_title_text='Frecuencia',
                    showlegend=False
                )
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    return

def run_scatter_fig_err(catalog, x, y, c, colorscale, nmax=10000, customXY=False):

    import plotly.graph_objects as go
    
    xaxis = catalog[x]
    yaxis = catalog[y]
    caxis = catalog[c]

    colorerr = "rgba(0, 0, 0, 0.2)"
    ssize = 8
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xaxis,
        y=yaxis,
        mode='markers',
        marker=dict(
            color=caxis,
            colorscale=colorscale,
            size=6,
            showscale=True
        ),
        name='Datos'
    ))
    
    fig.update_xaxes(title_text=x)
    fig.update_yaxes(title_text=y)
    fig.update_layout(legend=dict(orientation="h", y=-0.2))
    
    return fig

def run_stats_plot(catalog, nombre_df, variables_config=None, key='default_key'):
    """
    Crea gráficos interactivos de dispersión con variables dinámicas.
    """
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    
    catalog = catalog.copy()
    # Procesar fechas 
    catalog['fechahora'] = pd.to_datetime(
                catalog['fecha'].astype(str) + ' ' + catalog['hora'].astype(str),
                format='%Y-%m-%d %H:%M:%S',
                errors='coerce'
            )

    catalog = catalog.sort_values(by='fechahora')
    
    catalog = catalog.reset_index()
    
    # Eliminar columnas de metadata
    deletecols = ['n', 'usuario', 'id_loc', 'fecharegistro', 'index', 'Date', 
                 'usuario_origen', 'index', 'usuario']
    catalog = catalog.drop(columns=[col for col in deletecols if col in catalog.columns], errors='ignore')
    
    # Obtener columnas disponibles para gráficos
    if variables_config:
        # Usar variables configuradas y sus columnas relacionadas
        columnas_variables = [var_id for var_id in variables_config.keys() if var_id in catalog.columns]
        
        # Agregar columnas de metadata que pueden ser útiles
        columnas_utiles = ['fechahora', 'latitud', 'longitud', 'fecha', 'hora']
        columnas_disponibles = columnas_variables + [col for col in columnas_utiles if col in catalog.columns]
    else:
        # Si no hay variables_config, usar todas las columnas numéricas y de fecha
        numeric_cols = catalog.select_dtypes(include=['float64', 'float32', 'int32', 'int64']).columns.tolist()
        date_cols = ['fechahora'] if 'fechahora' in catalog.columns else []
        columnas_disponibles = numeric_cols + date_cols
    
    # Filtrar solo columnas que existen
    columnas_disponibles = [col for col in columnas_disponibles if col in catalog.columns]
    
    if not columnas_disponibles:
        st.warning("No hay columnas disponibles para graficar")
        return
    
    # Crear DataFrame para selección
    catalog_display = catalog[columnas_disponibles]
    
    # Selectores de ejes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x = st.selectbox("Eje X", columnas_disponibles, 
                        help="Selecciona la variable para el eje horizontal")
    
    with col2:
        y = st.selectbox("Eje Y", columnas_disponibles, 
                        help="Selecciona la variable para el eje vertical")
    
    with col3:
        # Columnas para color (excluyendo las seleccionadas como X e Y)
        columnas_color = [col for col in columnas_disponibles if col not in [x, y] and col != 'fechahora']
        
        if columnas_color:
            c = st.selectbox("Variable para color", columnas_color,
                           help="Selecciona la variable para codificar con color")
        else:
            c = x  # Fallback si no hay más columnas
    
    # Selector de paleta de colores
    scales = ['agsunset', 'blues', 'deep', 'electric', 'fall', 'geyser', 'gray', 
             'greens', 'greys', 'hot', 'ice', 'icefire', 'inferno', 'jet', 
             'magenta', 'magma', 'mint', 'oranges', 'plasma', 'purples', 
             'rainbow', 'reds', 'solar', 'spectral', 'sunset', 'sunsetdark',
             'tealrose', 'thermal', 'twilight', 'viridis']
    
    cs = st.selectbox("Paleta de colores", scales, index=scales.index('blues'))
    
    # Crear gráfico
    if x and y:
        try:
            # Usar plotly express para gráficos más robustos
            if c and c in catalog.columns:
                fig = px.scatter(
                    catalog,
                    x=x,
                    y=y,
                    color=c,
                    color_continuous_scale=cs,
                    title=f'{y} vs {x}',
                    hover_data=[col for col in catalog.columns if col not in [x, y, c]][:3]  # Primeras 3 columnas adicionales
                )
            else:
                fig = px.scatter(
                    catalog,
                    x=x,
                    y=y,
                    title=f'{y} vs {x}',
                    hover_data=[col for col in catalog.columns if col not in [x, y]][:3]
                )
            
            # Personalizar nombres de ejes si hay información en variables_config
            if variables_config:
                if x in variables_config:
                    x_name = variables_config[x]['nombre']
                    if 'unidad' in variables_config[x]:
                        x_name += f" ({variables_config[x]['unidad']})"
                    fig.update_xaxes(title_text=x_name)
                
                if y in variables_config:
                    y_name = variables_config[y]['nombre']
                    if 'unidad' in variables_config[y]:
                        y_name += f" ({variables_config[y]['unidad']})"
                    fig.update_yaxes(title_text=y_name)
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, theme="streamlit")
            
        except Exception as e:
            st.error(f"Error al crear el gráfico: {e}")
            # Fallback a la función original
            try:
                fig = run_scatter_fig_err(catalog_display, x, y, c, cs)
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            except:
                st.error("No se pudo crear el gráfico con los datos seleccionados")
    
    return

# Mantener estas funciones igual:
def calcular_distancia(lat1, lon1, lat2, lon2):
    import numpy as np
    
    R = 6371  # Radio de la Tierra en km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def cargar_configuracion_variables():
    """
    Carga la configuración de variables desde YAML.
    Si no existe, crea una por defecto.
    """
    try:
        with open('config_variables.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        # Configuración por defecto (compatible con tu código actual)
        st.warning("No se encontró config_variables.yaml. Usando configuración por defecto.")
        return {
            'variables': {
                'Tsky': {
                    'nombre': 'Temperatura al cielo',
                    'tipo': 'number',
                    'unidad': '°C',
                    'min': -60.0,
                    'max': 30.0,
                    'paso': 0.1,
                    'requerido': True,
                    'placeholder': 'T° cielo'
                },
                'Tamb': {
                    'nombre': 'Temperatura ambiente',
                    'tipo': 'number', 
                    'unidad': '°C',
                    'min': -30.0,
                    'max': 50.0,
                    'paso': 0.1,
                    'requerido': False,
                    'placeholder': 'T° ambiente'
                },
                'perc_cloud': {
                    'nombre': 'Porcentaje de nubosidad',
                    'tipo': 'select',
                    'unidad': '%',
                    'opciones': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                    'requerido': True,
                    'placeholder': 'Porcentaje nubosidad'
                }
            },
            'proyecto': {
                'nombre': 'TITANS: Midiendo vapor de agua',
                'descripcion': 'Proyecto científico escolar',
                'año': 2025
            }
        }



