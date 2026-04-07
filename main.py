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

/* Header */
.header-mini {
    background: #ffffff;
    border-bottom: 1px solid #d0d7de;
    padding: 10px 20px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-mini h1 {
    font-size: 1.4rem;
    margin: 0;
    color: #1a7f37;
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
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.sel-item {
    background: transparent;
    border: none;
    border-left: 4px solid #2ea843;
    border-radius: 6px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    width: 100%;
    min-height: 54px;
}

.price-tag {
    font-family: 'DM Mono', monospace;
    font-weight: 700;
    color: #1a7f37;
    font-size: 1.05rem;
}

/* Botones del detalle */
div[data-testid="stButton"] > button {
    width: 100% !important;
    min-width: 0 !important;
    height: 30px !important;
    min-height: 30px !important;
    padding: 0 !important;
    margin: 0 !important;
    line-height: 1 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}

/* Estilo específico para el botón de sincronización (más discreto) */
.sync-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Reduce el espacio vertical entre botones apilados en la columna de movimiento */
div[data-testid="column"] div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}

/* Mueve un poco el botón X para que quede centrado visualmente */
.delete-box {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
}

/* General */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
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
            data['Precio'] = (
                data['Precio']
                .astype(str)
                .str.replace(r'[\$\.\,\s]', '', regex=True)
            )
            data['Precio'] = pd.to_numeric(data['Precio'], errors='coerce').fillna(0).astype(int)
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
    cot = st.session_state.cotizacion
    if 0 <= index < len(cot):
        cot.pop(index)
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
# Usamos columnas para colocar el título y el botón de sincronización a la derecha
head_col1, head_col2 = st.columns([0.8, 0.2])

with head_col1:
    st.markdown("""
    <div style="display: flex; align-items: center; height: 100%;">
        <h1 style="font-size: 1.4rem; margin: 0; color: #1a7f37; font-family: 'Syne', sans-serif;">🌱 Cotizador FIA RAIZ 4.0</h1>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    # Botón de sincronización manual discreto
    subcol1, subcol2 = st.columns([0.6, 0.4])
    with subcol1:
        st.markdown("<div style='font-family:\"DM Mono\"; color:#57606a; font-size:0.75rem; text-align:right; margin-top:8px;'>AUTO-SYNC: ON</div>", unsafe_allow_html=True)
    with subcol2:
        if st.button("🔄", help="Sincronizar planilla de Google"):
            st.cache_data.clear()
            st.rerun()

st.markdown("---")

# ── Selector Horizontal ───────────────────────────────────────────────────────
if not df.empty:
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.5, 1.2, 2.5])

    with c1:
        cats = sorted(df["Categoría"].dropna().unique().tolist())
        cat_sel = st.selectbox("Categoría", cats, label_visibility="collapsed")

    mask_cat = df[df["Categoría"] == cat_sel]

    with c2:
        prods = sorted(mask_cat["Producto"].dropna().unique().tolist())
        prod_sel = st.selectbox("Producto", prods, label_visibility="collapsed")

    mask_prod = mask_cat[mask_cat["Producto"] == prod_sel]

    with c3:
        provs = mask_prod["Proveedor"].dropna().unique().tolist()
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
                    "Categoría": final_row["Categoría"],
                    "Producto": final_row["Producto"],
                    "Proveedor": final_row["Proveedor"],
                    "Precio": precio_actual
                })
                st.rerun()

        with b2:
            cheap = mask_cat.loc[mask_cat["Precio"].idxmin()]
            if st.button("⬇️ Barato", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": cheap["Categoría"],
                    "Producto": cheap["Producto"],
                    "Proveedor": cheap["Proveedor"],
                    "Precio": int(cheap["Precio"])
                })
                st.rerun()

        with b3:
            exp = mask_cat.loc[mask_cat["Precio"].idxmax()]
            if st.button("⬆️ Caro", use_container_width=True):
                st.session_state.cotizacion.append({
                    "Categoría": exp["Categoría"],
                    "Producto": exp["Producto"],
                    "Proveedor": exp["Proveedor"],
                    "Precio": int(exp["Precio"])
                })
                st.rerun()

# ── Detalle ───────────────────────────────────────────────────────────────────
st.write("")
left, right = st.columns([3, 1.2])

with left:
    st.markdown(
        "<div class='detail-title'>DETALLE DE COTIZACIÓN</div>",
        unsafe_allow_html=True
    )

    cot = st.session_state.cotizacion

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
                st.markdown("<div class='delete-box'>", unsafe_allow_html=True)
                st.button("✕", key=f"del_{idx}", use_container_width=True, on_click=delete_item, args=(idx,))
                st.markdown("</div>", unsafe_allow_html=True)

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

    # Campo para nombre del archivo
    today_str = datetime.now().strftime("%d-%m-%Y")
    default_filename = f"cotización_rizotron_{today_str}"
    
    file_name_input = st.text_input(
        "Nombre del Excel", 
        placeholder=default_filename,
        help="Si se deja vacío, se usará el nombre por defecto con la fecha de hoy."
    )
    
    # Lógica de nombre final
    final_name = file_name_input.strip() if file_name_input.strip() else default_filename

    if cot:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(cot).to_excel(writer, index=False)
        
        st.download_button(
            "📊 Descargar Excel (.xlsx)",
            data=output.getvalue(),
            file_name=f"{final_name}.xlsx",
            use_container_width=True
        )

    if st.button("🗑️ Vaciar Lista", use_container_width=True):
        st.session_state.cotizacion = []
        st.rerun()
