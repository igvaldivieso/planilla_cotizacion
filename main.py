import streamlit as st
import pandas as pd
import io
from datetime import datetime
from textwrap import dedent

# ── Configuración de Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Cotizador FIA RAIZ 4.0",
    page_icon="🌱",
    layout="wide",
)

# ── Estilos CSS Personalizados ───────────────────────────────────────────────
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
    font-size: 0.75rem;
    margin-top: 4px;
}

.app-subtitle a {
    color: #57606a;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.app-subtitle a:hover {
    color: #1a7f37;
    text-decoration: underline;
}

/* Detalle de Items */
.detail-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    margin-bottom: 12px;
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
    display: flex;
    align-items: center;
    gap: 10px;
    border-left: 4px solid #2ea843;
    padding-left: 12px;
    width: 100%;
}

.price-tag {
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: #1a7f37;
    font-size: 1.05rem;
}

/* Checklist Card */
.checklist-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 16px;
    margin-top: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.checklist-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 10px;
}

.checklist-summary {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #57606a;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 20px;
    padding: 3px 10px;
    display: inline-block;
    margin-bottom: 12px;
}

.checklist-item { margin-bottom: 8px; }

.checklist-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    border: 1px solid #f0f2f5;
    border-radius: 8px;
    background: #fbfcfd;
}

