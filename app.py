import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import yaml
from yaml import SafeLoader
import base64

try:
    from st_files_connection import FilesConnection  # Solo si usas S3
    import boto3
except ImportError:
    pass  # No crítico

# TU AUTHENTICATOR
import streamlit_authenticator as stauth

from funciones import *


st.set_page_config(page_title="Vapor de agua",page_icon=":earth_americas:", layout='wide')

def get_image_base64(image_path): #abre una imagen en modo binario, lo lee y codifica en base64 para insertarlo como texto HTML
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode() #lo convierte a string

def footer():  
    st.divider() #linea divisoria horizontal, se divide en unidades proporcionales: 20=20% del ancho total
    c0, col1,c00, col2,c000,col3, c0000 = st.columns([10,20,5,30,5,20,10])
    # espaciado letral: c0,c00,.. y las imagenes van en col1,col2,col3
    with col1:
        st.image("titanslogo.png", use_container_width =True)
    with col2:
        st.image("logo-do.svg", use_container_width =True) #AQUI PUEDES AGREGAR TU LOGO
    with col3:
        st.image("milenio.png", use_container_width =True)
    st.markdown("<p style='text-align: center;background-color: rgba(255, 255, 255, 0.4) !important'>© 2025 TITANS </h2>", unsafe_allow_html=True)
    #texto centrado fondo semitransparente, usa HTML
    return


@st.cache_data(ttl=1) #hace que streamlit guarde en cache el resultado de readdbfile, la cache dura 1s
def readdbfile(filename):
    f = conn.open(filename, "rb") #abre en modo binario usando conexion conn
    df = pd.read_csv(f, encoding="utf-8") # lee como dataframe
    f.close()
    return df


page_style() 

# Cargar configuración de variables GLOBAL
config_vars = cargar_configuracion_variables()
variables_config = config_vars['variables']

nombre_proyecto = config_vars['proyecto'].get('nombre', 'Proyecto Científico')
descripcion_corta = config_vars['proyecto'].get('descripcion_corta', '')
institucion_nombre = config_vars['institucion'].get('nombre', '')
email_contacto = config_vars['institucion'].get('email_contacto', '')


st.markdown("""<h3 style="padding-top: 5px;text-align: center;font-family: monospace;">Proyecto científico:</h3>""", unsafe_allow_html=True)
st.markdown(f"""<h1 style="color:white;padding-top: 10px;padding-bottom: 30px;text-align: center;">{nombre_proyecto}</h1>""", unsafe_allow_html=True)

#pestañas interactivas
tab1, tab3, tab4, tab5 = st.tabs(["Inicio", "Ingresa tus datos","Mediciones globales", "Estadística"])
#modifica el estilo de st.tabs usando CSS
st.markdown('''
    <style> 
        [data-testid="stTabs"] {
        background-color: rgba(255, 255, 255, 0.4);
        
        }

        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:18px;
        width: fit-content;
        justify-content:center;
        margin: auto; 
        }

        .stTabs [data-baseweb="tab-list"] {
        gap: 50px;
        width: fit-content;
        margin: auto;
        text-align:center;
        border-bottom: none ; 
        
        }

        .stTabs [data-baseweb="tab"] {
		height: 50px;
        white-space: pre-wrap;
		color: #232323;
		border-radius: 0px 4px 0px 0px;
		gap: 1px;
		padding-top: 10px;
        font-weight: bold;
		padding-bottom: 0px; 
        box-shadow: none ;
        border-bottom: none ;
        }

        .stTabs [data-baseweb="tab-border"] {
		display: none;
        visibility: hidden;
        height: 0px;
        border: none;
        }

        
	.stTabs [aria-selected="true"] {
  		color: #D62728;  
        
	}
    </style>
    ''', unsafe_allow_html=True)

