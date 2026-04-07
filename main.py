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

# ── Custom CSS Perfeccionado ──────────────────────────────────────────────────
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

/* Selector / preview / buttons - SIMETRÍA TOTAL */
.preview-box {
    background: #dafbe1;
    border: 1px solid #2ea84340;
    border-radius: 10px;
    padding: 0 12px;
    text-align: center;
    height: 52px; /* Altura base ajustada */
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
}

/* Forzamos que los botones de la fila superior midan lo mismo que la vista previa */
.top-row-selectors [data-testid="stButton"] button {
    height: 52px !important;
    min-height: 52px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem !important;
    border: 1px solid #d0d7de !important;
}

.preview-label {
    font-size: 0.55rem;
    color: #1a7f37;
    text-transform: uppercase;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 2px;
}

.preview-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    color: #116329;
    line-height: 1;
}

/* Detalle */
.detail-title {
    font-size: 0.78rem;
    font-weight: 800;
    color: #57606a;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    height: 18px;
}

/* Alineación exacta del Total Neto con el borde superior del primer ítem */
.total-container-offset {
    margin-top: 30px; /* Ajuste manual para que coincida visualmente */
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

/* Botones de acción lateral (más pequeños que los de arriba) */
[data-testid="column"] [data-testid="stButton"] button {
    border-radius: 8px;
}

/* Quitar espacios extra de Streamlit */
div[data-testid="column"] div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}

/* Estilo Checklist */
.checklist-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 14px;
    margin-top: 18px;
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
    except:
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
    if 0 <= index < len(st.session_state.cotizacion):
        st.session_state.cotizacion.pop(index)
        st.rerun()

# ── Layout Superior ──────────────────────────────────────────────────────────
st.markdown('<div class="app-header"><div class="app-title">🌱 Cotizador FIA RAIZ 4.0</div></div>', unsafe_allow_html=True)

cats_list = sorted(df["Categoría"].dropna().unique().tolist()) if not df.empty else []

if not df.empty and cats_list:
    # Envolvemos los selectores y botones superiores en una clase CSS propia
    st.markdown('<div class="top-row-selectors">', unsafe_allow_html=True)
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

    final_row = mask_prod[mask_prod["Proveedor"] == prov_sel].iloc[0] if not mask_prod.empty and prov_sel else None
    precio_actual = int(final_row["Precio"]) if final_row is not None else 0

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
            if st.button("➕", key="add", use_container_width=True, disabled=final_row is None):
                st.session_state.cotizacion.append(final_row.to_dict())
                st.rerun()
        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()] if not mask_cat.empty else None
            if st.button("💲", key="min", use_container_width=True, disabled=cheap is None):
                st.session_state.cotizacion.append(cheap.to_dict())
                st.rerun()
        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()] if not mask_cat.empty else None
            if st.button("💲💲💲", key="max", use_container_width=True, disabled=exp is None):
                st.session_state.cotizacion.append(exp.to_dict())
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Cuerpo: Detalle y Total ──────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2], vertical_alignment="top")

with left:
    st.markdown('<div class="detail-title">Detalle de cotización</div>', unsafe_allow_html=True)
    if not st.session_state.cotizacion:
        st.info("La lista está vacía.")
    else:
        for idx, item in enumerate(st.session_state.cotizacion):
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
                        <span class="price-tag" style="flex:1.2; text-align:right;">{fmt(int(item['Precio']))}</span>
                    </div>
                </div>
                """), unsafe_allow_html=True)
            with row[2]:
                st.button("✕", key=f"del_{idx}", use_container_width=True, on_click=delete_item, args=(idx,))

with right:
    total = sum(int(i["Precio"]) for i in st.session_state.cotizacion)
    
    # Cuadro de Total con offset de margen superior para alinearse con el primer ítem
    st.markdown(dedent(f"""
    <div class="total-container-offset">
        <div style="background:#ffffff; border:1px solid #d0d7de; padding:20px; border-radius:14px; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="font-size:0.7rem; color:#57606a; text-transform:uppercase; letter-spacing:1px; font-weight:bold;">Total neto</div>
            <div style="font-size:2.2rem; font-weight:800; color:#1a7f37; font-family:DM Mono; margin:10px 0;">{fmt(total)}</div>
            <div style="font-size:0.8rem; color:#8b949e; border-top:1px solid #f6f8fa; padding-top:10px;">{len(st.session_state.cotizacion)} componentes</div>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    st.write("")
    
    # Botones de Acción
    today_str = datetime.now().strftime("%d-%m-%Y")
    default_name = f"cotizacion_rizotron_{today_str}"
    custom_name = st.text_input("Nombre archivo", placeholder=default_name, label_visibility="collapsed")
    
    if st.session_state.cotizacion:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(st.session_state.cotizacion).to_excel(writer, index=False)
        st.download_button("📊 Descargar Excel", data=output.getvalue(), file_name=f"{custom_name or default_name}.xlsx", use_container_width=True)

    if st.button("🗑️ Vaciar lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
