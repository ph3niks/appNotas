import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Vanguard Notes | Portal Académico", layout="wide")

# 2. DICCIONARIO DE MATERIAS
MAPA_CURSOS = {
    "60299": "Matemáticas II",
    "55546": "Matemáticas II",
    "62529": "Matemáticas II",
    "55581": "Cálculo Diferencial",
    "63507": "Estadística Inferencial y Muestreo"
}

# 3. ESTILO CSS AVANZADO (KPIs y Tarjetas de Talleres)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    
    /* Estilo de los KPIs Principales */
    [data-testid="stMetric"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #E0E0E0 !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }
    [data-testid="stMetricValue"] {
        color: #00F2FF !important;
    }

    /* Estilo para las "Tarjetas" de Talleres (Moderno) */
    .taller-card {
        background-color: #1c2128;
        border: 1px solid #444c56;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
        transition: transform 0.3s;
    }
    .taller-card:hover {
        border-color: #00F2FF;
        transform: translateY(-3px);
    }
    .taller-label {
        color: #8b949e;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        display: block;
        margin-bottom: 5px;
    }
    .taller-value {
        color: #00F2FF;
        font-size: 1.2rem;
        font-weight: bold;
    }
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
            df.columns = [str(c).strip().upper() for c in df.columns]
            for col in df.columns:
                if col not in ['NOMBRE', 'ID', 'NRC']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            data[sheet] = df
        return data
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return None

def round_nota(val):
    return float(pd.Series([val]).apply(lambda x: round(x + 0.0000001, 1))[0])

dict_cursos = load_data()

# --- INTERFAZ ---
st.sidebar.title("💎 VANGUARD PORTAL")
if dict_cursos:
    nrc_sel = st.sidebar.selectbox("Seleccione el NRC", list(dict_cursos.keys()))
    nrc_limpio = str(nrc_sel).replace("NRC", "").strip()
    nombre_materia = MAPA_CURSOS.get(nrc_limpio, "Asignatura General")
    id_estudiante = st.sidebar.text_input("Ingrese su ID").strip()

    if id_estudiante:
        df_actual = dict_cursos[nrc_sel]
        if 'ID' in df_actual.columns:
            df_actual['ID'] = df_actual['ID'].astype(str).str.strip()
            est = df_actual[df_actual['ID'] == id_estudiante]

            if not est.empty:
                row = est.iloc[0]
                todas_cols = list(df_actual.columns)
                idx_p3 = todas_cols.index('P3') if 'P3' in todas_cols else len(todas_cols)

                # --- CABECERA Y PROGRESO ---
                st.markdown(f"### Bienvenid@, <span style='color:#00F2FF'>{row.get('NOMBRE', 'Estudiante')}</span>", unsafe_allow_html=True)
                
                p_c1 = round_nota(row.get('1CTE', 0)) * 0.5
                p_c2 = round_nota(row.get('2CTE', 0)) * 0.5
                total = p_c1 + p_c2
                color_b = "#00FF41" if total >= 3.0 else "#00F2FF"
                
                st.markdown(f"""
                    <div style="width: 100%; background-color: #333; border-radius: 20px; height: 25px; margin-top: 10px;">
                        <div style="width: {min((total/5)*100, 100)}%; background-color: {color_b}; height: 100%; border-radius: 20px; box-shadow: 0 0 15px {color_b}; transition: width 1s;"></div>
                    </div>
                """, unsafe_allow_html=True)
                st.write(f"Nota Acumulada Final: **{total:.2f} / 5.0**")

                t1, t2, t3 = st.tabs(["📌 Corte 1", "🚀 Corte 2", "🔮 Simulador"])
                
                with t1:
                    c1 = st.columns(4)
                    c1[0].metric("Parcial 1", f"{round_nota(row.get('P1', 0)):.1f}")
                    c1[1].metric("Parcial 2", f"{round_nota(row.get('P2', 0)):.1f}")
                    c1[2].metric("Prom. Talleres", f"{round_nota(row.get('PQT1', 0)):.1f}")
                    c1[3].metric("Nota Corte 1", f"{round_nota(row.get('1CTE', 0)):.1f}")
                    
                    st.markdown("#### 📝 Detalle de Talleres")
                    t_cols_1 = [col for col in todas_cols if col.startswith('TA') and todas_cols.index(col) < idx_p3]
                    
                    # Mostrar talleres como tarjetas modernas
                    cols_t = st.columns(7)
                    for i, col_name in enumerate(t_cols_1):
                        with cols_t[i % 7]:
                            st.markdown(f"""
                                <div class="taller-card">
                                    <span class="taller-label">Taller {col_name.replace('TA','')}</span>
                                    <span class="taller-value">{round_nota(row[col_name]):.1f}</span>
                                </div>
                            """, unsafe_allow_html=True)

                with t2:
                    c2 = st.columns(4)
                    c2[0].metric("Parcial 3", f"{round_nota(row.get('P3', 0)):.1f}")
                    c2[1].metric("Parcial 4", f"{round_nota(row.get('P4', 0)):.1f}")
                    c2[2].metric("Prom. Talleres", f"{round_nota(row.get('PQT2', 0)):.1f}")
                    c2[3].metric("Nota Corte 2", f"{round_nota(row.get('2CTE', 0)):.1f}")
                    
                    st.markdown("#### 📝 Detalle de Talleres")
                    t_cols_2 = [col for col in todas_cols if col.startswith('TA') and todas_cols.index(col) > idx_p3]
                    
                    if t_cols_2:
                        cols_t2 = st.columns(7)
                        for i, col_name in enumerate(t_cols_2):
                            with cols_t2[i % 7]:
                                st.markdown(f"""
                                    <div class="taller-card">
                                        <span class="taller-label">Taller {col_name.replace('TA','')}</span>
                                        <span class="taller-value">{round_nota(row[col_name]):.1f}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Sin registros de talleres en el segundo corte.")

                with t3:
                    st.subheader("🎯 Análisis de Meta")
                    req = (3.0 - p_c1) / 0.5
                    if total >= 3.0:
                        st.balloons()
                        st.success(f"¡Felicidades! Materia aprobada.")
                    else:
                        st.warning(f"Necesitas promediar **{req:.2f}** en el 2do Corte para pasar con 3.0.")
            else:
                st.warning("ID no encontrado.")
        else:
            st.error("Archivo sin columna ID.")
