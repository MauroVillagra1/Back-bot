"""crear_tabla_info_cursada

Revision ID: crear_info_cursada
Revises: refactor_roles_v2
Create Date: 2026-08-27

Crea la tabla info_cursada que existía en el modelo pero nunca tuvo migración.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "crear_info_cursada"
down_revision: Union[str, None] = "refactor_roles_v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "info_cursada",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cursada_id", sa.Integer(), nullable=False),
        sa.Column("condiciones_aprobacion", sa.Text(), nullable=True),
        sa.Column("cantidad_parciales", sa.Integer(), nullable=True),
        sa.Column("tiene_tfi", sa.Boolean(), nullable=True),
        sa.Column("descripcion_tfi", sa.Text(), nullable=True),
        sa.Column("modalidad_cursado", sa.String(length=200), nullable=True),
        sa.Column("info_adicional", sa.Text(), nullable=True),
        sa.Column("cargado_por", sa.Integer(), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["cargado_por"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["cursada_id"], ["cursadas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cursada_id", name="uq_info_cursada"),
    )
    op.create_index(op.f("ix_info_cursada_cursada_id"), "info_cursada", ["cursada_id"], unique=False)
    op.create_index(op.f("ix_info_cursada_id"), "info_cursada", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_info_cursada_id"), table_name="info_cursada")
    op.drop_index(op.f("ix_info_cursada_cursada_id"), table_name="info_cursada")
    op.drop_table("info_cursada")
