import streamlit as st
import pandas as pd
import plotly.graph_objects as go
#import streamlit as st
#import pandas as pd

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

# 3. ESTILO CSS ÚNICO
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
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #7000FF , #00F2FF); }
    h1, h2, h3 { color: #00F2FF; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = "app_notas.xlsx"
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        data = {}
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            for col in df.columns:
                if col not in ['NOMBRE', 'ID', 'NRC']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            data[sheet] = df
        return data
    except Exception as e:
        st.error(f"Error al cargar: {e}")
        return None

def round_nota(val):
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
            
            # --- SECCIÓN DE PROGRESO GLOBAL ---
            st.subheader("📈 Estado de la Materia (Escala 0.0 - 5.0)")
            
            # Calculamos los puntos sobre 5.0 (Corte 1 vale 2.5 max, Corte 2 vale 2.5 max)
            puntos_c1 = round_nota(row.get('1CTE', 0)) * 0.5
            puntos_c2 = round_nota(row.get('2CTE', 0)) * 0.5
            puntos_totales = puntos_c1 + puntos_c2
            
            # Color dinámico: Azul si no ha pasado, Verde si ya superó el 3.0
            color_barra = "#00F2FF" if puntos_totales < 3.0 else "#00FF41" 
            
            # Creamos una barra personalizada con HTML para permitir el cambio de color
            st.markdown(f"""
                <div style="width: 100%; background-color: #30363D; border-radius: 20px; height: 25px; margin-bottom: 10px;">
                    <div style="width: {(puntos_totales/5)*100}%; background-color: {color_barra}; height: 100%; border-radius: 20px; transition: width 0.5s;">
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>0.0</span>
                    <span style="color: #00FF41; font-weight: bold;">| Meta: 3.0</span>
                    <span>5.0</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"Nota acumulada actual: **{puntos_totales:.2f}**")

            # --- SISTEMA DE PESTAÑAS ---
            tab1, tab2, tab3 = st.tabs(["📌 1er Corte", "🚀 2do Corte", "🎯 Simulador Final"])

            with tab1:
                c1_cols = st.columns(4)
                c1_cols[0].metric("Parcial 1", f"{round_nota(row.get('P1', 0)):.1f}")
                c1_cols[1].metric("Parcial 2", f"{round_nota(row.get('P2', 0)):.1f}")
                c1_cols[2].metric("Promedio Talleres", f"{round_nota(row.get('PQT1', row.get('PQT', 0))):.1f}")
                c1_cols[3].metric("Nota 1er Corte", f"{round_nota(row.get('1CTE', 0)):.1f}")

                st.subheader("📝 Talleres 1er Corte")
                # Filtramos Ta1 a Ta6
                t_cols_1 = [c for c in df_actual.columns if c.startswith('Ta') and c in [f'Ta{i}' for i in range(1, 7)] and row[c] > 0]
                if t_cols_1:
                    mapping = {c: f"Taller No {c.replace('Ta','')}" for c in t_cols_1}
                    st.dataframe(est[t_cols_1].rename(columns=mapping).style.format("{:.1f}"), use_container_width=True, hide_index=True)

            with tab2:
                c2_cols = st.columns(4)
                c2_cols[0].metric("Parcial 3", f"{round_nota(row.get('P3', 0)):.1f}")
                c2_cols[1].metric("Parcial 4", f"{round_nota(row.get('P4', 0)):.1f}")
                c2_cols[2].metric("Promedio Talleres", f"{round_nota(row.get('PQT2', 0)):.1f}")
                c2_cols[3].metric("Nota 2do Corte", f"{round_nota(row.get('2CTE', 0)):.1f}")

                st.subheader("📝 Talleres 2do Corte")
                # Filtramos Ta7 en adelante
                t_cols_2 = [c for c in df_actual.columns if c.startswith('Ta') and c not in [f'Ta{i}' for i in range(1, 7)] and row[c] > 0]
                if t_cols_2:
                    mapping = {c: f"Taller No {c.replace('Ta','')}" for c in t_cols_2}
                    st.dataframe(est[t_cols_2].rename(columns=mapping).style.format("{:.1f}"), use_container_width=True, hide_index=True)
                else:
                    st.info("Aún no se han registrado talleres para el segundo corte.")

            with tab3:
                st.subheader("🔮 Simulador de Supervivencia")
                
                # Cálculo de lo que falta para el 3.0
                # Formula: (3.0 - (NotaCorte1 * 0.5)) / 0.5
                nota_necesaria = (3.0 - puntos_c1) / 0.5
                
                if puntos_totales >= 3.0:
                    st.balloons()
                    st.success(f"🎊 **¡ZONA SEGURA!** Ya has aprobado la materia. Tu nota actual es **{puntos_totales:.2f}**.")
                    st.info("Todo lo que saques en el segundo corte subirá tu promedio final.")
                else:
                    if nota_necesaria > 5.0:
                        st.error(f"⚠️ Situación Crítica: Necesitarías un **{nota_necesaria:.2f}** para pasar, lo cual supera el máximo de 5.0.")
                    else:
                        st.warning(f"🎯 Para aprobar con **3.0**, el promedio de tu Segundo Corte debe ser de al menos: **{nota_necesaria:.2f}**")
                        
                        # Visualización de esfuerzo
                        esfuerzo = (nota_necesaria / 5.0)
                        st.write("Nivel de esfuerzo requerido:")
                        st.progress(min(esfuerzo, 1.0))

        else:
            st.warning("⚠️ ID no encontrado.")
