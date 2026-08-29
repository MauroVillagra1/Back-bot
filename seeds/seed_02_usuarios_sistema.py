"""
seed_02_usuarios_sistema.py
Crea las cuentas de sistema que NO dependen de comisiones ni materias:
  - 1 Administrador general
  - 1 Administrativo
  - 1 Jefe de Departamento por cada carrera (excepto Básicas/H)

NOTA: El RolEnum de app/models/usuario.py tiene estos miembros:
  administrador, administrativo, jefe_departamento,
  profesor, profesor_directivo, alumno.
NO existe root ni master. Si necesitás distinguir niveles de admin,
extendé el enum ANTES de correr esta seed.

Contraseña de todas las cuentas: 123456
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.usuario import RolEnum, Usuario
from seeds.seed_utils import DEPARTAMENTOS, HASH_DEFAULT, get_or_create, log, normalizar_nombre


def _rol(nombre: str) -> RolEnum:
    """Devuelve RolEnum.<nombre> o lanza RuntimeError con mensaje claro."""
    try:
        return getattr(RolEnum, nombre)
    except AttributeError:
        miembros = [m.value for m in RolEnum]
        raise RuntimeError(
            f"RolEnum no tiene el miembro '{nombre}'. "
            f"Miembros disponibles: {miembros}. "
            f"Extendé el enum en app/models/usuario.py antes de correr esta seed."
        )


def seed(db) -> None:
    # ── Administrador general ─────────────────────────────────────────────────
    print("\n── Administrador ────────────────────────────────────────────────────")
    u, created = get_or_create(
        db, Usuario,
        defaults={
            "nombre":        "Administrador Sistema",
            "password_hash": HASH_DEFAULT,
            "rol":           _rol("administrador"),
            "activo":        True,
        },
        email="admin@admin.frt.utn.edu.ar",
    )
    log(created, f"admin@admin.frt.utn.edu.ar  [{u.rol.value}]")

    # ── Administrativo ────────────────────────────────────────────────────────
    # Para adicionales usar: admin1@admin.frt.utn.edu.ar, admin2@...
    print("\n── Administrativo ───────────────────────────────────────────────────")
    u, created = get_or_create(
        db, Usuario,
        defaults={
            "nombre":        "Personal Administrativo",
            "password_hash": HASH_DEFAULT,
            "rol":           _rol("administrativo"),
            "activo":        True,
        },
        email="administrativo@admin.frt.utn.edu.ar",
    )
    log(created, f"administrativo@admin.frt.utn.edu.ar  [{u.rol.value}]")

    # ── Jefes de Departamento ─────────────────────────────────────────────────
    # H = Básicas es transversal, no tiene jefe propio.
    print("\n── Jefes de Departamento ────────────────────────────────────────────")
    for letra, carrera in DEPARTAMENTOS.items():
        if letra == "H":
            print(f"  · omitido: Básicas (transversal, sin jefe propio)")
            continue

        carrera_norm = normalizar_nombre(carrera)   # ej: "sistemas", "mecanica"
        email        = f"jefe{carrera_norm}@depto.frt.utn.edu.ar"
        nombre       = f"Jefe Departamento {carrera}"

        u, created = get_or_create(
            db, Usuario,
            defaults={
                "nombre":        nombre,
                "password_hash": HASH_DEFAULT,
                "rol":           _rol("jefe_departamento"),
                "activo":        True,
            },
            email=email,
        )
        log(created, f"{email}  [{carrera}]")

    db.commit()
    print("\n✅ seed_02 completada.")
    print("   Contraseña de todas las cuentas: 123456")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error en seed_02: {e}")
        raise
    finally:
        db.close()
