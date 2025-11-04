import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import datetime

# Verificar dependencias
try:
    import openpyxl
    DEPENDENCIAS_OK = True
except ImportError as e:
    DEPENDENCIAS_OK = False
    st.error(f"❌ Error de dependencias: {str(e)}")
    st.stop()

# 🔐 SISTEMA DE USUARIOS AUTORIZADOS
USUARIOS_AUTORIZADOS = {
    "jefri": "dhl2025",
    "admin": "admin123",
    "supervisor": "sup456",
    "operario1": "op789",
    "gerente": "gerente000"
}

# Configurar página
st.set_page_config(
    page_title="DHL-MAKRO PRO - Sistema Universal",
    page_icon="🚀",
    layout="wide"
)

# CSS mejorado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #D40511 !important;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .login-header {
        font-size: 2.5rem !important;
        color: #D40511 !important;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .user-welcome {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton button {
        border-radius: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 🔐 SISTEMA DE AUTENTICACIÓN
if 'usuario_autenticado' not in st.session_state:
    st.session_state.usuario_autenticado = False
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = ""

if not st.session_state.usuario_autenticado:
    st.markdown('<div class="login-header">🔐 DHL-MAKRO PRO</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3064/3064155.png", width=120)
    
    with col2:
        usuario = st.text_input("👤 Usuario:")
        password = st.text_input("🔑 Contraseña:", type="password")
        
        if st.button("🚀 Ingresar al Sistema", use_container_width=True):
            if usuario in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario] == password:
                st.session_state.usuario_autenticado = True
                st.session_state.usuario_actual = usuario
                st.session_state.login_time = datetime.datetime.now()
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    
    st.stop()

# ✅ USUARIO AUTENTICADO - APP PRINCIPAL

