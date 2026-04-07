import streamlit as st
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Cotizador",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS (Light Mode) ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
code, .stCode, .mono { font-family: 'DM Mono', monospace; }

.stApp { background: #f6f8fa; color: #1f2328; }

/* Header */
.rizotron-header {
    background: linear-gradient(135deg, #e6ffed 0%, #dafbe1 50%, #ccf1d8 100%);
    border: 1px solid #2ea84340;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.rizotron-header h1 { font-size: 2.4rem; font-weight: 800; color: #1a7f37; margin: 0; }
.rizotron-header p { color: #57606a; font-size: 0.95rem; }

/* Metric cards */
.price-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.price-card .label { font-size: 0.75rem; color: #57606a; text-transform: uppercase; font-family: 'DM Mono', monospace; }
.price-card .value { font-size: 1.6rem; font-weight: 800; color: #1a7f37; font-family: 'DM Mono', monospace; }

/* Selection item */
.sel-item {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #2ea843;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
}
.sel-item .cat-badge {
    background: #dafbe1; color: #1a7f37; font-size: 0.65rem; padding: 2px 8px; border-radius: 4px;
}
.sel-item .price-tag { font-size: 1rem; font-weight: 700; color: #1a7f37; font-family: 'DM Mono', monospace; }

.section-title {
    font-size: 0.75rem; font-family: 'DM Mono', monospace; color: #57606a;
    text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #d0d7de;
    padding-bottom: 8px; margin-bottom: 16px;
}

/* Inputs & Buttons */
.stButton > button { background: #ffffff; border: 1px solid #d0d7de; color: #1a7f37; border-radius: 8px; }
.stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input {
    background: #ffffff !important; border-color: #d0d7de !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data Loading from Google Sheets ──────────────────────────────────────────
@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def load_data():
    # ID de tu planilla extraído de la URL enviada
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    # URL para exportar la primera hoja (gid=0) como CSV
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        df = pd.read_csv(url)
        # Limpieza básica: Asegurar que Precio sea entero
        if 'Precio' in df.columns:
            df['Precio'] = pd.to_numeric(df['Precio'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        # Retornar estructura vacía en caso de error
        return pd.DataFrame(columns=["Categoría","Producto","Proveedor","Precio","Fecha consulta"])

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

df = st.session_state.df

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rizotron-header">
    <h1>🌱 Rizotron IoT</h1>
    <p>Cotizador sincronizado con Google Sheets</p>
</div>
""", unsafe_allow_html=True)

# ── Botón de Refresco Manual ──────────────────────────────────────────────────
if st.sidebar.button("🔄 Sincronizar Planilla"):
    st.cache_data.clear()
    st.session_state.df = load_data()
    st.rerun()

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown('<div class="section-title">Agregar producto a cotización</div>', unsafe_allow_html=True)

    if not df.empty:
        cats = sorted(df["Categoría"].unique().tolist())
        cat_sel = st.selectbox("Categoría", cats, key="cat_sel")

        cat_df = df[df["Categoría"] == cat_sel].copy()
        cat_df["_label"] = cat_df.apply(
            lambda r: f"{r['Producto']}  ·  {r['Proveedor']}  ({fmt(r['Precio'])})", axis=1
        )
        prod_label = st.selectbox("Producto / Proveedor", cat_df["_label"].tolist(), key="prod_sel")

        row = cat_df[cat_df["_label"] == prod_label].iloc[0]

        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            qty = st.number_input("Cantidad", min_value=1, max_value=99, value=1)
        with col_b:
            st.write("")
            st.write("")
            if st.button("➕ Agregar", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": row["Categoría"],
                    "Producto": row["Producto"],
                    "Proveedor": row["Proveedor"],
                    "Precio unit.": int(row["Precio"]),
                    "Qty": qty,
                    "Subtotal": int(row["Precio"]) * qty,
                })
        with col_c:
            st.write("")
            st.write("")
            cheapest = cat_df.loc[cat_df["Precio"].idxmin()]
            if st.button("💚 + Barato", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": cheapest["Categoría"],
                    "Producto": cheapest["Producto"],
                    "Proveedor": cheapest["Proveedor"],
                    "Precio unit.": int(cheapest["Precio"]),
                    "Qty": 1,
                    "Subtotal": int(cheapest["Precio"]),
                })

    st.markdown('<div class="section-title" style="margin-top:2rem">Acciones rápidas</div>', unsafe_allow_html=True)
    if st.button("🗑️ Limpiar cotización", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()

    st.markdown('<div class="section-title" style="margin-top:2rem">Vista previa de la planilla</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True, height=250)

with right:
    st.markdown('<div class="section-title">Cotización actual</div>', unsafe_allow_html=True)

    cot = st.session_state.cotizacion
    total = sum(i["Subtotal"] for i in cot)
    n_items = len(cot)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="price-card"><div class="label">Total</div><div class="value">{fmt(total)}</div></div>', unsafe_allow_html=True)
    with c2:
        n_cats = len(set(i["Categoría"] for i in cot))
        st.markdown(f'<div class="price-card"><div class="label">Categorías</div><div class="value">{n_cats}</div></div>', unsafe_allow_html=True)

    if not cot:
        st.info("Selecciona productos para ver el resumen.")
    else:
        for idx, item in enumerate(cot):
            col_item, col_del = st.columns([10, 1])
            with col_item:
                st.markdown(f"""
                <div class="sel-item">
                    <div>
                        <span class="cat-badge">{item['Categoría']}</span><br>
                        <b>{item['Producto']}</b> (x{item['Qty']})
                    </div>
                    <div class="price-tag">{fmt(item['Subtotal'])}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"del_{idx}"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()

        if cot:
            csv = pd.DataFrame(cot).to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar CSV", data=csv, file_name="cotizacion.csv", use_container_width=True)
