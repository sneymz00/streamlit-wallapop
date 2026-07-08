"""
Scraper de Wallapop: extrae los productos del usuario y los guarda en productos.json
(además de CSV). Incluye imagen y campos extra cuando están disponibles.

Usa un perfil de Chrome PERSISTENTE (carpeta ./chrome-profile), de modo que
solo tengas que iniciar sesión la primera vez; en las siguientes ejecuciones
la sesión se reutiliza y no hace falta volver a loguearse.
"""

import os

# macOS + Python de python.org no traen los certificados del sistema, lo que
# rompe las descargas HTTPS (p.ej. la de ChromeDriver). Forzamos los de certifi.
try:
    import certifi

    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

import re
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "chrome-profile")
CSV_PATH = os.path.join(BASE_DIR, "mis_productos_wallapop.csv")
JSON_PATH = os.path.join(BASE_DIR, "productos.json")
URL_PRODUCTOS = "https://es.wallapop.com/app/catalog/published"
URL_STATS = "https://es.wallapop.com/app/stats"


def _limpiar_locks(profile_dir: str):
    """Elimina locks sobrantes de un Chrome que crasheó (causan 'instance exited')."""
    for nombre in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        ruta = os.path.join(profile_dir, nombre)
        try:
            if os.path.islink(ruta) or os.path.exists(ruta):
                os.remove(ruta)
        except OSError:
            pass


def _construir_options(profile_dir: str, headless: bool) -> Options:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(f"--user-data-dir={profile_dir}")
    if headless:
        options.add_argument("--headless=new")
    return options


def _intentar_arranque(options: Options) -> webdriver.Chrome:
    # 1) Selenium Manager (Selenium 4.6+): descarga el driver con su propia
    #    gestión TLS, sin depender de los certificados de Python.
    try:
        return webdriver.Chrome(options=options)
    except Exception:
        # 2) Respaldo: webdriver-manager (sin verificación SSL, que falla en
        #    este Python de macOS).
        os.environ.setdefault("WDM_SSL_VERIFY", "0")
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )


def _puerto_abierto(host: str, port: int, timeout: float = 1.0) -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _navegador_adjunto(port: int) -> webdriver.Chrome:
    """Se conecta a un Chrome YA ABIERTO en modo depuración remota (puerto dado),
    usando tu sesión actual. No lanza un Chrome nuevo ni toca tu perfil."""
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return _intentar_arranque(options)


def _configurar_navegador(headless: bool = False) -> webdriver.Chrome:
    os.makedirs(PROFILE_DIR, exist_ok=True)
    _limpiar_locks(PROFILE_DIR)

    # Intento 1: perfil persistente (mantiene tu sesión de Wallapop).
    try:
        return _intentar_arranque(_construir_options(PROFILE_DIR, headless))
    except Exception as e1:
        # Intento 2: perfil temporal limpio (descarta locks/perfil corrupto).
        import tempfile

        tmp_profile = tempfile.mkdtemp(prefix="wallapop-chrome-")
        try:
            return _intentar_arranque(_construir_options(tmp_profile, headless))
        except Exception as e2:
            raise RuntimeError(
                "No se pudo abrir Chrome. Comprueba que Google Chrome está "
                "instalado y actualizado.\n"
                f"- Con tu perfil: {e1}\n- Con perfil temporal: {e2}"
            ) from e2


def necesita_login(driver) -> bool:
    """Heurística: si no aparecen tarjetas de producto, probablemente falta login."""
    return len(_buscar_cards(driver)) == 0


def _buscar_cards(driver):
    # Página actual (catalog/published): cada producto es un <tsl-catalog-item>.
    cards = driver.find_elements(By.TAG_NAME, "tsl-catalog-item")
    # Respaldos para layouts antiguos de Wallapop.
    if len(cards) == 0:
        cards = driver.find_elements(By.TAG_NAME, "ts-item-card")
    if len(cards) == 0:
        cards = driver.find_elements(By.CSS_SELECTOR, "a.ItemCard")
    return cards


