import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(page_title="Vanguard Notes | Student Portal", layout="wide")

# --- ESTILO VANGUARDISTA (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; padding: 20px; }
    [data-testid="stMetricValue"] { color: #00F2FF !important; font-family: 'JetBrains Mono', monospace; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #7000FF , #00F2FF); }
    h1, h2, h3 { color: #00F2FF; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    file_path = "app_notas.xlsx"
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        # Retorna un diccionario donde la llave es el nombre del curso (pestaña)
        return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        st.error(f"Error: No se encontró '{file_path}'. Asegúrate de subirlo a GitHub.")
        return None

dict_cursos = load_data()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("🧬 VANGUARD AI")
if dict_cursos:
    curso_sel = st.sidebar.selectbox("Seleccione la Asignatura", list(dict_cursos.keys()))
    id_estudiante = st.sidebar.text_input("Identificación del Estudiante", placeholder="Ej: 123456")

    df_actual = dict_cursos[curso_sel].fillna(0)
    df_actual['ID'] = df_actual['ID'].astype(str)

    if id_estudiante:
        est = df_actual[df_actual['ID'] == id_estudiante]

        if not est.empty:
            row = est.iloc[0]
            st.title(f"Dashboard de Rendimiento")
            st.markdown(f"**Estudiante ID:** `{id_estudiante}` | **Curso:** {curso_sel}")

            # --- SECCIÓN 1: MÉTRICAS PRINCIPALES ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Parcial 1 (P1)", f"{row['P1']:.1f}")
            with col2:
                st.metric("Parcial 2 (P2)", f"{row['P2']:.1f}")
            with col3:
                st.metric("Nota 1er Corte (1CTE)", f"{row['1CTE']:.1f}")

            # --- SECCIÓN 2: BARRA DE PROGRESO GLOBAL ---
            st.divider()
            st.subheader("🏁 Evolución del Semestre (Hacia el 3.0)")
            # El 1er corte aporta el 50% de la nota final (máximo 2.5 puntos de 5.0)
            puntos_acumulados = row['1CTE'] * 0.5
            porcentaje_meta = min(puntos_acumulados / 3.0, 1.0)
            
            st.progress(porcentaje_meta)
            st.write(f"Has acumulado **{puntos_acumulados:.2f}** puntos de los **3.0** necesarios para aprobar.")

            # --- SECCIÓN 3: GRÁFICO DE RADAR ---
            st.divider()
            col_a, col_b = st.columns([1.5, 1])
            
            with col_a:
                st.subheader("🎯 Comparativa de Capacidades")
                promedio_grupo = df_actual[['P1', 'P2', '1CTE']].mean()
                
                fig = go.Figure()
                # Capa Estudiante
                fig.add_trace(go.Scatterpolar(
                    r=[row['P1'], row['P2'], row['1CTE']],
                    theta=['Parcial 1', 'Parcial 2', 'Corte Final'],
                    fill='toself', name='Tus Resultados', line_color='#00F2FF'
                ))
                # Capa Promedio
                fig.add_trace(go.Scatterpolar(
                    r=[promedio_grupo['P1'], promedio_grupo['P2'], promedio_grupo['1CTE']],
                    theta=['Parcial 1', 'Parcial 2', 'Corte Final'],
                    fill='toself', name='Promedio Clase', line_color='#7000FF', opacity=0.4
                ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="#30363D")),
                    template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.subheader("📝 Detalle de Talleres")
                # Identifica dinámicamente columnas de talleres y quices
                cols_extra = [c for c in df_actual.columns if any(x in c for x in ['Ta', 'Q', 'CN', 'PQT'])]
                if cols_extra:
                    for col in cols_extra:
                        st.write(f"**{col}:** {row[col]}")
                else:
                    st.info("No hay talleres registrados aún.")

            # --- SECCIÓN 4: SIMULADOR ---
            st.divider()
            st.subheader("🔮 Simulador de Aprobación")
            meta_2do_corte = st.slider("¿Qué nota esperas promediar en el segundo corte?", 0.0, 5.0, 3.0, 0.1)
            nota_final_est = puntos_acumulados + (meta_2do_corte * 0.5)
            
            if nota_final_est >= 3.0:
                st.balloons()
                st.success(f"Con un {meta_2do_corte} en el segundo corte, tu nota final sería **{nota_final_est:.2f}**. ¡Aprobado!")
            else:
                st.error(f"Tu nota final sería **{nota_final_est:.2f}**. Necesitas un promedio más alto en el segundo corte.")

        else:
            st.warning("⚠️ ID no encontrado en esta asignatura.")
    else:
        st.info("Ingresa tu ID en el panel izquierdo para visualizar tus notas.")
else:
    st.warning("Aguardando carga del archivo de datos...")
