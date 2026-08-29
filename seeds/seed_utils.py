"""
seed_utils.py — helpers reutilizables para todas las seeds.
No se ejecuta directamente; lo importan los demás módulos de seeds/.
"""
import difflib
import unicodedata

from app.core.security import hash_password

# ── Contraseña por defecto ────────────────────────────────────────────────────
PASSWORD_DEFAULT = "123456"
HASH_DEFAULT     = hash_password(PASSWORD_DEFAULT)

# ── Departamentos / carreras ──────────────────────────────────────────────────
# H (Básicas) es transversal; no tiene comisiones ni jefe propios.
DEPARTAMENTOS = {
    "K": "Sistemas",
    "S": "Mecánica",
    "Q": "Eléctrica",
    "O": "Civil",
    "R": "Electrónica",
    "H": "Básicas",
}


# ── Normalización de nombres ──────────────────────────────────────────────────

def normalizar_nombre(nombre: str) -> str:
    """
    Convierte un nombre en un string apto para email local.
    Ej: "José Augusto Nasrallah" → "jose.augusto.nasrallah"
    """
    # Quitar tildes (NFD + filtrar categoría Mn)
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", nombre.lower())
        if unicodedata.category(c) != "Mn"
    )
    # Reemplazar cualquier caracter no alfanumérico por punto
    import re
    punteado = re.sub(r"[^a-z0-9]+", ".", sin_tildes)
    # Limpiar puntos al inicio/final y dobles
    return punteado.strip(".")


# ── Emails únicos ─────────────────────────────────────────────────────────────

def email_unico(db, modelo, base_local: str, dominio: str, excluir_id=None) -> str:
    """
    Devuelve "<base_local>@<dominio>" si está libre, o
    "<base_local>2@<dominio>", "<base_local>3@..." hasta encontrar uno libre.
    """
    candidato = f"{base_local}@{dominio}"
    sufijo = 2
    while True:
        query = db.query(modelo).filter(modelo.email == candidato)
        if excluir_id is not None:
            query = query.filter(modelo.id != excluir_id)
        if not query.first():
            return candidato
        candidato = f"{base_local}{sufijo}@{dominio}"
        sufijo += 1


def email_docente(db, modelo, nombre: str) -> str:
    return email_unico(db, modelo, normalizar_nombre(nombre), "doc.frt.utn.edu.ar")


def email_alumno(db, modelo, nombre: str) -> str:
    return email_unico(db, modelo, normalizar_nombre(nombre), "alu.frt.utn.edu.ar")


# ── get_or_create ─────────────────────────────────────────────────────────────

def get_or_create(db, model, defaults: dict = None, **filters):
    """
    Busca model por filters; si no existe lo crea con filters + defaults.
    Devuelve (instancia, creado: bool).
    """
    defaults = defaults or {}
    instancia = db.query(model).filter_by(**filters).first()
    if instancia:
        return instancia, False
    instancia = model(**filters, **defaults)
    db.add(instancia)
    db.flush()
    return instancia, True


# ── Logging ───────────────────────────────────────────────────────────────────

def log(created: bool, label: str) -> None:
    if created:
        print(f"  ✓ creado:    {label}")
    else:
        print(f"  · ya existe: {label}")


# ── Detección de profesores duplicados ────────────────────────────────────────

def _similitud(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _nombres_equivalentes(a: str, b: str) -> bool:
    """
    True si similitud >= 0.82 O si las palabras normalizadas son las mismas
    en cualquier orden (detecta "Martínez Ariel" == "Ariel Martínez").
    """
    if _similitud(a, b) >= 0.82:
        return True
    palabras_a = set(normalizar_nombre(a).split("."))
    palabras_b = set(normalizar_nombre(b).split("."))
    return bool(palabras_a) and palabras_a == palabras_b


def buscar_profesor_similar(nombre: str, existentes: list, umbral_dudoso: float = 0.70):
    """
    Busca en `existentes` (lista de Usuario) un profesor con nombre equivalente.
    Devuelve (usuario_encontrado | None, lista_de_avisos_dudosos).
    Un aviso dudoso se emite cuando similitud está entre umbral_dudoso y 0.82
    (posible typo — requiere revisión manual).
    """
    avisos = []
    for u in existentes:
        if _nombres_equivalentes(nombre, u.nombre):
            return u, avisos
        sim = _similitud(nombre, u.nombre)
        if umbral_dudoso <= sim < 0.82:
            avisos.append(f"  ⚠️  '{nombre}' ≈ '{u.nombre}' (similitud {sim:.0%}) — revisar manualmente")
    return None, avisos


def crear_profesor(db, nombre_raw: str, existentes: list, rol_profesor):
    """
    Busca o crea un profesor por nombre similar.
    - Si encuentra uno existente, lo devuelve (imprimiendo avisos dudosos si los hay).
    - Si no, crea un Usuario nuevo, lo agrega a `existentes` in-place y lo devuelve.
    """
    from app.models.usuario import Usuario  # import local para evitar circular

    encontrado, avisos = buscar_profesor_similar(nombre_raw, existentes)
    for aviso in avisos:
        print(aviso)

    if encontrado:
        return encontrado

    email = email_docente(db, Usuario, nombre_raw)
    nuevo = Usuario(
        nombre=nombre_raw,
        email=email,
        password_hash=HASH_DEFAULT,
        rol=rol_profesor,
        activo=True,
    )
    db.add(nuevo)
    db.flush()
    existentes.append(nuevo)
    print(f"  ✓ Profesor — {nombre_raw} ({email})")
    return nuevo
