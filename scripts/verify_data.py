"""
Verify data integrity after migration.
Checks row counts, referential integrity, and data quality.
"""

import sqlite3
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / 'data' / 'surtax_pro.db'


def main():
    if not TARGET.exists():
        print(f"ERROR: Database not found: {TARGET}")
        sys.exit(1)

    conn = sqlite3.connect(str(TARGET))
    conn.row_factory = sqlite3.Row
    errors = 0
    warnings = 0

    print("=" * 60)
    print("Data Verification Report")
    print("=" * 60)

    # 1. Row counts
    print("\n1. Row Counts")
    expected = {
        'contracts': (250, 300),
        'vendors': (8, 15),
        'change_orders': (1, 50),
        'milestones': (1, 50),
        'concerns': (1, 50),
        'audit_log': (1, 100),
        'counties': (3, 10),
        'county_fiscal_data': (5, 50),
        'project_phases': (100, 500),
        'inspection_log': (50, 300),
        'committee_actions': (50, 300),
        'community_engagement': (50, 200),
        'contractor_performance': (1, 50),
    }
    for table, (min_rows, max_rows) in expected.items():
        count = conn.execute(f'SELECT COUNT(*) FROM [{table}]').fetchone()[0]
        status = 'OK' if min_rows <= count <= max_rows else 'WARN'
        if status == 'WARN':
            warnings += 1
        print(f"   {status:4s} {table}: {count} rows (expected {min_rows}-{max_rows})")

    # 2. Referential integrity
    print("\n2. Referential Integrity")
    checks = [
        ("change_orders -> contracts",
         "SELECT COUNT(*) FROM change_orders co WHERE co.contract_id NOT IN (SELECT contract_id FROM contracts)"),
        ("milestones -> contracts",
         "SELECT COUNT(*) FROM milestones m WHERE m.contract_id NOT IN (SELECT contract_id FROM contracts)"),
        ("project_phases -> contracts",
         "SELECT COUNT(*) FROM project_phases p WHERE p.contract_id NOT IN (SELECT contract_id FROM contracts)"),
        ("inspection_log -> contracts",
         "SELECT COUNT(*) FROM inspection_log i WHERE i.contract_id NOT IN (SELECT contract_id FROM contracts)"),
        ("concerns -> contracts",
         "SELECT COUNT(*) FROM concerns c WHERE c.contract_id IS NOT NULL AND c.contract_id NOT IN (SELECT contract_id FROM contracts)"),
    ]
    for name, query in checks:
        orphans = conn.execute(query).fetchone()[0]
        status = 'OK' if orphans == 0 else 'FAIL'
        if status == 'FAIL':
            errors += 1
        print(f"   {status:4s} {name}: {orphans} orphan records")

    # 3. Data quality
    print("\n3. Data Quality")

    # Contracts with titles
    no_title = conn.execute("SELECT COUNT(*) FROM contracts WHERE title IS NULL OR title = ''").fetchone()[0]
    print(f"   {'OK' if no_title == 0 else 'WARN':4s} Contracts without title: {no_title}")
    if no_title > 0:
        warnings += 1

    # Contracts with amounts
    no_amount = conn.execute("SELECT COUNT(*) FROM contracts WHERE current_amount IS NULL OR current_amount = 0").fetchone()[0]
    print(f"   {'OK' if no_amount < 10 else 'WARN':4s} Contracts without budget: {no_amount}")

    # Contracts with health scores
    no_health = conn.execute("SELECT COUNT(*) FROM contracts WHERE overall_health_score IS NULL").fetchone()[0]
    print(f"   {'OK' if no_health < 50 else 'WARN':4s} Contracts without health score: {no_health}")

    # Active contracts
    active = conn.execute("SELECT COUNT(*) FROM contracts WHERE status = 'Active'").fetchone()[0]
    print(f"   {'OK' if active > 0 else 'WARN':4s} Active contracts: {active}")

    # Surtax contracts
    surtax = conn.execute("SELECT COUNT(*) FROM contracts WHERE surtax_category IS NOT NULL").fetchone()[0]
    print(f"   {'OK' if surtax > 0 else 'WARN':4s} Surtax-categorized contracts: {surtax}")

    # Vendors with names
    no_name = conn.execute("SELECT COUNT(*) FROM vendors WHERE name IS NULL OR name = ''").fetchone()[0]
    print(f"   {'OK' if no_name == 0 else 'WARN':4s} Vendors without name: {no_name}")

    # 4. Financial sanity
    print("\n4. Financial Sanity")
    row = conn.execute('''
        SELECT SUM(original_amount) as orig, SUM(current_amount) as curr,
               SUM(total_paid) as paid
        FROM contracts WHERE is_deleted = 0
    ''').fetchone()
    orig, curr, paid = row['orig'] or 0, row['curr'] or 0, row['paid'] or 0
    print(f"   Total original: ${orig:,.0f}")
    print(f"   Total current:  ${curr:,.0f}")
    print(f"   Total paid:     ${paid:,.0f}")
    if paid > curr * 1.5:
        print("   WARN: Total paid exceeds 150% of current budget")
        warnings += 1
    else:
        print("   OK   Paid within budget bounds")

    # 5. Summary
    print(f"\n{'=' * 60}")
    print(f"Results: {errors} errors, {warnings} warnings")
    if errors == 0:
        print("PASS - Data migration verified successfully!")
    else:
        print("FAIL - Please review errors above")
    print("=" * 60)

    conn.close()
    sys.exit(1 if errors > 0 else 0)


if __name__ == '__main__':
    main()
