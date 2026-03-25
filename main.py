import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(page_title="Vanguard Notes | Sistema de Gestión", layout="wide")

# --- ESTILO VANGUARDISTA (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { background-color: #161B22; border-radius: 12px; border: 1px solid #30363D; padding: 15px; }
    [data-testid="stMetricValue"] { color: #00F2FF !important; font-size: 28px; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #7000FF , #00F2FF); }
    h1, h2, h3 { color: #00F2FF; font-family: 'Inter', sans-serif; font-weight: 700; }
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.9em; min-width: 400px; border-radius: 5px 5px 0 0; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- MAPEO DE ASIGNATURAS POR NRC ---
MAPA_CURSOS = {
    "60299": "Matemáticas II",
    "55546": "Matemáticas II",
    "62529": "Matemáticas II",
    "55581": "Cálculo Diferencial",
    "63507": "Estadística Inferencial y Muestreo"
}

@st.cache_data
def load_data():
    file_path = "app_notas.xlsx"
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

dict_cursos = load_data()

# --- BARRA LATERAL ---
st.sidebar.title("💎 VANGUARD PORTAL")
if dict_cursos:
    nrc_sel = st.sidebar.selectbox("Seleccione el NRC del Curso", list(dict_cursos.keys()))
    nombre_materia = MAPA_CURSOS.get(str(nrc_sel), "Asignatura General")
    st.sidebar.markdown(f"**Materia:** {nombre_materia}")
    
    id_estudiante = st.sidebar.text_input("Ingrese su ID de Estudiante")

    df_actual = dict_cursos[nrc_sel].fillna(0)
    df_actual['ID'] = df_actual['ID'].astype(str)

    if id_estudiante:
        est = df_actual[df_actual['ID'] == id_estudiante]

        if not est.empty:
            row = est.iloc[0]
            st.title(f"Dashboard: {nombre_materia}")
            st.caption(f"Estudiante ID: {id_estudiante} | NRC: {nrc_sel}")

            # --- SECCIÓN 1: KPIs (METAS PRINCIPALES) ---
            st.subheader("📌 Resumen de Corte")
            cols = st.columns(4)
            cols[0].metric("Parcial 1 (P1)", f"{row.get('P1', 0):.1f}")
            cols[1].metric("Parcial 2 (P2)", f"{row.get('P2', 0):.1f}")
            
            # Mostrar CN o PA si existen en el dataset
            if 'CN' in row and row['CN'] > 0:
                cols[2].metric("Nivelación (CN)", f"{row['CN']:.1f}")
            elif 'PA' in row and row['PA'] > 0:
                cols[2].metric("Proyecto (PA)", f"{row['PA']:.1f}")
            else:
                # Si no hay CN/PA, mostrar el promedio de quices/talleres PQT
                val_pqt = row.get('PQT1', row.get('PQT', 0))
                cols[2].metric("Promedio PQT", f"{val_pqt:.1f}")
            
            cols[3].metric("NOTA 1er CORTE", f"{row['1CTE']:.1f}", delta="Corte Actual")

            # --- SECCIÓN 2: TABLA DE NOTAS FILTRADA (Vanguardista) ---
            st.divider()
            st.subheader("📋 Registro Detallado de Notas")
            
            # Filtramos solo las columnas que tengan un valor mayor a 0 para este estudiante
            # Excluimos ID para la tabla
            cols_con_datos = [c for c in df_actual.columns if c != 'ID' and row[c] > 0]
            tabla_estudiante = est[cols_con_datos]
            
            st.dataframe(tabla_estudiante.style.format("{:.1f}").background_gradient(cmap='Blues'), use_container_width=True)

            # --- SECCIÓN 3: PROGRESO Y RADAR ---
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.subheader("📈 Evolución Global")
                # Cálculo de progreso hacia el 3.0 (Asumiendo 1CTE es el 50%)
                progreso = (row['1CTE'] * 0.5) / 3.0
                st.progress(min(progreso, 1.0))
                st.write(f"Has completado el **{min(progreso*100, 100.0):.1f}%** del camino requerido para aprobar el semestre.")

            with col_right:
                # Gráfico de Radar comparando con el promedio del curso
                promedio_nrc = df_actual[['P1', 'P2', '1CTE']].mean()
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row['P1'], row['P2'], row['1CTE']],
                    theta=['P1', 'P2', '1er Corte'], fill='toself', name='Tú', line_color='#00F2FF'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=[promedio_nrc['P1'], promedio_nrc['P2'], promedio_nrc['1CTE']],
                    theta=['P1', 'P2', '1er Corte'], fill='toself', name='Promedio NRC', line_color='#7000FF', opacity=0.5
                ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), template="plotly_dark", 
                                  margin=dict(l=40, r=40, t=20, b=20), height=300)
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("⚠️ ID no encontrado en este NRC.")
else:
    st.error("Archivo 'app_notas.xlsx' no detectado.")
