import streamlit as st
import pandas as pd
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Editor",
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
}
.preview-label { font-size: 0.6rem; color: #1a7f37; text-transform: uppercase; font-weight: bold; }
.preview-value { font-family: 'DM Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #116329; }

/* Item Row */
.sel-item {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #2ea843;
    border-radius: 6px;
    padding: 10px 15px;
    display: flex; align-items: center;
    font-size: 0.85rem;
    width: 100%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.price-tag { font-family: 'DM Mono', monospace; font-weight: 700; color: #1a7f37; }

/* Contenedor de botones de movimiento */
.move-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    height: 100%;
}

/* Estilización de los botones de flecha de Streamlit */
div.stButton > button:has(div:contains("v")), 
div.stButton > button:has(div:contains("^")) {
    padding: 0px !important;
    width: 28px !important;
    height: 20px !important;
    min-height: 20px !important;
    background-color: transparent !important;
    border: 1px solid #d0d7de !important;
    color: #57606a !important;
    line-height: 1 !important;
    font-size: 10px !important;
}

div.stButton > button:hover {
    border-color: #2ea843 !important;
    color: #2ea843 !important;
    background-color: #f0fff4 !important;
}

/* Botón Eliminar (X) */
.del-btn button {
    border: none !important;
    color: #cf222e !important;
    background: transparent !important;
}
.del-btn button:hover {
    background: #ffebe9 !important;
}

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

# ── Funciones de Movimiento ──────────────────────────────────────────────────
def move_item(index, direction):
    new_index = index + direction
    if 0 <= new_index < len(st.session_state.cotizacion):
        st.session_state.cotizacion[index], st.session_state.cotizacion[new_index] = \
            st.session_state.cotizacion[new_index], st.session_state.cotizacion[index]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-mini">
    <h1>🌱 Rizotron IoT</h1>
    <div style="font-family:'DM Mono'; color:#57606a; font-size:0.75rem;">AUTO-SYNC: ON</div>
</div>
""", unsafe_allow_html=True)

# ── Fila de Selección Horizontal ──────────────────────────────────────────────
if not df.empty:
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
            
    final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
    precio_actual = int(final_row["Precio"])

    with c4:
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-label">PRECIO VISTA PREVIA</div>
            <div class="preview-value">{fmt(precio_actual)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c5:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("➕ Añadir", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": final_row["Categoría"], "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"], "Precio": precio_actual
                })
        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()]
            if st.button("⬇️ Barato", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": cheap["Categoría"], "Producto": cheap["Producto"],
                    "Proveedor": cheap["Proveedor"], "Precio": int(cheap["Precio"])
                })
        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()]
            if st.button("⬆️ Caro", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": exp["Categoría"], "Producto": exp["Producto"],
                    "Proveedor": exp["Proveedor"], "Precio": int(exp["Precio"])
                })

# ── Detalle con Ordenamiento ──────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2])

with left:
    st.markdown("<div style='font-size:0.8rem; font-weight:bold; color:#57606a; margin-bottom:10px;'>DETALLE DE COTIZACIÓN</div>", unsafe_allow_html=True)
    cot = st.session_state.cotizacion
    
    if not cot:
        st.info("La lista está vacía.")
    else:
        for idx, item in enumerate(cot):
            # Layout de fila: [Controles de Movimiento, Tarjeta Info, Eliminar]
            col_move, col_info, col_del = st.columns([0.25, 10, 0.4])
            
            with col_move:
                # Contenedor vertical para las flechas
                st.write('<div class="move-controls">', unsafe_allow_html=True)
                if st.button("^", key=f"up_{idx}", help="Subir"):
                    move_item(idx, -1)
                    st.rerun()
                if st.button("v", key=f"down_{idx}", help="Bajar"):
                    move_item(idx, 1)
                    st.rerun()
                st.write('</div>', unsafe_allow_html=True)

            with col_info:
                st.markdown(f"""
                <div class="sel-item">
                    <span style="flex:1.2; font-weight:bold; color:#1a7f37;">{item['Categoría']}</span>
                    <span style="flex:2.5;">{item['Producto']}</span>
                    <span style="flex:1.2; color:#57606a; font-size:0.75rem;">{item['Proveedor']}</span>
                    <span class="price-tag" style="flex:1; text-align:right;">{fmt(item['Precio'])}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_del:
                st.write('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_{idx}", help="Eliminar"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()
                st.write('</div>', unsafe_allow_html=True)

with right:
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:10px; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px;">PRESUPUESTO TOTAL</div>
        <div style="font-size:2rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin-top:5px;">{fmt(total)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🗑️ Vaciar Lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
