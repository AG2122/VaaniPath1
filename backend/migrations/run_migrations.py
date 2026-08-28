"""VaniPath - Apply Supabase Migrations

Reads .env for DATABASE_URL, connects to PostgreSQL,
executes both migration files, and verifies results.
"""
import os
import sys
import time

# Ensure we're in the backend directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(".env")

import psycopg2


def run_sql_file(conn, filepath, label):
    """Execute a SQL file and report results."""
    print(f"\n{'='*60}")
    print(f"  Applying: {label}")
    print(f"  File:     {filepath}")
    print(f"{'='*60}")

    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()

    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print(f"  [OK] {label} applied successfully")
        return True
    except Exception as e:
        conn.rollback()
        print(f"  [ERROR] {label} failed: {e}")
        return False
    finally:
        cur.close()


def verify_tables(conn):
    """Count and list all tables in the public schema."""
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    return tables


def verify_indexes(conn):
    """Count non-system indexes."""
    cur = conn.cursor()
    cur.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND indexname LIKE 'idx_%'
        ORDER BY indexname
    """)
    indexes = [row[0] for row in cur.fetchall()]
    cur.close()
    return indexes


def verify_storage_buckets(conn):
    """Check storage buckets."""
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, public, file_size_limit
            FROM storage.buckets
            WHERE id LIKE 'vanipath-%'
            ORDER BY id
        """)
        buckets = cur.fetchall()
        cur.close()
        return buckets
    except Exception:
        cur.close()
        return []


def verify_rls(conn):
    """Check RLS is enabled on tables."""
    cur = conn.cursor()
    cur.execute("""
        SELECT c.relname, c.relrowsecurity
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND c.relrowsecurity = true
        ORDER BY c.relname
    """)
    rls_tables = [row[0] for row in cur.fetchall()]
    cur.close()
    return rls_tables


def main():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("[ERROR] DATABASE_URL not set in .env")
        sys.exit(1)
    if not db_url.startswith(("postgresql://", "postgresql+psycopg2://", "postgres://")):
        print(f"[ERROR] DATABASE_URL is not PostgreSQL (starts with: {db_url.split('://')[0]})")
        sys.exit(1)

    # Mask credentials for display
    masked = db_url.split("@")[-1] if "@" in db_url else "(local)"
    print(f"[INFO] Connecting to PostgreSQL: {masked}")

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)

    print("[OK] Connected to Supabase PostgreSQL")

    # Apply migrations
    base = os.path.dirname(os.path.abspath(__file__))
    schema_ok = run_sql_file(conn, os.path.join(base, "001_supabase_schema.sql"), "Schema Migration")
    storage_ok = run_sql_file(conn, os.path.join(base, "002_supabase_storage.sql"), "Storage Migration")

    # Verify
    print(f"\n{'='*60}")
    print(f"  VERIFICATION")
    print(f"{'='*60}")

    tables = verify_tables(conn)
    print(f"\n  Tables created: {len(tables)}")
    for t in tables:
        print(f"    - {t}")

    indexes = verify_indexes(conn)
    print(f"\n  Indexes created: {len(indexes)}")

    rls_tables = verify_rls(conn)
    print(f"\n  RLS enabled on: {len(rls_tables)} tables")

    buckets = verify_storage_buckets(conn)
    print(f"\n  Storage buckets: {len(buckets)}")
    for b in buckets:
        bid, name, public, limit = b
        pub_str = "public" if public else "private"
        print(f"    - {name} ({pub_str}, {limit // 1024 // 1024}MB)")

    conn.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"  MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Schema migration:    {'SUCCESS' if schema_ok else 'FAILED'}")
    print(f"  Storage migration:   {'SUCCESS' if storage_ok else 'FAILED'}")
    print(f"  Tables:              {len(tables)}")
    print(f"  Indexes:             {len(indexes)}")
    print(f"  RLS tables:          {len(rls_tables)}")
    print(f"  Storage buckets:     {len(buckets)}")
    print(f"{'='*60}")

    if not schema_ok or not storage_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
