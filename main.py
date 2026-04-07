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

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
}

.stApp {
    background: #f6f8fa;
    color: #1f2328;
}

/* Header */
.app-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #1a7f37;
    line-height: 1.1;
    margin: 0;
}

.app-subtitle {
    font-size: 0.72rem;
    color: #57606a;
    margin-top: 3px;
    margin-bottom: 10px;
}

/* Selector / preview */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 10px;
    padding: 7px 12px;
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
    font-weight: 700;
    line-height: 1;
    letter-spacing: 0.3px;
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
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.detail-row-wrap {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.sel-item {
    background: transparent;
    border: none;
    border-left: 4px solid #2ea843;
    border-radius: 8px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    width: 100%;
    min-height: 54px;
    flex-wrap: wrap;
}

.price-tag {
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: #1a7f37;
    font-size: 1.05rem;
}

/* Checklist nativa */
.checklist-wrap {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 14px;
    margin-top: 18px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.checklist-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f2f4;
}

.checklist-title2 {
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin: 0;
}

.checklist-summary2 {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #57606a;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 999px;
    padding: 4px 9px;
    white-space: nowrap;
}

.check-row {
    background: #fbfcfd;
    border: 1px solid #eef1f4;
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 8px;
}

.check-row:last-child {
    margin-bottom: 0;
}

.check-name {
    font-size: 0.88rem;
    color: #24292f;
    line-height: 1.2;
}

.check-status-ok {
    color: #1a7f37;
    font-weight: 800;
    font-size: 0.84rem;
    text-align: right;
    white-space: nowrap;
}

.check-status-no {
    color: #cf222e;
    font-weight: 800;
    font-size: 0.84rem;
    text-align: right;
    white-space: nowrap;
}

/* Botones */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
}

/* Ajustes de columnas */
div[data-testid="column"] div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}

/* Inputs más compactos */
div[data-baseweb="select"] > div {
    min-height: 40px;
}
</style>
"""), unsafe_allow_html=True)

# ── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data_auto():
    sheet_id = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        if "Precio" in data.columns:
            data["Precio"] = (
                data["Precio"]
                .astype(str)
                .str.replace(r'[\$\.\,\s]', '', regex=True)
            )
            data["Precio"] = pd.to_numeric(data["Precio"], errors="coerce").fillna(0).astype(int)
        return data
    except Exception:
        return pd.DataFrame(columns=["Categoría", "Producto", "Proveedor", "Precio"])

df = load_data_auto()

if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Acciones ─────────────────────────────────────────────────────────────────
def move_item(index, direction):
    cot = st.session_state.cotizacion
    new_index = index + direction
    if 0 <= new_index < len(cot):
        cot[index], cot[new_index] = cot[new_index], cot[index]
        st.rerun()

def delete_item(index):
    cot = st.session_state.cotizacion
    if 0 <= index < len(cot):
        cot.pop(index)
        st.rerun()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(dedent("""
