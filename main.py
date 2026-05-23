import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Unab | Portal de Notas", layout="wide")

# 2. DICCIONARIO DE MATERIAS
MAPA_CURSOS = {
    "60299": "Matemáticas II",
    "55546": "Matemáticas II",
    "62529": "Matemáticas II",
    "55581": "Cálculo Diferencial",
    "63507": "Estadística Inferencial y Muestreo"
}

# 3. ESTILO CSS AVANZADO
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    
    /* Nombre del estudiante - Color Plata Azulado Moderno */
    .user-welcome {
        color: #0755F2;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
    }

    /* Estilo de los KPIs */
    [data-testid="stMetric"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #E0E0E0 !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }
    [data-testid="stMetricValue"] { color: #00F2FF !important; }

    /* Tarjetas de Talleres */
    .taller-card {
        background-color: #1c2128;
        border: 1px solid #444c56;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .taller-label {
        color: #8b949e;
        font-size: 0.75rem;
        font-weight: bold;
        display: block;
        margin-bottom: 3px;
    }
    .taller-value {
        color: #00F2FF;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* Botón personalizado */
    .stButton>button {
        width: 100%;
        background-color: #00F2FF;
        color: #0E1117;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #00D1DB;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
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

# --- INTERFAZ PRINCIPAL (Más visible en móviles) ---
st.title("💎 Portal de Notas")

if dict_cursos:
    # Formulario de entrada en la página principal (no en el sidebar)
    col_input1, col_input2 = st.columns([1, 1])
    with col_input1:
        nrc_sel = st.selectbox("Seleccione su Curso (NRC)", list(dict_cursos.keys()))
    with col_input2:
        id_estudiante = st.text_input("Ingrese su ID de Estudiante", placeholder="Ej: U00123456").strip()
    
    # Botón de consulta para móviles
    consultar = st.button("Consultar mis Notas")

    if id_estudiante and consultar:
        df_actual = dict_cursos[nrc_sel]
        if 'ID' in df_actual.columns:
            df_actual['ID'] = df_actual['ID'].astype(str).str.strip()
            est = df_actual[df_actual['ID'] == id_estudiante]

            if not est.empty:
                row = est.iloc[0]
                todas_cols = list(df_actual.columns)
                idx_p3 = todas_cols.index('P3') if 'P3' in todas_cols else len(todas_cols)
                
                # --- CABECERA ---
                st.markdown(f'<p class="user-welcome">Bienvenid@, {row.get("NOMBRE", "Estudiante")}</p>', unsafe_allow_html=True)
                
                nrc_limpio = str(nrc_sel).replace("NRC", "").strip()
                st.write(f"📖 **{MAPA_CURSOS.get(nrc_limpio, 'Asignatura General')}** | NRC: {nrc_sel}")

                # --- LÓGICA DE SEMÁFORO INTELIGENTE ---
                # 1CTE es la nota del primer corte (0-5). Aporta el 50% (0-2.5 puntos)
                p_c1 = round_nota(row.get('1CTE', 0)) * 0.5 
                # 2CTE es lo que lleva en el segundo corte (0-5). Aporta el otro 50%
                p_c2 = round_nota(row.get('2CTE', 0)) * 0.5
                total = p_c1 + p_c2
                
                # Cálculo de cuánto necesita promediar en el Corte 2 para llegar a 3.0
                # Fórmula: (3.0 - puntos_obtenidos_en_C1) / 0.5
                nota_necesaria = (3.0 - p_c1) / 0.5
                
                # Determinar color y mensaje basado en el riesgo
                if total >= 3.0:
                    color_b = "#00FF41"  # Verde Neón (Ya pasó)
                    status_txt = "¡FELICITACIONES YA HAS APROBADO LA MATERIA! 🎉"
                elif nota_necesaria > 5.0:
                    color_b = "#FF3131"  # Rojo (Riesgo Alto)
                    status_txt = "Lo siento 😔. Ya no te alcaza para pasar la materia 😵"
                elif nota_necesaria > 3.7:
                    color_b = "#FF3131"  # Rojo (Riesgo Alto)
                    status_txt = "RIESGO ALTO 🚨: Necesitas esforzarte al máximo"
                elif nota_necesaria > 2.4:
                    color_b = "#F7B707"  # Naranja (Esfuerzo moderado)
                    status_txt = "ADVERTENCIA ⚠️: No bajes la guardia"
                else:
                    color_b = "#658F4D"  # Verde (Zona segura)
                    status_txt = "ZONA SEGURA: Vas muy bien 😀! Ya te falta muy poco"

                # --- VISUALIZACIÓN ---
                st.markdown(f"""
                    <div style="margin-bottom: 5px; display: flex; justify-content: space-between; align-items: flex-end;">
                        <span style="color:{color_b}; font-weight:bold; font-size:1.1rem;">{status_txt}</span>
                        <span style="color:#8b949e; font-size:0.8rem; font-weight:bold;">Meta mínima: 3.0</span>
                    </div>
                    <div style="width: 100%; background-color: #333; border-radius: 20px; height: 24px; position: relative; overflow: hidden;">
                        <div style="width: {min((total/5)*100, 100)}%; 
                                    background-color: {color_b}; 
                                    height: 100%; 
                                    border-radius: 20px; 
                                    box-shadow: 0 0 15px {color_b}; 
                                    transition: width 1.5s ease-in-out;
                                    position: absolute; z-index: 1;">
                        </div>
                        <div style="position: absolute; left: 60%; top: 0; width: 2px; height: 100%; 
                                    background-color: rgba(255,255,255,0.4); z-index: 2;">
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if total >= 3.0:
                    components.html("""
                        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
                        <script>
                            window.onload = function() {
                                // Inyectar el script en el documento padre (Streamlit)
                                var script = parent.document.createElement('script');
                                script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js';
                                script.onload = function() {
                                    var myConfetti = parent.confetti;
                                    
                                    // Explosión central
                                    myConfetti({
                                        particleCount: 250,
                                        spread: 160,
                                        origin: { x: 0.5, y: 0.4 },
                                        colors: ['#00FF41', '#00F2FF', '#FFD700', '#FF69B4', '#ffffff']
                                    });
                                    // Cañón izquierdo
                                    setTimeout(() => myConfetti({
                                        particleCount: 120,
                                        angle: 60,
                                        spread: 70,
                                        origin: { x: 0, y: 0.6 },
                                        colors: ['#00FF41', '#00F2FF', '#FFD700']
                                    }), 300);
                                    // Cañón derecho
                                    setTimeout(() => myConfetti({
                                        particleCount: 120,
                                        angle: 120,
                                        spread: 70,
                                        origin: { x: 1, y: 0.6 },
                                        colors: ['#00FF41', '#00F2FF', '#FFD700']
                                    }), 600);
                                };
                                parent.document.head.appendChild(script);
                            }
                        </script>
                        <div style="height:1px"></div>
                    """, height=80)
                
                # Texto informativo dinámico
                if total < 3.0:
                    st.write(f"Nota definitiva actual: **{total:.2f}** | Necesitas mínimo  **{max(0, nota_necesaria):.2f}** en el 2do Corte para pasar.")
                else:
                    st.write(f"Nota definitiva actual: **{total:.2f}** | ¡Felicidades, ya cumpliste la meta!")
                
                st.divider()

                # --- PESTAÑAS ---
                t1, t2, t3 = st.tabs(["📌 1ER CORTE", "🚀 2D0 CORTE", "🎯 Simulador Nota definitiva"])
                
                with t1:
                    # 1. Determinamos si existe la columna CN
                    tiene_cn = 'CN' in todas_cols
                    
                    # 2. Creamos las columnas necesarias (5 si hay CN, 4 si no)
                    cols_metricas = st.columns(5 if tiene_cn else 4)
                    
                    # 3. Asignamos las métricas fijas
                    cols_metricas[0].metric("Parcial 1", f"{round_nota(row.get('P1', 0)):.1f}")
                    cols_metricas[1].metric("Parcial 2", f"{round_nota(row.get('P2', 0)):.1f}")
                    
                    # 4. Lógica dinámica para la posición de PQT1 y 1CTE
                    if tiene_cn:
                        cols_metricas[2].metric("Curso Nivelación", f"{round_nota(row.get('CN', 0)):.1f}")
                        idx_pqt = 3
                        idx_corte = 4
                    else:
                        idx_pqt = 2
                        idx_corte = 3
                    
                    # 5. Mostramos el resto de notas en su lugar correspondiente
                    cols_metricas[idx_pqt].metric("Promedio Talleres", f"{round_nota(row.get('PQT1', 0)):.1f}")
                    cols_metricas[idx_corte].metric("Nota Corte 1", f"{round_nota(row.get('1CTE', 0)):.1f}")
                    
                    # --- DETALLE DE TALLERES ---
                    st.markdown("#### 📝 Detalle de Talleres")
                    t_cols_1 = [col for col in todas_cols if col.startswith('TA') and todas_cols.index(col) < idx_p3]
                    
                    if t_cols_1:
                        cols_t = st.columns(min(len(t_cols_1), 7))
                        for i, col_name in enumerate(t_cols_1):
                            with cols_t[i % 7]:
                                st.markdown(f"""
                                    <div class="taller-card">
                                        <span class="taller-label">T{col_name.replace('TA','')}</span>
                                        <span class="taller-value">{round_nota(row[col_name]):.1f}</span>
                                    </div>
                                """, unsafe_allow_html=True)

                with t2:
                    c2 = st.columns(5)
                    c2[0].metric("Parcial 3 (30%)", f"{round_nota(row.get('P3', 0)):.1f}")
                    c2[1].metric("Parcial 4 (30%)", f"{round_nota(row.get('P4', 0)):.1f}")
                    c2[2].metric("Proyecto de aula (20%)", f"{round_nota(row.get('PA', 0)):.1f}")
                    c2[3].metric("Promedio Talleres (20%)", f"{round_nota(row.get('PQT2', 0)):.1f}")
                    c2[4].metric("Nota Corte 2", f"{round_nota(row.get('2CTE', 0)):.1f}")
                    
                    st.markdown("#### 📝 Detalle de Talleres")
                    t_cols_2 = [col for col in todas_cols if col.startswith('TA') and todas_cols.index(col) > idx_p3]
                    if t_cols_2:
                        cols_t2 = st.columns(min(len(t_cols_2), 7) if len(t_cols_2)>0 else 1)
                        for i, col_name in enumerate(t_cols_2):
                            with cols_t2[i % 7]:
                                st.markdown(f"""<div class="taller-card"><span class="taller-label">T{col_name.replace('TA','')}</span>
                                    <span class="taller-value">{round_nota(row[col_name]):.1f}</span></div>""", unsafe_allow_html=True)
                    else:
                        st.info("Sin registros de talleres aún.")

                with t3:
                    st.subheader("🔮 ¿Qué necesito para aprobar?")
                
                    # Puntos ya fijos del corte 1
                    # p_c1 ya está calculado arriba como: round_nota(row.get('1CTE', 0)) * 0.5
                
                    # Aporte del corte 2 sin P4 ni PQT2
                    p3_val   = round_nota(row.get('P3', 0))
                    pa_val   = round_nota(row.get('PA', 0))
                    pqt2_val = round_nota(row.get('PQT2', 0))
                    p4_val   = round_nota(row.get('P4', 0))
                
                    # Pesos del 2do corte (sobre la nota del corte, que vale 0-5)
                    # P3=30%, P4=30%, PA=20%, PQT2=20%
                    acum_fijo_c2 = p3_val * 0.30 + pa_val * 0.20   # lo que ya no cambia en C2
                
                    # Lo que ya lleva del C2 completo (0-5), aportando el 50% a la definitiva
                    c2_actual = p3_val*0.30 + p4_val*0.30 + pa_val*0.20 + pqt2_val*0.20
                    total_actual = p_c1 + round(c2_actual * 0.5, 4)
                
                    # P4 mínimo necesario (con PQT2 actual) para que C2 >= (3.0 - p_c1)/0.5
                    c2_necesario = (3.0 - p_c1) / 0.5
                    p4_necesario = (c2_necesario - acum_fijo_c2 - pqt2_val * 0.20) / 0.30
                
                    st.markdown("##### Con el promedio de talleres actual:")
                    if p4_val > 0:
                        st.info(f"Ya tienes P4 registrado: **{p4_val:.1f}**. Tu nota definitiva actual es **{total_actual:.2f}**.")
                    elif p4_necesario <= 0:
                        st.success("¡Ya aprobaste sin necesitar P4! 🎉")
                    elif p4_necesario > 5.0:
                        st.error(f"Con PQT2 = {pqt2_val:.1f}, necesitarías **{p4_necesario:.2f}** en P4, superando el máximo de 5.0.")
                        st.warning("Intenta simular un mejor PQT2 con los sliders de abajo 👇")
                    else:
                        st.warning(f"Necesitas mínimo **{p4_necesario:.2f} / 5.0** en P4 para aprobar (con PQT2 = {pqt2_val:.1f}).")
                
                    st.divider()
                    st.markdown("##### 🎛️ Simula tus escenarios")
                
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        p4_sim = st.slider(
                            "Nota esperada en P4 (30%)", 0.0, 5.0,
                            value=float(p4_val) if p4_val > 0 else 3.0,
                            step=0.1, key="slider_p4")
                    with col_s2:
                        pqt2_sim = st.slider(
                            "Promedio de talleres proyectado — PQT2 (20%)", 0.0, 5.0,
                            value=float(pqt2_val), step=0.1, key="slider_pqt2")
                
                    c2_sim    = acum_fijo_c2 + p4_sim * 0.30 + pqt2_sim * 0.20
                    total_sim = round(p_c1 + c2_sim * 0.5 + 0.0000001, 2)
                
                    color_sim = "#00FF41" if total_sim >= 3.0 else ("#F7B707" if total_sim >= 2.5 else "#FF3131")
                    st.markdown(f"""
                        <div style="margin-top:10px; padding:16px; background-color:#161B22;
                                    border-radius:12px; border:1px solid #30363D; text-align:center;">
                            <span style="color:#8b949e; font-size:0.9rem;">Nota definitiva proyectada</span><br>
                            <span style="color:{color_sim}; font-size:2.5rem; font-weight:bold;">{total_sim:.2f}</span>
                            <span style="color:#8b949e; font-size:1rem;"> / 5.0</span><br>
                            <span style="color:{color_sim}; font-weight:bold;">
                                {"✅ APRUEBA" if total_sim >= 3.0 else "❌ NO APRUEBA"}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                
                    p4_min_sim = (((3.0 - p_c1) / 0.5) - acum_fijo_c2 - pqt2_sim * 0.20) / 0.30
                    if p4_min_sim <= 0:
                        st.success(f"Con PQT2 = {pqt2_sim:.1f}, ya apruebas sin importar P4. 🎉")
                    elif p4_min_sim > 5.0:
                        st.error(f"Con PQT2 = {pqt2_sim:.1f}, no es posible aprobar ni con 5.0 en P4 😞.")
                    else:
                        st.info(f"Con PQT2 = {pqt2_sim:.1f}, necesitas mínimo **{p4_min_sim:.2f}** en P4 para aprobar. ¡Vamos!!! 💪 🚀")
            else:
                st.warning("ID no encontrado en este NRC.")
        else:
            st.error("Error: Columna ID no detectada.")
