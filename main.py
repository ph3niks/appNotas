import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración estética
st.set_page_config(page_title="Vanguard Notes | Portal Académico", layout="wide")

# --- ESTILO VANGUARDISTA (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { background-color: #161B22; border-radius: 12px; border: 1px solid #30363D; padding: 15px; }
    [data-testid="stMetricValue"] { color: #00F2FF !important; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #7000FF , #00F2FF); }
    h1, h2, h3 { color: #00F2FF; font-family: 'Inter', sans-serif; }
    /* Estilo para tablas */
    .stDataFrame { border: 1px solid #30363D; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MAPEO DE ASIGNATURAS ---
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
        st.error(f"Error al cargar 'app_notas.xlsx': {e}")
        return None

dict_cursos = load_data()

# --- BARRA LATERAL ---
st.sidebar.title("💎 VANGUARD PORTAL")
if dict_cursos:
    nrc_sel = st.sidebar.selectbox("Seleccione el NRC del Curso", list(dict_cursos.keys()))
    
    # Limpieza de NRC para el mapeo de nombres
    nrc_limpio = str(nrc_sel).replace("NRC", "").strip()
    nombre_materia = MAPA_CURSOS.get(nrc_limpio, "Asignatura General")
    
    id_estudiante = st.sidebar.text_input("Ingrese su ID de Estudiante")

    df_actual = dict_cursos[nrc_sel].fillna(0)
    df_actual['ID'] = df_actual['ID'].astype(str)

    if id_estudiante:
        est = df_actual[df_actual['ID'] == id_estudiante]

        if not est.empty:
            row = est.iloc[0]
            
            # Saludo con el nombre (extraído del Excel)
            nombre_u = row.get('NOMBRE', row.get('Nombre', 'Estudiante'))
            
            st.markdown(f"### Bienvenid@, <span style='color:#00F2FF'>{nombre_u}</span>", unsafe_allow_html=True)
            st.markdown(f"**Asignatura:** {nombre_materia} | **NRC:** {nrc_sel}")

            # --- SECCIÓN 1: KPIs (Update Líneas 82-95) ---
            st.divider()
            cols = st.columns(4)
            
            # Aplicamos redondeo a 1 decimal (.1f) para cumplir tu regla
            cols[0].metric("Parcial 1 (P1)", f"{round(float(row.get('P1', 0)), 1):.1f}")
            cols[1].metric("Parcial 2 (P2)", f"{round(float(row.get('P2', 0)), 1):.1f}")
            
            val_pqt = row.get('PQT1', row.get('PQT', 0))
            cols[2].metric("Promedio PQT", f"{round(float(val_pqt), 1):.1f}")
            cols[3].metric("NOTA 1er CORTE", f"{round(float(row.get('1CTE', 0)), 1):.1f}")

            # --- SECCIÓN 2: REGISTRO DE TALLERES (Update Líneas 98-117) ---
            st.subheader("📝 Registro Detallado: Talleres y Quices")
            
            cols_detalle = []
            nombres_nuevos = {}
            
            for col in df_actual.columns:
                if col == 'No':
                    cols_detalle.append(col)
                # Buscamos columnas que empiecen por Ta o Q
                elif col.startswith(('Ta', 'Q')):
                    # Verificamos que sea número y mayor a 0 (para incluir el 0.1)
                    if pd.api.types.is_number(row[col]) and row[col] > 0:
                        cols_detalle.append(col)
                        # Creamos el nombre elegante: Ta1 -> Taller No 1
                        tipo = "Taller" if col.startswith('Ta') else "Quiz"
                        num = col.replace('Ta', '').replace('Q', '')
                        nombres_nuevos[col] = f"{tipo} No {num}"
            
            # Filtramos y renombramos
            df_vanguard = est[cols_detalle].rename(columns=nombres_nuevos)
            
            # Mostramos la tabla con redondeo a 1 decimal
            st.dataframe(
                df_vanguard.style.format(
                    formatter="{:.1f}", 
                    subset=[c for c in df_vanguard.columns if c != 'No']
                ), 
                use_container_width=True,
                hide_index=True
            )

            # --- SECCIÓN 3: PROGRESO (Update Líneas 120-128) ---
            st.divider()
            st.subheader("📈 Estado de Aprobación Semestral")
            puntos_actuales = row['1CTE'] * 0.5
            porcentaje = min(puntos_actuales / 3.0, 1.0)
            
            st.progress(porcentaje)
            st.write(f"Has acumulado **{puntos_actuales:.2f}** / 3.0 puntos necesarios.")
            
            # Mensaje de feedback elegante
            if puntos_actuales >= 1.5:
                st.success("✨ Excelente desempeño en este corte. Vas por encima de la media requerida.")
            else:
                st.info("💡 Recuerda que el segundo corte es una oportunidad para fortalecer tu promedio global.")
