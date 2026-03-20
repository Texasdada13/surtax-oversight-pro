"""Document management routes."""

from flask import Blueprint, render_template, request
from app.database import get_db, get_cursor

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


@documents_bp.route('/')
def home():
    """Document library."""
    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('''
        SELECT d.*, c.title as contract_title
        FROM documents d
        LEFT JOIN contracts c ON d.contract_id = c.contract_id
        WHERE d.is_deleted = 0
        ORDER BY d.uploaded_date DESC
    ''')
    docs = [dict(row) for row in cursor.fetchall()]

    # Group by type
    doc_types = {}
    for d in docs:
        dtype = d.get('document_type', 'Other')
        if dtype not in doc_types:
            doc_types[dtype] = []
        doc_types[dtype].append(d)

    return render_template('documents/documents.html',
                           title='Documents',
                           documents=docs,
                           doc_types=doc_types,
                           total=len(docs))


@documents_bp.route('/minutes')
def minutes():
    """Meeting minutes."""
    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('''
        SELECT * FROM meeting_minutes
        ORDER BY meeting_date DESC
    ''')
    meetings = [dict(row) for row in cursor.fetchall()]

    return render_template('documents/meeting_minutes.html',
                           title='Meeting Minutes',
                           meetings=meetings)


@documents_bp.route('/report')
def report():
    """Annual report with portfolio summary."""
    db = get_db()
    cursor = get_cursor(db)

    # Portfolio stats
    cursor.execute('''
        SELECT
            COUNT(*) as total_contracts,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as completed,
            SUM(original_amount) as total_original,
            SUM(current_amount) as total_current,
            SUM(total_paid) as total_spent,
            AVG(overall_health_score) as avg_health,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget
        FROM contracts WHERE is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    # By category
    cursor.execute('''
        SELECT surtax_category, COUNT(*) as count, SUM(current_amount) as budget,
               SUM(total_paid) as spent, AVG(overall_health_score) as avg_health
        FROM contracts WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category ORDER BY budget DESC
    ''')
    categories = [dict(row) for row in cursor.fetchall()]

    # Top vendors
    cursor.execute('''
        SELECT vendor_name, COUNT(*) as contracts, SUM(current_amount) as total_value
        FROM contracts WHERE is_deleted = 0 AND vendor_name IS NOT NULL
        GROUP BY vendor_name ORDER BY total_value DESC LIMIT 10
    ''')
    top_vendors = [dict(row) for row in cursor.fetchall()]

    # Major projects (top 10 by budget)
    cursor.execute('''
        SELECT contract_id, title, school_name, current_amount, percent_complete, status
        FROM contracts WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        ORDER BY current_amount DESC LIMIT 10
    ''')
    major_projects = [dict(row) for row in cursor.fetchall()]

    # Issues: delayed and over-budget
    cursor.execute('''
        SELECT title, is_delayed, delay_days, is_over_budget, budget_variance_pct, vendor_name
        FROM contracts
        WHERE is_deleted = 0 AND (is_delayed = 1 OR is_over_budget = 1)
        ORDER BY overall_health_score ASC
    ''')
    issues = [dict(row) for row in cursor.fetchall()]

    # On-track count
    on_track = (stats.get('total_contracts', 0) or 0) - (stats.get('delayed', 0) or 0) - (stats.get('over_budget', 0) or 0)
    spend_pct = round(((stats.get('total_spent', 0) or 0) / (stats.get('total_current', 1) or 1)) * 100, 1)

    return render_template('documents/annual_report.html',
                           title='Annual Report',
                           stats=stats,
                           categories=categories,
                           top_vendors=top_vendors,
                           major_projects=major_projects,
                           issues=issues,
                           on_track=on_track,
                           spend_pct=spend_pct)
