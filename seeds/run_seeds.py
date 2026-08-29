"""
run_seeds.py — orquestador de todas las seeds.
Corre todas en orden en una sola sesión de base de datos.

Uso:
    cd backend/
    python seeds/run_seeds.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from seeds import seed_01_periodos_materias
from seeds import seed_02_usuarios_sistema
from seeds import seed_03_comisiones_sistemas_1ano
from seeds import seed_04_alumnos_demo

PASOS = [
    ("01 — Períodos y materias",          seed_01_periodos_materias.seed),
    ("02 — Usuarios de sistema",          seed_02_usuarios_sistema.seed),
    ("03 — Comisiones 1º año Sistemas",   seed_03_comisiones_sistemas_1ano.seed),
    ("04 — Alumnos demo",                 seed_04_alumnos_demo.seed),
]


def main():
    print("\n" + "=" * 70)
    print("  UTN FRT — Seeds 2026")
    print("=" * 70)

    db = SessionLocal()
    try:
        for nombre, fn in PASOS:
            print(f"\n{'=' * 70}")
            print(f"  PASO: {nombre}")
            print("=" * 70)
            fn(db)

        print("\n" + "=" * 70)
        print("🎉  Todas las seeds corrieron correctamente.")
        print("=" * 70 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante las seeds: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