def _esperar_cards(driver, segundos: int = 15):
    """Espera (hasta `segundos`) a que aparezca la primera tarjeta de producto.
    Útil al reconectar a un Chrome abierto: la página puede tardar en cargar
    o estar aún navegando. Devuelve la lista de cards (vacía si no aparecen)."""
    fin = time.time() + segundos
    cards = _buscar_cards(driver)
    while not cards and time.time() < fin:
        time.sleep(1)
        cards = _buscar_cards(driver)
    return cards


def _click_ver_mas(driver) -> bool:
    """Pulsa el botón 'Ver más productos' / 'Cargar más' si existe. Wallapop
    carga el catálogo por lotes y a partir del primero exige pulsar este botón;
    sin él, el scraper se queda en ~100 productos. Devuelve True si hizo clic."""
    textos = ("ver más", "cargar más", "mostrar más", "ver mas", "cargar mas")
    candidatos = driver.find_elements(By.CSS_SELECTOR, "button, a, [role='button']")
    for el in candidatos:
        try:
            txt = (el.text or "").strip().lower()
            if not txt or not any(t in txt for t in textos):
                continue
            if not el.is_displayed():
                continue
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
            time.sleep(0.4)
            driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            continue
    return False


def _clave_item(item) -> str:
    """Clave estable para deduplicar tarjetas entre pasadas de scroll
    (Wallapop virtualiza la lista y reemplaza las tarjetas del DOM)."""
    enlace = _enlace_de_card(item)
    iid = _item_id(enlace)
    if iid:
        return iid
    if enlace:
        return enlace
    # Último recurso: título + precio del texto de la tarjeta.
    try:
        return (item.text or "").strip()[:80]
    except Exception:
        return ""


def _scroll_hasta_el_final(driver, max_iteraciones: int = 30):
    """Compatibilidad: hace scroll para cargar contenido (usado por /app/stats)."""
    ultimo_alto = driver.execute_script("return document.body.scrollHeight")
    estancado = 0
    for _ in range(max_iteraciones):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        _click_ver_mas(driver)
        time.sleep(2)
        nuevo_alto = driver.execute_script("return document.body.scrollHeight")
        if nuevo_alto == ultimo_alto:
            estancado += 1
            if estancado >= 3:
                break
        else:
            estancado = 0
        ultimo_alto = nuevo_alto


def _recolectar_scrolleando(
    driver,
    vendido: bool,
    max_iteraciones: int = 400,
    paciencia: int = 8,
    pausa: float = 1.3,
) -> list[dict]:
    """Carga TODO un catálogo con SCROLL INFINITO y extrae los productos de forma
    incremental (dedupe por id).

    Wallapop no usa botón de paginación: carga los productos a ráfagas a medida
    que te acercas al fondo, y VIRTUALIZA la lista (quita del DOM las tarjetas que
    salen de pantalla). Por eso:
      - Se baja de forma GRADUAL (aprox. 80% de pantalla por paso), no de un salto
        al fondo, para que cada ráfaga entre en el viewport y dé tiempo a cargar.
      - Se extrae en CADA paso, antes de que las tarjetas se reciclen.
      - Al llegar al fondo sin novedades se hace un 'empujón' (subir un poco y
        volver a bajar) para forzar la siguiente ráfaga.
    Solo se detiene tras `paciencia` intentos seguidos en el fondo sin que
    aparezcan tarjetas nuevas ni crezca la página."""
    vistos: dict[str, dict] = {}
    sin_novedad = 0
    ultimo_alto = 0

    def _recolectar_visibles() -> int:
        nuevos = 0
        for item in _buscar_cards(driver):
            clave = _clave_item(item)
            if not clave or clave in vistos:
                continue
            datos = _extraer_un_item(item, vendido)
            if datos:
                vistos[clave] = datos
                nuevos += 1
        return nuevos

    for _ in range(max_iteraciones):
        nuevos = _recolectar_visibles()

        alto = driver.execute_script("return document.body.scrollHeight")
        vh = driver.execute_script("return window.innerHeight") or 800

        # Bajar gradualmente (no de golpe al fondo).
        driver.execute_script("window.scrollBy(0, arguments[0]);", int(vh * 0.8))
        # Por si algún layout antiguo aún usa botón de 'ver más'.
        _click_ver_mas(driver)
        time.sleep(pausa)

        en_fondo = driver.execute_script(
            "return (window.innerHeight + window.pageYOffset) "
            ">= (document.body.scrollHeight - 4);"
        )
        nuevo_alto = driver.execute_script("return document.body.scrollHeight")

        if nuevos == 0 and nuevo_alto == ultimo_alto and en_fondo:
            sin_novedad += 1
            # Empujón para despertar la carga por ráfagas.
            driver.execute_script("window.scrollBy(0, -600);")
            time.sleep(0.5)
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(pausa)
            _recolectar_visibles()
            if sin_novedad >= paciencia:
                break
        else:
            sin_novedad = 0
        ultimo_alto = nuevo_alto

    # Última pasada por si quedó una ráfaga final sin recolectar.
    _recolectar_visibles()
    return list(vistos.values())


