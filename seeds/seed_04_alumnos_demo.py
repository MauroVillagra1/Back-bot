"""
seed_04_alumnos_demo.py
Carga 2 alumnos de prueba inscriptos en comisiones ya creadas.
Solo para poder probar endpoints de rol alumno.

Requiere: seed_03 (necesita que existan comisiones 1K01 y 1K02).
Contraseña de todas las cuentas: 123456
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.academico import Comision, UsuarioComision
from app.models.usuario import RolEnum, Usuario
from seeds.seed_utils import HASH_DEFAULT, email_alumno, get_or_create, log

ALUMNOS_DEMO = [
    ("Ana Martínez",  "1K01"),
    ("Carlos López",  "1K02"),
]


def seed(db) -> None:
    print("\n── Alumnos demo ─────────────────────────────────────────────────────")

    for nombre, nombre_comision in ALUMNOS_DEMO:
        # 1. Generar email único
        email = email_alumno(db, Usuario, nombre)

        # 2. Crear usuario alumno
        alumno, created = get_or_create(
            db, Usuario,
            defaults={
                "nombre":        nombre,
                "password_hash": HASH_DEFAULT,
                "rol":           RolEnum.estudiante,
                "activo":        True,
            },
            email=email,
        )
        log(created, f"{nombre} <{email}>")

        # 3. Buscar comisión
        comision = db.query(Comision).filter_by(nombre=nombre_comision).first()
        if not comision:
            print(f"  ⚠️  Comisión '{nombre_comision}' no encontrada — "
                  f"verificá que seed_03 haya corrido.")
            continue

        # 4. Inscribir en comisión
        _, created_insc = get_or_create(
            db, UsuarioComision,
            defaults={},
            usuario_id=alumno.id,
            comision_id=comision.id,
        )
        log(created_insc, f"Inscripción {nombre} → {nombre_comision}")

    db.commit()
    print("\n✅ seed_04 completada.")
    print("   Contraseña de todas las cuentas: 123456")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error en seed_04: {e}")
        raise
    finally:
        db.close()
