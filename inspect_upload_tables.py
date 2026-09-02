from db import get_engine
from sqlalchemy import text

engine = get_engine()

tables = ["daily", "floorsheet"]

with engine.connect() as conn:

    for table in tables:

        print()
        print("=" * 100)
        print(f"TABLE: public.{table}")
        print("=" * 100)

        sql = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = :table
        ORDER BY ordinal_position
        """

        result = conn.execute(
            text(sql),
            {"table": table},
        )

        for row in result:
            print(row)

        print()
        print("-" * 100)
        print("CONSTRAINTS")
        print("-" * 100)

        constraint_sql = """
        SELECT
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name = :table
        ORDER BY
            tc.constraint_type,
            tc.constraint_name,
            kcu.ordinal_position
        """

        result = conn.execute(
            text(constraint_sql),
            {"table": table},
        )

        for row in result:
            print(row)

        print()
        print("-" * 100)
        print("SAMPLE ROWS")
        print("-" * 100)

        try:

            sample_sql = text(
                f"SELECT * FROM public.{table} LIMIT 3"
            )

            result = conn.execute(sample_sql)

            for row in result:
                print(row)

        except Exception as exc:
            print(f"Could not read sample rows: {exc}")

print()
print("=" * 100)
print("INSPECTION COMPLETE")
print("=" * 100)
