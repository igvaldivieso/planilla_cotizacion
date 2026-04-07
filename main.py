import streamlit as st
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rizotron IoT · Cotizador",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}
code, .stCode, .mono { font-family: 'DM Mono', monospace; }

/* Background */
.stApp { background: #0d1117; color: #e6edf3; }

/* Header */
.rizotron-header {
    background: linear-gradient(135deg, #0d2818 0%, #1a4530 50%, #0a3d20 100%);
    border: 1px solid #2ea84380;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.rizotron-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, #2ea84320 0%, transparent 70%);
    border-radius: 50%;
}
.rizotron-header h1 {
    font-size: 2.4rem;
    font-weight: 800;
    color: #3fb950;
    margin: 0 0 4px 0;
    letter-spacing: -1px;
}
.rizotron-header p {
    color: #8b949e;
    font-size: 0.95rem;
    margin: 0;
}

/* Metric cards */
.price-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.price-card:hover { border-color: #2ea843; }
.price-card .label {
    font-size: 0.75rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'DM Mono', monospace;
}
.price-card .value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #3fb950;
    font-family: 'DM Mono', monospace;
    margin-top: 4px;
}
.price-card .sub {
    font-size: 0.8rem;
    color: #58a6ff;
    margin-top: 2px;
}

/* Selection item */
.sel-item {
    background: #161b22;
    border: 1px solid #21262d;
    border-left: 3px solid #2ea843;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.sel-item .cat-badge {
    display: inline-block;
    background: #1a4530;
    color: #3fb950;
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 4px;
}
.sel-item .prod-name {
    font-size: 0.85rem;
    color: #e6edf3;
    font-weight: 600;
}
.sel-item .prov-name {
    font-size: 0.75rem;
    color: #8b949e;
    margin-top: 2px;
    font-family: 'DM Mono', monospace;
}
.sel-item .price-tag {
    font-size: 1rem;
    font-weight: 700;
    color: #3fb950;
    font-family: 'DM Mono', monospace;
    white-space: nowrap;
}

/* Section headers */
.section-title {
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Total bar */
.total-bar {
    background: linear-gradient(90deg, #1a4530, #0d2818);
    border: 1px solid #2ea843;
    border-radius: 12px;
    padding: 20px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.total-bar .total-label {
    font-size: 0.8rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'DM Mono', monospace;
}
.total-bar .total-value {
    font-size: 2rem;
    font-weight: 800;
    color: #3fb950;
    font-family: 'DM Mono', monospace;
}

/* Table styling */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: #21262d; }

/* Buttons */
.stButton > button {
    background: #1a4530;
    border: 1px solid #2ea843;
    color: #3fb950;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    border-radius: 8px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #2ea843;
    color: #0d1117;
    border-color: #3fb950;
}

/* Select boxes */
.stSelectbox > div > div {
    background: #161b22 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}

/* Inputs */
.stTextInput > div > input {
    background: #161b22 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
}
.stNumberInput > div > input {
    background: #161b22 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}

/* Tags info */
.info-box {
    background: #0c2d6b20;
    border: 1px solid #1f6feb;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #79c0ff;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    raw = [
        ("Batería","BATERIA ULTRACELL 12V 7AH F1 UL7-12","ARTILEC",12828,"30-03-2026"),
        ("Batería","BATERIA ULTRACELL 12V 7AH F1 UL7-12","Casa Edison",15500,"30-03-2026"),
        ("Batería","BATERIA ULTRACELL 12V 7AH F1 UL7-12","SEFUTEC",16870,"30-03-2026"),
        ("Cámara","Cámara V2 para Raspberry Pi de 8mp","MCI electronics",29990,"30-03-2026"),
        ("Cámara","Cámara 3 para Raspberry Pi de 12mp","MCI electronics",48990,"30-03-2026"),
        ("Cámara IA","Cámara AI para Raspberry Pi de 12MP","MCI electronics",99990,"30-03-2026"),
        ("Cámara NOIR","Cámara NoIR para Raspberry Pi de 8mp","MCI electronics",28990,"30-03-2026"),
        ("Cámara NOIR","Cámara NoIR para Raspberry Pi de 8mp","Ripley",44990,"30-03-2026"),
        ("Cámara NOIR","Cámara 3 NoIR para Raspberry Pi de 12mp","Raspberry Pi OS",46990,"30-03-2026"),
        ("Cámara wide","Cámara 3 Wide para Raspberry Pi de 12mp","MCI electronics",61990,"30-03-2026"),
        ("Controlador","Regulador De Carga Solar Digital 12V/24V 10A","MCI electronics",6990,"07-04-2026"),
        ("Controlador","Regulador de Carga para Paneles Solares 10A 12/24V – Línea C","Enertik",13100,"07-04-2026"),
        ("Controlador","Controlador de carga 10A 12/24V PWM Epever EPD","Solarstore",22000,"07-04-2026"),
        ("Controlador","Controlador de carga 10A 12/24V PWM","Solarstore",33000,"07-04-2026"),
        ("Controlador","Controlador Solar MPPT 10A 12/24V Tracer1210A","Solartex",62200,"07-04-2026"),
        ("Kits","Kit Panel Solar 50W + Regulador De Carga Digital 12V 10A | FeelPower","FeelSECURE",69990,"07-04-2026"),
        ("Panel solar","Panel Solar 50W 12V Monocristalino Fotovoltaico","Fersontec",34990,"07-04-2026"),
        ("Panel solar","Panel Solar 50W 12V Mono Resun","Solarstore",35000,"07-04-2026"),
        ("Panel solar","Panel Solar 50W Monocristalino","Diacon",40000,"07-04-2026"),
        ("Raspberry Pi","Raspberry Pi 4 / 2GB RAM","MCI electronics",82990,"30-03-2026"),
        ("Raspberry Pi","Raspberry Pi 4 / 4GB RAM","MCI electronics",102990,"30-03-2026"),
        ("Raspberry Pi","Raspberry Pi 5 4GB RAM","Mechatronic STORE",107990,"30-03-2026"),
        ("Raspberry Pi","Raspberry Pi 5 8GB RAM","Mechatronic STORE",129990,"30-03-2026"),
        ("Raspberry Pi","Raspberry Pi 4 / 8GB RAM","MCI electronics",156990,"30-03-2026"),
        ("Raspberry Pi","Raspberry Pi 5 / 8GB RAM","MCI electronics",169990,"30-03-2026"),
        ("Raspberry Pi","Raspberry Pi 5 / 16GB RAM","MCI electronics",372990,"30-03-2026"),
        ("Router","Router celular industrial 4G LTE Wifi Dual SIM","Wiautomation",141176,"30-03-2026"),
        ("Router","Router celular industrial 4G LTE Wifi Dual SIM","Winpy",168320,"30-03-2026"),
        ("Router","Router celular industrial 4G LTE Wifi Dual SIM","MCI electronics",174990,"30-03-2026"),
        ("Sensor T","Sensor de Temperatura TMP36","MCI electronics",1990,"30-03-2026"),
        ("Sensor T","Sensor de Temperatura LM35DZ","MCI electronics",4290,"30-03-2026"),
        ("Sensor T","Sensor de Temperatura Pt100 400°C","MCI electronics",8990,"30-03-2026"),
        ("Sensor T","Sensor de temperatura DS18B20 resistente al agua","MCI electronics",19990,"30-03-2026"),
        ("Sensor TH","Sensor de Temperatura y Humedad AHT10","MCI electronics",3290,"30-03-2026"),
        ("Sensor TH","Sensor de Temperatura y Humedad DHT11","MCI electronics",3490,"30-03-2026"),
        ("Sensor TH","Sensor de Humedad y Temperatura DHT22","MCI electronics",6290,"30-03-2026"),
        ("Sensor TH","Sensor de Temperatura y Humedad LoRaWAN LHT65","MCI electronics",39900,"30-03-2026"),
        ("Sensor TH","Sensor de Temperatura y Humedad LoRaWAN – Milesight EM300-TH-915M","MCI electronics",59990,"30-03-2026"),
        ("Vidrio","Vidrio 8mm 500x500mm","Parque forestal",19170,"07-04-2026"),
        ("Vidrio","Vidrio 10mm 500x500mm","Parque forestal",22170,"07-04-2026"),
    ]
    return pd.DataFrame(raw, columns=["Categoría","Producto","Proveedor","Precio","Fecha consulta"])

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "cotizacion" not in st.session_state:
    st.session_state.cotizacion = []  # list of dicts

df = st.session_state.df

def fmt(price: int) -> str:
    return f"${price:,.0f}".replace(",", ".")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rizotron-header">
    <h1>🌱 Rizotron IoT</h1>
    <p>Cotizador de componentes · Selecciona productos y genera tu presupuesto</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

# ══════════════════════════════════════════════════════════════
# LEFT — Selector de productos
# ══════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="section-title">Agregar producto a cotización</div>', unsafe_allow_html=True)

    cats = sorted(df["Categoría"].unique().tolist())
    cat_sel = st.selectbox("Categoría", cats, key="cat_sel")

    cat_df = df[df["Categoría"] == cat_sel].copy()

    # Product options: "Nombre — Proveedor (Precio)"
    cat_df["_label"] = cat_df.apply(
        lambda r: f"{r['Producto']}  ·  {r['Proveedor']}  ({fmt(r['Precio'])})", axis=1
    )
    prod_label = st.selectbox("Producto / Proveedor", cat_df["_label"].tolist(), key="prod_sel")

    row = cat_df[cat_df["_label"] == prod_label].iloc[0]

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        qty = st.number_input("Cantidad", min_value=1, max_value=99, value=1, key="qty")
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
        # Cheapest in category
        cheapest = cat_df.loc[cat_df["Precio"].idxmin()]
        if st.button("💚 + Más barato", use_container_width=True, help=f"Agrega la opción más barata de {cat_sel}"):
            st.session_state.cotizacion.append({
                "Categoría": cheapest["Categoría"],
                "Producto": cheapest["Producto"],
                "Proveedor": cheapest["Proveedor"],
                "Precio unit.": int(cheapest["Precio"]),
                "Qty": 1,
                "Subtotal": int(cheapest["Precio"]),
            })

    # ── Bulk: add cheapest of ALL categories ──────────────────
    st.divider()
    st.markdown('<div class="section-title">Acciones rápidas</div>', unsafe_allow_html=True)

    col_x, col_y = st.columns(2)
    with col_x:
        if st.button("🚀 Agregar más barato por categoría", use_container_width=True):
            added = []
            for cat in cats:
                cheapest_row = df[df["Categoría"] == cat].loc[df[df["Categoría"] == cat]["Precio"].idxmin()]
                st.session_state.cotizacion.append({
                    "Categoría": cheapest_row["Categoría"],
                    "Producto": cheapest_row["Producto"],
                    "Proveedor": cheapest_row["Proveedor"],
                    "Precio unit.": int(cheapest_row["Precio"]),
                    "Qty": 1,
                    "Subtotal": int(cheapest_row["Precio"]),
                })
                added.append(cheapest_row["Categoría"])
            st.success(f"Agregadas {len(added)} categorías (opción más barata)")
    with col_y:
        if st.button("🗑️ Limpiar cotización", use_container_width=True):
            st.session_state.cotizacion = []
            st.rerun()

    # ── Tabla de referencia ───────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">Tabla de productos disponibles</div>', unsafe_allow_html=True)

    filter_cat = st.multiselect("Filtrar por categoría", cats, default=[], placeholder="Todas las categorías")
    display_df = df if not filter_cat else df[df["Categoría"].isin(filter_cat)]
    display_df = display_df[["Categoría","Producto","Proveedor","Precio","Fecha consulta"]].copy()
    display_df["Precio"] = display_df["Precio"].apply(fmt)
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=300)

    # ── Agregar producto personalizado ────────────────────────
    st.divider()
    st.markdown('<div class="section-title">Agregar producto personalizado</div>', unsafe_allow_html=True)
    with st.expander("➕ Nuevo producto / componente"):
        nc1, nc2 = st.columns(2)
        with nc1:
            new_cat = st.text_input("Categoría", placeholder="ej. Sensor CO2")
            new_prod = st.text_input("Nombre del producto", placeholder="ej. SCD41 CO2 Sensor")
        with nc2:
            new_prov = st.text_input("Proveedor", placeholder="ej. MCI electronics")
            new_price = st.number_input("Precio (CLP)", min_value=0, value=0, step=100)
        if st.button("Guardar en tabla", use_container_width=True):
            if new_cat and new_prod and new_prov and new_price > 0:
                new_row = pd.DataFrame([{
                    "Categoría": new_cat,
                    "Producto": new_prod,
                    "Proveedor": new_prov,
                    "Precio": new_price,
                    "Fecha consulta": pd.Timestamp.today().strftime("%d-%m-%Y"),
                }])
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                df = st.session_state.df
                st.success(f"'{new_prod}' agregado a la tabla.")
                st.rerun()
            else:
                st.warning("Completa todos los campos.")

# ══════════════════════════════════════════════════════════════
# RIGHT — Cotización actual
# ══════════════════════════════════════════════════════════════
with right:
    st.markdown('<div class="section-title">Cotización actual</div>', unsafe_allow_html=True)

    cot = st.session_state.cotizacion
    total = sum(i["Subtotal"] for i in cot)
    n_items = len(cot)

    # Summary metrics
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="price-card">
            <div class="label">Total cotización</div>
            <div class="value">{fmt(total)}</div>
            <div class="sub">{n_items} producto{'s' if n_items != 1 else ''} seleccionado{'s' if n_items != 1 else ''}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        n_cats = len(set(i["Categoría"] for i in cot))
        st.markdown(f"""
        <div class="price-card">
            <div class="label">Categorías</div>
            <div class="value">{n_cats}</div>
            <div class="sub">de {len(cats)} disponibles</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    if not cot:
        st.markdown('<div class="info-box">👆 Agrega productos desde el panel izquierdo para comenzar tu cotización.</div>', unsafe_allow_html=True)
    else:
        for idx, item in enumerate(cot):
            col_item, col_del = st.columns([10, 1])
            with col_item:
                qty_label = f" ×{item['Qty']}" if item["Qty"] > 1 else ""
                st.markdown(f"""
                <div class="sel-item">
                    <div>
                        <span class="cat-badge">{item['Categoría']}</span><br>
                        <span class="prod-name">{item['Producto']}{qty_label}</span><br>
                        <span class="prov-name">{item['Proveedor']}</span>
                    </div>
                    <div class="price-tag">{fmt(item['Subtotal'])}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"del_{idx}", help="Eliminar"):
                    st.session_state.cotizacion.pop(idx)
                    st.rerun()

        # Breakdown por categoría
        st.divider()
        st.markdown('<div class="section-title">Desglose por categoría</div>', unsafe_allow_html=True)
        cat_totals = {}
        for item in cot:
            cat_totals[item["Categoría"]] = cat_totals.get(item["Categoría"], 0) + item["Subtotal"]
        for cat_name, cat_total in sorted(cat_totals.items(), key=lambda x: -x[1]):
            pct = (cat_total / total * 100) if total else 0
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding: 6px 0; border-bottom: 1px solid #21262d;">
                <span style="color:#8b949e; font-size:0.82rem; font-family:'DM Mono',monospace;">{cat_name}</span>
                <span style="color:#3fb950; font-family:'DM Mono',monospace; font-size:0.9rem; font-weight:600;">
                    {fmt(cat_total)}
                    <span style="color:#8b949e; font-size:0.7rem;"> ({pct:.1f}%)</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Export como tabla
        st.divider()
        export_df = pd.DataFrame(cot)[["Categoría","Producto","Proveedor","Qty","Precio unit.","Subtotal"]]
        export_df["Precio unit."] = export_df["Precio unit."].apply(fmt)
        export_df["Subtotal"] = export_df["Subtotal"].apply(fmt)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar cotización CSV",
            data=csv,
            file_name="rizotron_cotizacion.csv",
            mime="text/csv",
            use_container_width=True,
        )
