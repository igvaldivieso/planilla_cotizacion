import streamlit as st
import pandas as pd
import re
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Editor",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS (Ultra-Refined) ───────────────────────────────────────────────
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

/* Item Row - Tarjeta Principal */
.sel-item {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #2ea843;
    border-radius: 6px;
    padding: 12px 18px;
    display: flex; align-items: center;
    font-size: 0.9rem;
    width: 100%;
    min-height: 52px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.price-tag { font-family: 'DM Mono', monospace; font-weight: 700; color: #1a7f37; font-size: 1.1rem; }

/* --- FIX DE MOVIMIENTO (FLECHAS PEQUEÑAS Y UNIDAS) --- */
/* Eliminamos el gap de Streamlit en la columna de movimiento */
[data-testid="column"]:first-child div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}

/* Estilizamos los botones de flecha ▲ ▼ */
div.stButton > button:has(div:contains("▲")), 
div.stButton > button:has(div:contains("▼")) {
    width: 32px !important;
    height: 26px !important;
    min-height: 26px !important;
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    color: #57606a !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 10px !important;
    transition: all 0.2s;
}

/* Unimos visualmente los botones */
div.stButton > button:has(div:contains("▲")) {
    border-radius: 6px 6px 0 0 !important;
}
div.stButton > button:has(div:contains("▼")) {
    border-radius: 0 0 6px 6px !important;
    border-top: none !important;
}

div.stButton > button:has(div:contains("▲")):hover, 
div.stButton > button:has(div:contains("▼")):hover {
    background: #f0fff4 !important;
    color: #1a7f37 !important;
    border-color: #2ea843 !important;
    z-index: 10;
}

/* Botón Eliminar (X) más elegante */
div.stButton > button:has(div:contains("✕")) {
    background: transparent !important;
    border: 1px solid #d0d7de !important;
    color: #cf222e !important;
    border-radius: 6px !important;
    width: 32px !important;
    height: 32px !important;
}
div.stButton > button:has(div:contains("✕")):hover {
    background: #ffebe9 !important;
    border-color: #cf222e !important;
}

.block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────
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

# ── Movimiento ────────────────────────────────────────────────────────────────
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

# ── Selector Horizontal ───────────────────────────────────────────────────────
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
            <div class="preview-label">VISTA PREVIA</div>
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

# ── Detalle ───────────────────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2])

with left:
    st.markdown("<div style='font-size:0.8rem; font-weight:bold; color:#57606a; margin-bottom:12px;'>DETALLE DE COTIZACIÓN</div>", unsafe_allow_html=True)
    cot = st.session_state.cotizacion
    
    if not cot:
        st.info("La lista está vacía.")
    else:
        for idx, item in enumerate(cot):
            # Layout: [Control Mover, Tarjeta, Borrar]
            col_move, col_info, col_del = st.columns([0.2, 10, 0.4])
            
            with col_move:
                # Botones ▲ ▼ pegados sin gap
                if st.button("▲", key=f"up_{idx}"):
                    move_item(idx, -1)
                    st.rerun()
                if st.button("▼", key=f"down_{idx}"):
                    move_item(idx, 1)
                    st.rerun()

            with col_info:
                st.markdown(f"""
                <div class="sel-item">
                    <span style="flex:1.2; font-weight:800; color:#1a7f37;">{item['Categoría']}</span>
                    <span style="flex:3;">{item['Producto']}</span>
                    <span style="flex:1.5; color:#57606a; font-size:0.8rem; text-align:center;">{item['Proveedor']}</span>
                    <span class="price-tag" style="flex:1.2; text-align:right;">{fmt(item['Precio'])}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_del:
                # X para borrar centrada verticalmente
                st.write('<div style="padding-top:10px;">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_{idx}"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()
                st.write('</div>', unsafe_allow_html=True)

with right:
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:12px; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">TOTAL NETO</div>
        <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin:10px 0;">{fmt(total)}</div>
        <div style="font-size:0.8rem; color:#8b949e; border-top:1px solid #f6f8fa; padding-top:10px;">{len(cot)} componentes</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🗑️ Vaciar Lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
        
    if cot:
        # Buffer para exportar a Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(cot).to_excel(writer, index=False)
        st.download_button("📊 Descargar Excel (.xlsx)", data=output.getvalue(), file_name="cotizacion.xlsx", use_container_width=True)