def _precio_a_numero(precio: str):
    """'1.234,50 €' -> 1234.5  (para poder filtrar/ordenar y graficar)."""
    if not precio:
        return None
    limpio = re.sub(r"[^\d,.]", "", precio)
    if not limpio:
        return None
    # formato europeo: . miles , decimales
    limpio = limpio.replace(".", "").replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        return None


def _item_id(enlace: str) -> str:
    """Extrae el id numérico del anuncio de su URL.
    'https://es.wallapop.com/item/boligrafo-...-1273922753' -> '1273922753'."""
    if not enlace:
        return ""
    m = re.search(r"-(\d+)(?:[/?#]|$)", enlace)
    return m.group(1) if m else ""


def _a_entero(texto: str):
    """'53', '1.234', '2,3 mil'... -> int (o None). Toma los dígitos."""
    if not texto:
        return None
    solo = re.sub(r"[^\d]", "", texto)
    return int(solo) if solo else None


def _texto(item, selector):
    try:
        return item.find_element(By.CSS_SELECTOR, selector).text.strip()
    except Exception:
        return ""


def _primer_existente(item, selectores):
    """Devuelve el texto del primer selector que exista en el item."""
    for sel in selectores:
        txt = _texto(item, sel)
        if txt:
            return txt
    return ""


def _imagen_de_card(item) -> str:
    """Extrae la URL de imagen. En el layout actual la imagen es un
    background-image de .ItemAvatar; en layouts antiguos es un <img>."""
    # 1) background-image en .ItemAvatar / .item-image
    for sel in (".ItemAvatar", ".item-image", "[style*='background-image']"):
        try:
            estilo = item.find_element(By.CSS_SELECTOR, sel).get_attribute("style") or ""
            m = re.search(r"url\(['\"]?(https?://[^'\")]+)", estilo)
            if m:
                return m.group(1)
        except Exception:
            continue
    # 2) <img> clásico
    for sel in ("img", ".ItemCard__image img", "tsl-image img"):
        try:
            el = item.find_element(By.CSS_SELECTOR, sel)
            src = (
                el.get_attribute("src")
                or el.get_attribute("data-src")
                or el.get_attribute("srcset")
                or ""
            )
            if src:
                return src.split(" ")[0]  # primer item de srcset
        except Exception:
            continue
    return ""


def _enlace_de_card(item) -> str:
    """Enlace al anuncio. El item suele tener varios <a> al mismo /item/."""
    try:
        href = item.get_attribute("href")
        if href:
            return href
    except Exception:
        pass
    for sel in ("a[href*='/item/']", "a[tslitemanchorroute]", "a[href]"):
        try:
            href = item.find_element(By.CSS_SELECTOR, sel).get_attribute("href")
            if href:
                return href
        except Exception:
            continue
    return ""