# Header con información de usuario
st.markdown(f"""
<div class="user-welcome">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h3 style="margin:0;">🚚 DHL-MAKRO PRO</h3>
            <p style="margin:0;">Conectado como: <strong>{st.session_state.usuario_actual}</strong></p>
        </div>
        <div>
            {st.button("🚪 Cerrar Sesión", key="logout")}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Función mejorada para detectar columna de órdenes
def detectar_columna_orden(df):
    """Detecta automáticamente la columna que contiene los números de orden"""
    
    # Lista ampliada de posibles nombres de columnas
    posibles_columnas = [
        'ORDEN', 'ORDER', 'Order #', 'ORDER_NUMBER', 'ORDER_NO', 'ORDER_NUM',
        'NÚMERO', 'NUMERO', 'NUMBER', 'NO_ORDEN', 'NUM_ORDEN',
        'CODIGO', 'CÓDIGO', 'CODE', 'ID', 'ID_ORDEN', 'REFERENCIA',
        'PEDIDO', 'PEDIDO_NO', 'PEDIDO_NUM', 'OC', 'ORDEN_COMPRA'
    ]
    
    # Buscar columnas por nombre exacto
    for columna in df.columns:
        if str(columna).upper().strip() in [pc.upper() for pc in posibles_columnas]:
            return columna
    
    # Buscar columnas que contengan palabras clave
    for columna in df.columns:
        columna_upper = str(columna).upper()
        if any(palabra in columna_upper for palabra in ['ORDEN', 'ORDER', 'PEDIDO', 'NUM', 'NO', 'ID']):
            return columna
    
    # Si no encuentra, buscar columnas con datos numéricos únicos
    for columna in df.columns:
        try:
            # Verificar si la columna tiene principalmente números
            muestra = df[columna].dropna().head(10)
            if len(muestra) > 0:
                # Intentar convertir a numérico
                numericos = pd.to_numeric(muestra, errors='coerce')
                if numericos.notna().sum() > len(muestra) * 0.8:  # 80% son números
                    return columna
        except:
            continue
    
    return None

# Función de búsqueda universal mejorada
def buscar_orden_universal(df, orden_buscar):
    """Busca una orden en cualquier formato y maneja duplicados"""
    
    # Detectar columna de órdenes
    columna_orden = detectar_columna_orden(df)
    
    if not columna_orden:
        return None, "No se pudo detectar la columna de órdenes"
    
    # Preparar el término de búsqueda
    orden_limpio = str(orden_buscar).strip()
    
    # Intentar diferentes métodos de búsqueda
    resultados = None
    
    # Método 1: Búsqueda exacta como string
    try:
        resultados = df[df[columna_orden].astype(str).str.strip() == orden_limpio]
    except:
        pass
    
    # Método 2: Búsqueda numérica (sin ceros)
    if resultados is None or resultados.empty:
        try:
            # Intentar convertir a número
            orden_numerico = int(orden_limpio.lstrip('0') or 0)
            resultados = df[df[columna_orden] == orden_numerico]
        except:
            pass
    
    # Método 3: Búsqueda flexible (contiene)
    if resultados is None or resultados.empty:
        try:
            resultados = df[df[columna_orden].astype(str).str.contains(orden_limpio, na=False)]
        except:
            pass
    
    # Método 4: Búsqueda numérica flexible
    if resultados is None or resultados.empty:
        try:
            orden_numerico = float(orden_limpio)
            resultados = df[df[columna_orden] == orden_numerico]
        except:
            pass
    
    if resultados is None or resultados.empty:
        return None, f"Orden no encontrada: '{orden_buscar}'"
    
    return resultados, f"Columna detectada: '{columna_orden}'"

# INTERFAZ PRINCIPAL MEJORADA
st.markdown('<div class="main-header">🔍 BUSCADOR UNIVERSAL DE ÓRDENES</div>', unsafe_allow_html=True)

# Sección de carga de archivo
st.subheader("📁 CARGAR ARCHIVO EXCEL")
archivo = st.file_uploader(
    "Arrastra o selecciona cualquier archivo Excel", 
    type=['xlsx', 'xls', 'xlsm', 'xlsb'],
    help="✅ Compatible con: .xlsx, .xls, .xlsm, .xlsb"
)

df = None
info_archivo = ""

if archivo is not None:
    try:
        # Leer archivo Excel
        df = pd.read_excel(archivo)
        
        # Detectar columna de órdenes automáticamente
        columna_detectada = detectar_columna_orden(df)
        
        # Mostrar información del archivo
        st.markdown(f'<div class="success-box">', unsafe_allow_html=True)
        st.write(f"**✅ ARCHIVO CARGADO EXITOSAMENTE**")
        st.write(f"**📊 Datos:** {len(df)} filas × {len(df.columns)} columnas")
        st.write(f"**📋 Columna de órdenes detectada:** `{columna_detectada if columna_detectada else 'NO DETECTADA'}`")
        st.write(f"**📝 Archivo:** {archivo.name}")
        st.markdown(f'</div>', unsafe_allow_html=True)
        
        # Mostrar vista previa
        with st.expander("👁️ **VISTA PREVIA DEL ARCHIVO**", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
            
        # Mostrar estadísticas de la columna de órdenes
        if columna_detectada:
            with st.expander("📈 **ESTADÍSTICAS DE ÓRDENES**"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Órdenes únicas", df[columna_detectada].nunique())
                with col2:
                    st.metric("Órdenes duplicadas", len(df) - df[columna_detectada].nunique())
                with col3:
                    st.metric("Valores vacíos", df[columna_detectada].isna().sum())
                
                # Mostrar ejemplos de órdenes
                st.write("**🔢 Ejemplos de órdenes:**")
                ejemplos = df[columna_detectada].dropna().head(10).tolist()
                for i, ejemplo in enumerate(ejemplos):
                    st.write(f"`{ejemplo}`", end=" • " if i < len(ejemplos)-1 else "")
        
    except Exception as e:
        st.error(f"❌ **ERROR AL LEER EL ARCHIVO:** {str(e)}")
        st.info("💡 **Sugerencias:** Verifica que el archivo no esté corrupto y que sea un Excel válido.")

# BÚSQUEDA MEJORADA
if df is not None:
    st.subheader("🔍 BUSCAR ÓRDENES")
    
    col_busqueda, col_info = st.columns([2, 1])
    
    with col_busqueda:
        orden_buscar = st.text_input(
            "🔢 **NÚMERO DE ORDEN:**",
            placeholder="Ej: 146, 00146, ABC123, PED-2024...",
            help="💡 Puede ser cualquier formato: números, texto, códigos mixtos"
        )
    
    with col_info:
        st.write("")  # Espacio
        st.write("")
        if st.button("🚀 **BUSCAR ÓRDEN**", use_container_width=True, type="primary"):
            pass
    
    if orden_buscar.strip():
        # Realizar búsqueda
        resultados, mensaje = buscar_orden_universal(df, orden_buscar)
        
        if resultados is not None and not resultados.empty:
            st.success(f"✅ **{len(resultados)} ORDEN(ES) ENCONTRADA(S)**")
            st.info(f"**{mensaje}**")
            
            # Mostrar resultados
            for idx, (_, fila) in enumerate(resultados.iterrows(), 1):
                with st.container():
                    st.markdown(f"---")
                    st.subheader(f"📦 **ORDEN {idx} de {len(resultados)}**")
                    
                    # Mostrar información principal en columnas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Buscar columnas comunes automáticamente
                    columnas_comunes = {
                        'MUELLE': '🏭 Muelle', 
                        'CARGA': '📦 Carga', 
                        'POSICION': '📍 Posición',
                        'UBICACION': '📌 Ubicación',
                        'LOCATION': '📌 Location',
                        'Route #': '🛣️ Ruta',
                        'CLIENTE': '👤 Cliente',
                        'Customer Name': '👤 Cliente'
                    }
                    
                    for col_db, col_show in columnas_comunes.items():
                        if col_db in df.columns and pd.notna(fila[col_db]):
                            with col1:
                                st.metric(col_show, fila[col_db])
                            break
                    
                    # Mostrar información completa
                    with st.expander(f"📄 **INFORMACIÓN COMPLETA - Orden {idx}**"):
                        for columna in df.columns:
                            if pd.notna(fila[columna]):
                                st.write(f"**{columna}:** `{fila[columna]}`")
            
            # Opción para descargar resultados
            st.markdown("---")
            st.subheader("💾 **EXPORTAR RESULTADOS**")
            
            csv = resultados.to_csv(index=False)
            st.download_button(
                label="📥 **Descargar resultados en CSV**",
                data=csv,
                file_name=f"ordenes_{orden_buscar}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
        else:
            st.error(f"❌ {mensaje}")
            st.markdown("""
            **💡 CONSEJOS DE BÚSQUEDA:**
            - Verifica el número exacto
            - Prueba diferentes formatos
            - Si es numérico, prueba con/sin ceros
            - Si es texto, verifica mayúsculas/minúsculas
            """)

# INSTRUCCIONES INICIALES
else:
    st.markdown("""
    <div class="warning-box">
    <h3>📱 INSTRUCCIONES DE USO</h3>
    
    **1. 📁 CARGA TU EXCEL**
    - Sube cualquier archivo Excel (.xlsx, .xls, .xlsm, .xlsb)
    - El sistema detectará automáticamente la columna de órdenes
    
    **2. 🔍 BUSCA ÓRDENES**  
    - Escribe el número de orden en cualquier formato
    - El sistema buscará en todas las columnas posibles
    - Maneja automáticamente órdenes duplicadas
    
    **3. ✅ OBTÉN RESULTADOS**
    - Verás todas las coincidencias encontradas
    - Información completa de cada orden
    - Opción de descargar resultados
    
    **🎯 COMPATIBLE CON:** Cualquier estructura de Excel, múltiples formatos de órdenes, órdenes duplicadas
    </div>
    """, unsafe_allow_html=True)

# PIE DE PÁGINA
st.markdown("---")
st.caption(f"**DHL-MAKRO PRO** © 2025 | Usuario: {st.session_state.usuario_actual} | Versión: Universal 2.0")