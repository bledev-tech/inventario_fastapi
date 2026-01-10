"""Allow uso to use the same locacion as destino.

Revision ID: 20260109_allow_uso_same_locacion
Revises: 
Create Date: 2026-01-09 19:10:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260109_allow_uso_same_locacion"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("chk_mov_uso", "movimientos", type_="check")
    op.execute(
        "ALTER TABLE movimientos "
        "ADD CONSTRAINT chk_mov_uso "
        "CHECK ((tipo <> 'uso') OR (from_locacion_id IS NOT NULL))"
    )


def downgrade() -> None:
    op.drop_constraint("chk_mov_uso", "movimientos", type_="check")
    op.execute(
        "ALTER TABLE movimientos "
        "ADD CONSTRAINT chk_mov_uso "
        "CHECK ((tipo <> 'uso') OR (from_locacion_id IS NOT NULL "
        "AND (to_locacion_id IS NULL OR to_locacion_id <> from_locacion_id)))"
    )