def _extraer_un_item(item, vendido: bool = False) -> dict | None:
    """Extrae los datos de UNA tarjeta de producto. Devuelve None si falla."""
    try:
        # Título
        titulo = _primer_existente(item, [".info-title", ".ItemCard__title"])
        if not titulo:
            try:
                titulo = (
                    item.find_element(By.CSS_SELECTOR, "[title]").get_attribute("title")
                    or ""
                ).strip()
            except Exception:
                pass
        if not titulo:
            titulo = "Sin título / No detectado"

        # Precio
        precio = _primer_existente(
            item, [".info-price", ".ItemCard__price", ".ts-item-card-price"]
        )
        if not precio:
            precio = "0 €"

        # Enlace e imagen
        enlace = _enlace_de_card(item)
        imagen = _imagen_de_card(item)

        # Estado: vendido > caducado > badge clásico > en venta
        if vendido:
            estado = "Vendido"
        else:
            estado = ""
            try:
                if item.find_elements(
                    By.CSS_SELECTOR, ".CatalogItem__content--expired"
                ):
                    estado = "Caducado"
            except Exception:
                pass
            if not estado:
                estado = _texto(item, ".ItemCard__badge, .item-card-badge")
            if not estado:
                estado = "En venta"

        return {
            "titulo": titulo.strip(),
            "precio": precio.strip(),
            "precio_num": _precio_a_numero(precio),
            "estado": estado,
            "vendido": vendido,
            "imagen": imagen,
            "enlace": enlace,
            "item_id": _item_id(enlace),
            # Se rellenan luego al cruzar con /app/stats:
            "visualizaciones": None,
            "chats": None,
            "favoritos": None,
            "fecha_publicacion": "",
        }
    except Exception:
        return None


def _extraer_items(driver, vendido: bool = False) -> list[dict]:
    productos = []
    for item in _buscar_cards(driver):
        datos = _extraer_un_item(item, vendido)
        if datos:
            productos.append(datos)
    return productos


