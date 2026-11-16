import logging
from sqlalchemy import inspect, text
from app.core.database import engine, Base

logger = logging.getLogger("architect_ai.migrate")

def auto_migrate():
    """
    Automatically inspects existing database tables and adds any missing columns
    declared in SQLAlchemy models. This ensures SQLite schemas stay in sync
    without requiring manual migrations or losing existing records.
    """
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        with engine.begin() as conn:
            for table in Base.metadata.sorted_tables:
                if table.name in existing_tables:
                    existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
                    for col in table.columns:
                        if col.name not in existing_cols:
                            # Compile column type for the target dialect (e.g. SQLite)
                            col_type = col.type.compile(engine.dialect)
                            default_clause = ""
                            
                            # For SQLite, ADD COLUMN with NOT NULL requires a DEFAULT value
                            if col.default is not None and col.default.arg is not None and not callable(col.default.arg):
                                val = col.default.arg
                                default_clause = f" DEFAULT '{val}'"
                            elif not col.nullable:
                                type_str = str(col_type).lower()
                                if "int" in type_str or "float" in type_str:
                                    default_clause = " DEFAULT 0"
                                elif "bool" in type_str:
                                    default_clause = " DEFAULT 0"
                                else:
                                    default_clause = " DEFAULT ''"

                            alter_sql = f"ALTER TABLE {table.name} ADD COLUMN {col.name} {col_type}{default_clause}"
                            print(f"[AutoMigrate] Applying schema update: {alter_sql}")
                            conn.execute(text(alter_sql))
    except Exception as e:
        print(f"[AutoMigrate] Error during schema auto-migration: {e}")
