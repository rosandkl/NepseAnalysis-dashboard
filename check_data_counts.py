from db import get_engine
from sqlalchemy import text

print("Connecting to database...")

engine = get_engine()

with engine.connect() as conn:

    print("Connected.")
    print()

    print("Counting Daily rows...")
    daily_rows = conn.execute(
        text("SELECT COUNT(*) FROM public.daily")
    ).scalar()

    print("Counting Daily dates...")
    daily_dates = conn.execute(
        text("SELECT COUNT(DISTINCT tdate) FROM public.daily")
    ).scalar()

    print("Counting Floorsheet rows...")
    floorsheet_rows = conn.execute(
        text("SELECT COUNT(*) FROM public.floorsheet")
    ).scalar()

    print("Counting Floorsheet dates...")
    floorsheet_dates = conn.execute(
        text("SELECT COUNT(DISTINCT tdate) FROM public.floorsheet")
    ).scalar()


print()
print("=" * 70)
print("DATABASE DATA COVERAGE")
print("=" * 70)
print(f"Daily Rows          : {daily_rows:,}")
print(f"Daily Trading Dates : {daily_dates:,}")
print()
print(f"Floorsheet Rows     : {floorsheet_rows:,}")
print(f"Floorsheet Dates    : {floorsheet_dates:,}")
print("=" * 70)
