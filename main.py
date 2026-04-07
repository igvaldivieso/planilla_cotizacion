import streamlit as st
import pandas as pd
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Express",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS (Compact & Light) ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; font-size: 14px; }
.stApp { background: #f6f8fa; color: #1f2328; }

/* Header ultra compacto */
.header-mini {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 10px 20px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-mini h1 { font-size: 1.5rem; margin: 0; color: #1a7f37; }

/* Tarjetas de cotización compactas */
.sel-item {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #2ea843;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
}

.price-tag { font-family: 'DM Mono', monospace; font-weight: 700; color: #1a7f37; }

/* Eliminar espacio extra de Streamlit */
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading con Limpieza de Precios ─────────────────────────────────────
@st.cache_data(ttl=30)
def load_data_auto():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        # Limpieza agresiva de la columna Precio:
        # 1. Convertir a string
        # 2. Quitar $, puntos, comas y espacios
        # 3. Convertir a numérico
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
    <div style="font-family:'DM Mono'; color:#57606a; font-size:0.8rem;">● LIVE SYNC ACTIVO</div>
</div>
""", unsafe_allow_html=True)

# ── Selector Horizontal (Sin Scroll) ──────────────────────────────────────────
if not df.empty:
    with st.container():
        # Layout de 5 columnas para selección en una sola línea
        col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1.5, 1])
        
        with col1:
            cats = sorted(df["Categoría"].unique().tolist())
            cat_sel = st.selectbox("Categoría", cats, label_visibility="collapsed", index=0)
        
        # Filtrar productos por categoría
        mask_cat = df[df["Categoría"] == cat_sel]
        
        with col2:
            prods = sorted(mask_cat["Producto"].unique().tolist())
            prod_sel = st.selectbox("Producto", prods, label_visibility="collapsed")
            
        # Obtener fila específica (si hay varios proveedores, elegimos el primero o filtramos)
        mask_prod = mask_cat[mask_cat["Producto"] == prod_sel]
        
        with col3:
            provs = mask_prod["Proveedor"].unique().tolist()
            prov_sel = st.selectbox("Proveedor", provs, label_visibility="collapsed")
            
        # Datos finales de la selección
        final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
        precio_actual = int(final_row["Precio"])
        
        with col4:
            # Mostrar precio detectado como texto estático para confirmación
            st.markdown(f"<div style='padding-top:10px; font-family:DM Mono; font-weight:bold; color:#1a7f37;'>{fmt(precio_actual)}</div>", unsafe_allow_html=True)
            
        with col5:
            if st.button("➕ Añadir", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": final_row["Categoría"],
                    "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"],
                    "Precio": precio_actual,
                    "Subtotal": precio_actual
                })

# ── Cotización Actual ─────────────────────────────────────────────────────────
st.write("---")
left, right = st.columns([3, 1.5])

with left:
    st.markdown("### Detalle")
    cot = st.session_state.cotizacion
    if not cot:
        st.info("No hay productos en la lista.")
    else:
        for idx, item in enumerate(cot):
            col_i, col_d = st.columns([12, 1])
            with col_i:
                st.markdown(f"""
                <div class="sel-item">
                    <span style="flex:1;"><b>{item['Categoría']}</b></span>
                    <span style="flex:2;">{item['Producto']}</span>
                    <span style="flex:1; color:#57606a;">{item['Proveedor']}</span>
                    <span class="price-tag" style="flex:1; text-align:right;">{fmt(item['Precio'])}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_d:
                if st.button("✕", key=f"del_{idx}"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()

with right:
    st.markdown("### Total")
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:10px; text-align:center;">
        <div style="font-size:0.8rem; color:#57606a; text-transform:uppercase;">Presupuesto Total</div>
        <div style="font-size:2rem; font-weight:800; color:#1a7f37; font-family:DM Mono;">{fmt(total)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Vaciar Cotización", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
