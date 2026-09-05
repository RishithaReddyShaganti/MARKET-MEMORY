from alembic.config import Config
from alembic.script import ScriptDirectory


def test_initial_migration_is_available() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    revisions = list(script.walk_revisions())

    assert len(revisions) == 1
    assert revisions[0].revision == "20260904_0001"