with tab1:
    c0, col1, c00 = st.columns([5,90,5])
    with col1:
 
        # Mostrar enlaces dinámicos si existen
        enlaces = config_vars.get('enlaces_utiles', {})

        st.markdown(f"""
            <div style='padding: 20px;margin: 20px 0px;
            color:black;'>
            <h4 style="color:black;padding-top: 20px;text-align: left;">Resumen</h4>
            {descripcion_corta} <br>

            <h4 style="color:black;padding-top: 20px;text-align: left;">¿Quieres participar?</h4>
            Encuentra la información de cómo participar en nuestra página de <a href="{enlaces['pagina_web']}" target="_blank">página web oficial</a> y registrate en <a href="{enlaces['formulario_inscripcion']}" target="_blank">formulario de inscripción</a>. Si tienes alguna duda no dudes en contactarnos en <strong>{email_contacto}</strong>. <br>

            <h4 style="color:black;padding-top: 20px;text-align: left;">¿Ya estás inscrito?</h4>
            Si ya te inscribiste, inicia sesión en la pestaña "Ingresa tus datos" para subir tus mediciones a nuestra base de datos.
                
            <br>
            </div>
            """, unsafe_allow_html=True)
        # Mostrar información de coordinadores (opcional)
        if 'coordinadores' in config_vars:
            for coord in config_vars['coordinadores']:
                st.write(f"**{coord.get('nombre', '')}** - {coord.get('rol', '')}")
                if coord.get('email'):
                    st.write(f"📧 {coord['email']}")
        
        # Mostrar colaboradores (opcional)
        if 'colaboradores' in config_vars and config_vars['colaboradores']:
            for colab in config_vars['colaboradores']:
                st.write(f"• {colab}")
    footer()

