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

            # --- SECCIÓN 1: KPIs ---
            st.divider()
            cols = st.columns(4)
            cols[0].metric("Parcial 1 (P1)", f"{row.get('P1', 0):.1f}")
            cols[1].metric("Parcial 2 (P2)", f"{row.get('P2', 0):.1f}")
            
            # Lógica dinámica para el tercer KPI
            val_pqt = row.get('PQT1', row.get('PQT', 0))
            label_pqt = "Promedio PQT"
            if 'CN' in row and row['CN'] > 0:
                val_pqt, label_pqt = row['CN'], "Nivelación (CN)"
            elif 'PA' in row and row['PA'] > 0:
                val_pqt, label_pqt = row['PA'], "Proyecto (PA)"
                
            cols[2].metric(label_pqt, f"{val_pqt:.1f}")
            cols[3].metric("NOTA 1er CORTE", f"{row['1CTE']:.1f}")

            # --- SECCIÓN 2: TABLA DETALLADA (FILTRADA) ---
            st.subheader("📋 Registro de Calificaciones")
            
            # Definimos columnas a omitir (ID, NRC y variaciones de Nombre)
            cols_a_omitir = ['ID', 'NRC', 'NOMBRE', 'Nombre', 'nombre', 'estudiante', 'ESTUDIANTE']
            
            # Filtramos columnas: que no estén en la lista de omisión y que tengan nota > 0
            cols_notas = []
            for col in df_actual.columns:
                if col not in cols_a_omitir:
                    # Incluimos 'No' siempre si existe, de lo contrario validamos que sea numérico y > 0
                    if col == 'No' or (pd.api.types.is_number(row[col]) and row[col] > 0):
                        cols_notas.append(col)
            
            # Renderizamos la tabla solo con los datos del estudiante
            st.dataframe(
                est[cols_notas].style.format(
                    # Formateamos con 1 decimal solo las que no sean 'No'
                    formatter="{:.1f}", 
                    subset=[c for c in cols_notas if c != 'No']
                ), 
                use_container_width=True,
                hide_index=True # Ocultamos el índice de pandas para más limpieza
            )

            # --- SECCIÓN 3: PROGRESO GLOBAL ---
            st.divider()
            st.subheader("📈 Evolución hacia la Aprobación")
            # 1er corte = 50% de la nota final. Meta = 3.0 total.
            puntos_acumulados = row['1CTE'] * 0.5
            progreso_meta = min(puntos_acumulados / 3.0, 1.0)
            
            st.progress(progreso_meta)
            st.write(f"Has acumulado **{puntos_acumulados:.2f}** puntos de los **3.0** necesarios para aprobar el semestre.")
            
            if puntos_acumulados >= 1.5:
                st.success("✅ Estás en la zona segura. Mantén el ritmo en el segundo corte.")
            else:
                st.warning("⚠️ Atención: Debes mejorar tu promedio en el segundo corte para alcanzar el 3.0.")

        else:
            st.warning("⚠️ ID no encontrado en este NRC.")
else:
    st.info("Aguardando conexión con el archivo 'app_notas.xlsx'...")
