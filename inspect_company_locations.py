from db import get_engine
from sqlalchemy import text

engine = get_engine()

sql = """
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_name IN (
    'company_name',
    'security_master',
    'stock_screener'
)
ORDER BY table_schema, table_name;
"""

with engine.connect() as conn:
    result = conn.execute(text(sql))

    print("\nTABLE LOCATIONS")
    print("=" * 100)

    for row in result:
        print(row)
