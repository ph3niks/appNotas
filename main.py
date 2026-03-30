import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN INICIAL (DEBE SER LA PRIMERA LÍNEA)
st.set_page_config(page_title="Vanguard Notes | Portal Académico", layout="wide")

# 2. DICCIONARIO DE MATERIAS
MAPA_CURSOS = {
    "60299": "Matemáticas II",
    "55546": "Matemáticas II",
    "62529": "Matemáticas II",
    "55581": "Cálculo Diferencial",
    "63507": "Estadística Inferencial y Muestreo"
}

# 3. ESTILO CSS VANGUARDISTA
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
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        data = {}
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            # Limpieza: Convertir todo lo que no es texto a número (evita error de fechas)
            for col in df.columns:
                if col.strip().upper() not in ['NOMBRE', 'ID', 'NRC']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            data[sheet] = df
        return data
    except Exception as e:
        st.error(f"Error al cargar Excel: {e}")
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
    id_estudiante = st.sidebar.text_input("Ingrese su ID de Estudiante").strip()

    if id_estudiante:
        df_actual = dict_cursos[nrc_sel]
        
        # --- BÚSQUEDA SEGURA DE LA COLUMNA ID ---
        # Buscamos cualquier columna que se llame ID (sin importar espacios o minúsculas)
        col_id_real = next((c for c in df_actual.columns if c.strip().upper() == 'ID'), None)
        
        if col_id_real:
            df_actual[col_id_real] = df_actual[col_id_real].astype(str).str.strip()
            est = df_actual[df_actual[col_id_real] == id_estudiante]

            if not est.empty:
                row = est.iloc[0]
                nombre_u = row.get('NOMBRE', row.get('Nombre', 'Estudiante'))
                
                # Identificamos dónde empieza el 2do corte (P3)
                todas_cols = list(df_actual.columns)
                idx_p3 = todas_cols.index('P3') if 'P3' in todas_cols else len(todas_cols)

                # --- CABECERA ---
                st.markdown(f"### Bienvenid@, <span style='color:#00F2FF'>{nombre_u}</span>", unsafe_allow_html=True)
                st.write(f"**{nombre_materia}** (NRC {nrc_sel})")
                
                # --- BARRA DE PROGRESO DINÁMICA ---
                puntos_c1 = round_nota(row.get('1CTE', 0)) * 0.5
                puntos_c2 = round_nota(row.get('2CTE', 0)) * 0.5
                puntos_totales = puntos_c1 + puntos_c2
                
                color_b = "#00FF41" if puntos_totales >= 3.0 else "#00F2FF"
                
                st.markdown(f"""
                    <div style="width: 100%; background-color: #30363D; border-radius: 20px; height: 25px; margin-top: 20px;">
                        <div style="width: {min((puntos_totales/5)*100, 100)}%; background-color: {color_b}; 
                                    height: 100%; border-radius: 20px; transition: width 0.8s;
                                    box-shadow: 0 0 15px {color_b};">
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 5px; color: #E0E0E0;">
                        <span>0.0</span> <span style="color: #00FF41; font-weight:bold;">META 3.0</span> <span>5.0</span>
                    </div>
                """, unsafe_allow_html=True)
                st.write(f"Puntos acumulados: **{puntos_totales:.2f} / 5.0**")
                st.divider()

                # --- PESTAÑAS ---
                t1, t2, t3 = st.tabs(["📌 1er Corte", "🚀 2do Corte", "🎯 Simulador Final"])

                with t1:
                    c = st.columns(4)
                    c[0].metric("Parcial 1", f"{round_nota(row.get('P1', 0)):.1f}")
                    c[1].metric("Parcial 2", f"{round_nota(row.get('P2', 0)):.1f}")
                    c[2].metric("Promedio Talleres", f"{round_nota(row.get('PQT1', row.get('PQT', 0))):.1f}")
                    c[3].metric("Nota 1er Corte", f"{round_nota(row.get('1CTE', 0)):.1f}")
                    
                    st.subheader("📝 Detalle Talleres")
                    t_c1 = [col for col in todas_cols if col.startswith('Ta') and todas_cols.index(col) < idx_p3 and row[col] > 0]
                    if t_c1:
                        st.dataframe(est[t_c1].rename(columns={x: f"Taller {x[2:]}" for x in t_c1}).style.format("{:.1f}"), use_container_width=True, hide_index=True)

                with t2:
                    c = st.columns(4)
                    c[0].metric("Parcial 3", f"{round_nota(row.get('P3', 0)):.1f}")
                    c[1].metric("Parcial 4", f"{round_nota(row.get('P4', 0)):.1f}")
                    c[2].metric("Promedio Talleres", f"{round_nota(row.get('PQT2', 0)):.1f}")
                    c[3].metric("Nota 2do Corte", f"{round_nota(row.get('2CTE', 0)):.1f}")
                    
                    st.subheader("📝 Detalle Talleres")
                    t_c2 = [col for col in todas_cols if col.startswith('Ta') and todas_cols.index(col) > idx_p3 and row[col] > 0]
                    if t_c2:
                        st.dataframe(est[t_c2].rename(columns={x: f"Taller {x[2:]}" for x in t_c2}).style.format("{:.1f}"), use_container_width=True, hide_index=True)
                    else:
                        st.info("Aún no hay registros de talleres para el segundo corte.")

                with t3:
                    st.subheader("🔮 Proyección de Resultados")
                    req = (3.0 - puntos_c1) / 0.5
                    if puntos_totales >= 3.0:
                        st.balloons()
                        st.success(f"¡Felicidades! Ya aprobaste la materia con **{puntos_totales:.2f}**")
                    else:
                        if req > 5.0:
                            st.error(f"Necesitas un promedio de {req:.2f} en el 2do corte para pasar. Situación crítica.")
                        else:
                            st.warning(f"Para aprobar con 3.0, necesitas promediar **{req:.2f}** en el 2do corte.")
            else:
                st.warning("⚠️ ID no encontrado en este curso.")
        else:
            st.error("❌ Error de Formato: No se encontró la columna 'ID' en el Excel.")
