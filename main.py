import streamlit as st
import pandas as pd
import io
from streamlit_sortables import sort_items # Componente para arrastrar
import re # Usado para extraer IDs de las etiquetas HTML

# ── Configuración de Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Cotizador Live",
    page_icon="🌱",
    layout="wide",
)

# ── Estilos CSS Personalizados ───────────────────────────────────────────────
# Mantenemos el modo claro profesional y ajustamos el diseño horizontal.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; font-size: 13px; }
.stApp { background: #f6f8fa; color: #1f2328; }

/* Header ultra compacto */
.header-mini {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 10px 24px;
    margin-bottom: 15px;
    display: flex; justify-content: space-between; align-items: center;
    border-radius: 0 0 10px 10px;
}
.header-mini h1 { font-size: 1.5rem; margin: 0; color: #1a7f37; font-weight: 800; }

/* Caja de Vista Previa del Precio (en el selector) */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 8px;
    padding: 5px 12px;
    text-align: center;
}
.preview-label { font-size: 0.6rem; color: #1a7f37; text-transform: uppercase; font-weight: bold; }
.preview-value { font-family: 'DM Mono', monospace; font-size: 1.15rem; font-weight: 700; color: #116329; }

/* --- DISEÑO DE TARJETA DETALLE (RECUPERADO) --- */
.sel-item {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #2ea843;
    border-radius: 6px;
    padding: 8px 12px;
    display: flex; align-items: center;
    font-size: 0.85rem;
    width: 100%; /* Ocupar todo el espacio disponible */
}

/* Indicador de precio DM Mono */
.price-tag { font-family: 'DM Mono', monospace; font-weight: 700; color: #1a7f37; }

/* Indicador de arrastre (⋮⋮) */
.drag-handle {
    cursor: grab;
    font-size: 1.2rem;
    color: #8b949e;
    margin-right: 12px;
    font-weight: bold;
}

/* Limpiar contenedor del componente de arrastre para que no tenga bordes extra */
.stSortableList > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
.stSortableList [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    padding: 0 !important;
}

.block-container { padding-top: 0.5rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Carga y Limpieza de Datos (Auto-sync 30s) ─────────────────────────────────
@st.cache_data(ttl=30)
def load_data_auto():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        # Limpieza agresiva de la columna Precio (elimina $, puntos, comas y espacios)
        if 'Precio' in data.columns:
            # Reemplaza regex: símbolos de dinero, puntos, comas y espacios en blanco
            data['Precio'] = data['Precio'].astype(str).str.replace(r'[\$\.\,\s]', '', regex=True)
            data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0).astype(int)
        return data
    except Exception as e:
        st.error(f"Error cargando la planilla: {e}")
        return pd.DataFrame(columns=["Categoría","Producto","Proveedor","Precio"])

df = load_data_auto()

# Estado de la sesión (Presupuesto)
if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-mini">
    <h1>🌱 Rizotron IoT · Live Excel</h1>
    <div style="font-family:'DM Mono'; color:#1a7f37; font-size:0.75rem; background:#dafbe1; padding:4px 12px; border-radius:20px;">● Sincronizado (Google Sheets)</div>
</div>
""", unsafe_allow_html=True)

# ── Fila de Selección Horizontal (Top Bar) ────────────────────────────────────
if not df.empty:
    with st.container():
        # Diseño de 5 columnas para selector side-by-side
        c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5])
        
        with c1:
            cats = sorted(df["Categoría"].unique().tolist())
            cat_sel = st.selectbox("Categoría", cats, label_visibility="collapsed")
        
        mask_cat = df[df["Categoría"] == cat_sel]
        
        with c2:
            prods = sorted(mask_cat["Producto"].unique().tolist())
            prod_sel = st.selectbox("Producto", prods, label_visibility="collapsed")
            
        mask_prod = mask_cat[mask_cat["Producto"] == prod_sel]
        
        with c3:
            provs = mask_prod["Proveedor"].unique().tolist()
            prov_sel = st.selectbox("Proveedor", provs, label_visibility="collapsed")
                
        # Datos finales de la selección para vista previa y acciones
        final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
        precio_actual = int(final_row["Precio"])

        with c4:
            # Muestra el precio antes de seleccionar
            st.markdown(f"""
            <div class="preview-box">
                <div class="preview-label">VISTA PREVIA</div>
                <div class="preview-value">{fmt(precio_actual)}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c5:
            # Botones de acción compactos
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("➕ Añadir", use_container_width=True):
                    st.session_state.cotizacion.append({
                        "Categoría": final_row["Categoría"], "Producto": final_row["Producto"],
                        "Proveedor": final_row["Proveedor"], "Precio": precio_actual
                    })
                    st.rerun() # Actualiza para que aparezca en el detalle
            with b2:
                cheap = mask_cat.loc[mask_cat["Precio"].idxmin()]
                if st.button("⬇️ Barato", use_container_width=True, help=f"Añadir {cheap['Producto']} ({fmt(cheap['Precio'])})"):
                    st.session_state.cotizacion.append({
                        "Categoría": cheap["Categoría"], "Producto": cheap["Producto"],
                        "Proveedor": cheap["Proveedor"], "Precio": int(cheap["Precio"])
                    })
                    st.rerun()
            with b3:
                exp = mask_cat.loc[mask_cat["Precio"].idxmax()]
                if st.button("⬆️ Caro", use_container_width=True, help=f"Añadir {exp['Producto']} ({fmt(exp['Precio'])})"):
                    st.session_state.cotizacion.append({
                        "Categoría": exp["Categoría"], "Producto": exp["Producto"],
                        "Proveedor": exp["Proveedor"], "Precio": int(exp["Precio"])
                    })
                    st.rerun()

# ── Sección de Cuerpo Principal ──────────────────────────────────────────────
st.write("")
col_detalle, col_resumen = st.columns([3, 1.2])

# --- DETALLE ARRASTRABLE (RECUPERADO VISUALMENTE) ---
with col_detalle:
    st.markdown("### 📋 Presupuesto (Arrastra para reordenar)")
    
    cot_list = st.session_state.cotizacion
    
    if not cot_list:
        st.info("Lista de componentes vacía.")
    else:
        # 1. Generamos los bloques HTML para CADA tarjeta del detalle.
        # Deben ser strings únicos para que el componente funcione con duplicados.
        # Usamos el índice `i` al principio de la cadena HTML para garantizar unicidad.
        html_sortable_items = []
        for i, item in enumerate(cot_list):
            
            # Formato de la tarjeta: Recuperado del diseño anterior pero incrustado en HTML para el sortable.
            # Agregamos los tres puntitos ⋮⋮ a la izquierda.
            
            # Unicidad ID:{i}| al inicio del string. No se renderiza en la UI pero lo usamos en la lógica.
            unique_key = f"ID:{i}|"
            
            card_html_content = f"""
            <div class="draggable-card" style="display:flex; align-items:center; margin-bottom: 2px;">
                <div class="drag-handle">⋮⋮</div>
                
                <div class="sel-item">
                    <span style="flex:1.2; font-weight:bold; color:#1a7f37; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; padding-right:5px;">{item['Categoría']}</span>
                    <span style="flex:2.5; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; padding-right:5px;">{item['Producto']}</span>
                    <span style="flex:1.2; color:#57606a; font-size:0.75rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; padding-right:5px;">{item['Proveedor']}</span>
                    <span class="price-tag" style="flex:1; text-align:right;">{fmt(item['Precio'])}</span>
                </div>
            </div>
            """
            # Combinamos ID único y HTML para el componente.
            html_sortable_items.append(f"{unique_key}{card_html_content}")

        # 2. Renderizar el componente Drag & Drop.
        # Recibe strings únicos (que son HTML) y los ordena verticalmente.
        # Streamlit-sortables permite renderizar strings HTML internamente.
        sorted_html_list = sort_items(html_sortable_items, direction='vertical', key="cotizacion_draggable_cards_v3")

        # 3. Lógica de Sincronización: Actualizar la lista original si el orden cambió.
        # sorted_html_list contiene el nuevo orden de los strings HTML.
        
        if sorted_html_list: # Something moved or sorted (could be the same order)
             # Creamos una copia del estado previo para comparar.
            st.session_state.cotizacion_old_v3 = st.session_state.cotizacion.copy()
            
            new_indices_order = []
            for html_str in sorted_html_list:
                # Extraemos el índice original usando regex desde el inicio del string "ID:X|..."
                match = re.search(r"^ID:(\d+)\|", html_str)
                if match:
                    original_index = int(match.group(1))
                    new_indices_order.append(original_index)
            
            # Sincronizamos la lista real basándonos en los índices extraídos
            st.session_state.cotizacion = [st.session_state.cotizacion[i] for i in new_indices_order]
            
            # Es CRUCIAL forzar un rerun si la lista cambió, para re-generar los IDs en el loop i+1 
            # de `enumerate(cot_list)` en la siguiente renderización.
            if st.session_state.cotizacion != st.session_state.cotizacion_old_v3:
                st.rerun()

        # Botón de vaciar para gestión de lista (opcional ponerlo aquí o en resumen)
        if st.button("🗑️ Eliminar último ítem añadido"):
             if st.session_state.cotizacion:
                st.session_state.cotizacion.pop()
                st.rerun()

with col_resumen:
    total = sum(i["Precio"] for i in st.session_state.cotizacion)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:12px; text-align:center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">PRESUPUESTO ESTIMADO</div>
        <div style="font-size:2.4rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin:10px 0;">{fmt(total)}</div>
        <div style="font-size:0.85rem; color:#8b949e; border-top:1px solid #f6f8fa; padding-top:10px;">{len(st.session_state.cotizacion)} componentes en total</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("❌ Vaciar Lista Completa", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
    
    # ── Exportar a EXCEL ──────────────────────────────────────────────────────
    if st.session_state.cotizacion:
        # Preparar DataFrame para exportar
        df_export = pd.DataFrame(st.session_state.cotizacion)
        
        # Buffer para archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Cotización Rizotron')
        
        st.download_button(
            label="📊 Descargar Excel (.xlsx)",
            data=output.getvalue(),
            file_name="cotizacion_rizotron.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
