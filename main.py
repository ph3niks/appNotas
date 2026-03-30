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

# 3. ESTILO CSS RESTAURADO (Para visibilidad en fondo negro)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    
    /* Estilo de las cajas de métricas (KPIs) */
    [data-testid="stMetric"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    
    /* Color de los Títulos (Parcial 1, etc.) - BLANCO para que se vea */
    [data-testid="stMetricLabel"] p {
        color: #E0E0E0 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }
    
    /* Color de los Números - AZUL NEÓN */
    [data-testid="stMetricValue"] {
        color: #00F2FF !important;
        font-family: 'Courier New', monospace !important;
    }
    
    h1, h2, h3 { color: #00F2FF; }
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
            # Normalización de columnas
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

# --- BARRA LATERAL ---
st.sidebar.title("💎 VANGUARD PORTAL")
if dict_cursos:
    nrc_sel = st.sidebar.selectbox("Seleccione el NRC", list(dict_cursos.keys()))
    nrc_limpio = str(nrc_sel).replace("NRC", "").strip()
    nombre_materia = MAPA_CURSOS.get(nrc_limpio, "Asignatura General")
    id_estudiante = st.sidebar.text_input("Ingrese su ID").strip()

    if id_estudiante:
        df_actual = dict_cursos[nrc_sel]
        
        # Búsqueda segura de ID
        col_id = 'ID' if 'ID' in df_actual.columns else None
        
        if col_id:
            df_actual[col_id] = df_actual[col_id].astype(str).str.strip()
            est = df_actual[df_actual[col_id].str.contains(id_estudiante, case=False, na=False)]

            if not est.empty:
                row = est.iloc[0]
                
                # Identificar frontera de talleres (P3)
                todas_cols = list(df_actual.columns)
                idx_p3 = todas_cols.index('P3') if 'P3' in todas_cols else len(todas_cols)

                # --- CABECERA ---
                st.markdown(f"### Bienvenid@, <span style='color:#00F2FF'>{row.get('NOMBRE', 'Estudiante')}</span>", unsafe_allow_html=True)
                st.write(f"**{nombre_materia}** | NRC {nrc_sel}")
                
                # --- BARRA DE PROGRESO ---
                p_c1 = round_nota(row.get('1CTE', 0)) * 0.5
                p_c2 = round_nota(row.get('2CTE', 0)) * 0.5
                total = p_c1 + p_c2
                
                color_b = "#00FF41" if total >= 3.0 else "#00F2FF"
                st.markdown(f"""
                    <div style="width: 100%; background-color: #333; border-radius: 20px; height: 25px; margin-top: 10px;">
                        <div style="width: {min((total/5)*100, 100)}%; background-color: {color_b}; height: 100%; border-radius: 20px; box-shadow: 0 0 15px {color_b}; transition: width 1s;"></div>
                    </div>
                """, unsafe_allow_html=True)
                st.write(f"Nota Acumulada: **{total:.2f} / 5.0**")
                st.divider()

                # --- PESTAÑAS CON KPIs RESTAURADOS ---
                t1, t2, t3 = st.tabs(["📌 1er Corte", "🚀 2do Corte", "🔮 Simulador"])
                
                with t1:
                    st.subheader("Resultados Consolidados")
                    c1 = st.columns(4)
                    c1[0].metric("Parcial 1", f"{round_nota(row.get('P1', 0)):.1f}")
                    c1[1].metric("Parcial 2", f"{round_nota(row.get('P2', 0)):.1f}")
                    c1[2].metric("Prom. Talleres", f"{round_nota(row.get('PQT', 0)):.1f}")
                    c1[3].metric("Nota 1er Corte", f"{round_nota(row.get('1CTE', 0)):.1f}")
                    
                    st.subheader("📝 Detalle Talleres")
                    t_cols_1 = [col for col in todas_cols if col.startswith('TA') and todas_cols.index(col) < idx_p3 and row[col] > 0]
                    if t_cols_1:
                        st.dataframe(est[t_cols_1].style.format("{:.1f}"), use_container_width=True, hide_index=True)

                with t2:
                    st.subheader("Resultados Consolidados")
                    c2 = st.columns(4)
                    c2[0].metric("Parcial 3", f"{round_nota(row.get('P3', 0)):.1f}")
                    c2[1].metric("Parcial 4", f"{round_nota(row.get('P4', 0)):.1f}")
                    # En el 2do corte, buscamos la columna PQT que esté después de P3
                    c2[2].metric("Prom. Talleres", f"{round_nota(row.get('PQT', 0)):.1f}") 
                    c2[3].metric("Nota 2do Corte", f"{round_nota(row.get('2CTE', 0)):.1f}")
                    
                    st.subheader("📝 Detalle Talleres")
                    t_cols_2 = [col for col in todas_cols if col.startswith('TA') and todas_cols.index(col) > idx_p3 and row[col] > 0]
                    if t_cols_2:
                        st.dataframe(est[t_cols_2].style.format("{:.1f}"), use_container_width=True, hide_index=True)
                    else:
                        st.info("Aún no hay talleres registrados para este corte.")

                with t3:
                    st.subheader("🎯 ¿Qué necesitas?")
                    req = (3.0 - p_c1) / 0.5
                    if total >= 3.0:
                        st.balloons()
                        st.success(f"¡Felicidades! Ya pasaste la materia con {total:.2f}")
                    else:
                        st.warning(f"Para pasar con 3.0, necesitas promediar **{req:.2f}** en el 2do Corte.")
            else:
                st.warning("Estudiante no encontrado.")
        else:
            st.error("Archivo sin columna ID.")
