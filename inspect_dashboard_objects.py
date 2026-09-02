from db import get_engine
from sqlalchemy import text

engine = get_engine()

sql = """
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema IN (
    'public',
    'stock_dashboard',
    'research'
)
ORDER BY
    table_schema,
    table_name;
"""

with engine.connect() as conn:

    result = conn.execute(text(sql))

    print()
    print("=" * 100)
    print("DATABASE TABLE / VIEW INVENTORY")
    print("=" * 100)

    for row in result:
        print(
            f"{row.table_schema:20} "
            f"{row.table_name:40} "
            f"{row.table_type}"
        )

print()
print("CHECK COMPLETE")
