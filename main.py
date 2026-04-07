import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cotizador FIA RAIZ 4.0",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; font-size: 13px; }
.stApp { background: #f6f8fa; color: #1f2328; }

/* Header Clean */
.header-container {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 10px 20px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Preview Price Card */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 8px;
    padding: 5px 12px;
    text-align: center;
    min-height: 58px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.preview-label {
    font-size: 0.6rem;
    color: #1a7f37;
    text-transform: uppercase;
    font-weight: bold;
    line-height: 1;
}
.preview-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #116329;
    line-height: 1.2;
    margin-top: 4px;
}

/* Detalle */
.detail-title {
    font-size: 0.8rem;
    font-weight: bold;
    color: #57606a;
    margin-bottom: 12px;
}
.detail-row-wrap {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 8px;
}
.sel-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    border-left: 4px solid #2ea843;
    padding-left: 12px;
}
.price-tag {
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: #1a7f37;
    font-size: 1.05rem;
}

/* Checklist */
.checklist-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 15px;
    margin-top: 15px;
}
.checklist-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #f6f8fa;
    font-size: 0.85rem;
}

/* Eliminar espacios fantasma de Streamlit */
.block-container { padding-top: 0rem !important; }
div[data-testid="stVerticalBlock"] > div:has(div.header-container) { padding: 0; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        if 'Precio' in data.columns:
            data['Precio'] = data['Precio'].astype(str).str.replace(r'[\$\.\,\s]', '', regex=True)
            data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["Categoría", "Producto", "Proveedor", "Precio"])

df = load_data()
if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(p): return f"${p:,.0f}".replace(",", ".")

# ── Header (Sin contenedores rotos) ───────────────────────────────────────────
c_h1, c_h2 = st.columns([0.85, 0.15])
with c_h1:
    st.markdown('<h1 style="color:#1a7f37; font-size:1.4rem; margin-top:15px;">🌱 Cotizador FIA RAIZ 4.0</h1>', unsafe_allow_html=True)
with c_h2:
    st.write("") # Espaciador
    if st.button("🔄 Sync", help="Sincronizar planilla", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown('<hr style="margin:0 0 20px 0; border:0; border-top:1px solid #d0d7de;">', unsafe_allow_html=True)

# ── Selector ─────────────────────────────────────────────────────────────────
if not df.empty:
    cats_list = sorted(df["Categoría"].dropna().unique().tolist())
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5])
    
    with c1: cat_sel = st.selectbox("Cat", cats_list, label_visibility="collapsed")
    mask_cat = df[df["Categoría"] == cat_sel]
    
    with c2: prod_sel = st.selectbox("Prod", sorted(mask_cat["Producto"].unique()), label_visibility="collapsed")
    mask_prod = mask_cat[mask_cat["Producto"] == prod_sel]
    
    with c3: prov_sel = st.selectbox("Prov", mask_prod["Proveedor"].unique(), label_visibility="collapsed")
    
    final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0]
    precio_actual = int(final_row["Precio"])

    with c4:
        st.markdown(f'<div class="preview-box"><div class="preview-label">VISTA PREVIA</div><div class="preview-value">{fmt(precio_actual)}</div></div>', unsafe_allow_html=True)

    with c5:
        b1, b2, b3 = st.columns(3)
        if b1.button("➕ Añadir", use_container_width=True):
            st.session_state.cotizacion.append(final_row.to_dict())
            st.rerun()
        if b2.button("⬇️ Barato", use_container_width=True):
            st.session_state.cotizacion.append(mask_cat.loc[mask_cat["Precio"].idxmin()].to_dict())
            st.rerun()
        if b3.button("⬆️ Caro", use_container_width=True):
            st.session_state.cotizacion.append(mask_cat.loc[mask_cat["Precio"].idxmax()].to_dict())
            st.rerun()

# ── Cuerpo ───────────────────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2])

with left:
    st.markdown("<div class='detail-title'>DETALLE DE COTIZACIÓN</div>", unsafe_allow_html=True)
    if not st.session_state.cotizacion:
        st.info("La lista está vacía.")
    else:
        for idx, item in enumerate(st.session_state.cotizacion):
            r = st.columns([0.5, 9, 0.5], vertical_alignment="center")
            with r[0]:
                if st.button("▲", key=f"u{idx}") and idx > 0:
                    st.session_state.cotizacion[idx], st.session_state.cotizacion[idx-1] = st.session_state.cotizacion[idx-1], st.session_state.cotizacion[idx]
                    st.rerun()
            with r[1]:
                st.markdown(f"""<div class="detail-row-wrap"><div class="sel-item">
                    <span style="flex:1.2; font-weight:800; color:#1a7f37;">{item['Categoría']}</span>
                    <span style="flex:3;">{item['Producto']}</span>
                    <span style="flex:1.5; color:#57606a; font-size:0.8rem; text-align:center;">{item['Proveedor']}</span>
                    <span class="price-tag" style="flex:1.2; text-align:right;">{fmt(item['Precio'])}</span>
                </div></div>""", unsafe_allow_html=True)
            with r[2]:
                if st.button("✕", key=f"d{idx}"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()

with right:
    # Card Total
    total = sum(int(i["Precio"]) for i in st.session_state.cotizacion)
    st.markdown(f"""<div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:12px; text-align:center;">
        <div style="font-size:0.7rem; color:#57606a; font-weight:bold;">TOTAL NETO</div>
        <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono;">{fmt(total)}</div>
    </div>""", unsafe_allow_html=True)

    st.write("")
    
    # Nombre de archivo (ahora con label para que no parezca un hueco vacío)
    filename = st.text_input("Nombre del archivo Excel", value=f"cotización_rizotron_{datetime.now().strftime('%d-%m-%Y')}")

    if st.session_state.cotizacion:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(st.session_state.cotizacion).to_excel(writer, index=False)
        st.download_button("📊 Descargar Excel", data=output.getvalue(), file_name=f"{filename}.xlsx", use_container_width=True)

    if st.button("🗑️ Vaciar Lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()

    # Checklist de Categorías
    st.markdown('<div class="checklist-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.75rem; font-weight:800; color:#57606a; margin-bottom:10px;">ESTADO POR CATEGORÍA</div>', unsafe_allow_html=True)
    presentes = {i['Categoría'] for i in st.session_state.cotizacion}
    for c in cats_list:
        icon = "✅" if c in presentes else "❌"
        color = "#1a7f37" if c in presentes else "#cf222e"
        st.markdown(f'<div class="checklist-item"><span>{c}</span><span style="color:{color};">{icon}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
