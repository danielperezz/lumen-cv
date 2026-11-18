from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text

PREVIOUS_REVISION = "20260506_0001"


def document_column(engine: Engine) -> dict | None:
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT data_type, is_nullable, column_default FROM information_schema.columns "
                    "WHERE table_name = 'profiles' AND column_name = 'document'"
                )
            )
            .mappings()
            .first()
        )
    return dict(row) if row else None


def test_downgrade_removes_document_and_upgrade_restores_it(engine: Engine, alembic_config: Config) -> None:
    try:
        command.downgrade(alembic_config, "-1")

        with engine.connect() as connection:
            version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert version == PREVIOUS_REVISION
        assert document_column(engine) is None

        command.upgrade(alembic_config, "head")

        assert document_column(engine) == {
            "data_type": "jsonb",
            "is_nullable": "NO",
            "column_default": "'{}'::jsonb",
        }
    finally:
        command.upgrade(alembic_config, "head")
