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

# 3. ESTILO CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { 
        background-color: #161B22; border-radius: 12px; border: 1px solid #30363D; padding: 15px;
    }
    [data-testid="stMetricValue"] { color: #00F2FF !important; }
    h1, h2, h3 { color: #00F2FF; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = "app_notas.xlsx"
    try:
        # Intentamos leer como Excel (ajustar a pd.read_csv si usas CSVs sueltos en local)
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        data = {}
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            # Limpieza profunda de nombres de columnas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Convertir notas a números
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
    id_estudiante = st.sidebar.text_input("Ingrese su ID (ej: U00...)").strip()

    if id_estudiante:
        df_actual = dict_cursos[nrc_sel]
        
        # Buscamos la columna ID (ya normalizada a mayúsculas en load_data)
        if 'ID' in df_actual.columns:
            df_actual['ID'] = df_actual['ID'].astype(str).str.strip()
            est = df_actual[df_actual['ID'].str.contains(id_estudiante, case=False, na=False)]

            if not est.empty:
                row = est.iloc[0]
                
                # Cálculo de puntos (Corte 1: 50%, Corte 2: 50%)
                p_c1 = round_nota(row.get('1CTE', 0)) * 0.5
                p_c2 = round_nota(row.get('2CTE', 0)) * 0.5
                total = p_c1 + p_c2
                
                st.header(f"Hola, {row.get('NOMBRE', 'Estudiante')}")
                
                # --- BARRA DE PROGRESO DINÁMICA ---
                color = "#00FF41" if total >= 3.0 else "#00F2FF"
                st.markdown(f"**Progreso hacia el 3.0**")
                st.markdown(f"""
                    <div style="width: 100%; background-color: #333; border-radius: 10px; height: 20px;">
                        <div style="width: {min((total/5)*100, 100)}%; background-color: {color}; height: 100%; border-radius: 10px; box-shadow: 0 0 10px {color};"></div>
                    </div>
                """, unsafe_allow_html=True)
                st.write(f"Nota actual: **{total:.2f}**")

                # Pestañas
                t1, t2, t3 = st.tabs(["📌 Corte 1", "🚀 Corte 2", "🔮 Simulador"])
                
                with t1:
                    c = st.columns(3)
                    c[0].metric("P1", f"{round_nota(row.get('P1', 0))}")
                    c[1].metric("P2", f"{round_nota(row.get('P2', 0))}")
                    c[2].metric("CORTE 1", f"{round_nota(row.get('1CTE', 0))}")
                
                with t2:
                    c = st.columns(3)
                    c[0].metric("P3", f"{round_nota(row.get('P3', 0))}")
                    c[1].metric("P4", f"{round_nota(row.get('P4', 0))}")
                    c[2].metric("CORTE 2", f"{round_nota(row.get('2CTE', 0))}")

                with t3:
                    falta = (3.0 - p_c1) / 0.5
                    if total >= 3.0:
                        st.success("¡Ya aprobaste la materia!")
                    else:
                        st.warning(f"Necesitas un **{falta:.2f}** en el promedio del 2do Corte para pasar.")
            else:
                st.warning("ID no encontrado en este NRC.")
        else:
            st.error(f"No se detectó columna 'ID'. Columnas: {list(df_actual.columns)}")
