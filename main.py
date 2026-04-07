import streamlit as st
import pandas as pd
import io
from datetime import datetime
from textwrap import dedent

# ── Configuración de la hoja (Sheet ID) ──────────────────────────────────────
SHEET_ID = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cotizador FIA RAIZ 4.0",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(dedent(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Syne', sans-serif;
    font-size: 13px;
}}

.stApp {{
    background: #f6f8fa;
    color: #1f2328;
}}

/* Header */
.app-header {{
    padding: 4px 2px 12px 2px;
    margin-bottom: 8px;
}}

.app-title {{
    font-size: 1.35rem;
    font-weight: 800;
    color: #1a7f37;
    line-height: 1.1;
    margin: 0;
}}

.app-subtitle {{
    font-size: 0.72rem;
    margin-top: 3px;
}}

.app-subtitle a {{
    color: #57606a;
    text-decoration: none;
    transition: all 0.2s ease;
}}

.app-subtitle a:hover {{
    color: #1a7f37;
    text-decoration: underline;
}}

/* ── Ajuste de Altura Identica ── */
/* Forzamos 42px para el contenedor y para los botones */
.preview-box {{
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 10px;
    height: 42px !important; 
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
}}

div[data-testid="column"] button {{
    height: 42px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 !important;
    padding: 0 !important;
}}

.preview-value {{
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #116329;
    line-height: 1;
}}

/* Detalle y Checklist */
.detail-title {{
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    margin-bottom: 10px;
    text-transform: uppercase;
}}

.detail-row-wrap {{
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 8px;
}}

.sel-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    width: 100%;
}}

.price-tag {{
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: #1a7f37;
}}

.checklist-card {{
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 14px;
    margin-top: 18px;
}}

.progress-track {{
    width: 100%;
    height: 7px;
    border-radius: 999px;
    background: #eaeef2;
    overflow: hidden;
    margin-top: 7px;
}}

.progress-fill {{
    height: 100%;
    background: #2ea843;
}}

/* Reset de espaciado interno de columnas de Streamlit */
div[data-testid="column"] div[data-testid="stVerticalBlock"] {{
    gap: 0rem !important;
}}
</style>
"""), unsafe_allow_html=True)

# ── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data_auto():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        if "Precio" in data.columns:
            data["Precio"] = data["Precio"].astype(str).str.replace(r'[\$\.\,\s]', '', regex=True)
            data["Precio"] = pd.to_numeric(data["Precio"], errors="coerce").fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["Categoría", "Producto", "Proveedor", "Precio"])

df = load_data_auto()

if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Acciones (Callbacks) ─────────────────────────────────────────────────────
def move_item(index, direction):
    cot = st.session_state.cotizacion
    new_index = index + direction
    if 0 <= new_index < len(cot):
        cot[index], cot[new_index] = cot[new_index], cot[index]

def delete_item(index):
    cot = st.session_state.cotizacion
    if 0 <= index < len(cot):
        cot.pop(index)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(dedent(f"""
<div class="app-header">
    <div class="app-title">🌱 Cotizador FIA RAIZ 4.0</div>
    <div class="app-subtitle">
        <a href="{SHEET_URL}" target="_blank" title="Abrir planilla de Google Sheets">
            Cotización rápida desde planilla Google Sheets ↗
        </a>
    </div>
