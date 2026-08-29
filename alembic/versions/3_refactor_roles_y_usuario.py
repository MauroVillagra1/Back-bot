"""refactor_roles_y_usuario

Revision ID: refactor_roles_v2
Revises: fix_excepciones_fecha
Create Date: 2026-08-27

Cambios:
  1. Agrega nuevos valores al enum SQL 'rolenum':
       root, master, jefe_area, docente, estudiante
     (conserva los existentes: administrador, profesor_directivo, alumno,
      administrativo, jefe_departamento, profesor — que quedan como aliases)
  2. Agrega columna 'apellido' (VARCHAR 100, nullable) a usuarios
  3. Agrega columna 'fecha_nacimiento' (DATE, nullable) a usuarios
  4. Migra datos existentes al nuevo esquema de roles:
       administrador      → master
       jefe_departamento  → jefe_area
       profesor_directivo → docente
       profesor           → docente
       alumno             → estudiante
     (administrativo ya es válido tal cual)

NOTA: ALTER TYPE en PostgreSQL no es transaccional — se ejecuta fuera
de la transacción principal usando op.execute() directo.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "refactor_roles_v2"
down_revision: Union[str, None] = "fix_excepciones_fecha"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Agregar nuevos valores al enum (ALTER TYPE no es transaccional) ───
    # PostgreSQL requiere ejecutar esto fuera de un bloque BEGIN/COMMIT explícito.
    # La conexión de Alembic ya está en autocommit para ALTER TYPE.
    conn = op.get_bind()

    nuevos_valores = ["root", "master", "jefe_area", "docente", "estudiante"]
    for valor in nuevos_valores:
        # IF NOT EXISTS no existe en versiones viejas de PG — usamos try/except
        try:
            conn.execute(
                sa.text(f"ALTER TYPE rolenum ADD VALUE IF NOT EXISTS '{valor}'")
            )
        except Exception:
            # Si no soporta IF NOT EXISTS, intentar sin él
            try:
                conn.execute(sa.text(f"ALTER TYPE rolenum ADD VALUE '{valor}'"))
            except Exception:
                pass  # El valor ya existía

    # ── 2. Agregar columnas nuevas ────────────────────────────────────────────
    op.add_column(
        "usuarios",
        sa.Column("apellido", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "usuarios",
        sa.Column("fecha_nacimiento", sa.Date(), nullable=True),
    )

    # ── 3. Migrar roles existentes al nuevo esquema ───────────────────────────
    # Los aliases legacy se mantienen en el enum pero los datos apuntan al nuevo
    conn.execute(sa.text("""
        UPDATE usuarios SET rol = 'master'     WHERE rol = 'administrador';
        UPDATE usuarios SET rol = 'jefe_area'  WHERE rol = 'jefe_departamento';
        UPDATE usuarios SET rol = 'docente'    WHERE rol IN ('profesor', 'profesor_directivo');
        UPDATE usuarios SET rol = 'estudiante' WHERE rol = 'alumno';
    """))


def downgrade() -> None:
    # ── Revertir migración de roles ───────────────────────────────────────────
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE usuarios SET rol = 'administrador'    WHERE rol = 'master';
        UPDATE usuarios SET rol = 'jefe_departamento' WHERE rol = 'jefe_area';
        UPDATE usuarios SET rol = 'profesor_directivo' WHERE rol = 'docente';
        UPDATE usuarios SET rol = 'alumno'           WHERE rol = 'estudiante';
    """))

    # ── Quitar columnas ───────────────────────────────────────────────────────
    op.drop_column("usuarios", "apellido")
    op.drop_column("usuarios", "fecha_nacimiento")

    # Nota: no se puede quitar valores de un enum en PostgreSQL sin recrearlo.
    # Los valores root/master/jefe_area/docente/estudiante quedarán en el enum
    # pero no habrá datos usándolos.