with tab3:
    c0, col1, c00 = st.columns([5,90,5])
    with col1: #config.yaml config de usuarios y cookies de authenitacion
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
#crea un objeto authenticator
        authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

        try: #muestra un formulario de login
            authenticator.login() 

        except Exception as e: #si ocurre algun error lo muestra
            st.error(e)
        #crea una conexion a un bucket de amazon s3
        #conn = st.connection('s3', type=FilesConnection) 
 
        df_user = pd.read_csv('users-info.csv')
        df_dir = pd.read_csv('users-dir.csv')
        df_data = pd.read_csv('data.csv')
        # convierte la columna hora a a hora H,M,S
        df_data['hora'] = pd.to_datetime(df_data['hora'], format='%H:%M:%S').dt.time 

        if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
            authenticator.logout() #muestra el boton de logout
            username = st.session_state.get('username', None)#obtiene el username
            
            if username:
                st.write(f'Bienvenido/a *{st.session_state["name"]}*')#saludo personalizado
                
                st.subheader('Selecciona tu dirección')
    
                user_full = df_user[df_user['usuario'] == username]
    
                user_dirs = df_dir[df_dir['id_usuario'].values == user_full['id'].values]
                id_direcciones = user_dirs['id_dir']       
                op_direcciones = user_dirs['nombre_dir']     

                #menu desplegable, 'collapsed': oculta el texto del label, index=0 seleciona la primera opcion por defecto, key es la clave unica para guardar el valor seleccionado
                selected_cat = st.selectbox('Selecciona la dirección en la que estás tomando tus mediciones', options = user_dirs['nombre_dir'], index = 0, label_visibility='collapsed', key='seldir')
                #muestra el nombre de la direccion seleccionada en la interfaz
                dir_sel = user_dirs['direccion'][user_dirs['nombre_dir']==selected_cat].values[0]
                st.markdown("Dirección seleccionada: %s"%dir_sel)

                sel_dirid_i = user_dirs.index[user_dirs['nombre_dir']==selected_cat] 
                sel_dirid = user_dirs['id_dir'].loc[sel_dirid_i].values[0]

                dir_lat = user_dirs['latitud'].loc[sel_dirid_i].values[0]
                dir_lon = user_dirs['longitud'].loc[sel_dirid_i].values[0]

                st.subheader('Anota tus mediciones')

                #crea un formulario con identificador, todo lo que esta dentro se ejecuta cuando el usuario aprieta submit
                with st.form(key="measurement_form"):
                    st.write('Indica la fecha de la medición')
                    c1,c2,c3,c4 = st.columns([0.2,0.2,0.2,0.4])

                    day = c1.selectbox('Día',list(range(1,32,1)),index=None,placeholder = 'Día',label_visibility='visible')
                    month = c2.selectbox('Mes',list(range(1,13,1)),index=None,placeholder = 'Mes',label_visibility='visible')
                    year = c3.selectbox('Año',['2025','2026'],index=0,placeholder = 'Año',label_visibility='visible')
        
                    time = c4.time_input('Hora de medición', value=None,label_visibility='visible')

                    st.write('Indica tus mediciones')

                    num_vars = len(variables_config)
                    
                    # Crear columnas dinámicas
                    if num_vars <= 3:
                        cols = st.columns(num_vars)
                        var_ids = list(variables_config.keys())
                        valores_medicion = {}
                        
                        for i, var_id in enumerate(var_ids):
                            var_config = variables_config[var_id]
                            with cols[i]:
                                etiqueta = var_config['nombre']
                                if 'unidad' in var_config:
                                    etiqueta = f"{var_config['nombre']} ({var_config['unidad']})"
                                
                                if var_config['tipo'] == 'number':
                                    valor = st.number_input(
                                        etiqueta,
                                        min_value=float(var_config.get('min', 0)),
                                        max_value=float(var_config.get('max', 100)),
                                        step=float(var_config.get('paso', 1.0)),
                                        value=None,
                                        placeholder=var_config.get('placeholder', etiqueta)
                                    )
                                elif var_config['tipo'] == 'select':     
                                    valor = st.selectbox(
                                        etiqueta,
                                        options=var_config['opciones'],
                                        index=None,
                                        placeholder=var_config.get('placeholder', 'Seleccionar...')
                                    )
                                elif var_config['tipo'] == 'text':
                                    valor = st.text_input(
                                        etiqueta,
                                        placeholder=var_config.get('placeholder', 'Escribe aquí...')
                                    )
                                valores_medicion[var_id] = valor
                    else:
                        # Si hay más de 3 variables, crear múltiples filas
                        valores_medicion = {}
                        num_filas = (num_vars + 2) // 3
                        
                        for fila in range(num_filas):
                            inicio = fila * 3
                            fin = min(inicio + 3, num_vars)
                            cols = st.columns(fin - inicio)
                            
                            var_ids = list(variables_config.keys())[inicio:fin]
                            
                            for i, var_id in enumerate(var_ids):
                                var_config = variables_config[var_id]
                                with cols[i]:
                                    etiqueta = var_config['nombre']
                                    if 'unidad' in var_config:
                                        etiqueta = f"{var_config['nombre']} ({var_config['unidad']})"
                                    
                                    if var_config['tipo'] == 'number':
                                        valor = st.number_input(
                                            etiqueta,
                                            min_value=float(var_config.get('min', 0)),
                                            max_value=float(var_config.get('max', 100)),
                                            step=float(var_config.get('paso', 1.0)),
                                            value=None,
                                            placeholder=var_config.get('placeholder', etiqueta)
                                        )
                                    elif var_config['tipo'] == 'select':     
                                        valor = st.selectbox(
                                            etiqueta,
                                            options=var_config['opciones'],
                                            index=None,
                                            placeholder=var_config.get('placeholder', 'Seleccionar...')
                                        )
                                    elif var_config['tipo'] == 'text':
                                        valor = st.text_input(
                                            etiqueta,
                                            placeholder=var_config.get('placeholder', 'Escribe aquí...')
                                        )
                                    valores_medicion[var_id] = valor
    
                    if day!=None and month!=None and year!=None:
                        date = str(year)+"-"+f"{month:02d}"+"-"+f"{day:02d}" 
                    else:
                        date=None

                    #boton tipo radio?
                    reemp = st.radio("¿Desea reemplazar valores existentes en caso de ingresar la misma fecha y hora?",["Si", "No"],index=1)

                    submitted = st.form_submit_button("Guardar")

                if submitted:
                    errores = []
                    if date is None:
                        errores.append("La fecha es requerida")
                    if time is None:
                        errores.append("La hora es requerida")
                    
                    for var_id, var_config in variables_config.items():
                        if var_config.get('requerido', False):
                            valor = valores_medicion.get(var_id)
                            if valor is None:
                                errores.append(f"{var_config['nombre']} es requerido")

                    if errores:
                        for error in errores:
                            st.error(error)
                    else:
                        now = datetime.now()
                        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                        n_entries = len(df_data)
                        
                        # Crear diccionario base para la nueva fila
                        new_row_dict = {
                            'n': n_entries + 1,
                            'usuario': username,
                            'id_loc': sel_dirid,
                            'latitud': str(dir_lat),
                            'longitud': str(dir_lon),
                            'fecharegistro': dt_string,
                            'fecha': str(date),
                            'hora': str(time)
                        }
                        
                        # Agregar todas las variables dinámicamente
                        for var_id in variables_config.keys():
                            valor = valores_medicion.get(var_id)
                            if valor is None:
                                new_row_dict[var_id] = np.nan
                            else:
                                new_row_dict[var_id] = str(valor)
                        
                        # Crear DataFrame
                        new_row = pd.DataFrame([new_row_dict])
                        
                        # Buscar medición existente
                        existing_entry_idx = df_data.index[
                            (df_data['fecha'] == str(date)) & 
                            (df_data['hora'] == str(time)) & 
                            (df_data['usuario'] == username) & 
                            (df_data['id_loc'] == sel_dirid)
                        ]
                        
                        if len(existing_entry_idx) > 0:
                            if reemp == "Si":
                                # Actualizar valores existentes dinámicamente
                                for var_id in variables_config.keys():
                                    if var_id in df_data.columns:
                                        valor = valores_medicion.get(var_id)
                                        if valor is None:
                                            df_data.loc[existing_entry_idx, var_id] = np.nan
                                        else:
                                            df_data.loc[existing_entry_idx, var_id] = str(valor)
                                
                                st.write('Se actualizaron valores existentes.')
                                st.success("Medición se guarda en versión no local")
                            elif reemp == "No":
                                st.write('Se mantendrán los valores existentes.')
                                st.success("Medición se guarda en versión no local")
                        
                        else:
                            df_data = pd.concat([df_data, new_row], ignore_index=True)
                            st.success("Medición se guarda en versión no local")


        elif st.session_state['authentication_status'] is False:
            st.error('Usuario o contraseña incorrecto')
        elif st.session_state['authentication_status'] is None:
            st.info('Inicia sesión para ingresar o ver tus datos')

        if st.session_state["authentication_status"]: 
            df_data = pd.read_csv('data.csv')
            df_datauser = df_data[df_data['usuario']==username].copy() 

            if len(df_datauser) > 0:
                st.subheader('Tus datos') 
                df_datauser['fechahora'] = pd.to_datetime(
                df_datauser['fecha'] + ' ' + df_datauser['hora'].astype(str),format='%Y-%m-%d %H:%M:%S',
                errors='coerce'
            )
                df_datauser = df_datauser.sort_values(by='fechahora')
                df_datauser = df_datauser.reset_index() 
                df_datauser['fechahora_str'] = df_datauser['fechahora'].dt.strftime('%d-%m-%Y %H:%M:%S')
                df_datauser['customindex'] = df_datauser.index + 1

                # Crear gráficos dinámicos para cada variable
                for var_id, var_config in variables_config.items():
                    if var_id in df_datauser.columns:
                        # Convertir a numérico si es posible
                        df_datauser[var_id] = pd.to_numeric(df_datauser[var_id], errors='coerce')
                        
                        # Filtrar valores no nulos
                        df_plot = df_datauser.dropna(subset=[var_id])
                        
                        if len(df_plot) > 0 and var_config['tipo'] in ['number', 'select']:
                            # Determinar título del eje Y
                            yaxis_title = var_config['nombre']
                            if 'unidad' in var_config:
                                yaxis_title = f"{var_config['nombre']} ({var_config['unidad']})"
                            
                            # Crear gráfico
                            fig = px.scatter(df_plot, x='fechahora', y=var_id)
                            fig.update_traces(
                                customdata=df_plot[['customindex', 'fechahora_str']].values,
                                hovertemplate='Medición %{customdata[0]}<br>' + 
                                             f'{var_config["nombre"]}: %{{y}}<br>' + 
                                             'Fecha: %{customdata[1]}'
                            )
                            fig.update_layout(
                                xaxis_title="Fecha",
                                yaxis_title=yaxis_title,
                                height=250
                            )
                            fig.update_xaxes(tickformat='%d-%m-%Y')
                            st.plotly_chart(fig, use_container_width=True)


            else:
                st.subheader('Tus datos')
                st.write('Aún no has ingresado datos')
        else:
            st.empty()
    footer()

