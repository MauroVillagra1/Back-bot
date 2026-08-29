"""
seed_01_periodos_materias.py
Crea los períodos académicos 2026 y el catálogo completo de materias
del Plan 2023 de Ingeniería en Sistemas.
Idempotente: correrlo dos veces no duplica nada.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date

from app.core.database import SessionLocal
from app.models.academico import DuracionEnum, Materia, PeriodoAcademico, TipoPeriodoEnum
from seeds.seed_utils import get_or_create, log


# ── Catálogo de materias ──────────────────────────────────────────────────────
# (codigo, nombre, duracion)
MATERIAS = [
    # 1º año — todas anuales
    ("P23-AM1",  "Análisis Matemático I",                        DuracionEnum.anual),
    ("P23-AGA",  "Álgebra y Geometría Analítica",                DuracionEnum.anual),
    ("P23-AED",  "Algoritmos y Estructuras de Datos",            DuracionEnum.anual),
    ("P23-AC",   "Arquitectura de Computadoras",                 DuracionEnum.anual),
    ("P23-F1",   "Física I",                                     DuracionEnum.anual),
    ("P23-LED",  "Lógica y Estructuras Discretas",               DuracionEnum.anual),
    ("P23-SPN",  "Sistemas y Procesos de Negocio",               DuracionEnum.anual),
    ("P23-IS",   "Ingeniería y Sociedad",                        DuracionEnum.anual),
    # 2º año — todas anuales
    ("P23-AM2",  "Análisis Matemático II",                       DuracionEnum.anual),
    ("P23-F2",   "Física II",                                    DuracionEnum.anual),
    ("P23-PP",   "Paradigmas de Programación",                   DuracionEnum.anual),
    ("P23-SO",   "Sistemas Operativos",                          DuracionEnum.anual),
    ("P23-SSL",  "Sintaxis y Semántica de los Lenguajes",        DuracionEnum.anual),
    ("P23-ASI",  "Análisis de Sistemas de Información",          DuracionEnum.anual),
    # 3º año — todas cuatrimestrales
    ("P23-ECO",  "Economía",                                     DuracionEnum.cuatrimestral),
    ("P23-CD",   "Comunicación de Datos",                        DuracionEnum.cuatrimestral),
    ("P23-AN",   "Análisis Numérico",                            DuracionEnum.cuatrimestral),
    ("P23-DS",   "Desarrollo de Software",                       DuracionEnum.cuatrimestral),
    ("P23-DSI",  "Diseño de Sistemas de Información",            DuracionEnum.cuatrimestral),
    ("P23-SI",   "Seguridad Informática",                        DuracionEnum.cuatrimestral),
    ("P23-UXD",  "Diseño UX para Productos Digitales",           DuracionEnum.cuatrimestral),
    ("P23-UXUI", "Fundamentos del Diseño UX/UI",                 DuracionEnum.cuatrimestral),
    ("P23-SEM",  "Seminario Integrador",                         DuracionEnum.cuatrimestral),
    # 4º año — todas cuatrimestrales
    ("P23-RD",    "Redes de Datos",                              DuracionEnum.cuatrimestral),
    ("P23-ICS",   "Ingeniería y Calidad de Software",            DuracionEnum.cuatrimestral),
    ("P23-TA",    "Tecnologías para la Automatización",          DuracionEnum.cuatrimestral),
    ("P23-ADSI",  "Administración de Sistemas de Información",   DuracionEnum.cuatrimestral),
    ("P23-CLOUD", "Computación en la Nube",                      DuracionEnum.cuatrimestral),
    ("P23-AGOH",  "Algoritmos Genéticos y Optimización Heurística", DuracionEnum.cuatrimestral),
    ("P23-SGC",   "Sistemas de Gestión de la Calidad",           DuracionEnum.cuatrimestral),
    ("P23-SIG",   "Sistemas de Información Geográfica",          DuracionEnum.cuatrimestral),
    ("P23-SRI",   "Seguridad en Redes e Infraestructura",        DuracionEnum.cuatrimestral),
    ("P23-PAD",   "Programación de Aplicaciones Distribuidas",   DuracionEnum.cuatrimestral),
    ("P23-FID",   "Fundamentos de Ingeniería de Datos",          DuracionEnum.cuatrimestral),
]


def seed(db) -> dict:
    print("\n── Períodos académicos ──────────────────────────────────────────────")

    periodo_anual, created = get_or_create(
        db, PeriodoAcademico,
        defaults={
            "tipo":        TipoPeriodoEnum.anual,
            "fecha_inicio": date(2026, 3, 16),
            "fecha_fin":    date(2026, 12, 11),
        },
        nombre="Ciclo Lectivo Anual 2026",
    )
    log(created, "Ciclo Lectivo Anual 2026")

    periodo_2c, created = get_or_create(
        db, PeriodoAcademico,
        defaults={
            "tipo":        TipoPeriodoEnum.segundo_cuatrimestre,
            "fecha_inicio": date(2026, 8, 3),
            "fecha_fin":    date(2026, 12, 11),
        },
        nombre="2do Cuatrimestre 2026",
    )
    log(created, "2do Cuatrimestre 2026")

    print("\n── Materias ─────────────────────────────────────────────────────────")
    for codigo, nombre, duracion in MATERIAS:
        _, created = get_or_create(
            db, Materia,
            defaults={"nombre": nombre, "duracion": duracion},
            codigo=codigo,
        )
        log(created, f"{codigo} — {nombre}")

    db.commit()
    print("\n✅ seed_01 completada.")
    return {"periodo_anual": periodo_anual, "periodo_2c": periodo_2c}


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error en seed_01: {e}")
        raise
    finally:
        db.close()
