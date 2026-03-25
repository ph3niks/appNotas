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
    h1, h2 { color: #00F2FF; font-family: 'Inter', sans-serif; }
    .nombre-estudiante { font-size: 24px; color: #7000FF; font-weight: bold; margin-bottom: 20px; }
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
        st.error(f"Error al cargar 'app_notas.xlsx': {e}")
        return None

dict_cursos = load_data()

# --- BARRA LATERAL ---
st.sidebar.title("💎 VANGUARD PORTAL")
if dict_cursos:
    nrc_sel = st.sidebar.selectbox("Seleccione el NRC del Curso", list(dict_cursos.keys()))
    # Convertimos a string para asegurar el mapeo
    nombre_materia = MAPA_CURSOS.get(str(nrc_sel), "Asignatura General")
    id_estudiante = st.sidebar.text_input("Ingrese su ID de Estudiante")

    df_actual = dict_cursos[nrc_sel].fillna(0)
    df_actual['ID'] = df_actual['ID'].astype(str)

    if id_estudiante:
        est = df_actual[df_actual['ID'] == id_estudiante]

        if not est.empty:
            row = est.iloc[0]
            
            # --- IDENTIFICACIÓN DEL ESTUDIANTE ---
            # Asumimos que la columna se llama 'Nombre' o 'Estudiante'
            nombre_u = row.get('Nombre', row.get('NOMBRE', 'Estudiante'))
            
            st.markdown(f"### Bienvenid@, <span style='color:#00F2FF'>{nombre_u}</span>", unsafe_allow_html=True)
            st.markdown(f"**Curso:** {nombre_materia} | **NRC:** {nrc_sel}")

            # --- SECCIÓN 1: KPIs ---
            st.divider()
            cols = st.columns(4)
            cols[0].metric("Parcial 1 (P1)", f"{row.get('P1', 0):.1f}")
            cols[1].metric("Parcial 2 (P2)", f"{row.get('P2', 0):.1f}")
            
            # Lógica para CN, PA o PQT
            if 'CN' in row and row['CN'] > 0:
                cols[2].metric("Nivelación (CN)", f"{row['CN']:.1f}")
            elif 'PA' in row and row['PA'] > 0:
                cols[2].metric("Proyecto (PA)", f"{row['PA']:.1f}")
            else:
                val_pqt = row.get('PQT1', row.get('PQT', 0))
                cols[2].metric("Promedio PQT", f"{val_pqt:.1f}")
            
            cols[3].metric("NOTA 1er CORTE", f"{row['1CTE']:.1f}")

            # --- SECCIÓN 2: TABLA DETALLADA (SOLUCIÓN AL ERROR) ---
            st.subheader("📋 Registro Detallado de Notas")
            
            # FILTRO DINÁMICO: Solo columnas numéricas y con valores mayores a 0
            # Evitamos errores comparando tipos de datos
            cols_con_datos = []
            for col in df_actual.columns:
                # Si la columna es numérica y el valor es mayor a 0
                if pd.api.types.is_number(row[col]) and row[col] > 0:
                    # Excluimos el ID y el NRC si estuvieran como números
                    if col not in ['ID', 'NRC']:
                        cols_con_datos.append(col)
            
            # Mostramos la fila con el nombre y sus notas
            # Incluimos 'Nombre' manualmente al inicio si existe para que se vea en la tabla
            cols_finales = (['Nombre'] if 'Nombre' in row else []) + cols_con_datos
            st.dataframe(est[cols_finales].style.format(subset=cols_con_datos, formatter="{:.1f}"), use_container_width=True)

            # --- SECCIÓN 3: PROGRESO ---
            st.subheader("📈 Evolución Global (Meta de Aprobación)")
            # Asumiendo 1CTE es el 50% del semestre
            puntos_acumulados = row['1CTE'] * 0.5
            progreso_meta = min(puntos_acumulados / 3.0, 1.0)
            
            st.progress(progreso_meta)
            st.write(f"Has acumulado **{puntos_acumulados:.2f}** puntos hacia el mínimo de **3.0**.")

        else:
            st.warning("⚠️ ID no encontrado en este NRC.")
else:
    st.error("Archivo 'app_notas.xlsx' no detectado.")
