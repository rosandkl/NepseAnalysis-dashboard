from db import get_engine
from sqlalchemy import text

engine = get_engine()

sql = """
SELECT
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.table_name IN (
    'company_name',
    'security_master',
    'stock_screener'
)
ORDER BY
    tc.table_schema,
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name,
    kcu.ordinal_position;
"""

with engine.connect() as conn:
    result = conn.execute(text(sql))

    print("\nCONSTRAINT STRUCTURE")
    print("=" * 100)

    for row in result:
        print(row)
