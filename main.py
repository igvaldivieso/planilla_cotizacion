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
.app-header {
    padding: 4px 2px 12px 2px;
    margin-bottom: 8px;
}

.app-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #1a7f37;
    line-height: 1.1;
    margin: 0;
}

.app-subtitle {
    margin-top: 5px;
}

.app-subtitle a {
    font-size: 0.75rem;
    color: #57606a;
    text-decoration: none;
    transition: color 0.2s;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 1px;
    font-weight: 500;
}

.app-subtitle a:hover {
    color: #1a7f37;
    border-bottom-color: #1a7f37;
}

/* Detalle */
.detail-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    height: 18px;
}

.total-container-offset {
    margin-top: 28px;
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
    border-radius: 14px;
    padding: 14px;
    margin-top: 18px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.checklist-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 8px;
}

.checklist-summary {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #57606a;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 999px;
    padding: 4px 9px;
    display: inline-block;
    margin-bottom: 10px;
}

.checklist-item {
    margin-bottom: 8px;
}

.checklist-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 7px 8px;
    border: 1px solid #eef1f4;
    border-radius: 10px;
    background: #fbfcfd;
}

.checklist-name {
    color: #24292f;
    font-size: 0.88rem;
    line-height: 1.2;
    flex: 1;
    padding-right: 8px;
}

.check-status {
    font-weight: 800;
    font-size: 0.84rem;
    min-width: 72px;
    text-align: right;
    white-space: nowrap;
}

.ok { color: #1a7f37; }
.no { color: #cf222e; }

.progress-track {
    width: 100%;
    height: 7px;
    border-radius: 999px;
    background: #eaeef2;
    overflow: hidden;
    margin-top: 7px;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: #2ea843;
}

div[data-testid="stButton"] > button {
    border-radius: 10px !important;
}

div[data-testid="column"] div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
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
            data["Precio"] = (
                data["Precio"]
                .astype(str)
                .str.replace(r'[\$\.\,\s]', '', regex=True)
            )
            data["Precio"] = pd.to_numeric(data["Precio"], errors="coerce").fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["Categoría", "Producto", "Proveedor", "Precio"])

df = load_data_auto()

# Inicialización de estados
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
        <a href="{SHEET_URL}" target="_blank">
            Acceder a planilla (Google Sheets) ↗
        </a>
    </div>
</div>
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
        # Selector nativo de precio (solo visualización/deshabilitado)
        st.selectbox("Precio", [fmt(precio_actual)], label_visibility="collapsed", disabled=True, key="price_preview_select")

    with c5:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("➕", key="btn_add", use_container_width=True, disabled=final_row is None):
                st.session_state.cotizacion.append({
                    "Categoría": final_row["Categoría"],
                    "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"],
                    "Precio": precio_actual
                })

        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()] if not mask_cat.empty else None
            if st.button("💲", key="btn_min", use_container_width=True, disabled=cheap is None):
                st.session_state.cotizacion.append({
                    "Categoría": cheap["Categoría"],
                    "Producto": cheap["Producto"],
                    "Proveedor": cheap["Proveedor"],
                    "Precio": int(cheap["Precio"])
                })

        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()] if not mask_cat.empty else None
            if st.button("💲💲💲", key="btn_max", use_container_width=True, disabled=exp is None):
                st.session_state.cotizacion.append({
                    "Categoría": exp["Categoría"],
                    "Producto": exp["Producto"],
                    "Proveedor": exp["Proveedor"],
                    "Precio": int(exp["Precio"])
                })
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

    st.markdown(dedent(f"""
    <div class="total-container-offset">
        <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:14px; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">Total neto</div>
            <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin:10px 0;">{fmt(total)}</div>
            <div style="font-size:0.8rem; color:#8b949e; border-top:1px solid #f6f8fa; padding-top:10px;">{len(cot)} componentes</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    st.write("")

    # --- Lógica de nombre de archivo corregida ---
    today_str = datetime.now().strftime("%d-%m-%Y")
    default_name = f"cotización_rizotron_{today_str}"
    
    # Usamos un key para que Streamlit mantenga el estado y actualice la variable al cambiar
    name_input = st.text_input(
        "Nombre del archivo", 
        value=st.session_state.get("file_name_val", default_name),
        placeholder="Escribe el nombre...", 
        label_visibility="collapsed",
        key="file_name_val"
    )
    
    # Aseguramos que siempre tenga extensión .xlsx
    final_filename = f"{name_input.strip() if name_input.strip() else default_name}.xlsx"

    if cot:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(cot).to_excel(writer, index=False)
        
        st.download_button(
            "📊 Descargar Excel",
            data=output.getvalue(),
            file_name=final_filename,
            use_container_width=True,
            key="dl_btn" # Key para forzar re-renderizado si cambia algo
        )

    if st.button("🗑️ Vaciar lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()

    # ── Checklist ──
    checklist_rows = []
    for c in cats_list:
        en_lista = c in cats_en_cot
        icon = "✓" if en_lista else "✕"
        status_class = "ok" if en_lista else "no"
        label = "Incluida" if en_lista else "Pendiente"
        pct = 100 if en_lista else 0

        item_html = dedent(f"""
            <div class="checklist-item">
                <div class="checklist-row">
                    <div class="checklist-name">{c}</div>
                    <div class="check-status {status_class}">{icon} {label}</div>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{pct}%;"></div>
                </div>
            </div>
        """).strip()
        checklist_rows.append(item_html)

    checklist_html = dedent(f"""
    <div class="checklist-card">
        <div class="checklist-title">Estado por categoría</div>
        <div class="checklist-summary">{completas}/{total_cats} completas</div>
    {''.join(checklist_rows) if cats_list else '<div style="color:#57606a; font-size:0.85rem;">No hay categorías cargadas.</div>'}
    </div>
    """).strip()

    st.markdown(checklist_html, unsafe_allow_html=True)
