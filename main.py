import streamlit as st
import pandas as pd
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Pro",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; font-size: 13px; }
.stApp { background: #f6f8fa; color: #1f2328; }

/* Header */
.header-mini {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 10px 20px;
    margin-bottom: 15px;
    display: flex; justify-content: space-between; align-items: center;
}
.header-mini h1 { font-size: 1.4rem; margin: 0; color: #1a7f37; }

/* Preview Price Card */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 8px;
    padding: 5px 12px;
    text-align: center;
    min-width: 100px;
}
.preview-label { font-size: 0.65rem; color: #1a7f37; text-transform: uppercase; font-weight: bold; }
.preview-value { font-family: 'DM Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #116329; }

/* Item Row */
.sel-item {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #2ea843;
    border-radius: 6px;
    padding: 6px 12px;
    margin-bottom: 4px;
    display: flex; align-items: center;
    font-size: 0.85rem;
}
.price-tag { font-family: 'DM Mono', monospace; font-weight: 700; color: #1a7f37; }

/* Botones pequeños */
.stButton > button { font-size: 0.8rem !important; padding: 0.2rem 0.5rem !important; }

.block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading & Cleaning ──────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data_auto():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        # Limpieza de columna Precio (quita $, puntos, comas y espacios)
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

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-mini">
    <h1>🌱 Rizotron IoT</h1>
    <div style="font-family:'DM Mono'; color:#57606a; font-size:0.75rem;">LIVE SYNC: ON (30s)</div>
</div>
""", unsafe_allow_html=True)

# ── Fila de Selección Horizontal (Sin Scroll) ─────────────────────────────────
if not df.empty:
    # 6 columnas para Categoría, Producto, Proveedor, Vista Previa y Acciones
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
            
    # Fila final para la vista previa
    final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
    precio_actual = int(final_row["Precio"])

    with c4:
        # VISTA PREVIA DEL PRECIO
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-label">PRECIO</div>
            <div class="preview-value">{fmt(precio_actual)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c5:
        # BOTONES DE ACCIÓN
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.button("➕ Añadir", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": final_row["Categoría"], "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"], "Precio": precio_actual
                })
        
        with btn_col2:
            # Lógica del más barato de la categoría
            cheapest = mask_cat.loc[mask_cat["Precio"].idxmin()]
            if st.button("⬇️ Barato", help=f"Añadir {cheapest['Producto']} ({fmt(cheapest['Precio'])})", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": cheapest["Categoría"], "Producto": cheapest["Producto"],
                    "Proveedor": cheapest["Proveedor"], "Precio": int(cheapest["Precio"])
                })
        
        with btn_col3:
            # Lógica del más caro de la categoría
            expensive = mask_cat.loc[mask_cat["Precio"].idxmax()]
            if st.button("⬆️ Caro", help=f"Añadir {expensive['Producto']} ({fmt(expensive['Precio'])})", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": expensive["Categoría"], "Producto": expensive["Producto"],
                    "Proveedor": expensive["Proveedor"], "Precio": int(expensive["Precio"])
                })

# ── Detalle de Cotización ─────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2])

with left:
    st.markdown("<div style='font-size:0.8rem; font-weight:bold; color:#57606a; margin-bottom:5px;'>LISTA DE COMPRA</div>", unsafe_allow_html=True)
    cot = st.session_state.cotizacion
    if not cot:
        st.info("No hay productos seleccionados.")
    else:
        for idx, item in enumerate(cot):
            col_i, col_d = st.columns([12, 1])
            with col_i:
                st.markdown(f"""
                <div class="sel-item">
                    <span style="flex:1.2; font-weight:bold; color:#1a7f37;">{item['Categoría']}</span>
                    <span style="flex:2.5;">{item['Producto']}</span>
                    <span style="flex:1.2; color:#57606a; font-size:0.75rem;">{item['Proveedor']}</span>
                    <span class="price-tag" style="flex:1; text-align:right;">{fmt(item['Precio'])}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_d:
                if st.button("✕", key=f"del_{idx}"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()

with right:
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:15px; border-radius:10px; text-align:center;">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px;">TOTAL NETO</div>
        <div style="font-size:1.8rem; font-weight:800; color:#1a7f37; font-family:DM Mono;">{fmt(total)}</div>
        <div style="font-size:0.75rem; color:#8b949e; margin-top:5px;">{len(cot)} componentes</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Vaciar Lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
    
    if cot:
        csv = pd.DataFrame(cot).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar", data=csv, file_name="cotizacion_rizotron.csv", use_container_width=True)
