from db import get_engine
from sqlalchemy import text

engine = get_engine()

sql = """
SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name IN (
    'company_name',
    'security_master',
    'stock_screener'
)
ORDER BY
    table_schema,
    table_name,
    ordinal_position;
"""

with engine.connect() as conn:
    result = conn.execute(text(sql))

    print("\nCOLUMN STRUCTURE")
    print("=" * 100)

    for row in result:
        print(row)
