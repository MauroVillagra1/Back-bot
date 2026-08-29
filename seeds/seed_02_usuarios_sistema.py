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


def seed(db) -> None:
    print("\n── Administrador / Root ─────────────────────────────────────────────")
    u, created = get_or_create(
        db, Usuario,
        defaults={
            "nombre":        "Mauro",
            "apellido":      "Villagra",
            "password_hash": HASH_DEFAULT,
            "rol":           RolEnum.root,
            "activo":        True,
        },
        email="root@root.frt.utn.edu.ar",
    )
    log(created, f"root@root.frt.utn.edu.ar  [root]")

    print("\n── Master ───────────────────────────────────────────────────────────")
    u, created = get_or_create(
        db, Usuario,
        defaults={
            "nombre":        "Mauro",
            "apellido":      "Villagra",
            "password_hash": HASH_DEFAULT,
            "rol":           RolEnum.master,
            "activo":        True,
        },
        email="master@master.frt.utn.edu.ar",
    )
    log(created, f"master@master.frt.utn.edu.ar  [master]")

    print("\n── Administrativo ───────────────────────────────────────────────────")
    u, created = get_or_create(
        db, Usuario,
        defaults={
            "nombre":        "Mauro",
            "apellido":      "Villagra",
            "password_hash": HASH_DEFAULT,
            "rol":           RolEnum.administrativo,
            "activo":        True,
        },
        email="admin@admin.frt.utn.edu.ar",
    )
    log(created, f"admin@admin.frt.utn.edu.ar  [administrativo]")

    print("\n── Jefes de Área ────────────────────────────────────────────────────")
    for letra, carrera in DEPARTAMENTOS.items():
        if letra == "H":
            print(f"  · omitido: Básicas (transversal, sin jefe propio)")
            continue
        carrera_norm = normalizar_nombre(carrera)
        email = f"jefe{carrera_norm}@depto.frt.utn.edu.ar"
        u, created = get_or_create(
            db, Usuario,
            defaults={
                "nombre":        "Mauro",
                "apellido":      "Villagra",
                "password_hash": HASH_DEFAULT,
                "rol":           RolEnum.jefe_area,
                "activo":        True,
            },
            email=email,
        )
        log(created, f"{email}  [{carrera}]")

    db.commit()
    print("\n✅ seed_02 completada.")
    print("   Cuentas creadas:")
    print("   root@root.frt.utn.edu.ar         / 123456  [root]")
    print("   master@master.frt.utn.edu.ar     / 123456  [master]")
    print("   admin@admin.frt.utn.edu.ar       / 123456  [administrativo]")
    print("   jefesistemas@depto.frt.utn.edu.ar / 123456  [jefe_area]")


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
