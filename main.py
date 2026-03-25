import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Portal de Notas Vanguard", layout="wide")

# --- ESTILO CSS PERSONALIZADO (Vanguardista) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stMetric { background-color: #1A1C24; padding: 15px; border-radius: 10px; border-left: 5px solid #00F2FF; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #7000FF , #00F2FF); }
    h1, h2, h3 { color: #00F2FF; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    # Reemplaza con el nombre de tu archivo
    file_path = "app_notas.xlsx" 
    try:
        xls = pd.ExcelFile(file_path)
        return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

data_dict = load_data()

# --- SIDEBAR: FILTROS ---
st.sidebar.title("🚀 Panel de Control")
if data_dict:
    curso_seleccionado = st.sidebar.selectbox("Selecciona tu curso", list(data_dict.keys()))
    df_curso = data_dict[curso_seleccionado]
    
    id_estudiante = st.sidebar.text_input("Digita tu ID de Estudiante")

    if id_estudiante:
        # Buscamos al estudiante en el DataFrame del curso
        # Aseguramos que el ID se compare como string
        df_curso['ID'] = df_curso['ID'].astype(str)
        estudiante = df_curso[df_curso['ID'] == id_estudiante]

        if not estudiante.empty:
            row = estudiante.iloc[0].fillna(0) # Si está vacío es 0
            
            st.title(f"Bienvenido al Semestre, {id_estudiante}")
            st.markdown(f"### Curso: {curso_seleccionado}")
            
            # --- SECCIÓN DE MÉTRICAS (KPIs) ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Parcial 1 (P1)", f"{row['P1']:.1f}")
            with col2:
                st.metric("Parcial 2 (P2)", f"{row['P2']:.1f}")
            with col3:
                st.metric("Nota 1er Corte (50%)", f"{row['1CTE']:.1f}")

            # --- BARRA DE PROGRESO GLOBAL ---
            # Si el semestre es de 0 a 5, y el 1er corte es el 50%, 
            # la nota actual aporta la mitad al total.
            nota_actual_global = row['1CTE'] * 0.5
            progreso_porcentaje = min(nota_actual_global / 3.0, 1.0) # Respecto al mínimo de 3.0
            
            st.subheader("Evolución hacia la Aprobación (Meta: 3.0)")
            st.progress(progreso_porcentaje)
            
            distancia = 3.0 - nota_actual_global
            if distancia > 0:
                st.warning(f"Te falta acumular **{distancia:.2f}** en el segundo corte para alcanzar el 3.0 mínimo.")
            else:
                st.success("¡Felicidades! Con las notas actuales ya tienes asegurada la base del curso.")

            # --- TABLA DE DETALLE (Vanguardista) ---
            with st.expander("Ver detalle de Talleres y Quices"):
                # Mostramos solo las columnas que no son ID ni las principales ya vistas
                cols_interes = [c for c in df_curso.columns if 'Ta' in c or 'Q' in c or 'CN' in c]
                st.table(estudiante[cols_interes])

            # --- SIMULADOR INTERACTIVO ---
            st.divider()
            st.subheader("🔮 Simulador de Meta")
            nota_deseada = st.slider("¿Qué nota esperas sacar en el Segundo Corte?", 0.0, 5.0, 3.5)
            proyeccion_final = nota_actual_global + (nota_deseada * 0.5)
            
            st.write(f"Si obtienes un promedio de **{nota_deseada}** en el restante del semestre...")
            if proyeccion_final >= 3.0:
                st.info(f"Tu nota final estimada sería: **{proyeccion_final:.2f}** ✅ ¡Aprobarías!")
            else:
                st.error(f"Tu nota final estimada sería: **{proyeccion_final:.2f}** ⚠️ Necesitas esforzarte un poco más.")

        else:
            st.error("ID no encontrado en este curso. Verifica los datos.")
else:
    st.info("Por favor, asegúrate de que el archivo 'notas_estudiantes.xlsx' esté en la misma carpeta.")
