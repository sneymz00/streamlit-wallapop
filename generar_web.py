import os
import json
import pandas as pd
from scraper import CSV_PATH

def generar():
    """Lee el CSV de productos y genera un index.html con un diseño profesional y sobrio."""
    if not os.path.exists(CSV_PATH):
        print(f"No se encontró {CSV_PATH}. No se generará la web.")
        return

    # Leer datos y rellenar nulos
    df = pd.read_csv(CSV_PATH)
    df = df.fillna("")
    
    # Asegurar que el precio numérico sea válido para el JSON
    if "precio_num" in df.columns:
        df["precio_num"] = pd.to_numeric(df["precio_num"], errors="coerce")
        # Cambiar NaN a None para que json.dumps lo convierta en null
        df["precio_num"] = df["precio_num"].where(pd.notnull(df["precio_num"]), None)

    productos = df.to_dict(orient="records")
    json_productos = json.dumps(productos, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mi catálogo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,400,0,0" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {{
    --primary: #2563eb; 
    --primary-hover: #1d4ed8;
    --bg: #f8fafc; 
    --surface: #ffffff; 
    --text-main: #0f172a; 
    --text-muted: #64748b;
    --border: #e2e8f0; 
    --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    --shadow-hover: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    --radius: 12px;
    --badge-bg: #f1f5f9;
  }}
  
  [data-theme="dark"] {{
    --primary: #3b82f6; 
    --primary-hover: #60a5fa;
    --bg: #0f172a; 
    --surface: #1e293b; 
    --text-main: #f8fafc; 
    --text-muted: #94a3b8;
    --border: #334155; 
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.3);
    --shadow-hover: 0 10px 15px -3px rgba(0,0,0,0.4);
    --badge-bg: #334155;
  }}

  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0; background: var(--bg); color: var(--text-main);
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif; 
    line-height: 1.5;
    transition: background 0.2s, color 0.2s;
  }}
  a {{ color: inherit; text-decoration: none; }}
  .material-symbols-outlined {{ vertical-align: middle; font-size: 18px; }}

  header {{
    position: sticky; top: 0; z-index: 20; 
    backdrop-filter: blur(8px);
    background: color-mix(in srgb, var(--surface) 85%, transparent);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 16px; padding: 14px 32px;
  }}
  .logo {{ 
    width: 32px; height: 32px; border-radius: 8px; background: var(--primary);
    display: flex; align-items: center; justify-content: center; color: white;
  }}
  .title-h {{ font-weight: 700; font-size: 1.1rem; }}
  .meta {{ margin-left: auto; color: var(--text-muted); font-size: 0.85rem; font-weight: 500;}}
  .theme-btn {{
    border: 1px solid var(--border); background: var(--surface); color: var(--text-main);
    width: 36px; height: 36px; border-radius: 8px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background 0.2s;
  }}
  .theme-btn:hover {{ background: var(--border); }}

  .hero {{ padding: 32px 32px 16px; }}
  .hero h1 {{ margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; color: var(--text-main); }}
  .hero p {{ margin: 8px 0 0; color: var(--text-muted); font-weight: 500; }}

  .controls {{ display: flex; flex-wrap: wrap; gap: 16px; align-items: center; padding: 16px 32px; }}
  .input-group {{ position: relative; display: flex; align-items: center; }}
  .input-group .material-symbols-outlined {{ position: absolute; left: 12px; color: var(--text-muted); pointer-events: none; }}
  
  .controls input[type=search], .controls select {{
    background: var(--surface); color: var(--text-main); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 16px; font-family: inherit; font-size: 0.9rem;
    box-shadow: var(--shadow-sm); transition: border-color 0.2s; outline: none;
  }}
  .controls input[type=search] {{ min-width: 280px; padding-left: 38px; }}
  .controls input:focus, .controls select:focus {{ border-color: var(--primary); }}
  
  .controls label {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 12px; }}
  .controls input[type=range] {{ accent-color: var(--primary); cursor: pointer; }}
  
  .seg {{ display: flex; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; box-shadow: var(--shadow-sm); }}
  .seg button {{ border: 0; background: transparent; color: var(--text-muted); padding: 8px 12px; cursor: pointer; display: flex; align-items: center; gap: 6px; font-weight: 500;}}
  .seg button:hover {{ background: var(--badge-bg); }}
  .seg button.on {{ background: var(--primary); color: #fff; }}

  .layout {{ display: grid; grid-template-columns: 1fr; gap: 32px; padding: 24px 32px 64px; }}
  @media(min-width: 1024px) {{ .layout {{ grid-template-columns: 300px 1fr; align-items: start; }} }}

  .panel {{ 
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 24px; box-shadow: var(--shadow-md); position: sticky; top: 96px; 
  }}
  .kpis {{ display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }}
  .kpi {{ display: flex; flex-direction: column; }}
  .kpi b {{ font-size: 1.8rem; font-weight: 800; line-height: 1.2; color: var(--text-main); }}
  .kpi span {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 500; }}
  .panel h3 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin: 0 0 16px; font-weight: 700; }}

  .grid {{ display: grid; gap: 24px; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }}
  .grid.lista {{ grid-template-columns: 1fr; }}
  
  .item {{ 
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    overflow: hidden; box-shadow: var(--shadow-sm); display: flex; flex-direction: column;
    transition: transform 0.2s ease, box-shadow 0.2s ease; 
  }}
  .item:hover {{ transform: translateY(-4px); box-shadow: var(--shadow-hover); }}
  .grid.lista .item {{ flex-direction: row; height: 160px; }}
  
  .thumb {{ position: relative; aspect-ratio: 1/1; background: var(--badge-bg); flex: none; border-bottom: 1px solid var(--border); }}
  .grid.lista .thumb {{ width: 160px; border-bottom: none; border-right: 1px solid var(--border); }}
  .thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  
  .badge {{ 
    position: absolute; top: 12px; left: 12px; 
    font-size: 0.7rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;
    letter-spacing: 0.02em; text-transform: uppercase;
  }}
  .badge.venta {{ background: var(--primary); color: white; }}
  .badge.vendido {{ background: #10b981; color: white; }}
  .badge.caducado {{ background: var(--text-muted); color: white; }}
  
  .grid.lista .thumb.agotado img, .thumb.agotado img {{ filter: grayscale(1) opacity(0.6); }}
  
  .item .body {{ padding: 20px; display: flex; flex-direction: column; gap: 8px; flex: 1; }}
  .item .titulo {{ font-size: 1rem; font-weight: 600; line-height: 1.4; color: var(--text-main); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
  .item .precio {{ font-size: 1.4rem; font-weight: 800; color: var(--text-main); margin-top: -4px; }}
  
  .item .stats {{ display: flex; flex-wrap: wrap; gap: 16px; color: var(--text-muted); font-size: 0.8rem; font-weight: 500; margin-top: 4px; }}
  .item .stats span {{ display: inline-flex; align-items: center; gap: 4px; }}
  .item .stats .material-symbols-outlined {{ font-size: 16px; }}
  
  .item .footer-card {{ margin-top: auto; display: flex; align-items: center; justify-content: space-between; padding-top: 12px; border-top: 1px solid var(--border); }}
  .item .fecha {{ color: var(--text-muted); font-size: 0.75rem; font-weight: 500; display: flex; align-items: center; gap: 4px;}}
  .item .cta {{ 
    font-weight: 600; font-size: 0.85rem; color: var(--primary);
    display: flex; align-items: center; gap: 4px; transition: color 0.2s;
  }}
  .item .cta:hover {{ color: var(--primary-hover); }}
  
  .vacio {{ color: var(--text-muted); padding: 64px; text-align: center; grid-column: 1/-1; font-weight: 500; }}

  footer {{ padding: 32px; color: var(--text-muted); font-size: 0.85rem; text-align: center; border-top: 1px solid var(--border); font-weight: 500; }}
</style>
</head>
<body>

<header>
  <div class="logo"><span class="material-symbols-outlined">inventory_2</span></div>
  <div class="title-h">Mi catálogo</div>
  <div class="meta" id="meta"></div>
  <button class="theme-btn" id="tema" title="Cambiar tema">
    <span class="material-symbols-outlined" id="icono-tema">dark_mode</span>
  </button>
</header>

<section class="hero">
  <h1>Resumen de productos</h1>
  <p id="resumen"></p>
</section>

<div class="controls">
  <div class="input-group">
    <span class="material-symbols-outlined">search</span>
    <input id="buscar" type="search" placeholder="Buscar por título...">
  </div>
  <select id="estado">
    <option value="todos">Estado: Todos</option>
    <option value="venta">Solo en venta</option>
    <option value="vendido">Solo vendidos</option>
    <option value="caducado">Solo caducados</option>
  </select>
  <select id="orden">
    <option value="rel">Ordenar por: Original</option>
    <option value="precio_asc">Precio: Menor a mayor</option>
    <option value="precio_desc">Precio: Mayor a menor</option>
    <option value="titulo">Título A-Z</option>
    <option value="vistas">Más visitas</option>
    <option value="favoritos">Más favoritos</option>
    <option value="chats">Más chats</option>
  </select>
  <label>Precio máx: <b id="precioMaxLbl"></b> €
    <input id="precioMax" type="range" min="0" max="100" value="100">
  </label>
  <div class="seg" id="vista" style="margin-left: auto;">
    <button data-v="grid" class="on" title="Cuadrícula"><span class="material-symbols-outlined">grid_view</span></button>
    <button data-v="lista" title="Lista"><span class="material-symbols-outlined">view_list</span></button>
  </div>
</div>

<div class="layout">
  <aside class="panel">
    <div class="kpis">
      <div class="kpi"><b id="kpiTotal">0</b><span>Productos mostrados</span></div>
      <div class="kpi"><b id="kpiVendidos">0</b><span>Vendidos</span></div>
      <div class="kpi"><b id="kpiVistas">0</b><span>Visitas totales</span></div>
      <div class="kpi"><b id="kpiMedia">0 €</b><span>Precio medio</span></div>
    </div>
    <hr style="border: 0; border-top: 1px solid var(--border); margin: 24px 0;">
    <h3>Distribución de precios</h3>
    <canvas id="grafico" height="220"></canvas>
  </aside>
  
  <main>
    <div class="grid" id="grid"></div>
  </main>
</div>

<footer>Catálogo interactivo · Generado automáticamente</footer>

<script>
// Aquí inyectamos el JSON generado desde Python
const PRODUCTOS = {json_productos};

let chart;

function esc(s){{
  return String(s==null?'':s)
    .replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')
    .replaceAll('"','&quot;').replaceAll("'",'&#39;');
}}

function urlSegura(u){{
  u = String(u==null?'':u).trim();
  return /^https?:\\/\\//i.test(u) ? u : '';
}}

function fmt(n){{ return (n==null?0:n).toLocaleString('es-ES'); }}
function precios(){{ return PRODUCTOS.map(p=>p.precio_num).filter(v=>v!=null); }}

function aplicarTema(tema){{
  document.documentElement.setAttribute('data-theme', tema);
  document.getElementById('icono-tema').textContent = tema === 'dark' ? 'light_mode' : 'dark_mode';
}}

function init(){{
  let temaGuardado = null;
  try {{ temaGuardado = localStorage.getItem('tema'); }} catch(e){{}}
  if(!temaGuardado){{
    temaGuardado = window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }}
  aplicarTema(temaGuardado);

  const ps = precios();
  const max = ps.length ? Math.ceil(Math.max(...ps)) : 100;
  const slider = document.getElementById('precioMax');
  slider.max = max; slider.value = max;
  document.getElementById('precioMaxLbl').textContent = fmt(max);
  document.getElementById('meta').textContent = 'Actualizado: ' + new Date().toLocaleDateString('es-ES');

  ['buscar','estado','orden','precioMax'].forEach(id =>
    document.getElementById(id).addEventListener('input', render));

  document.getElementById('vista').addEventListener('click', e=>{{
    const b = e.target.closest('button'); if(!b) return;
    document.querySelectorAll('#vista button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    document.getElementById('grid').classList.toggle('lista', b.dataset.v==='lista');
  }});

  document.getElementById('tema').addEventListener('click', ()=>{{
    const dark = document.documentElement.getAttribute('data-theme')==='dark';
    const nuevo = dark ? 'light' : 'dark';
    aplicarTema(nuevo);
    try {{ localStorage.setItem('tema', nuevo); }} catch(e){{}}
    render();
  }});

  render();
}}

function claseEstado(p){{
  if(p.vendido || /vendido/i.test(p.estado||'')) return 'vendido';
  if(/caducad/i.test(p.estado||'')) return 'caducado';
  return 'venta';
}}
const ETIQUETA = {{ vendido:'Vendido', caducado:'Caducado', venta:'En venta' }};

function filtrar(){{
  const q = document.getElementById('buscar').value.trim().toLowerCase();
  const est = document.getElementById('estado').value;
  const pmax = parseFloat(document.getElementById('precioMax').value);
  document.getElementById('precioMaxLbl').textContent = fmt(pmax);
  let arr = PRODUCTOS.filter(p =>
    String(p.titulo||'').toLowerCase().includes(q) &&
    (p.precio_num==null || p.precio_num<=pmax) &&
    (est==='todos' || claseEstado(p)===est));
  const orden = document.getElementById('orden').value;
  const num = (v)=> v==null || v==='' ? -1 : parseFloat(v);
  if(orden==='precio_asc') arr.sort((a,b)=>(a.precio_num??1e15)-(b.precio_num??1e15));
  if(orden==='precio_desc') arr.sort((a,b)=>(b.precio_num??-1)-(a.precio_num??-1));
  if(orden==='titulo') arr.sort((a,b)=>String(a.titulo||'').localeCompare(String(b.titulo||'')));
  if(orden==='vistas') arr.sort((a,b)=>num(b.visualizaciones)-num(a.visualizaciones));
  if(orden==='favoritos') arr.sort((a,b)=>num(b.favoritos)-num(a.favoritos));
  if(orden==='chats') arr.sort((a,b)=>num(b.chats)-num(a.chats));
  return arr;
}}

function render(){{
  const arr = filtrar();
  const grid = document.getElementById('grid');
  grid.innerHTML = arr.map(p => {{
    const img = urlSegura(p.imagen);
    const enlace = urlSegura(p.enlace);
    const cls = claseEstado(p);
    const agotado = (cls==='vendido' || cls==='caducado') ? ' agotado' : '';
    
    const stat = (icon, v, title)=> (v==null || v==='') ? '' : `<span title="${{title}}"><span class="material-symbols-outlined">${{icon}}</span> ${{fmt(v)}}</span>`;
    const stats = [
      stat('visibility', p.visualizaciones, 'Visitas'),
      stat('favorite', p.favoritos, 'Favoritos'),
      stat('chat_bubble', p.chats, 'Chats'),
    ].join('');
    
    return `
    <article class="item">
      <div class="thumb${{agotado}}">
        ${{img ? `<img loading="lazy" src="${{esc(img)}}" alt="${{esc(p.titulo)}}" onerror="this.style.opacity=.15">` : ''}}
        <span class="badge ${{cls}}">${{esc(ETIQUETA[cls])}}</span>
      </div>
      <div class="body">
        <div class="titulo">${{esc(p.titulo)}}</div>
        <div class="precio">${{esc(p.precio)}}</div>
        ${{stats ? `<div class="stats">${{stats}}</div>` : ''}}
        
        <div class="footer-card">
            ${{p.fecha_publicacion ? `<div class="fecha"><span class="material-symbols-outlined" style="font-size:14px;">calendar_today</span> ${{esc(p.fecha_publicacion)}}</div>` : '<div></div>'}}
            ${{enlace ? `<a class="cta" href="${{esc(enlace)}}" target="_blank" rel="noopener noreferrer">Abrir <span class="material-symbols-outlined" style="font-size:16px;">open_in_new</span></a>` : ''}}
        </div>
      </div>
    </article>`;
  }}).join('') || '<p class="vacio">No hay productos que coincidan con el filtro.</p>';

  const ps = arr.map(p=>p.precio_num).filter(v=>v!=null);
  const media = ps.length ? ps.reduce((a,b)=>a+b,0)/ps.length : 0;
  const vendidos = arr.filter(p=>claseEstado(p)==='vendido').length;
  const vistas = arr.reduce((a,p)=>a+(parseInt(p.visualizaciones)||0),0);
  
  document.getElementById('kpiTotal').textContent = arr.length;
  document.getElementById('kpiVendidos').textContent = vendidos;
  document.getElementById('kpiVistas').textContent = fmt(vistas);
  document.getElementById('kpiMedia').textContent = fmt(Math.round(media)) + ' €';
  
  document.getElementById('resumen').textContent =
    arr.length + ' productos mostrados de ' + PRODUCTOS.length + ' en total';
  dibujarGrafico(ps);
}}

function dibujarGrafico(ps){{
  const ctx = document.getElementById('grafico');
  const css = getComputedStyle(document.documentElement);
  const muted = css.getPropertyValue('--text-muted').trim() || '#64748b';
  const border = css.getPropertyValue('--border').trim() || '#e2e8f0';
  const primary = css.getPropertyValue('--primary').trim() || '#2563eb';
  
  const bins = 6;
  const max = ps.length ? Math.max(...ps) : 0;
  const ancho = max>0 ? max/bins : 1;
  const labels=[], data=new Array(bins).fill(0);
  for(let i=0;i<bins;i++) labels.push(Math.round(i*ancho)+'-'+Math.round((i+1)*ancho)+'€');
  ps.forEach(v=>{{ let idx=Math.min(bins-1,Math.floor(v/ancho)); data[idx]++; }});
  
  if(chart) chart.destroy();
  
  chart = new Chart(ctx, {{
    type:'bar',
    data:{{ labels, datasets:[{{ label:'Productos', data, backgroundColor: primary, borderRadius: 4 }}] }},
    options:{{
      animation:{{ duration: 0 }},
      plugins:{{ legend:{{ display:false }} }},
      scales:{{
        x:{{ ticks:{{ color:muted, font:{{ size:11 }} }}, grid:{{ display:false }} }},
        y:{{ ticks:{{ color:muted, precision:0 }}, beginAtZero:true, grid:{{ color: border }} }}
      }}
    }}
  }});
}}

init();
</script>
</body>
</html>
"""
    
    # Escribir el archivo
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Archivo index.html generado con éxito.")

if __name__ == "__main__":
    generar()