"""
Panel de Wallapop (Streamlit) — se ejecuta en TU ordenador (Windows).

Arráncalo con doble clic en INICIAR.bat (o: streamlit run script.py).

Flujo:
1. "Sincronizar Datos" abre Chrome con tu sesión, extrae tus productos
   (con imágenes) y genera index.html, la web autónoma que puedes subir
   a cualquier hosting.
2. Aquí mismo puedes filtrar, ordenar, ver imágenes y un gráfico de precios,
   descargar index.html / CSV y publicar en GitHub Pages.

NOTA: necesita tu navegador con tu login, por lo que funciona en local,
NO en Streamlit Community Cloud.
"""

import os
import subprocess
import datetime as dt
import pandas as pd
import altair as alt
import streamlit as st
import html as _html

from scraper import extraer_productos, CSV_PATH
import generar_web

# Paleta Profesional
ACCENT = "#2563eb"  # Azul profesional
COLOR_ESTADO = {"vendido": "#10b981", "venta": "#2563eb", "caducado": "#64748b"}
ETIQUETA_ESTADO = {"vendido": "Vendido", "venta": "En venta", "caducado": "Caducado"}
_MESES_ES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


def _parse_fecha_es(texto):
    """'19 jun 2026' -> Timestamp. Devuelve NaT si no se reconoce."""
    if not isinstance(texto, str) or not texto.strip():
        return pd.NaT
    partes = texto.lower().replace(".", "").split()
    try:
        dia = int(partes[0])
        mes = _MESES_ES.get(partes[1][:3])
        anio = int(partes[2])
        if mes:
            return pd.Timestamp(year=anio, month=mes, day=dia)
    except (ValueError, IndexError):
        pass
    return pd.NaT


def _estilo(chart):
    """Estilo común y responsive para las gráficas de Altair."""
    return (
        chart.configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#64748b",
            titleColor="#64748b",
            domainColor="#e2e8f0",
            gridColor="#f1f5f9",
            labelFontSize=11,
            titleFontSize=12,
            labelLimit=220,
        )
        .configure_legend(orient="bottom", titleColor="#64748b", labelColor="#64748b")
    )


def _grafico_interes(df: pd.DataFrame):
    """Ranking de productos por interés (visitas), con favoritos y chats en tooltip."""
    d = df.copy()
    d["visualizaciones"] = d["visualizaciones"].fillna(0)
    d["favoritos"] = d["favoritos"].fillna(0)
    d["chats"] = d["chats"].fillna(0)
    d["Estado"] = d["_estado"].map(ETIQUETA_ESTADO)
    chart = (
        alt.Chart(d)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X("visualizaciones:Q", title="Visitas", axis=alt.Axis(grid=False, format="d", tickMinStep=1)),
            y=alt.Y("titulo:N", title=None, sort="-x", axis=alt.Axis(labelLimit=180)),
            color=alt.Color(
                "_estado:N",
                scale=alt.Scale(
                    domain=list(COLOR_ESTADO), range=list(COLOR_ESTADO.values())
                ),
                legend=alt.Legend(title="Estado", labelExpr=(
                    "datum.label == 'vendido' ? 'Vendido' : "
                    "datum.label == 'venta' ? 'En venta' : 'Caducado'"
                )),
            ),
            tooltip=[
                alt.Tooltip("titulo:N", title="Producto"),
                alt.Tooltip("visualizaciones:Q", title="Visitas"),
                alt.Tooltip("favoritos:Q", title="Favoritos"),
                alt.Tooltip("chats:Q", title="Chats"),
                alt.Tooltip("Estado:N"),
            ],
        )
        .properties(height=max(200, 64 * len(d)))
    )
    return _estilo(chart)


