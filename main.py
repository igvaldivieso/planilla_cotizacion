import streamlit as st
import pandas as pd
import io
from datetime import datetime
from textwrap import dedent

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cotizador FIA RAIZ 4.0",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS (Theme Adaptive) ──────────────────────────────────────────────
st.markdown(dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;700&family=Syne:wght@400;600;800&display=swap');

/* Reset general y Tipografía */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
}

/* Header */
.app-header {
    padding: 10px 0px;
    margin-bottom: 15px;
}

.app-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1a7f37; /* Color marca, se ve bien en ambos */
    line-height: 1.1;
    margin: 0;
}

.app-subtitle {
    margin-top: 8px;
}

.app-subtitle a {
    font-size: 0.85rem;
    color: var(--text-color);
    opacity: 0.8;
    text-decoration: none;
    border-bottom: 1px solid #1a7f37;
    padding-bottom: 2px;
    transition: all 0.3s ease;
}

.app-subtitle a:hover {
    opacity: 1;
    color: #1a7f37;
}

/* Contenedores Adaptativos */
.detail-row-wrap, .checklist-card {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.sel-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    width: 100%;
    color: var(--text-color);
}

.price-tag {
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: #1a7f37;
    font-size: 1.1rem;
}

/* Checklist */
.checklist-title {
    font-size: 0.8rem;
    font-weight: 800;
    color: var(--text-color);
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}

.checklist-summary {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    background: rgba(26, 127, 55, 0.1);
    color: #1a7f37;
    border-radius: 20px;
    padding: 4px 12px;
    display: inline-block;
    margin-bottom: 12px;
}

.checklist-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    border-radius: 8px;
    background: var(--background-color);
    margin-bottom: 6px;
    border: 1px solid rgba(128, 128, 128, 0.1);
}

.check-status.ok { color: #2ea843; }
.check-status.no { color: #cf222e; }

/* Progress bar */
.progress-track {
    width: 100%;
    height: 6px;
    background: rgba(128, 128, 128, 0.2);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 12px;
}
.progress-fill {
    height: 100%;
    background: #1a7f37;
}

/* Quitar espacios extra de Streamlit */
div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}

/* Estilo para el total */
.total-box {
    background: #1a7f37;
    color: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-top: 30px;
}
</style>
"""), unsafe_allow_html=True)

# ── Data Loading ─────────────────────────────────────────────────────────────
SHEET_ID = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

@st.cache_data(ttl=60)
def load_data_auto():
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(csv_url)
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

# ── Acciones ──
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
        <a href="{SHEET_URL}" target="_blank">Base de datos en tiempo real (Google Sheets) ↗</a>
    </div>
</div>
"""), unsafe_allow_html=True)

# ── Selector Horizontal ──────────────────────────────────────────────────────
cats_list = sorted(df["Categoría"].dropna().unique().tolist()) if not df.empty else []

if not df.empty and cats_list:
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5])

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
        # Selectbox nativo para el precio
        st.selectbox("Precio", [fmt(precio_actual)], label_visibility="collapsed", disabled=True)

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

# ── Detalle y Resultados ─────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2], gap="medium")

cot = st.session_state.cotizacion
cats_en_cot = {item["Categoría"] for item in cot}

with left:
    st.markdown('<div class="checklist-title">Detalle de la Cotización</div>', unsafe_allow_html=True)
    if not cot:
        st.info("No has agregado productos aún.")
    else:
        for idx, item in enumerate(cot):
            row = st.columns([0.6, 9.5, 0.6], gap="small", vertical_alignment="center")
            with row[0]:
                st.button("▲", key=f"u{idx}", use_container_width=True, on_click=move_item, args=(idx, -1))
                st.button("▼", key=f"d{idx}", use_container_width=True, on_click=move_item, args=(idx, 1))
            with row[1]:
                st.markdown(f"""
                <div class="detail-row-wrap">
                    <div class="sel-item">
                        <span style="flex:1.5; font-weight:800; color:#1a7f37;">{item['Categoría']}</span>
                        <span style="flex:3;">{item['Producto']}</span>
                        <span style="flex:1.5; opacity:0.7; text-align:center;">{item['Proveedor']}</span>
                        <span class="price-tag" style="flex:1.2; text-align:right;">{fmt(item['Precio'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with row[2]:
                st.button("✕", key=f"del{idx}", use_container_width=True, on_click=delete_item, args=(idx,))

with right:
    # --- Cálculo de Total ---
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div class="total-box">
        <div style="font-size:0.75rem; text-transform:uppercase; font-weight:600; opacity:0.9;">Total Estimado</div>
        <div style="font-size:2.2rem; font-weight:800; font-family:'DM Mono'; margin:5px 0;">{fmt(total)}</div>
        <div style="font-size:0.8rem; opacity:0.8;">{len(cot)} ítems seleccionados</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")

    # --- Lógica de Archivo ---
    today_str = datetime.now().strftime("%d-%m-%Y")
    if "filename_state" not in st.session_state:
        st.session_state.filename_state = f"cotizacion_rizotron_{today_str}"

    filename_input = st.text_input("Nombre del archivo", key="filename_state", label_visibility="collapsed")
    
    # El botón de descarga ahora usa el valor actual de session_state
    if cot:
        df_export = pd.DataFrame(cot)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False)
        
        st.download_button(
            label="📊 Descargar Excel",
            data=output.getvalue(),
            file_name=f"{filename_input}.xlsx",
            use_container_width=True,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()

    # --- Checklist ---
    completas = sum(1 for c in cats_list if c in cats_en_cot)
    total_cats = len(cats_list)
    
    checklist_html = f"""
    <div class="checklist-card">
        <div class="checklist-title">Cobertura de Categorías</div>
        <div class="checklist-summary">{completas} de {total_cats} cubiertas</div>
    """
    for c in cats_list:
        en_lista = c in cats_en_cot
        icon = "✓" if en_lista else "○"
        status = "ok" if en_lista else "no"
        pct = 100 if en_lista else 0
        checklist_html += f"""
        <div class="checklist-row">
            <div style="font-size:0.85rem; color:var(--text-color);">{c}</div>
            <div class="check-status {status}" style="font-weight:700;">{icon}</div>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:{pct}%;"></div></div>
        """
    checklist_html += "</div>"
    st.markdown(checklist_html, unsafe_allow_html=True)
