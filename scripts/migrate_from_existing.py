"""
Migrate data from three source apps into surtax-oversight-pro unified database.

Sources:
  - contract-oversight-system/data/contracts.db (296 contracts, 10 vendors, core tables)
  - florida-school-surtax-oversight/data/surtax.db (county_benchmarks supplement)
  - surtax-oversight-dashboard/data/contracts.db (project_phases, inspections, actions, etc.)

Target:
  - surtax-oversight-pro/data/surtax_pro.db
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime

# Paths
BASE = Path(__file__).resolve().parent.parent.parent
SRC_CONTRACT = BASE / 'contract-oversight-system' / 'data' / 'contracts.db'
SRC_SURTAX = BASE / 'florida-school-surtax-oversight' / 'data' / 'surtax.db'
SRC_DASHBOARD = BASE / 'surtax-oversight-dashboard' / 'data' / 'contracts.db'
TARGET = Path(__file__).resolve().parent.parent / 'data' / 'surtax_pro.db'

# Column mapping: source → target for contracts
CONTRACT_COL_MAP = {
    'contract_id': 'contract_id',
    'contract_number': 'contract_number',
    'title': 'title',
    'description': 'description',
    'contract_type': 'type',
    'vendor_id': 'vendor_id',
    'vendor_name': 'vendor_name',
    'original_amount': 'original_amount',
    'current_amount': 'current_amount',
    'total_paid': 'total_paid',
    'remaining_balance': 'remaining_balance',
    'solicitation_date': 'solicitation_date',
    'award_date': 'award_date',
    'start_date': 'start_date',
    'original_end_date': 'original_end_date',
    'current_end_date': 'current_end_date',
    'actual_end_date': 'actual_end_date',
    'status': 'status',
    'phase': 'phase',
    'percent_complete': 'percent_complete',
    'performance_score': 'performance_score',
    'cost_variance_score': 'cost_variance_score',
    'schedule_variance_score': 'schedule_variance_score',
    'compliance_score': 'compliance_score',
    'overall_health_score': 'overall_health_score',
    'risk_level': 'risk_level',
    'procurement_method': 'procurement_method',
    'bid_count': 'bid_count',
    'is_sole_source': 'is_sole_source',
    'justification': 'justification',
    'board_approval_date': 'board_approval_date',
    'requires_insurance': 'requires_insurance',
    'insurance_verified': 'insurance_verified',
    'requires_bond': 'requires_bond',
    'bond_verified': 'bond_verified',
    'project_location': 'project_location',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'council_district': 'council_district',
    'change_order_count': 'change_order_count',
    'total_change_order_amount': 'total_change_order_amount',
    'school_name': 'school_name',
    'school_id': 'school_id',
    'surtax_category': 'surtax_category',
    'expenditure_type': 'expenditure_type',
    'is_delayed': 'is_delayed',
    'delay_days': 'delay_days',
    'delay_reason': 'delay_reason',
    'is_over_budget': 'is_over_budget',
    'budget_variance_amount': 'budget_variance_amount',
    'budget_variance_pct': 'budget_variance_pct',
    'cost_per_sqft': 'cost_per_sqft',
    'community_impact': 'community_impact',
    'project_purpose': 'purpose',
    'project_scope': 'scope',
    'created_by': 'created_by',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'is_deleted': 'is_deleted',
    'is_emergency': 'is_emergency',
    'notes': 'notes',
}


def connect(path):
    """Connect to a SQLite database with Row factory."""
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def get_source_columns(conn, table):
    """Get column names for a table."""
    return [c[1] for c in conn.execute(f'PRAGMA table_info([{table}])').fetchall()]


def migrate_contracts(src, dst):
    """Migrate contracts from source to target with column mapping."""
    src_cols = get_source_columns(src, 'contracts')
    rows = src.execute('SELECT * FROM contracts').fetchall()

    # Build insert statement from mapping
    target_cols = []
    src_indices = []
    for src_col, tgt_col in CONTRACT_COL_MAP.items():
        if src_col in src_cols:
            target_cols.append(tgt_col)
            src_indices.append(src_cols.index(src_col))

    placeholders = ', '.join(['?'] * len(target_cols))
    cols_str = ', '.join(target_cols)

    dst.execute('DELETE FROM contracts')
    inserted = 0
    for row in rows:
        values = [row[i] for i in src_indices]
        dst.execute(f'INSERT OR REPLACE INTO contracts ({cols_str}) VALUES ({placeholders})', values)
        inserted += 1

    return inserted


def migrate_vendors(src, dst):
    """Migrate vendors with column mapping."""
    src_cols = get_source_columns(src, 'vendors')
    rows = src.execute('SELECT * FROM vendors').fetchall()

    # Map source vendor columns to target
    col_map = {
        'vendor_id': 'vendor_id',
        'vendor_name': 'name',
        'vendor_type': 'vendor_type',
        'contact_name': 'contact_name',
        'contact_email': 'email',
        'contact_phone': 'phone',
        'address': 'address',
        'city': 'city',
        'state': 'state',
        'zip_code': 'zip_code',
        'vendor_size': 'vendor_size',
        'headquarters_city': 'headquarters_city',
        'headquarters_state': 'headquarters_state',
        'tax_id': 'tax_id',
        'registration_date': 'registration_date',
        'status': 'status',
        'performance_score': 'performance_score',
        'total_contracts': 'total_contracts',
        'total_awarded': 'total_awarded',
        'minority_owned': 'minority_owned',
        'woman_owned': 'woman_owned',
        'small_business': 'small_business',
        'local_business': 'local_business',
        'years_in_business': 'years_in_business',
        'bonding_capacity': 'bonding_capacity',
        'certifications': 'certifications',
        'license_number': 'license_number',
        'insurance_expiry': 'insurance_expiry',
        'notes': 'notes',
    }

    target_cols = []
    src_indices = []
    for src_col, tgt_col in col_map.items():
        if src_col in src_cols:
            target_cols.append(tgt_col)
            src_indices.append(src_cols.index(src_col))

    placeholders = ', '.join(['?'] * len(target_cols))
    cols_str = ', '.join(target_cols)

    dst.execute('DELETE FROM vendors')
    inserted = 0
    for row in rows:
        values = [row[i] for i in src_indices]
        dst.execute(f'INSERT OR REPLACE INTO vendors ({cols_str}) VALUES ({placeholders})', values)
        inserted += 1
    return inserted


def migrate_simple_table(src, dst, table, col_map=None):
    """Migrate a table with optional column mapping, or direct copy if columns match."""
    src_cols = get_source_columns(src, table)
    dst_cols = get_source_columns(dst, table)
    rows = src.execute(f'SELECT * FROM [{table}]').fetchall()

    if not rows:
        return 0

    if col_map:
        target_cols = []
        src_indices = []
        for src_col, tgt_col in col_map.items():
            if src_col in src_cols and tgt_col in dst_cols:
                target_cols.append(tgt_col)
                src_indices.append(src_cols.index(src_col))
    else:
        # Direct match: use columns that exist in both
        common = [c for c in src_cols if c in dst_cols]
        target_cols = common
        src_indices = [src_cols.index(c) for c in common]

    if not target_cols:
        return 0

    placeholders = ', '.join(['?'] * len(target_cols))
    cols_str = ', '.join(target_cols)

    dst.execute(f'DELETE FROM [{table}]')
    inserted = 0
    for row in rows:
        values = [row[i] for i in src_indices]
        try:
            dst.execute(f'INSERT OR REPLACE INTO [{table}] ({cols_str}) VALUES ({placeholders})', values)
            inserted += 1
        except sqlite3.IntegrityError as e:
            print(f'  SKIP {table} row: {e}')
    return inserted


def migrate_dashboard_tables(src, dst):
    """Migrate dashboard-specific tables that have unique data."""
    results = {}

    # project_phases: src has (id, contract_id, phase_name, start_date, end_date, status, percent_complete, data_source, ...)
    # target has (phase_id, contract_id, phase_name, phase_order, start_date, end_date, status, percent_complete, notes)
    phase_map = {
        'contract_id': 'contract_id',
        'phase_name': 'phase_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'status': 'status',
        'percent_complete': 'percent_complete',
    }
    results['project_phases'] = migrate_simple_table(src, dst, 'project_phases', phase_map)

    # inspection_log: src has (id, contract_id, inspection_date, inspector_name, findings, deficiencies_count, status, ...)
    # target has (inspection_id, contract_id, inspection_date, inspector_name, inspection_type, findings, deficiency_count, status, ...)
    insp_map = {
        'contract_id': 'contract_id',
        'inspection_date': 'inspection_date',
        'inspector_name': 'inspector_name',
        'findings': 'findings',
        'deficiencies_count': 'deficiency_count',
        'status': 'status',
    }
    results['inspection_log'] = migrate_simple_table(src, dst, 'inspection_log', insp_map)

    # committee_actions: src has (id, contract_id, meeting_date, action_item, assigned_to, status, due_date, ...)
    # target has (action_id, contract_id, action_item, assignee, due_date, status, priority, created_date, ...)
    action_map = {
        'contract_id': 'contract_id',
        'action_item': 'action_item',
        'assigned_to': 'assignee',
        'due_date': 'due_date',
        'status': 'status',
        'meeting_date': 'created_date',
    }
    results['committee_actions'] = migrate_simple_table(src, dst, 'committee_actions', action_map)

    # community_engagement: src has (id, contract_id, meeting_date, attendees, feedback_summary, concerns_raised, ...)
    # target has (engagement_id, contract_id, meeting_date, attendee_count, feedback_summary, concerns_raised, location)
    engage_map = {
        'contract_id': 'contract_id',
        'meeting_date': 'meeting_date',
        'feedback_summary': 'feedback_summary',
        'concerns_raised': 'concerns_raised',
    }
    results['community_engagement'] = migrate_simple_table(src, dst, 'community_engagement', engage_map)

    # contractor_performance: src uses vendor_id, target requires contract_id
    # Map vendor_id to a contract_id via contracts table
    rows = src.execute('SELECT * FROM contractor_performance').fetchall()
    dst.execute('DELETE FROM contractor_performance')
    inserted = 0
    for row in rows:
        row_dict = dict(row)
        vendor_id = row_dict.get('vendor_id', '')
        # Find first contract for this vendor
        c_row = dst.execute('SELECT contract_id FROM contracts WHERE vendor_id = ? LIMIT 1', (vendor_id,)).fetchone()
        contract_id = c_row[0] if c_row else f'UNKNOWN-{vendor_id}'
        try:
            dst.execute('''
                INSERT INTO contractor_performance (contract_id, vendor_name, safety_record, quality_score,
                    past_projects, deficiency_rate, local_hiring_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract_id,
                vendor_id,
                row_dict.get('safety_record', 'Good'),
                row_dict.get('quality_score', 0),
                row_dict.get('past_projects_count', 0),
                row_dict.get('deficiency_rate', 0),
                row_dict.get('local_hiring_percent', 0),
            ))
            inserted += 1
        except Exception as e:
            print(f'  SKIP contractor_performance row: {e}')
    results['contractor_performance'] = inserted

    return results


def migrate_issues_to_concerns(src, dst):
    """Migrate issues table to concerns table."""
    rows = src.execute('SELECT * FROM issues').fetchall()
    dst.execute('DELETE FROM concerns')
    inserted = 0
    for row in rows:
        row_dict = dict(row)
        try:
            dst.execute('''
                INSERT INTO concerns (concern_id, contract_id, title, description,
                    category, severity, status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row_dict.get('issue_id'),
                row_dict.get('contract_id'),
                row_dict.get('title'),
                row_dict.get('description'),
                row_dict.get('issue_type', 'Other'),
                row_dict.get('severity', 'Medium'),
                row_dict.get('status', 'Open'),
                row_dict.get('created_at'),
            ))
            inserted += 1
        except Exception as e:
            print(f'  SKIP concern row: {e}')
    return inserted


def main():
    print("=" * 60)
    print("Surtax Oversight Pro - Data Migration")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    # Verify source files
    for name, path in [('contract-oversight', SRC_CONTRACT), ('florida-surtax', SRC_SURTAX),
                        ('surtax-dashboard', SRC_DASHBOARD)]:
        if not path.exists():
            print(f"ERROR: Source DB not found: {path}")
            sys.exit(1)
        print(f"Source [{name}]: {path}")

    if not TARGET.exists():
        print(f"\nERROR: Target DB not found: {TARGET}")
        print("Run 'python scripts/init_db.py' first to create the schema.")
        sys.exit(1)

    print(f"Target: {TARGET}")

    # Use surtax-dashboard as primary source (most data)
    src_main = connect(SRC_DASHBOARD)
    src_surtax = connect(SRC_SURTAX)
    dst = connect(TARGET)

    print("\n--- Migrating contracts (from surtax-dashboard) ---")
    n = migrate_contracts(src_main, dst)
    print(f"  Contracts: {n} rows")

    print("\n--- Migrating vendors ---")
    n = migrate_vendors(src_main, dst)
    print(f"  Vendors: {n} rows")

    print("\n--- Migrating shared tables ---")
    for table in ['change_orders', 'milestones', 'audit_log', 'county_fiscal_data']:
        n = migrate_simple_table(src_main, dst, table)
        print(f"  {table}: {n} rows")

    # Counties: source has county_name, target has name
    counties_map = {
        'county_id': 'county_id',
        'county_name': 'name',
        'state': 'state',
        'population': 'population',
    }
    n = migrate_simple_table(src_main, dst, 'counties', counties_map)
    print(f"  counties: {n} rows")

    print("\n--- Migrating issues to concerns ---")
    n = migrate_issues_to_concerns(src_main, dst)
    print(f"  concerns: {n} rows")

    print("\n--- Migrating dashboard-specific tables ---")
    results = migrate_dashboard_tables(src_main, dst)
    for table, count in results.items():
        print(f"  {table}: {count} rows")

    print("\n--- Migrating county_benchmarks (from florida-surtax) ---")
    # county_benchmarks exist in florida-surtax but not in target schema
    # Skip this - the benchmarking engine uses its own in-memory data
    rows = src_surtax.execute('SELECT COUNT(*) FROM county_benchmarks').fetchone()[0]
    print(f"  county_benchmarks: {rows} rows (skipped - not in target schema)")

    # Commit
    dst.commit()
    print("\n--- Migration complete! ---")

    # Verify
    print("\n--- Verification ---")
    for table in ['contracts', 'vendors', 'change_orders', 'milestones', 'concerns',
                   'audit_log', 'counties', 'county_fiscal_data',
                   'project_phases', 'inspection_log', 'committee_actions',
                   'community_engagement', 'contractor_performance']:
        count = dst.execute(f'SELECT COUNT(*) FROM [{table}]').fetchone()[0]
        print(f"  {table}: {count} rows")

    src_main.close()
    src_surtax.close()
    dst.close()


if __name__ == '__main__':
    main()