def _grafico_ganancias(realizado: float, activo: float, caducado: float):
    """Comparativa: ya ingresado (vendido) vs pendiente (en venta) vs caducado."""
    d = pd.DataFrame(
        {
            "Categoría": ["Ya ingresado", "En venta", "Caducado"],
            "clave": ["vendido", "venta", "caducado"],
            "Euros": [realizado, activo, caducado],
        }
    )
    orden = list(d["Categoría"])
    base = alt.Chart(d).encode(
        y=alt.Y("Categoría:N", title=None, sort=orden, axis=alt.Axis(labelLimit=200)),
        x=alt.X("Euros:Q", title="Euros (€)", axis=alt.Axis(grid=True, format="d")),
    )
    barras = base.mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
        color=alt.Color(
            "clave:N",
            scale=alt.Scale(
                domain=list(COLOR_ESTADO), range=list(COLOR_ESTADO.values())
            ),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("Categoría:N"),
            alt.Tooltip("Euros:Q", title="€", format=".2f"),
        ],
    )
    texto = base.mark_text(align="left", dx=5, color="#0f172a", fontWeight="bold").encode(
        text=alt.Text("Euros:Q", format=".0f")
    )
    return _estilo((barras + texto).properties(height=180))


def _grafico_temporal(df: pd.DataFrame):
    """Productos situados en el tiempo por su fecha; los vendidos en verde."""
    d = df.copy()
    d["fecha_dt"] = d["fecha_publicacion"].apply(_parse_fecha_es)
    d = d[d["fecha_dt"].notna() & d["precio_num"].notna()].sort_values("fecha_dt")
    if d.empty:
        return None
    d["acumulado"] = d["precio_num"].cumsum()
    d["Estado"] = d["_estado"].map(ETIQUETA_ESTADO)

    base = alt.Chart(d)
    eje_x = alt.X(
        "fecha_dt:T",
        title="Fecha",
        axis=alt.Axis(tickCount=5, labelAngle=0, format="%b %Y"),
    )
    linea = base.mark_line(color=ACCENT, strokeWidth=2, point=False).encode(
        x=eje_x,
        y=alt.Y("acumulado:Q", title="Valor acumulado (€)", axis=alt.Axis(format="d")),
    )
    puntos = base.mark_point(size=110, filled=True, opacity=0.9).encode(
        x=eje_x,
        y="acumulado:Q",
        color=alt.Color(
            "_estado:N",
            scale=alt.Scale(domain=list(COLOR_ESTADO), range=list(COLOR_ESTADO.values())),
            legend=alt.Legend(title="Estado", labelExpr=(
                "datum.label == 'vendido' ? 'Vendido' : "
                "datum.label == 'venta' ? 'En venta' : 'Caducado'"
            )),
        ),
        tooltip=[
            alt.Tooltip("titulo:N", title="Producto"),
            alt.Tooltip("fecha_dt:T", title="Fecha", format="%d/%m/%Y"),
            alt.Tooltip("precio:N", title="Precio"),
            alt.Tooltip("Estado:N"),
        ],
    )
    return _estilo((linea + puntos).properties(height=300))


st.set_page_config(
    page_title="Mi catálogo",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="auto",
)