.checklist-name { color: #24292f; font-size: 0.85rem; flex: 1; }
.check-status { font-weight: 700; font-size: 0.8rem; min-width: 80px; text-align: right; }
.ok { color: #1a7f37; }
.no { color: #cf222e; }

.progress-track {
    width: 100%; height: 6px; border-radius: 10px; background: #eaeef2;
    overflow: hidden; margin-top: 4px;
}
.progress-fill { height: 100%; background: #2ea843; transition: width 0.3s ease; }

/* Botones y Selectores */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
}

div[data-testid="column"] div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}
</style>
"""), unsafe_allow_html=True)

# ── Carga de Datos ───────────────────────────────────────────────────────────
SHEET_ID = "1qWaXRLZtPQ4lX9Nvmkky_IJLaxLGDBTudTKrxAPU6Ak"

@st.cache_data(ttl=60)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        if "Precio" in data.columns:
            data["Precio"] = data["Precio"].astype(str).str.replace(r'[\$\.\,\s]', '', regex=True)
            data["Precio"] = pd.to_numeric(data["Precio"], errors="coerce").fillna(0).astype(int)
        return data
    except Exception:
        return pd.DataFrame(columns=["Categoría", "Producto", "Proveedor", "Precio"])

df = load_data()

if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Funciones de Acción ──────────────────────────────────────────────────────
def move_item(index, direction):
    cot = st.session_state.cotizacion
    new_index = index + direction
    if 0 <= new_index < len(cot):
        cot[index], cot[new_index] = cot[new_index], cot[index]

def delete_item(index):
    st.session_state.cotizacion.pop(index)

# ── Encabezado ───────────────────────────────────────────────────────────────
st.markdown(dedent(f"""
<div class="app-header">
    <div class="app-title">🌱 Cotizador FIA RAIZ 4.0</div>
    <div class="app-subtitle">
        <a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit" target="_blank">
            Gestionar base de datos en Google Sheets ↗
        </a>
    </div>
</div>
"""), unsafe_allow_html=True)

# ── Selector Principal ───────────────────────────────────────────────────────
if not df.empty:
    cats_list = sorted(df["Categoría"].dropna().unique().tolist())
    
    # Grid: Cat | Prod | Prov | Precio (Simulado con Selectbox) | Acciones
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 1.2])

    with c1:
        cat_sel = st.selectbox("Cat", cats_list, label_visibility="collapsed")

    mask_cat = df[df["Categoría"] == cat_sel]
    prods = sorted(mask_cat["Producto"].dropna().unique().tolist())
    
    with c2:
        prod_sel = st.selectbox("Prod", prods, label_visibility="collapsed")

    mask_prod = mask_cat[mask_cat["Producto"] == prod_sel]
    provs = mask_prod["Proveedor"].dropna().unique().tolist()
    
    with c3:
        prov_sel = st.selectbox("Prov", provs, label_visibility="collapsed")

    # Obtener el precio actual basado en la selección
    hit = mask_prod[mask_prod["Proveedor"] == prov_sel]
    final_row = hit.iloc[0] if not hit.empty else None
    precio_actual = int(final_row["Precio"]) if final_row is not None else 0

    with c4:
        # El precio se muestra en el MISMO tipo de componente que los selectores anteriores
        st.selectbox("Precio", [fmt(precio_actual)], label_visibility="collapsed", disabled=True, key="price_preview")

    with c5:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("➕", key="add", use_container_width=True, disabled=final_row is None):
                st.session_state.cotizacion.append(final_row.to_dict())
        with b2:
            if st.button("💲", key="min", use_container_width=True, help="Añadir el más económico"):
                st.session_state.cotizacion.append(mask_cat.loc[mask_cat["Precio"].idxmin()].to_dict())
        with b3:
            if st.button("💰", key="max", use_container_width=True, help="Añadir el más costoso"):
                st.session_state.cotizacion.append(mask_cat.loc[mask_cat["Precio"].idxmax()].to_dict())

# ── Cuerpo Principal (Detalle y Checklist) ───────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2])

cot = st.session_state.cotizacion
cats_en_cot = {item["Categoría"] for item in cot}

with left:
    st.markdown('<div class="detail-title">Detalle de cotización</div>', unsafe_allow_html=True)
    if not cot:
        st.info("No hay productos seleccionados aún.")
    else:
        for idx, item in enumerate(cot):
            r = st.columns([0.4, 9, 0.4], gap="small", vertical_alignment="center")
            with r[0]:
                st.button("▲", key=f"up{idx}", on_click=move_item, args=(idx, -1), use_container_width=True)
                st.button("▼", key=f"dw{idx}", on_click=move_item, args=(idx, 1), use_container_width=True)
            with r[1]:
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
            with r[2]:
                st.button("✕", key=f"del{idx}", on_click=delete_item, args=(idx,), use_container_width=True)

with right:
    # Card de Total
    total = sum(i["Precio"] for i in cot)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:14px; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">Total neto</div>
        <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin:10px 0;">{fmt(total)}</div>
        <div style="font-size:0.8rem; color:#8b949e; border-top:1px solid #f6f8fa; padding-top:10px;">{len(cot)} componentes</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Exportar y Limpiar
    if cot:
        today = datetime.now().strftime("%d-%m-%Y")
        fname = st.text_input("Nombre del archivo", placeholder=f"cotizacion_{today}", label_visibility="collapsed")
        final_name = (fname if fname else f"cotizacion_{today}") + ".xlsx"
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(cot).to_excel(writer, index=False)
        st.download_button("📊 Descargar Excel", data=output.getvalue(), file_name=final_name, use_container_width=True)
    
    if st.button("🗑️ Vaciar lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()

    # ── Checklist de Categorías ──
    if not df.empty:
        completas = sum(1 for c in cats_list if c in cats_en_cot)
        total_c = len(cats_list)
        
        checklist_rows = ""
        for c in cats_list:
            ready = c in cats_en_cot
            icon = "✓" if ready else "✕"
            cls = "ok" if ready else "no"
            label = "Listo" if ready else "Pendiente"
            pct = 100 if ready else 0
            checklist_rows += f"""
            <div class="checklist-item">
                <div class="checklist-row">
                    <div class="checklist-name">{c}</div>
                    <div class="check-status {cls}">{icon} {label}</div>
                </div>
                <div class="progress-track"><div class="progress-fill" style="width:{pct}%;"></div></div>
            </div>"""

        st.markdown(f"""
        <div class="checklist-card">
            <div class="checklist-title">Estado por categoría</div>
            <div class="checklist-summary">{completas}/{total_c} categorías</div>
            {checklist_rows}
        </div>
        """, unsafe_allow_html=True)
