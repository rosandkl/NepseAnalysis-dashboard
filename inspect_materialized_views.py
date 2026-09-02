from db import get_engine
from sqlalchemy import text

engine = get_engine()

sql = """
SELECT
    schemaname,
    matviewname,
    ispopulated
FROM pg_matviews
ORDER BY
    schemaname,
    matviewname;
"""

with engine.connect() as conn:

    result = conn.execute(text(sql))

    print()
    print("=" * 100)
    print("MATERIALIZED VIEWS")
    print("=" * 100)

    rows = result.fetchall()

    if not rows:
        print("No materialized views found.")
    else:
        for row in rows:
            print(row)

print()
print("CHECK COMPLETE")