with tab4:
    c0, col1, c00 = st.columns([5,90,5])
    with col1:
        st.cache_data.clear()

        df_user = pd.read_csv('users-info.csv')
        df_dir = pd.read_csv('users-dir.csv')
        df_data = pd.read_csv('data.csv')
        
        st.markdown('## Mapa de mediciones')

        st.map(df_dir,latitude='latitud',longitude='longitud',use_container_width=False)
 
        admins = df_user['usuario'][df_user['rol']=='admin']

        if st.session_state["authentication_status"]:
            if user_full['rol'].values[0] == 'admin':
                st.markdown('## Vista administrador')
                df_data['fechahora'] = pd.to_datetime(df_datauser['fecha'].astype(str) + ' ' + df_datauser['hora'].astype(str), errors='coerce')
                df_data = df_data.sort_values(by='fechahora')
                df_data = df_data.reset_index() 
                
                st.subheader('Mediciones vs tiempo')

                df_data['fechahora_str'] = df_data['fechahora'].dt.strftime('%d-%m-%Y %H:%M:%S')
                df_data['customindex'] = df_data.index + 1

                # Crear gráficos dinámicos para administrador
                for var_id, var_config in variables_config.items():
                    if var_id in df_data.columns:
                        # Convertir a numérico si es posible
                        df_data[var_id] = pd.to_numeric(df_data[var_id], errors='coerce')
                        
                        # Filtrar valores no nulos
                        df_plot = df_data.dropna(subset=[var_id])
                        
                        if len(df_plot) > 0 and var_config['tipo'] in ['number', 'select']:
                            # Determinar título del eje Y
                            yaxis_title = var_config['nombre']
                            if 'unidad' in var_config:
                                yaxis_title = f"{var_config['nombre']} ({var_config['unidad']})"
                            
                            # Crear gráfico
                            fig = px.scatter(df_plot, x='fechahora', y=var_id)
                            fig.update_traces(
                                customdata=df_plot[['customindex', 'fechahora_str']].values,
                                hovertemplate='Medición %{customdata[0]}<br>' + 
                                             f'{var_config["nombre"]}: %{{y}}<br>' + 
                                             'Fecha: %{customdata[1]}'
                            )
                            fig.update_layout(
                                xaxis_title="Fecha",
                                yaxis_title=yaxis_title,
                                height=250
                            )
                            fig.update_xaxes(tickformat='%d-%m-%Y')
                            # Usar key dinámico para cada gráfico
                            st.plotly_chart(fig, use_container_width=True, key=f'all_data_plot_{var_id}')

    footer()
    
