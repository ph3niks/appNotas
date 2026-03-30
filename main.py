import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURACIÓN INICIAL (DEBE SER LA PRIMERA)
st.set_page_config(page_title="Vanguard Notes | Portal Académico", layout="wide")

# 2. DICCIONARIO DE MATERIAS
MAPA_CURSOS = {
    "60299": "Matemáticas II",
    "55546": "Matemáticas II",
    "62529": "Matemáticas II",
    "55581": "Cálculo Diferencial",
    "63507": "Estadística Inferencial y Muestreo"
}

# 3. ESTILO CSS ÚNICO (Incluye el diseño de etiquetas y métricas)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { 
        background-color: #161B22; 
        border-radius: 12px; 
        border: 1px solid #30363D; 
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #00F2FF !important; font-weight: 700; }
    [data-testid="stMetricLabel"] p { 
        color: #E0E0E0 !important; 
        font-size: 1.1rem !important; 
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h1, h2, h3 { color: #00F2FF; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = "app_notas.xlsx"
    try:
        # Cargamos el Excel. Streamlit Cloud leerá el archivo que subas al repo.
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        data = {}
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            # Limpieza de datos: Convertir a número y manejar errores de formato/fechas
            for col in df.columns:
                if col not in ['NOMBRE', 'ID', 'NRC']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            data[sheet] = df
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return None

def round_nota(val):
    """Función de redondeo académico (0.5 sube al siguiente)"""
    return float(pd.Series([val]).apply(lambda x: round(x + 0.0000001, 1))[0])

dict_cursos = load_data()

# --- BARRA LATERAL ---
st.sidebar.title("💎 VANGUARD PORTAL")
if dict_cursos:
    nrc_sel = st.sidebar.selectbox("Seleccione el NRC del Curso", list(dict_cursos.keys()))
    nrc_limpio = str(nrc_sel).replace("NRC", "").strip()
    nombre_materia = MAPA_CURSOS.get(nrc_limpio, "Asignatura General")
    id_estudiante = st.sidebar.text_input("Ingrese su ID de Estudiante")

    if id_estudiante:
        df_actual = dict_cursos[nrc_sel]
        df_actual['ID'] = df_actual['ID'].astype(str)
        est = df_actual[df_actual['ID'] == id_estudiante]

        if not est.empty:
            row = est.iloc[0]
            nombre_u = row.get('NOMBRE', row.get('Nombre', 'Estudiante'))
            
            # --- LÓGICA DE POSICIÓN DE COLUMNAS ---
            todas_las_columnas = list(df_actual.columns)
            try:
                indice_p3 = todas_las_columnas.index('P3')
            except ValueError:
                indice_p3 = len(todas_las_columnas)

            # --- CABECERA ---
            st.markdown(f"### Bienvenid@, <span style='color:#00F2FF'>{nombre_u}</span>", unsafe_allow_html=True)
            st.markdown(f"**Asignatura:** {nombre_materia} | **NRC:** {nrc_sel}")
            
            # --- PROGRESO GLOBAL (ESCALA 0-5) ---
            st.subheader("📈 Estado de la Materia (Meta 3.0)")
            puntos_c1 = round_nota(row.get('1CTE', 0)) * 0.5
            puntos_c2 = round_nota(row.get('2CTE', 0)) * 0.5
            puntos_totales = puntos_c1 + puntos_c2
            
            # Color dinámico: Verde si pasó, Azul si no
            color_barra = "#00FF41" if puntos_totales >= 3.0 else "#00F2FF"
            
            st.markdown(f"""
                <div style="width: 100%; background-color: #30363D; border-radius: 20px; height: 25px; margin-bottom: 5px;">
                    <div style="width: {min((puntos_totales/5)*100, 100)}%; background-color: {color_barra}; 
                                height: 100%; border-radius: 20px; transition: width 0.5s;
                                box-shadow: 0 0 10px {color_barra};">
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #E0E0E0;">
                    <span>0.0</span>
                    <span style="color: #00FF41; font-weight: bold;">META: 3.0</span>
                    <span>5.0</span>
                </div>
            """, unsafe_allow_html=True)
            st.write(f"Nota acumulada actual: **{puntos_totales:.2f} / 5.0**")
            st.divider()

            # --- SISTEMA DE PESTAÑAS ---
            tab1, tab2, tab3 = st.tabs(["📌 1er Corte", "🚀 2do Corte", "🎯 Simulador Final"])

            with tab1:
                st.subheader("Resultados Consolidados")
                c1_cols = st.columns(4)
                c1_cols[0].metric("Parcial 1", f"{round_nota(row.get('P1', 0)):.1f}")
                c1_cols[1].metric("Parcial 2", f"{round_nota(row.get('P2', 0)):.1f}")
                # Buscamos PQT o PQT1
                pqt1_val = row.get('PQT1', row.get('PQT', 0))
                c1_cols[2].metric("Promedio Talleres", f"{round_nota(pqt1_val):.1f}")
                c1_cols[3].metric("Nota 1er Corte", f"{round_nota(row.get('1CTE', 0)):.1f}")

                st.subheader("📝 Talleres 1er Corte")
                # Talleres antes de P3
                t_cols_1 = [c for c in todas_las_columnas if c.startswith('Ta') and 
                            todas_las_columnas.index(c) < indice_p3 and row[c] > 0]
                if t_cols_1:
                    mapping1 = {c: f"Taller No {c.replace('Ta','')}" for c in t_cols_1}
                    st.dataframe(est[t_cols_1].rename(columns=mapping1).style.format("{:.1f}"), 
                                 use_container_width=True, hide_index=True)

            with tab2:
                st.subheader("Resultados Consolidados")
                c2_cols = st.columns(4)
                c2_cols[0].metric("Parcial 3", f"{round_nota(row.get('P3', 0)):.1f}")
                c2_cols[1].metric("Parcial 4", f"{round_nota(row.get('P4', 0)):.1f}")
                # Buscamos PQT2 o el segundo PQT
                pqt2_val = row.get('PQT2', 0)
                c2_cols[2].metric("Promedio Talleres", f"{round_nota(pqt2_val):.1f}")
                c2_cols[3].metric("Nota 2do Corte", f"{round_nota(row.get('2CTE', 0)):.1f}")

                st.subheader("📝 Talleres 2do Corte")
                # Talleres después de P3
                t_cols_2 = [c for c in todas_las_columnas if c.startswith('Ta') and 
                            todas_las_columnas.index(c) > indice_p3 and row[c] > 0]
                if t_cols_2:
                    mapping2 = {c: f"Taller No {c.replace('Ta','')}" for c in t_cols_2}
                    st.dataframe(est[t_cols_2].rename(columns=mapping2).style.format("{:.1f}"), 
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("Aún no se han registrado talleres para el segundo corte.")

            with tab3:
                st.subheader("🔮 ¿Qué necesitas para pasar?")
                # Lo que falta para llegar a 3.0 sabiendo que el 1er corte ya puso su parte
                nota_necesaria = (3.0 - puntos_c1) / 0.5
                
                if puntos_totales >= 3.0:
                    st.balloons()
                    st.success(f"🎊 **¡ZONA SEGURA!** Ya has aprobado la materia con **{puntos_totales:.2f}**.")
                else:
                    if nota_necesaria > 5.0:
                        st.error(f"⚠️ Situación Crítica: Necesitarías un **{nota_necesaria:.2f}** para pasar.")
                    else:
                        st.warning(f"🎯 Para aprobar con 3.0, necesitas un **{nota_necesaria:.2f}** en el promedio del 2do Corte.")
        else:
            st.warning("⚠️ ID de estudiante no encontrado en este NRC.")
else:
    st.info("Esperando carga de datos...")