# --- Estilo (Limpio y Profesional) ---
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
      
      html, body, [class*="css"]  { font-family:'Plus Jakarta Sans',sans-serif; }
      .stApp { background: #f8fafc; }
      
      .hero {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px; 
        padding: 24px 30px; 
        margin-bottom: 24px;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
      }
      .hero h1 { margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em; color: #0f172a; }
      .hero p { margin: 6px 0 0; color: #64748b; font-weight: 500; }
      
      div[data-testid="stMetric"] {
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 12px;
        padding: 16px; 
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
      }
      div[data-testid="stMetricValue"] { font-weight: 800; color: #0f172a !important; }
      div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        color: #64748b !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.75rem !important;
      }
      
      .stButton>button {
        background: #2563eb; color: #fff; border: 0; border-radius: 8px;
        font-weight: 600; padding: 0.5rem 1rem; transition: background 0.2s;
      }
      .stButton>button:hover { background: #1d4ed8; color: #fff;}
      
      .prod-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05); margin-bottom: 16px; position: relative;
        transition: transform 0.2s, box-shadow 0.2s;
      }
      .prod-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
      .prod-card .pad { padding: 16px; display: flex; flex-direction: column; gap: 8px; }
      .prod-card .titulo { font-weight: 600; line-height: 1.4; color: #0f172a; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.8em;}
      .prod-card .precio { font-weight: 800; color: #0f172a; font-size: 1.3rem; }
      .prod-card .stats { color: #64748b; font-size: 0.8rem; font-weight: 500; display: flex; gap: 12px; flex-wrap: wrap; }
      
      .prod-card .footer-card { margin-top: 8px; display: flex; align-items: center; justify-content: space-between; padding-top: 12px; border-top: 1px solid #e2e8f0; }
      .prod-card .fecha { color: #64748b; font-size: 0.75rem; font-weight: 500;}
      
      .badge {
        position: absolute; top: 12px; left: 12px; z-index: 2; font-size: 0.65rem; font-weight: 700;
        padding: 4px 10px; border-radius: 6px; letter-spacing: 0.02em; text-transform: uppercase;
      }
      .badge.vendido { background: #10b981; color: #fff; }
      .badge.caducado { background: #64748b; color: #fff; }
      .badge.venta { background: #2563eb; color: #fff; }
      .prod-card.agotado img { filter: grayscale(1) opacity(0.6); }
      
      [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
        opacity: 1 !important; visibility: visible !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>Panel de Control</h1>'
    "<p>Extrae tus productos, analiza el rendimiento y publica tu catálogo.</p></div>",
    unsafe_allow_html=True,
)

# --- Barra lateral ---
st.sidebar.header("Sincronización")
usar_chrome_abierto = st.sidebar.checkbox(
    "Usar Chrome en modo debug (puerto 9222)", value=True
)
st.sidebar.caption(
    "Abre la ventana con doble clic en `abrir_chrome_debug.bat` e inicia "
    "sesión. El panel reutilizará tu sesión activa."
)
primera_vez = st.sidebar.checkbox(
    "Forzar espera de inicio de sesión", value=False
)
publicar_auto = st.sidebar.checkbox(
    "Publicar en GitHub tras sincronizar", value=True
)
auto = st.sidebar.toggle("Refresco automático UI", value=False)
intervalo_min = st.sidebar.number_input(
    "Frecuencia (minutos)", min_value=1, max_value=180, value=15, step=1
)
if auto:
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=int(intervalo_min) * 60 * 1000, key="auto_refresh")
    except ImportError:
        st.sidebar.warning("Instala 'streamlit-autorefresh' para esta función.")
    st.sidebar.caption("Actualiza los datos locales. Para escanear la web, pulsa el botón.")


def cargar_csv() -> pd.DataFrame:
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()


def actualizar():
    puerto = 9222 if usar_chrome_abierto else None
    espera = 0 if usar_chrome_abierto else (90 if primera_vez else 0)
    with st.spinner("Sincronizando inventario..."):
        try:
            df_nuevo = extraer_productos(
                esperar_login_segundos=espera, adjuntar_puerto=puerto
            )
        except RuntimeError as e:
            st.error(str(e))
            return
        generar_web.generar()
    st.session_state["ultima"] = dt.datetime.now()
    if df_nuevo.empty:
        st.warning(
            "No se encontró ningún producto. Verifica tu sesión."
        )
        return
    # Tras refrescar la base de datos, subir automáticamente a GitHub.
    # (publicar() no sube nada si no hay cambios reales, así que es seguro.)
    if publicar_auto:
        publicar()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _git(args):
    """Ejecuta un comando git en la carpeta del proyecto y devuelve el resultado."""
    return subprocess.run(
        ["git"] + args, cwd=BASE_DIR, capture_output=True, text=True
    )


def publicar():
    """Regenera la web y la sube a GitHub Pages (git add + commit + push)."""
    with st.spinner("Publicando en GitHub Pages..."):
        generar_web.generar()  # asegura que index.html está al día
        if not os.path.exists(os.path.join(BASE_DIR, "index.html")):
            st.error("Aún no hay index.html. Pulsa 'Sincronizar Datos' primero.")
            return
        if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
            st.error(
                "Esta carpeta no está conectada a GitHub todavía. Configúrala "
                "una vez (ver README, apartado 'Publicar') y vuelve a intentarlo."
            )
            return
        # Identidad de git (solo si no está configurada, para poder commitear).
        if not _git(["config", "user.email"]).stdout.strip():
            _git(["config", "user.email", "wallapop@local"])
            _git(["config", "user.name", "Panel Wallapop"])

        _git(["add", "index.html"])
        if os.path.exists(os.path.join(BASE_DIR, "productos.json")):
            _git(["add", "productos.json"])

        # ¿Hay algo que subir?
        if _git(["diff", "--cached", "--quiet"]).returncode == 0:
            st.info("No hay cambios nuevos que publicar.")
            return

        _git(["commit", "-m", f"Actualiza catálogo ({dt.datetime.now():%d/%m/%Y %H:%M})"])
        push = _git(["push"])
        if push.returncode == 0:
            st.success(
                "✅ Catálogo publicado. En 1-2 minutos estará actualizado en tu web."
            )
        else:
            st.error(
                "No se pudo subir a GitHub:\n\n"
                + (push.stderr or push.stdout or "Error desconocido")
                + "\n\nSi es la primera vez, es posible que Git te pida iniciar "
                "sesión en una ventana emergente."
            )


if st.button("Sincronizar Datos", type="primary"):
    actualizar()

df = cargar_csv()

ultima = st.session_state.get("ultima")
if ultima:
    st.caption(f"Última actualización: {ultima:%d/%m/%Y %H:%M:%S}")

if df.empty:
    st.info(
        "Base de datos vacía. Pulsa **Sincronizar Datos** para comenzar."
    )
    st.stop()

# --- Preparación de datos ---
vista = df.copy()
for col, defecto in (
    ("precio_num", None), ("vendido", False), ("estado", ""),
    ("visualizaciones", None), ("favoritos", None), ("chats", None),
    ("fecha_publicacion", ""),
):
    if col not in vista.columns:
        vista[col] = defecto


def _clase_estado(row) -> str:
    if bool(row.get("vendido")) or "vendido" in str(row.get("estado", "")).lower():
        return "vendido"
    if "caduc" in str(row.get("estado", "")).lower():
        return "caducado"
    return "venta"


vista["_estado"] = vista.apply(_clase_estado, axis=1)

# --- Filtros ---
st.sidebar.divider()
st.sidebar.header("Filtros")
busqueda = st.sidebar.text_input("Buscar artículo")
estado_sel = st.sidebar.selectbox(
    "Estado", ["Todos", "En venta", "Vendidos", "Caducados"]
)
orden = st.sidebar.selectbox(
    "Ordenar por",
    ["Relevancia", "Precio ↑", "Precio ↓", "Título A-Z",
     "Visualizaciones", "Favoritos", "Interacciones (Chats)"],
)

mapa_estado = {"En venta": "venta", "Vendidos": "vendido", "Caducados": "caducado"}
if estado_sel in mapa_estado:
    vista = vista[vista["_estado"] == mapa_estado[estado_sel]]

if vista["precio_num"].notna().any():
    pmin = float(vista["precio_num"].min())
    pmax = float(vista["precio_num"].max())
    if pmax > pmin:
        rango = st.sidebar.slider("Rango de precio (€)", pmin, pmax, (pmin, pmax))
        vista = vista[
            vista["precio_num"].isna()
            | vista["precio_num"].between(rango[0], rango[1])
        ]

if busqueda:
    vista = vista[vista["titulo"].str.contains(busqueda, case=False, na=False)]

if orden == "Precio ↑":
    vista = vista.sort_values("precio_num", na_position="last")
elif orden == "Precio ↓":
    vista = vista.sort_values("precio_num", ascending=False, na_position="last")
elif orden == "Título A-Z":
    vista = vista.sort_values("titulo")
elif orden == "Visualizaciones":
    vista = vista.sort_values("visualizaciones", ascending=False, na_position="last")
elif orden == "Favoritos":
    vista = vista.sort_values("favoritos", ascending=False, na_position="last")
elif orden == "Interacciones (Chats)":
    vista = vista.sort_values("chats", ascending=False, na_position="last")

# --- KPIs ---
realizado = float(vista.loc[vista["_estado"] == "vendido", "precio_num"].fillna(0).sum())
activo = float(vista.loc[vista["_estado"] == "venta", "precio_num"].fillna(0).sum())
caducado = float(vista.loc[vista["_estado"] == "caducado", "precio_num"].fillna(0).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mostrados", len(vista))
c2.metric("Vendidos", int((vista["_estado"] == "vendido").sum()))
c3.metric("Ingresos", f"{realizado:,.0f} €".replace(",", "."))
c4.metric(
    "Valor Activo",
    f"{activo:,.0f} €".replace(",", "."),
    help="Suma total de los artículos actualmente listados para la venta.",
)
st.write("")

# --- Gráficas ---
tab_int, tab_gan, tab_tmp = st.tabs(
    ["Métricas de Interés", "Distribución Financiera", "Evolución Temporal"]
)

with tab_int:
    if vista["visualizaciones"].fillna(0).sum() > 0 or len(vista):
        st.altair_chart(_grafico_interes(vista), width="stretch")
    else:
        st.info("No hay datos suficientes para generar esta gráfica.")

with tab_gan:
    st.altair_chart(_grafico_ganancias(realizado, activo, caducado), width="stretch")
    total = realizado + activo + caducado
    st.caption(
        f"**Ingresos totales:** {realizado:,.0f} € &nbsp;|&nbsp; **Proyección activa:** {activo:,.0f} € &nbsp;|&nbsp; "
        f"**Capital en artículos caducados:** {caducado:,.0f} € &nbsp;→&nbsp; "
        f"**Valor total del inventario:** {total:,.0f} €".replace(",", ".")
    )

with tab_tmp:
    chart_tmp = _grafico_temporal(vista)
    if chart_tmp is None:
        st.info("No existen registros temporales válidos en el conjunto de datos.")
    else:
        st.altair_chart(chart_tmp, width="stretch")

# --- Grid de imágenes ---
st.divider()
st.subheader("Inventario")

def _num(row, col):
    v = row.get(col)
    return None if v is None or (isinstance(v, float) and pd.isna(v)) else int(v)

cols = st.columns(4)
for i, (_, row) in enumerate(vista.iterrows()):
    with cols[i % 4]:
        img = row.get("imagen") if isinstance(row.get("imagen"), str) else ""
        titulo = _html.escape(str(row.get("titulo", "")))
        precio = _html.escape(str(row.get("precio", "")))
        enlace = row.get("enlace") if isinstance(row.get("enlace"), str) else ""
        clase = row.get("_estado", "venta")
        agotado = " agotado" if clase in ("vendido", "caducado") else ""
        fecha = _html.escape(str(row.get("fecha_publicacion") or ""))

        img_html = (
            f'<img src="{img}" style="width:100%;aspect-ratio:1/1;object-fit:cover;display:block;border-bottom:1px solid #e2e8f0;">'
            if img else
            '<div style="width:100%;aspect-ratio:1/1;background:#f1f5f9;border-bottom:1px solid #e2e8f0;"></div>'
        )
        partes = []
        for ico, col in (("👁", "visualizaciones"), ("❤️", "favoritos"), ("💬", "chats")):
            v = _num(row, col)
            if v is not None:
                partes.append(f"<span>{ico} {v}</span>")
        stats_html = f'<div class="stats">{"".join(partes)}</div>' if partes else ""
        
        fecha_html = f'<div class="fecha">{fecha}</div>' if fecha else "<div></div>"
        cta = (
            f'<a href="{enlace}" target="_blank" style="color:#2563eb;text-decoration:none;'
            f'font-weight:600;font-size:0.85rem;">Abrir ↗</a>'
            if enlace else ""
        )
        
        st.markdown(
            f'<div class="prod-card{agotado}">'
            f'<span class="badge {clase}">{ETIQUETA_ESTADO.get(clase, "")}</span>'
            f'{img_html}'
            f'<div class="pad">'
            f'<div class="titulo">{titulo}</div>'
            f'<div class="precio">{precio}</div>{stats_html}'
            f'<div class="footer-card">{fecha_html}{cta}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# --- Descargas ---
st.sidebar.divider()
st.sidebar.header("Exportación")
st.sidebar.download_button(
    "Descargar datos (CSV)",
    vista.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
    "inventario.csv",
    "text/csv",
)
html_path = os.path.join(os.path.dirname(__file__), "index.html")
if os.path.exists(html_path):
    with open(html_path, "rb") as f:
        st.sidebar.download_button(
            "Descargar Catálogo (HTML)", f.read(), "index.html", "text/html"
        )

st.sidebar.divider()
st.sidebar.header("Publicar")
st.sidebar.caption("Sube tu catálogo a la web (GitHub Pages).")
if st.sidebar.button("Publicar en GitHub Pages"):
    publicar()