with tab5:
    #conn = st.connection('s3', type=FilesConnection)
    c0, col1, c00 = st.columns([5,90,5])
    with col1:
        st.cache_data.clear()

        df_user = pd.read_csv('users-info.csv')
        df_dir = pd.read_csv('users-dir.csv')
        df_data = pd.read_csv('data.csv')

        st.markdown(f"""
            <div style='padding: 20px;margin: 20px 0px;
            color:black;'>
            <h4 style="color:black;padding-top: 20px;text-align: left;">Análisis de los datos</h4>
            En esta sección puedes acceder a la estadística de los datos.<br> 
            La sección "Intercomparar" permite comparar tus mediciones con la de otros grupos. Esta función solo está disponible para usuarios registrados.
            </div>
            """, unsafe_allow_html=True)

        if st.session_state["authentication_status"]:
            user_full = df_user[df_user['usuario'] == username]
            user_dir = df_dir[df_dir['id_usuario'] == user_full['id'].iloc[0]]
            if user_full['rol'].iloc[0] == 'admin':
                username = "apex.monitor"
                user_full = df_user[df_user['usuario'] == username]
                st.warning(f"Modo Admin: Probando como usuario '{username}'")
            df_datauser = df_data[df_data['usuario']==username]
            grupo_usuario_actual = user_full['grupo'].iloc[0]
            usuario_es_admin = user_full['rol'].iloc[0] == 'admin'
        else:
            df_datauser = pd.DataFrame()
            grupo_usuario_actual = ""
            usuario_es_admin = False


        tab0, tab00 = st.tabs(["Explorar", "Intercomparar"])
        df_completo = pd.merge(df_data, df_user[['usuario', 'grupo']], on='usuario', how='left')
        with tab0:
           
           if st.session_state.get("authentication_status", False):
               user_key = username
           else:
               user_key = "public"

           st.title('Explora nuestras mediciones')
           st.write(
                   """
                   En esta sección puedes acceder a la estadística de las columnas de nuestra base de datos y a histogramas de frecuencia de las mediciones. Además, puedes visualizar distintos gráficos escogiendo las variables disponibles en los ejes x, y, z.

                   """
                   )
           
           selected_file = df_data

           tab1, tab2 = st.tabs(["Estadísticas", "Gráfico de las columnas"])

           with tab1:
               cat_stats(selected_file, variables_config)

           with tab2:
               st.subheader('Grafica el catálogo')
               run_stats_plot(selected_file,'df_data', variables_config, key='tab2_df_data')

    if st.session_state["authentication_status"] and not user_full.empty:
        with tab00:
            st.title('Compara con otros grupos')
            st.subheader("🎛️ Controles de Análisis")
        
            # Obtener nombre del grupo
            usuarios_no_admin = df_user[df_user['rol'] != 'admin']['usuario'].unique()
            grupos_comparacion = df_user[df_user['usuario'].isin(usuarios_no_admin)]['grupo'].unique()

            # Selector de tipo de comparación
            analysis_type = st.selectbox(
            "Tipo de análisis:", 
            ["Radio de distancia", "Comparación entre grupos", "Análisis por altitud"],
            key="analysis_type_selector"
        )
        
            # Panel principal
            col1, col2 = st.columns([2, 1])
            with col1:
                # Unir df_data con la columna 'group' de df_user
                if 'grupo' in df_user.columns:
                    df_completo = pd.merge(df_data, df_user[['usuario', 'grupo']], on='usuario', how='left')
                else:
                    # Si no existe columna grupo, crear una temporal
                   df_user['grupo'] = 'Sin grupo'
                   df_completo = pd.merge(df_data, df_user[['usuario', 'grupo']], on='usuario', how='left')
            
                # Obtener el grupo del usuario actual
                grupo_usuario_actual = ""
                if not user_full.empty and 'grupo' in user_full.columns:
                    grupo_usuario_actual = user_full['grupo'].iloc[0]
            
                # Obtener todos los grupos excepto el del usuario actual
                if 'grupo' in df_user.columns and 'rol' in df_user.columns:
                    todos_grupos = df_user[df_user['rol'] != 'admin']['grupo'].unique()
                    grupos_comparacion = [grupo for grupo in todos_grupos if grupo != grupo_usuario_actual]
                else:
                    grupos_comparacion = []
            
                if df_datauser.empty:
                    st.warning("📝 **Aún no tienes mediciones registradas**")
                    st.markdown("""
    <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #2196F3;'>
    <h4>🚀 ¿Cómo empezar?</h4>
    <ol>
    <li>Ve a la pestaña <strong>'Mediciones'</strong></li>
    <li>Registra tu primera medición con tus coordenadas</li>
    <li>¡Vuelve aquí para comparar con otros grupos!</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
                    try:
                        user_coords = df_dir[df_dir['id_usuario'] == user_full['id'].iloc[0]]
                        st.write(f"**Tu ubicación de perfil:** Lat {user_coords['latitud'].iloc[0]}, Lon {user_coords['longitud'].iloc[0]}")
                    except:
                        st.write("**No se encontró tu ubicación de perfil**")
                else:
                    try:
                        lat_usuario = df_datauser['latitud'].iloc[0]
                        lon_usuario = df_datauser['longitud'].iloc[0]
                        st.write(f"**Tu ubicación:** Latitud {float(lat_usuario):.4f}, Longitud {float(lon_usuario):.4f}")
                    except:
                        st.error("No se encontraron datos de ubicación (latitud/longitud) para tu usuario")
                        lat_usuario = None
                        lon_usuario = None

                    if analysis_type == "Radio de distancia":
                        st.header("📍 Comparación por Radio de Distancia")
                    
                        radio_km = st.slider(
                        "Radio de distancia (km):",
                        min_value=1,
                        max_value=100,
                        value=10,
                        key="radio_distancia"
                    )
                    
                        # Obtener variables numéricas de la configuración
                        variables_numericas = [var_id for var_id, var_config in variables_config.items() 
                                          if var_config['tipo'] in ['number', 'select']]
                    
                        if not variables_numericas:
                            st.warning("No hay variables numéricas configuradas")
                        else:
                            # Crear nombres descriptivos para el selectbox
                            opciones_variables = []
                            for var_id in variables_numericas:
                                var_config = variables_config[var_id]
                                nombre_completo = f"{var_config['nombre']} ({var_id})"
                                if 'unidad' in var_config:
                                    nombre_completo = f"{var_config['nombre']} ({var_config['unidad']}) - {var_id}"
                                opciones_variables.append((var_id, nombre_completo))
                        
                            # Selector de variable con nombres descriptivos
                            variable_seleccionada = st.selectbox(
                            "Selecciona la variable a analizar:", 
                            options=[opt[0] for opt in opciones_variables],
                            format_func=lambda x: next((opt[1] for opt in opciones_variables if opt[0] == x), x),
                            key="variable_radio"
                        )
                        
                            if st.button("🔍 Buscar grupos dentro del radio", key="buscar_radio"):
                                if lat_usuario is None or lon_usuario is None:
                                    st.error("No se pudo obtener tu ubicación")
                                else:
                                    grupos_cercanos = []
                                    distancias_grupos = {}
                                
                                    for grupo in grupos_comparacion:
                                        usuarios_grupo = df_completo[df_completo['grupo'] == grupo]
                                        if not usuarios_grupo.empty:
                                            primer_usuario = usuarios_grupo.iloc[0]
                                            try:
                                                distancia = calcular_distancia(lat_usuario, lon_usuario,
                                                primer_usuario['latitud'], primer_usuario['longitud']
                                            )
                                                distancias_grupos[grupo] = distancia
                                                if distancia <= radio_km:
                                                    grupos_cercanos.append(grupo)
                                            except:
                                                continue
                                
                                    if grupos_cercanos:
                                        st.success(f"Encontrados {len(grupos_cercanos)} grupos dentro de {radio_km} km")
                                        st.write("**Distancias a los grupos:**")
                                        for grupo in grupos_cercanos:
                                            st.write(f"- {grupo}: {distancias_grupos[grupo]:.1f} km")

                                        todos_grupos_plot = [grupo_usuario_actual] + grupos_cercanos
                                        datos_radio = df_completo[df_completo['grupo'].isin(todos_grupos_plot)]

                                        fig_radio = go.Figure()
                                        for grupo in todos_grupos_plot:
                                            datos_grupo = datos_radio[datos_radio['grupo'] == grupo][variable_seleccionada].dropna()
                                            if len(datos_grupo) > 0:
                                                es_grupo_actual = (grupo == grupo_usuario_actual)
                                                color = '#FF4B4B' if es_grupo_actual else '#1F77B4'
                                                nombre_grupo = f"{grupo} (TU GRUPO)" if es_grupo_actual else f"📍 {grupo} ({distancias_grupos.get(grupo, 0):.1f} km)"
                                            
                                                # Obtener nombre de variable para el título
                                                var_nombre = variables_config.get(variable_seleccionada, {}).get('nombre', variable_seleccionada)
                                                var_unidad = variables_config.get(variable_seleccionada, {}).get('unidad', '')

                                                fig_radio.add_trace(go.Violin(
                                                y=datos_grupo,
                                                name=nombre_grupo,
                                                box_visible=True,
                                                meanline_visible=True,
                                                points=False,
                                                side='positive',
                                                hoverinfo='y+name',
                                                line_color=color,
                                                fillcolor='rgba(255, 75, 75, 0.2)' if es_grupo_actual else 'rgba(31, 119, 180, 0.2)'
                                            ))
                                    
                                        # Configurar título con nombre de variable
                                        var_config = variables_config.get(variable_seleccionada, {})
                                        titulo_var = var_config.get('nombre', variable_seleccionada)
                                        if 'unidad' in var_config:
                                            titulo_var = f"{var_config['nombre']} ({var_config['unidad']})"
                                    
                                        fig_radio.update_layout(
                                        title=f'Comparación de {titulo_var} - Grupos dentro de {radio_km} km',
                                        yaxis_title=titulo_var,
                                        showlegend=True,
                                        height=500,
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        paper_bgcolor='rgba(0,0,0,0)'
                                    )
                                    
                                        st.plotly_chart(fig_radio, use_container_width=True, theme="streamlit")
                                    else:
                                        st.warning(f"ℹ️ No se encontraron grupos dentro de {radio_km} km de tu ubicación")

                    elif analysis_type == "Análisis por altitud":
                        st.header("Comparación por Altitudes")
                    
                        # Verificar que existe la columna altitud
                        if 'altitud' not in df_completo.columns:
                            st.error("No se encontró la columna 'altitud' en los datos")
                        else:
                            # Obtener variables numéricas de la configuración
                            variables_numericas = [var_id for var_id, var_config in variables_config.items() 
                                              if var_config['tipo'] in ['number', 'select']]
                        
                            if not variables_numericas:
                                st.warning("No hay variables numéricas configuradas")
                            else:
                            #     Crear nombres descriptivos para el selectbox
                                opciones_variables = []
                                for var_id in variables_numericas:
                                    var_config = variables_config[var_id]
                                    nombre_completo = f"{var_config['nombre']} ({var_id})"
                                    if 'unidad' in var_config:
                                        nombre_completo = f"{var_config['nombre']} ({var_config['unidad']}) - {var_id}"
                                opciones_variables.append((var_id, nombre_completo))
                            
                                # Selector de variable
                                variable_seleccionada = st.selectbox(
                                "Selecciona la variable a analizar:", 
                                options=[opt[0] for opt in opciones_variables],
                                format_func=lambda x: next((opt[1] for opt in opciones_variables if opt[0] == x), x),
                                key="variable_altitud"
                            )
                            
                                # Selector de grupos para comparar
                                grupos_seleccionados = st.multiselect(
                                "Selecciona grupos para comparar:", 
                                options=grupos_comparacion, 
                                default=[], 
                                key="grupos_altitud"
                            )
                            
                                if variable_seleccionada and grupos_seleccionados:
                                    # Combinar grupos para análisis
                                    todos_grupos_plot = [grupo_usuario_actual] + grupos_seleccionados
                                    datos_altitud = df_completo[df_completo['grupo'].isin(todos_grupos_plot)]
                                
                                    # Obtener nombre de variable para el título y etiquetas
                                    var_config = variables_config.get(variable_seleccionada, {})
                                    nombre_var = var_config.get('nombre', variable_seleccionada)
                                    unidad_var = var_config.get('unidad', '')
                                
                                    # Crear gráfico de dispersión altitud vs variable
                                    fig_altitud = px.scatter(
                                    datos_altitud,
                                    x='altitud',
                                    y=variable_seleccionada,
                                    color='grupo',
                                    title=f'Relación Altitud vs {nombre_var}',
                                    labels={
                                        'altitud': 'Altitud (m)',
                                        variable_seleccionada: f"{nombre_var} ({unidad_var})" if unidad_var else nombre_var,
                                        'grupo': 'Grupo'
                                    },
                                    hover_data=['fecha', 'hora', 'usuario']
                                )
                                
                                    fig_altitud.update_layout(height=500)
                                    st.plotly_chart(fig_altitud, use_container_width=True)

                    elif analysis_type == "Comparación entre grupos":
                        st.header("📊 Comparación entre grupos")
                    
                        # Obtener variables numéricas de la configuración
                        variables_numericas = [var_id for var_id, var_config in variables_config.items() 
                                          if var_config['tipo'] in ['number', 'select']]
                    
                        if not variables_numericas:
                            st.warning("No hay variables numéricas configuradas para comparar")
                        else:
                            # Crear nombres descriptivos para el selectbox
                            opciones_variables = []
                            for var_id in variables_numericas:
                                var_config = variables_config[var_id]
                                nombre_completo = f"{var_config['nombre']} ({var_id})"
                                if 'unidad' in var_config:
                                    nombre_completo = f"{var_config['nombre']} ({var_config['unidad']}) - {var_id}"
                            opciones_variables.append((var_id, nombre_completo))
                        
                            # Mostrar selector múltiple de grupos
                            grupos_seleccionados = st.multiselect(
                            "Selecciona grupos para comparar:", 
                            options=grupos_comparacion, 
                            default=[], 
                            key="grupos_comparacion"
                        )
                        
                            # Selector de variable
                            variable_seleccionada = st.selectbox(
                            "Selecciona la variable a analizar:", 
                            options=[opt[0] for opt in opciones_variables],
                            format_func=lambda x: next((opt[1] for opt in opciones_variables if opt[0] == x), x),
                            key="variable_analisis"
                        )
                        
                            # Gráficos tu grupo vs seleccionados
                            if grupos_seleccionados and variable_seleccionada:
                            # Combinar el grupo del usuario + grupo/s seleccionado/s
                                todos_grupos_plot = [grupo_usuario_actual] + grupos_seleccionados
                            
                                # Filtrar datos para los grupos
                                datos_comparacion = df_completo[df_completo['grupo'].isin(todos_grupos_plot)]
                            
                                # Obtener nombre de variable para el título
                                var_config = variables_config.get(variable_seleccionada, {})
                                nombre_var = var_config.get('nombre', variable_seleccionada)
                                unidad_var = var_config.get('unidad', '')
                            
                                fig = go.Figure()
                                for grupo in todos_grupos_plot:
                                    datos_grupo_seleccionado = datos_comparacion[datos_comparacion['grupo'] == grupo][variable_seleccionada].dropna().values
                                
                                    if len(datos_grupo_seleccionado) > 0:
                                        # Destacar el grupo actual con color diferente
                                        es_grupo_actual = (grupo == grupo_usuario_actual)
                                        colores = ['#FF4B4B', '#1F77B4', '#2CA02C', '#FF7F0E', '#9467BD', '#8C564B', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF']
                                        color_idx = todos_grupos_plot.index(grupo) % len(colores)
                                        color = colores[color_idx]
                                        nombre_grupo = f"{grupo} (TU GRUPO)" if es_grupo_actual else str(grupo)
                                    
                                        # Gráfico grupo vs grupo/s seleccionado/s
                                        fig.add_trace(go.Violin(
                                        y=datos_grupo_seleccionado,
                                        name=nombre_grupo,
                                        box_visible=True,
                                        meanline_visible=True,
                                        points=False,
                                        side='positive',
                                        hoverinfo='y+name',
                                        line_color=color,
                                        fillcolor='rgba(255, 75, 75, 0.2)' if es_grupo_actual else f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)'
                                    ))
                            
                            # Configurar título con nombre de variable
                                titulo_var = f"{nombre_var} ({unidad_var})" if unidad_var else nombre_var
                            
                                fig.update_layout(
                                title=f'Comparación: {titulo_var} - Tu Grupo vs Seleccionados',
                                xaxis_title=f'{titulo_var} - Tu Grupo ({grupo_usuario_actual})',
                                yaxis_title=f'{titulo_var} - Grupos Seleccionados',
                                showlegend=True,
                                height=500
                            )
                                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    footer()