def _clic_pestana_vendidos(driver) -> bool:
    """Hace clic en la pestaña 'Vendidos' del catálogo. Devuelve True si lo logró.
    (La URL /app/catalog/sold redirige a published; hay que navegar por SPA)."""
    from selenium.webdriver.common.by import By as _By

    for xpath in (
        "//a[normalize-space()='Vendidos']",
        "//a[@nav-link][contains(., 'Vendido')]",
        "//*[@role='tab'][contains(., 'Vendido')]",
    ):
        try:
            tab = driver.find_element(_By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", tab)
            time.sleep(2)
            _esperar_cards(driver, segundos=6)
            return True
        except Exception:
            continue
    return False


def _extraer_stats(driver) -> dict:
    """Navega a /app/stats y devuelve {item_id: {visualizaciones, chats,
    favoritos, fecha_publicacion}} para cruzar con los productos."""
    stats = {}
    try:
        driver.get(URL_STATS)
    except Exception:
        return stats
    # Esperar a que carguen las filas de estadísticas.
    fin = time.time() + 12
    filas = driver.find_elements(By.TAG_NAME, "tsl-item-stats-row")
    while not filas and time.time() < fin:
        time.sleep(1)
        filas = driver.find_elements(By.TAG_NAME, "tsl-item-stats-row")
    _scroll_hasta_el_final(driver, max_iteraciones=15)
    filas = driver.find_elements(By.TAG_NAME, "tsl-item-stats-row")

    # Mapea cada icono de contador a su métrica.
    iconos = {"views": "visualizaciones", "ico-message": "chats", "heart": "favoritos"}
    for fila in filas:
        try:
            enlace = ""
            try:
                enlace = fila.find_element(
                    By.CSS_SELECTOR, "a[href*='/item/']"
                ).get_attribute("href") or ""
            except Exception:
                pass
            iid = _item_id(enlace)
            if not iid:
                continue
            registro = {
                "visualizaciones": None,
                "chats": None,
                "favoritos": None,
                "fecha_publicacion": _texto(fila, ".col-date span, .col-date"),
            }
            for contador in fila.find_elements(By.CSS_SELECTOR, ".col-counters"):
                try:
                    icono = contador.find_element(
                        By.CSS_SELECTOR, "tsl-svg-icon"
                    ).get_attribute("src") or ""
                except Exception:
                    icono = ""
                metrica = next(
                    (v for k, v in iconos.items() if k in icono), None
                )
                if metrica:
                    registro[metrica] = _a_entero(contador.text)
            stats[iid] = registro
        except Exception:
            continue
    return stats


def extraer_productos(
    esperar_login_segundos: int = 0,
    adjuntar_puerto: int | None = None,
) -> pd.DataFrame:
    """
    Extrae los productos y los guarda en productos.json y CSV. Devuelve un DataFrame.

    - adjuntar_puerto: si se indica (p.ej. 9222), se conecta a tu Chrome YA ABIERTO
      en modo depuración remota y usa tu sesión actual (no abre ventana nueva ni
      cierra tu navegador). Si es None, lanza un Chrome propio con perfil persistente.
    """
    adjunto = adjuntar_puerto is not None
    if adjunto:
        if not _puerto_abierto("127.0.0.1", adjuntar_puerto):
            raise RuntimeError(
                f"No hay ningún Chrome escuchando en el puerto {adjuntar_puerto}.\n"
                "Cierra Chrome del todo (Cmd+Q) y vuelve a abrirlo en modo "
                "depuración con:\n"
                "  bash abrir_chrome_debug.sh"
            )
        driver = _navegador_adjunto(adjuntar_puerto)
    else:
        driver = _configurar_navegador(headless=False)

    try:
        # 1) EN VENTA. Al reconectar puede que estés en otra página; forzamos
        #    la del catálogo y esperamos a que cargue de verdad.
        driver.get(URL_PRODUCTOS)
        _esperar_cards(driver, segundos=8)

        if esperar_login_segundos and necesita_login(driver):
            # Aún sin sesión: damos tiempo a iniciar sesión y reintentamos.
            time.sleep(esperar_login_segundos)
            driver.get(URL_PRODUCTOS)
            _esperar_cards(driver, segundos=8)

        productos = _recolectar_scrolleando(driver, vendido=False)

        # 2) VENDIDOS (pestaña; su URL directa redirige a published).
        if _clic_pestana_vendidos(driver):
            productos += _recolectar_scrolleando(driver, vendido=True)

        # Deduplicar por id de anuncio (por si una tarjeta aparece en ambas vistas).
        unicos = {}
        for p in productos:
            clave = p.get("item_id") or p.get("enlace") or p.get("titulo")
            # Preferimos la versión 'vendido' si el mismo id aparece dos veces.
            if clave not in unicos or p.get("vendido"):
                unicos[clave] = p
        productos = list(unicos.values())

        # 3) ESTADÍSTICAS: visualizaciones, chats y favoritos por anuncio.
        stats = _extraer_stats(driver)
        for p in productos:
            s = stats.get(p.get("item_id", ""))
            if s:
                p["visualizaciones"] = s["visualizaciones"]
                p["chats"] = s["chats"]
                p["favoritos"] = s["favoritos"]
                if s.get("fecha_publicacion"):
                    p["fecha_publicacion"] = s["fecha_publicacion"]
    finally:
        # Si estamos adjuntos a TU Chrome, no lo cerramos (driver.quit cerraría
        # tu navegador). Solo soltamos la conexión.
        if adjunto:
            driver.command_executor.close()
        else:
            driver.quit()

    # Guardar JSON (lo consume la web HTML) y CSV
    if productos:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(productos, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(productos)
    if not df.empty:
        df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    print("🚀 Abriendo Wallapop. Si es la primera vez, inicia sesión en la ventana.")
    df = extraer_productos(esperar_login_segundos=60)
    if df.empty:
        print("❌ No se extrajeron productos. ¿Iniciaste sesión y estabas en 'Productos'?")
    else:
        print(f"✅ {len(df)} productos guardados en {JSON_PATH} y {CSV_PATH}")
        print(df.head())
