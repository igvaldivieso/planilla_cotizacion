import streamlit as st
import pandas as pd
import re
import io
from streamlit_sortables import sort_items

# ── Configuración de Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Cotizador Pro",
    page_icon="🌱",
    layout="wide",
)

# ── Estilos CSS (Light Mode & Compact) ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; font-size: 13px; }
.stApp { background: #f6f8fa; color: #1f2328; }

/* Header */
.header-mini {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 12px 24px;
    margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: center;
    border-radius: 0 0 12px 12px;
}
.header-mini h1 { font-size: 1.6rem; margin: 0; color: #1a7f37; font-weight: 800; }

/* Preview Price Card */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 8px;
    padding: 6px 12px;
    text-align: center;
}
.preview-label { font-size: 0.6rem; color: #1a7f37; text-transform: uppercase; font-weight: bold; }
.preview-value { font-family: 'DM Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #116329; }

/* Estilo para los ítems en el detalle */
.price-tag { font-family: 'DM Mono', monospace; font-weight: 700; color: #1a7f37; }

/* Contenedor de Arrastre */
.stSortableList > div {
    background: white !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
}

.block-container { padding-top: 0.5rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Carga y Limpieza de Datos (Sync 30s) ─────────────────────────────────────
@st.cache_data(ttl=30)
def load_data_auto():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        # Limpieza de la columna Precio (elimina $, puntos, espacios)
        if 'Precio' in data.columns:
            data['Precio'] = data['Precio'].astype(str).str.replace(r'[\$\.\,\s]', '', regex=True)
            data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0).astype(int)
        return data
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(columns=["Categoría","Producto","Proveedor","Precio"])

df = load_data_auto()

# Estado de la sesión
if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-mini">
    <h1>🌱 Rizotron IoT <span style="font-size:0.8rem; font-weight:400; color:#57606a;">| Cotizador de Componentes</span></h1>
    <div style="font-family:'DM Mono'; color:#1a7f37; font-size:0.75rem; background:#dafbe1; padding:4px 12px; border-radius:20px;">● LIVE SYNC ACTIVO</div>
</div>
""", unsafe_allow_html=True)

# ── Selector Horizontal (Top Bar) ────────────────────────────────────────────
if not df.empty:
    with st.container():
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
                
        # Datos finales de la selección para vista previa
        final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
        precio_actual = int(final_row["Precio"])

        with c4:
            st.markdown(f"""
            <div class="preview-box">
                <div class="preview-label">PRECIO</div>
                <div class="preview-value">{fmt(precio_actual)}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c5:
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("➕ Añadir", use_container_width=True):
                    st.session_state.cotizacion.append({
                        "Categoría": final_row["Categoría"], 
                        "Producto": final_row["Producto"],
                        "Proveedor": final_row["Proveedor"], 
                        "Precio": precio_actual
                    })
                    st.rerun()
            with b2:
                cheap = mask_cat.loc[mask_cat["Precio"].idxmin()]
                if st.button("⬇️ Barato", use_container_width=True, help=f"Añadir el más económico de {cat_sel}"):
                    st.session_state.cotizacion.append({
                        "Categoría": cheap["Categoría"], "Producto": cheap["Producto"],
                        "Proveedor": cheap["Proveedor"], "Precio": int(cheap["Precio"])
                    })
                    st.rerun()
            with b3:
                exp = mask_cat.loc[mask_cat["Precio"].idxmax()]
                if st.button("⬆️ Caro", use_container_width=True, help=f"Añadir el de mayor gama de {cat_sel}"):
                    st.session_state.cotizacion.append({
                        "Categoría": exp["Categoría"], "Producto": exp["Producto"],
                        "Proveedor": exp["Proveedor"], "Precio": int(exp["Precio"])
                    })
                    st.rerun()

# ── Cuerpo Principal ─────────────────────────────────────────────────────────
st.write("")
col_main, col_summary = st.columns([3, 1.2])

with col_main:
    st.markdown("### 📋 Detalle de Compra (Arrastra para ordenar)")
    
    if not st.session_state.cotizacion:
        st.info("No has añadido productos todavía.")
    else:
        # Generar lista de strings para el componente sortable
        # Agregamos el índice al inicio para manejar productos idénticos
        labels_sortables = [
            f"{i+1}. {item['Categoría']} | {item['Producto']} | {item['Proveedor']} | {fmt(item['Precio'])}"
            for i, item in enumerate(st.session_state.cotizacion)
        ]

        # Componente Drag & Drop
        new_labels_order = sort_items(labels_sortables, direction='vertical', key="sortable_list")

        # Si el orden cambia, actualizamos el session_state
        if new_labels_order != labels_sortables:
            indices_nuevos = []
            for label in new_labels_order:
                # Recuperamos el índice original desde el string (el número antes del primer punto)
                idx_original = int(label.split(".")[0]) - 1
                indices_nuevos.append(idx_original)
            
            st.session_state.cotizacion = [st.session_state.cotizacion[i] for i in indices_nuevos]
            st.rerun()

        if st.button("🗑️ Eliminar último ítem añadido", type="secondary"):
             if st.session_state.cotizacion:
                st.session_state.cotizacion.pop()
                st.rerun()

with col_summary:
    total = sum(i["Precio"] for i in st.session_state.cotizacion)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:24px; border-radius:12px; text-align:center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="font-size:0.75rem; color:#57606a; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">PRESUPUESTO TOTAL</div>
        <div style="font-size:2.4rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin:10px 0;">{fmt(total)}</div>
        <div style="font-size:0.85rem; color:#8b949e; border-top:1px solid #f6f8fa; padding-top:10px;">{len(st.session_state.cotizacion)} componentes seleccionados</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("❌ Vaciar Lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
    
    # ── Exportar a EXCEL ──────────────────────────────────────────────────────
    if st.session_state.cotizacion:
        # Preparar DataFrame para exportar
        df_export = pd.DataFrame(st.session_state.cotizacion)
        
        # Crear buffer en memoria para el Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Cotización')
        
        st.download_button(
            label="📊 Descargar como Excel (.xlsx)",
            data=output.getvalue(),
            file_name="cotizacion_rizotron.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
