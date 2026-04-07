import streamlit as st
import pandas as pd
import re
import io
from streamlit_sortables import sort_items # Librería para arrastrar

# ── Configuración de Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Cotizador RAIZ 4.0",
    page_icon="🌱",
    layout="wide",
)

# ── Estilos CSS (Modo Claro & Compacto) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; font-size: 13px; }
.stApp { background: #f6f8fa; color: #1f2328; }

.header-mini {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 10px 20px;
    margin-bottom: 15px;
    display: flex; justify-content: space-between; align-items: center;
}
.header-mini h1 { font-size: 1.4rem; margin: 0; color: #1a7f37; }

/* Caja de Vista Previa */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 8px;
    padding: 5px 12px;
    text-align: center;
}
.preview-label { font-size: 0.6rem; color: #1a7f37; text-transform: uppercase; font-weight: bold; }
.preview-value { font-family: 'DM Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #116329; }

/* El contenedor del sortable suele ser una lista, le damos estilo */
.stSortableList > div {
    background: white !important;
    border: 1px solid #d0d7de !important;
    border-radius: 8px !important;
    padding: 5px !important;
}

.block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Carga y Limpieza de Datos ────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data_auto():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        if 'Precio' in data.columns:
            data['Precio'] = data['Precio'].astype(str).str.replace(r'[\$\.\,\s]', '', regex=True)
            data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["Categoría","Producto","Proveedor","Precio"])

df = load_data_auto()

if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-mini">
    <h1>🌱 Rizotron IoT · Excel Mode</h1>
    <div style="font-family:'DM Mono'; color:#57606a; font-size:0.75rem;">DRAG & DROP ENABLED</div>
</div>
""", unsafe_allow_html=True)

# ── Selector Horizontal ──────────────────────────────────────────────────────
if not df.empty:
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5])
    
    with c1:
        cats = sorted(df["Categoría"].unique().tolist())
        cat_sel = st.selectbox("Cat", cats, label_visibility="collapsed")
    
    mask_cat = df[df["Categoría"] == cat_sel]
    
    with c2:
        prods = sorted(mask_cat["Producto"].unique().tolist())
        prod_sel = st.selectbox("Prod", prods, label_visibility="collapsed")
        
    mask_prod = mask_cat[mask_cat["Producto"] == prod_sel]
    
    with c3:
        provs = mask_prod["Proveedor"].unique().tolist()
        prov_sel = st.selectbox("Prov", provs, label_visibility="collapsed")
            
    final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
    precio_actual = int(final_row["Precio"])

    with c4:
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-label">VISTA PREVIA</div>
            <div class="preview-value">{fmt(precio_actual)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c5:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("➕ Añadir", use_container_width=True):
                st.session_state.cotizacion.append({
                    "id": len(st.session_state.cotizacion), # ID para tracking
                    "Categoría": final_row["Categoría"], "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"], "Precio": precio_actual
                })
        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()]
            if st.button("⬇️ Barato", use_container_width=True):
                st.session_state.cotizacion.append({
                    "id": len(st.session_state.cotizacion),
                    "Categoría": cheap["Categoría"], "Producto": cheap["Producto"],
                    "Proveedor": cheap["Proveedor"], "Precio": int(cheap["Precio"])
                })
        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()]
            if st.button("⬆️ Caro", use_container_width=True):
                st.session_state.cotizacion.append({
                    "id": len(st.session_state.cotizacion),
                    "Categoría": exp["Categoría"], "Producto": exp["Producto"],
                    "Proveedor": exp["Proveedor"], "Precio": int(exp["Precio"])
                })

# ── Detalle Arrastrable ───────────────────────────────────────────────────────
st.write("---")
left, right = st.columns([3, 1.2])

with left:
    st.markdown("### 📋 Detalle (Arrastra para reordenar)")
    
    if not st.session_state.cotizacion:
        st.info("Lista vacía.")
    else:
        # Preparamos los items para el componente sortable
        # Usamos un formato de string que incluya toda la info relevante
        sort_input = []
        for i, item in enumerate(st.session_state.cotizacion):
            label = f"{item['Categoría']} | {item['Producto']} | {item['Proveedor']} | {fmt(item['Precio'])}"
            sort_input.append({'header': label, 'id': i})

        # Renderizamos el componente de arrastre
        sorted_items = sort_items(sort_input, direction='vertical', key="main_sortable")
        
        # Sincronizamos el orden de session_state con el nuevo orden
        if sorted_items:
            new_order = [item['id'] for item in sorted_items]
            st.session_state.cotizacion = [st.session_state.cotizacion[i] for i in new_order]
            
        if st.button("🗑️ Eliminar último ítem", type="secondary"):
             if st.session_state.cotizacion:
                st.session_state.cotizacion.pop()
                st.rerun()

with right:
    total = sum(i["Precio"] for i in st.session_state.cotizacion)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:10px; text-align:center;">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase;">TOTAL ESTIMADO</div>
        <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono;">{fmt(total)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("❌ Vaciar Todo", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
    
    # ── Exportar a EXCEL ──────────────────────────────────────────────────────
    if st.session_state.cotizacion:
        df_export = pd.DataFrame(st.session_state.cotizacion).drop(columns=['id'], errors='ignore')
        
        # Buffer para archivo Excel
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