</div>
"""), unsafe_allow_html=True)

# ── Selector Horizontal ──────────────────────────────────────────────────────
cats_list = sorted(df["Categoría"].dropna().unique().tolist()) if not df.empty else []

if not df.empty and cats_list:
    # El vertical_alignment="bottom" asegura que se alineen con la base de los selectboxes
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5], vertical_alignment="bottom")

    with c1:
        cat_sel = st.selectbox("Categoría", cats_list, label_visibility="collapsed")

    mask_cat = df[df["Categoría"] == cat_sel]
    prods = sorted(mask_cat["Producto"].dropna().unique().tolist())
    
    with c2:
        prod_sel = st.selectbox("Producto", prods, label_visibility="collapsed") if prods else None

    mask_prod = mask_cat[mask_cat["Producto"] == prod_sel] if prod_sel else pd.DataFrame()
    provs = mask_prod["Proveedor"].dropna().unique().tolist()
    
    with c3:
        prov_sel = st.selectbox("Proveedor", provs, label_visibility="collapsed") if provs else None

    final_row = None
    if prov_sel and not mask_prod.empty:
        hit = mask_prod[mask_prod["Proveedor"] == prov_sel]
        if not hit.empty: final_row = hit.iloc[0]

    precio_actual = int(final_row["Precio"]) if final_row is not None else 0

    with c4:
        # Contenedor solo con el valor numérico
        st.markdown(f"""
        <div class="preview-box">
            <div class="preview-value">{fmt(precio_actual)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("➕", key="btn_add", use_container_width=True, disabled=final_row is None):
                st.session_state.cotizacion.append({
                    "Categoría": final_row["Categoría"], "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"], "Precio": precio_actual
                })
        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()] if not mask_cat.empty else None
            if st.button("💲", key="btn_min", use_container_width=True, disabled=cheap is None):
                st.session_state.cotizacion.append({
                    "Categoría": cheap["Categoría"], "Producto": cheap["Producto"],
                    "Proveedor": cheap["Proveedor"], "Precio": int(cheap["Precio"])
                })
        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()] if not mask_cat.empty else None
            if st.button("💲💲💲", key="btn_max", use_container_width=True, disabled=exp is None):
                st.session_state.cotizacion.append({
                    "Categoría": exp["Categoría"], "Producto": exp["Producto"],
                    "Proveedor": exp["Proveedor"], "Precio": int(exp["Precio"])
                })
else:
    st.warning("No se pudieron cargar datos.")

# ── Detalle ──────────────────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2], vertical_alignment="top")
cot = st.session_state.cotizacion

with left:
    st.markdown('<div class="detail-title">Detalle de cotización</div>', unsafe_allow_html=True)
    if not cot:
        st.info("La lista está vacía.")
    else:
        for idx, item in enumerate(cot):
            row = st.columns([0.55, 9.8, 0.65], gap="small", vertical_alignment="center")
            with row[0]:
                st.button("▲", key=f"up_{idx}", use_container_width=True, on_click=move_item, args=(idx, -1))
                st.button("▼", key=f"down_{idx}", use_container_width=True, on_click=move_item, args=(idx, 1))
            with row[1]:
                st.markdown(f"""
                <div class="detail-row-wrap">
                    <div class="sel-item">
                        <span style="flex:1.2; font-weight:800; color:#1a7f37;">{item['Categoría']}</span>
                        <span style="flex:3;">{item['Producto']}</span>
                        <span style="flex:1.5; color:#57606a; font-size:0.8rem; text-align:center;">{item['Proveedor']}</span>
                        <span class="price-tag" style="flex:1.2; text-align:right;">{fmt(item['Precio'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with row[2]:
                st.button("✕", key=f"del_{idx}", use_container_width=True, on_click=delete_item, args=(idx,))

with right:
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:14px; text-align:center;">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; font-weight:bold;">Total neto</div>
        <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono;">{fmt(total)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if cot:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(cot).to_excel(writer, index=False)
        st.download_button("📊 Descargar Excel", data=output.getvalue(), file_name="cotizacion.xlsx", use_container_width=True)
        if st.button("🗑️ Vaciar lista", use_container_width=True):
            st.session_state.cotizacion = []
            st.rerun()

    # Checklist
    cats_en_cot = {item["Categoría"] for item in cot}
    cats_list_all = sorted(df["Categoría"].dropna().unique().tolist()) if not df.empty else []
    
    st.markdown('<div class="checklist-card"><div class="checklist-title">Estado</div>', unsafe_allow_html=True)
    for c in cats_list_all:
        en_lista = c in cats_en_cot
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-top:8px;">
                <span>{c}</span><span style="color:{'#1a7f37' if en_lista else '#cf222e'}">{'✓' if en_lista else '✕'}</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:{100 if en_lista else 0}%;"></div></div>
        """, unsafe_allow_html=True)