<div class="app-title">🌱 Cotizador FIA RAIZ 4.0</div>
<div class="app-subtitle">Cotización rápida desde planilla Google Sheets</div>
"""), unsafe_allow_html=True)

# ── Selector Horizontal ──────────────────────────────────────────────────────
cats_list = sorted(df["Categoría"].dropna().unique().tolist()) if not df.empty and "Categoría" in df.columns else []

if not df.empty and cats_list:
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5])

    with c1:
        cat_sel = st.selectbox("Categoría", cats_list, label_visibility="collapsed")

    mask_cat = df[df["Categoría"] == cat_sel]

    prods = sorted(mask_cat["Producto"].dropna().unique().tolist()) if not mask_cat.empty else []
    with c2:
        prod_sel = st.selectbox("Producto", prods, label_visibility="collapsed") if prods else None

    mask_prod = mask_cat[mask_cat["Producto"] == prod_sel] if prod_sel is not None else pd.DataFrame()

    provs = mask_prod["Proveedor"].dropna().unique().tolist() if not mask_prod.empty else []
    with c3:
        prov_sel = st.selectbox("Proveedor", provs, label_visibility="collapsed") if provs else None

    final_row = None
    if prov_sel is not None and not mask_prod.empty:
        hit = mask_prod[mask_prod["Proveedor"] == prov_sel]
        if not hit.empty:
            final_row = hit.iloc[0]

    precio_actual = int(final_row["Precio"]) if final_row is not None else 0

    with c4:
        st.markdown(dedent(f"""
        <div class="preview-box">
            <div class="preview-label">VISTA PREVIA</div>
            <div class="preview-value">{fmt(precio_actual)}</div>
        </div>
        """), unsafe_allow_html=True)

    with c5:
        b1, b2, b3 = st.columns(3)

        with b1:
            if st.button("➕ Añadir", use_container_width=True, disabled=final_row is None):
                st.session_state.cotizacion.append({
                    "Categoría": final_row["Categoría"],
                    "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"],
                    "Precio": precio_actual
                })
                st.rerun()

        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()] if not mask_cat.empty else None
            if st.button("⬇️ Barato", use_container_width=True, disabled=cheap is None):
                st.session_state.cotizacion.append({
                    "Categoría": cheap["Categoría"],
                    "Producto": cheap["Producto"],
                    "Proveedor": cheap["Proveedor"],
                    "Precio": int(cheap["Precio"])
                })
                st.rerun()

        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()] if not mask_cat.empty else None
            if st.button("⬆️ Caro", use_container_width=True, disabled=exp is None):
                st.session_state.cotizacion.append({
                    "Categoría": exp["Categoría"],
                    "Producto": exp["Producto"],
                    "Proveedor": exp["Proveedor"],
                    "Precio": int(exp["Precio"])
                })
                st.rerun()
else:
    st.warning("No se pudieron cargar categorías desde la planilla.")

# ── Detalle ──────────────────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2], vertical_alignment="top")

cot = st.session_state.cotizacion
cats_en_cot = {item["Categoría"] for item in cot}
completas = sum(1 for c in cats_list if c in cats_en_cot)
total_cats = len(cats_list)

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
                st.markdown(dedent(f"""
                <div class="detail-row-wrap">
                    <div class="sel-item">
                        <span style="flex:1.2; font-weight:800; color:#1a7f37;">{item['Categoría']}</span>
                        <span style="flex:3;">{item['Producto']}</span>
                        <span style="flex:1.5; color:#57606a; font-size:0.8rem; text-align:center;">{item['Proveedor']}</span>
                        <span class="price-tag" style="flex:1.2; text-align:right;">{fmt(item['Precio'])}</span>
                    </div>
                </div>
                """), unsafe_allow_html=True)

            with row[2]:
                st.button("✕", key=f"del_{idx}", use_container_width=True, on_click=delete_item, args=(idx,))

with right:
    total = sum(i["Precio"] for i in cot)

    st.metric("Total neto", fmt(total))
    st.caption(f"{len(cot)} componentes")

    today_str = datetime.now().strftime("%d-%m-%Y")
    default_name = f"cotización_rizotron_{today_str}"
    custom_name = st.text_input("Nombre del archivo", placeholder=default_name, label_visibility="collapsed")
    final_filename = f"{custom_name.strip() if custom_name.strip() else default_name}.xlsx"

    if cot:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(cot).to_excel(writer, index=False)
        st.download_button(
            "📊 Descargar Excel",
            data=output.getvalue(),
            file_name=final_filename,
            use_container_width=True
        )

    if st.button("🗑️ Vaciar lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()

    st.markdown('<div class="checklist-wrap">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="checklist-head"><div class="checklist-title2">Estado por categoría</div><div class="checklist-summary2">{completas}/{total_cats} completas</div></div>',
        unsafe_allow_html=True
    )

    if not cats_list:
        st.caption("No hay categorías cargadas.")
    else:
        for c in cats_list:
            en_lista = c in cats_en_cot
            etiqueta = "Incluida" if en_lista else "Pendiente"
            clase = "check-status-ok" if en_lista else "check-status-no"
            simbolo = "✓" if en_lista else "✕"

            row = st.columns([4.5, 1.5], vertical_alignment="center")
            with row[0]:
                st.markdown(f'<div class="check-name">{c}</div>', unsafe_allow_html=True)
            with row[1]:
                st.markdown(f'<div class="{clase}">{simbolo} {etiqueta}</div>', unsafe_allow_html=True)

        st.progress(completas / total_cats if total_cats else 0)

    st.markdown('</div>', unsafe_allow_html=True)
