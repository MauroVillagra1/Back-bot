"""
seed_03_comisiones_sistemas_1ano.py
Crea las 10 comisiones de 1er año de Sistemas (1K01–1K10),
sus cursadas con horarios reales, y los profesores asignados.

Requiere: seed_01 (período "Ciclo Lectivo Anual 2026" y materias P23-*)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.academico import Comision, Materia, PeriodoAcademico
from app.models.cursada import Cursada, CursadaProfesor, ModalidadEnum
from app.models.usuario import RolEnum
from seeds.seed_utils import crear_profesor, get_or_create, log

# ── Códigos de materias de 1º año ─────────────────────────────────────────────
CODIGOS_1ANIO = ["P23-AM1", "P23-AGA", "P23-AED", "P23-AC",
                 "P23-F1",  "P23-LED", "P23-SPN", "P23-IS"]

# ── Datos por comisión ────────────────────────────────────────────────────────
# Estructura: nombre -> {
#   "aula": str,
#   "turno": str,
#   "materias": { codigo: (horario, [docentes]) }
# }
# Docentes "A designar" se omiten de la lista (no se crean).
# Horarios tomados literalmente de seed_horarios.py (fuente oficial 2026).

COMISIONES_1ANO = {
    "1K01": {
        "aula":  "103/105",
        "turno": "Mañana",
        "materias": {
            "P23-AM1": ("Lunes 08:00-09:30 | Jueves 08:00-09:30",              ["Montesino Rafael", "Susana Moya"]),
            "P23-AGA": ("Martes 08:00-09:30 | Viernes 08:00-09:30",            ["Dip Marisol"]),
            "P23-AED": ("Martes 09:30-11:00 (Lab.154) | Viernes 10:15-12:30 (Lab.151)", ["Nasrallah José"]),
            "P23-AC":  ("Miércoles 10:15-11:45 | Jueves 11:00-12:30",          ["Greco Oscar", "Such Victor"]),
            "P23-F1":  ("Martes 11:00-12:30 | Jueves 09:30-11:00",             ["Aparicio Gabriela"]),
            "P23-LED": ("Lunes 10:15-12:30",                                   ["Caporale Maria Concepcion"]),
            "P23-SPN": ("Miércoles 08:00-10:15",                               ["Caporale Maria Concepcion"]),
            "P23-IS":  ("Miércoles 11:45-12:30",                               ["Aparicio Gabriela"]),
        },
    },
    "1K02": {
        "aula":  "107/109",
        "turno": "Mañana",
        "materias": {
            "P23-AM1": ("Martes 10:15-12:30 | Miércoles 09:30-12:30",          ["Arias Jorge", "Cruz Pedro"]),
            "P23-AGA": ("Martes 08:00-09:30 | Jueves 11:00-12:30 | Viernes 08:00-11:00", ["Nasrallah José", "Susana Moya"]),
            "P23-AED": ("Miércoles 08:00-09:30 (Lab.151) | Jueves 09:30-11:00", ["Dip Marisol"]),
            "P23-AC":  ("Lunes 08:00-09:30 | Jueves 08:00-09:30",              ["Moyano Alberto"]),
            "P23-F1":  ("Lunes 09:30-12:30",                                   ["Valdez Ocampo T."]),
            "P23-LED": ("Viernes 11:00-13:15",                                 ["Bedran Marisel"]),
            "P23-SPN": ("Martes 08:00-10:15",                                  ["Bedran Marisel"]),
            "P23-IS":  ("Lunes 09:30-10:15",                                   ["Susana Moya"]),
        },
    },
    "1K03": {
        "aula":  "Sub 7/Sub 9",
        "turno": "Mañana",
        "materias": {
            "P23-AM1": ("Lunes 08:00-09:30 | Viernes 10:15-12:30",             ["Carrion Martin", "Canto Javier"]),
            "P23-AGA": ("Miércoles 10:15-12:30 | Jueves 09:30-11:00",          ["Such Victor"]),
            "P23-AED": ("Lunes 09:30-11:00 | Viernes 08:00-09:30 (Lab.151)",   ["Aparicio Gabriela"]),
            "P23-AC":  ("Martes 11:00-12:30 | Jueves 08:00-09:30",             ["Valla Sandra"]),
            "P23-F1":  ("Lunes 11:00-12:30 | Martes 08:00-09:30",              ["Caporale Maria Concepcion"]),
            "P23-LED": ("Miércoles 08:00-10:15",                               ["Moya Susana"]),
            "P23-SPN": ("Jueves 11:00-13:15",                                  ["Caporale Maria Concepcion"]),
            "P23-IS":  ("Martes 09:30-11:00",                                  ["Aparicio Gabriela"]),
        },
    },
    "1K04": {
        "aula":  "104/106",
        "turno": "Mañana",
        "materias": {
            "P23-AM1": ("Martes 08:00-09:30 | Viernes 10:15-12:30",            ["Nasrallah José", "Carrion Martin"]),
            "P23-AGA": ("Miércoles 10:15-12:30 | Jueves 08:00-09:30",          ["Valla Sandra"]),
            "P23-AED": ("Lunes 11:00-12:30 (Lab.151) | Jueves 11:00-13:15 (Lab.151)", ["Cruz Pedro"]),
            "P23-AC":  ("Lunes 09:30-11:00 | Jueves 09:30-11:00",              ["Susana Moya"]),
            "P23-F1":  ("Lunes 08:00-09:30 | Miércoles 08:00-10:15",           ["Dip Marisol"]),
            "P23-LED": ("Viernes 08:00-09:30",                                 ["Valdez Ocampo T."]),
            "P23-SPN": ("Martes 09:30-13:15",                                  ["Bedran Marisel"]),
            "P23-IS":  ("Martes 09:30-10:15",                                  ["Bedran Marisel"]),
        },
    },
    "1K05": {
        "aula":  "Sub 8/Sub 10",
        "turno": "Mañana",
        "materias": {
            "P23-AM1": ("Jueves 11:45-12:30 | Viernes 08:00-10:15",            ["Caporale Maria Concepcion", "Canto Javier"]),
            "P23-AGA": ("Martes 09:30-11:45 | Miércoles 08:00-10:15",          ["Such Victor"]),
            "P23-AED": ("Miércoles 10:15-11:00 (Lab.154) | Jueves 08:00-09:30 (Lab.151)", ["Aparicio Gabriela"]),
            "P23-AC":  ("Martes 08:00-09:30 | Jueves 10:15-11:45",             ["Montesino Rafael"]),
            "P23-F1":  ("Miércoles 11:00-12:30 | Viernes 10:15-12:30",         ["Herrera Fernando"]),
            "P23-LED": ("Lunes 08:00-11:45",                                   ["Dip Marisol"]),
            "P23-SPN": ("Lunes 11:45-12:30",                                   ["Dip Marisol"]),
            "P23-IS":  ("Martes 11:45-12:30",                                  ["Aparicio Gabriela"]),
        },
    },
    "1K06": {
        "aula":  "108/110",
        "turno": "Mañana",
        "materias": {
            "P23-AM1": ("Lunes 10:15-12:30 | Jueves 10:15-11:45",              ["Cruz Pedro", "Nasrallah Augusto José"]),
            "P23-AGA": ("Martes 08:00-09:30 | Miércoles 08:00-09:30",          ["Herrera Fernando"]),
            "P23-AED": ("Martes 10:15-11:45 (Lab.154) | Jueves 08:00-09:30 (Lab.154)", ["Montesino Rafael"]),
            "P23-AC":  ("Martes 09:30-10:15 | Viernes 10:15-11:45",            ["Such Victor"]),
            "P23-F1":  ("Lunes 08:00-10:15 | Jueves 11:45-12:30",              ["Aparicio Gabriela"]),
            "P23-LED": ("Miércoles 09:30-11:45",                               ["De Luca Alejandra"]),
            "P23-SPN": ("Viernes 08:00-09:30",                                 ["Dip Marisol"]),
            "P23-IS":  ("Viernes 11:45-12:30",                                 ["Aparicio Gabriela"]),
        },
    },
    "1K07": {
        "aula":  "103/105",
        "turno": "Tarde",
        "materias": {
            "P23-AM1": ("Miércoles 16:15-18:30 | Jueves 13:15-15:30",          ["Montesino Rafael", "Guillermo Brito"]),
            "P23-AGA": ("Lunes 16:15-18:30 | Jueves 17:00-18:30",              ["Valdez Ocampo Teresa"]),
            "P23-AED": ("Martes 13:15-14:45 (Lab.151) | Viernes 17:00-19:15 (Lab.151)", ["De Luca Alejandra"]),
            "P23-AC":  ("Martes 14:45-15:30 | Viernes 15:30-17:00",            ["Dip Marisol"]),
            "P23-F1":  ("Lunes 14:00-16:15 | Viernes 14:00-15:30",             ["Caporale Concepcion"]),
            "P23-LED": ("Martes 15:30-18:30",                                  ["Martinez Ariel"]),
            "P23-SPN": ("Miércoles 14:00-16:15",                               ["Bedran Marisel"]),
            "P23-IS":  ("Jueves 15:30-17:00",                                  ["Mambrini Carlos"]),
        },
    },
    "1K08": {
        "aula":  "104/106",
        "turno": "Tarde",
        "materias": {
            "P23-AM1": ("Miércoles 14:00-15:30 | Jueves 15:30-17:00",          ["Valdez Ocampo Teresa", "Martinez Ariel"]),
            "P23-AGA": ("Lunes 14:00-16:15 | Jueves 14:00-15:30",              ["Bedran Marisel"]),
            "P23-AED": ("Martes 17:00-18:30 | Viernes 17:00-19:15 (Lab.154)",  ["Nasrallah José Augusto"]),
            "P23-AC":  ("Martes 15:30-17:00 | Viernes 14:00-15:30",            ["Dip Marisol"]),
            "P23-F1":  ("Lunes 16:15-18:30 | Viernes 15:30-17:00",             ["Cruz Pedro"]),
            "P23-LED": ("Martes 14:00-15:30",                                  ["Oris Ramon"]),
            "P23-SPN": ("Miércoles 15:30-18:30",                               ["Valla Sandra"]),
            "P23-IS":  ("Jueves 17:00-18:30",                                  ["Valla Sandra"]),
        },
    },
    "1K09": {
        "aula":  "115",
        "turno": "Noche",
        "materias": {
            "P23-AM1": ("Miércoles 19:00-21:15 | Jueves 19:00-21:15",          ["Caporale Concepcion", "Valla Sandra"]),
            "P23-AGA": ("Lunes 19:00-21:15 | Jueves 17:30-19:00",              ["De Luca Alejandra"]),
            "P23-AED": ("Lunes 21:15-23:30 (Lab.154) | Martes 19:00-20:30",   ["Ballesteros Walter"]),
            "P23-AC":  ("Jueves 21:15-23:30 | Viernes 18:15-19:00",            ["Martinez Ariel"]),
            "P23-F1":  ("Viernes 19:00-21:15",                                 ["Bedran Marisel"]),
            "P23-LED": ("Miércoles 21:15-23:30",                               ["Martinez Ariel"]),
            "P23-SPN": ("Martes 20:30-22:45",                                  ["Bedran Marisel"]),
            "P23-IS":  ("Viernes 21:15-23:30",                                 ["De Luca Alejandra"]),
        },
    },
    "1K10": {
        "aula":  "112",
        "turno": "Noche",
        "materias": {
            "P23-AM1": ("Martes 18:15-19:45 | Miércoles 18:15-21:15",          ["Martinez Ariel", "Bedran Marisel"]),
            "P23-AGA": ("Lunes 20:30-22:45 | Jueves 18:15-19:45",              ["Montesino Rafael"]),
            "P23-AED": ("Jueves 19:45-21:15 (Lab.155) | Miércoles 21:15-23:30 (Lab.151)", ["Carlos Mambrini"]),
            "P23-AC":  ("Martes 22:00-23:30 | Viernes 19:45-21:15",            ["Analia Barrionuevo"]),
            "P23-F1":  ("Martes 19:45-22:00 | Viernes 18:15-19:45",            ["De Luca Alejandra"]),
            "P23-LED": ("Lunes 19:00-20:30",                                   ["Dip Marisol"]),
            "P23-SPN": ("Viernes 21:15-23:30",                                 ["De Luca Alejandra"]),
            "P23-IS":  ("Jueves 21:15-23:30",                                  ["Dip Marisol"]),
        },
    },
}


def seed(db) -> None:
    # ── Verificar que seed_01 ya corrió ──────────────────────────────────────
    periodo = db.query(PeriodoAcademico).filter_by(
        nombre="Ciclo Lectivo Anual 2026"
    ).first()
    if not periodo:
        raise RuntimeError(
            "No existe el período 'Ciclo Lectivo Anual 2026'. "
            "Corré seed_01_periodos_materias.py primero."
        )

    # ── Cargar materias en dict {codigo: Materia} ─────────────────────────────
    materias = {}
    for cod in CODIGOS_1ANIO:
        mat = db.query(Materia).filter_by(codigo=cod).first()
        if not mat:
            print(f"  ⚠️  Materia no encontrada: {cod} — verificá que seed_01 haya corrido.")
        else:
            materias[cod] = mat

    # ── Profesores existentes (para detección de duplicados por nombre similar) ─
    profesores_existentes = list(
        db.query(
            __import__("app.models.usuario", fromlist=["Usuario"]).Usuario
        ).filter(
            __import__("app.models.usuario", fromlist=["Usuario"]).Usuario.rol.in_(
                ["docente", "profesor", "profesor_directivo"]
            )
        ).all()
    )

    # ── Iterar comisiones ─────────────────────────────────────────────────────
    for nombre_com, datos in COMISIONES_1ANO.items():
        print(f"\n── Comisión {nombre_com} ({datos['turno']}) — Aula {datos['aula']} ──")

        comision, created = get_or_create(
            db, Comision,
            defaults={},
            nombre=nombre_com,
            periodo_id=periodo.id,
        )
        log(created, f"Comisión {nombre_com}")

        for cod_mat, (horario, docentes) in datos["materias"].items():
            if cod_mat not in materias:
                print(f"  ⚠️  Materia {cod_mat} no encontrada, saltando.")
                continue

            mat = materias[cod_mat]

            # Crear / actualizar cursada
            cursada, created = get_or_create(
                db, Cursada,
                defaults={
                    "aula":      datos["aula"],
                    "horario":   horario,
                    "modalidad": ModalidadEnum.presencial,
                },
                materia_id=mat.id,
                comision_id=comision.id,
                periodo_id=periodo.id,
            )
            # Siempre actualizar horario por si cambió
            if cursada.horario != horario:
                cursada.horario = horario
            log(created, f"{cod_mat} — {mat.nombre}")

            # Asignar docentes
            for nombre_doc in docentes:
                prof = crear_profesor(
                    db, nombre_doc, profesores_existentes, RolEnum.docente
                )
                get_or_create(
                    db, CursadaProfesor,
                    defaults={},
                    cursada_id=cursada.id,
                    profesor_id=prof.id,
                )

    db.commit()
    print("\n✅ seed_03 completada.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error en seed_03: {e}")
        raise
    finally:
        db.close()
