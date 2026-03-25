import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración estética de la página
st.set_page_config(page_title="Vanguard Notes v1.0", layout="wide", initial_sidebar_state="expanded")

# --- ESTILO CSS AVANZADO (NEÓN VANGUARDISTA) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    [data-testid="stMetricValue"] { color: #00F2FF !important; font-size: 36px; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #7000FF , #00F2FF); }
    h1, h2, h3 { color: #00F2FF; text-shadow: 0px 0px 10px rgba(0, 242, 255, 0.3); }
    .stAlert { background-color: #1A1C24; border: 1px solid #7000FF; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PARA CARGAR DATOS ---
@st.cache_data
def load_data():
    file_path = "notas_estudiantes.xlsx"
    try:
        # Lee todas las pestañas del Excel
        return pd.read_excel(file_path, sheet_name=None)
    except Exception as e:
        st.error(f"No se encontró el archivo 'notas_estudiantes.xlsx' o el formato es incorrecto.")
        return None

dict_cursos = load_data()

# --- INTERFAZ LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
st.sidebar.title("Portal Estudiantil")

if dict_cursos:
    lista_cursos = list(dict_cursos.keys())
    curso_sel = st.sidebar.selectbox("Selecciona la Asignatura:", lista_cursos)
    id_usuario = st.sidebar.text_input("Ingresa tu ID de Estudiante:", placeholder="Ej: 2024001")
    
    df_actual = dict_cursos[curso_sel]
    # Limpieza: IDs a string y llenar vacíos con 0
    df_actual['ID'] = df_actual['ID'].astype(str)
    df_actual = df_actual.fillna(0)

    if id_usuario:
        datos_estudiante = df_actual[df_actual['ID'] == id_usuario]

        if not datos_estudiante.empty:
            est = datos_estudiante.iloc[0]
            st.title(f"📊 Estado Académico: {id_usuario}")
            
            # --- SECCIÓN 1: MÉTRICAS CLAVE ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Parcial 1 (P1)", f"{est['P1']:.1f}")
            with col2:
                st.metric("Parcial 2 (P2)", f"{est['P2']:.1f}")
            with col3:
                st.metric("Nota 1er Corte", f"{est['1CTE']:.1f}", delta_color="normal")

            # --- SECCIÓN 2: PROGRESO GLOBAL (META 3.0) ---
            st.subheader("🚀 Evolución Global del Semestre")
            # El 1er Corte vale el 50% del total del semestre
            peso_actual = est['1CTE'] * 0.5 
            progreso_visual = min(peso_actual / 3.0, 1.0)
            
            st.progress(progreso_visual)
            
            if peso_actual < 3.0:
                puntos_faltantes = 3.0 - peso_actual
                st.info(f"Vas por buen camino. Te faltan **{puntos_faltantes:.2f}** unidades (sobre el total de 5.0) para asegurar el aprobado del semestre.")
            else:
                st.success("¡Meta de aprobación alcanzada para este corte!")

            # --- SECCIÓN 3: GRÁFICO DE RADAR (COMPARATIVO) ---
            st.divider()
            st.subheader("🎯 Comparativa de Rendimiento")
            
            promedio_curso = df_actual[['P1', 'P2', '1CTE']].mean()
            
            # Creamos el gráfico de radar
            fig = go.Figure()
            
            # Capa del Estudiante
            fig.add_trace(go.Scatterpolar(
                r=[est['P1'], est['P2'], est['1CTE']],
                theta=['Parcial 1', 'Parcial 2', 'Corte Final'],
                fill='toself',
                name='Tus Notas',
                line_color='#00F2FF'
            ))
            
            # Capa del Promedio General
            fig.add_trace(go.Scatterpolar(
                r=[promedio_curso['P1'], promedio_curso['P2'], promedio_curso['1CTE']],
                theta=['Parcial 1', 'Parcial 2', 'Corte Final'],
                fill='toself',
                name='Promedio del Grupo',
                line_color='#7000FF',
                opacity=0.5
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="#444")),
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # --- SECCIÓN 4: DETALLE DE TALLERES ---
            with st.expander("📝 Ver desglose de talleres y quices"):
                # Filtramos columnas que empiecen por 'Ta' o 'Q' o 'CN' o 'PQT'
                cols_det = [c for c in df_actual.columns if any(x in c for x in ['Ta', 'Q', 'CN', 'PQT'])]
                st.dataframe(datos_estudiante[cols_det].style.highlight_max(axis=0, color='#1A3A3A'))

        else:
            st.warning("⚠️ ID no encontrado en este curso. Por favor verifica.")
    else:
        st.info("👋 Por favor, ingresa tu ID en la barra lateral para ver tus resultados.")

else:
    st.error("Error: Sube el archivo 'notas_estudiantes.xlsx' para activar el sistema.")
