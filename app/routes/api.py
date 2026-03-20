"""API routes - JSON endpoints for AJAX, persona/view switching, data export."""

import csv
import io
from flask import Blueprint, jsonify, request, session, Response
from app.database import get_db, get_cursor

api_bp = Blueprint('api', __name__)


@api_bp.route('/set-persona', methods=['POST'])
def set_persona():
    """Switch user persona."""
    from config.personas import PERSONAS
    data = request.get_json() or {}
    persona = data.get('persona', 'committee')
    if persona in PERSONAS:
        session['persona'] = persona
    return jsonify({'success': True, 'persona': session.get('persona')})


@api_bp.route('/set-view-mode', methods=['POST'])
def set_view_mode():
    """Switch view mode (surtax/contracts)."""
    from config.personas import VIEW_MODES
    data = request.get_json() or {}
    view_mode = data.get('view_mode', 'surtax')
    if view_mode in VIEW_MODES:
        session['view_mode'] = view_mode
    return jsonify({'success': True, 'view_mode': session.get('view_mode')})


@api_bp.route('/ask', methods=['POST'])
def ask():
    """Process AI question via Claude API."""
    from app.services.ai_chat import ask_claude

    data = request.get_json() or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    db = get_db()
    cursor = get_cursor(db)
    result = ask_claude(question, cursor)
    return jsonify(result)


@api_bp.route('/stats')
def stats():
    """Summary stats for sidebar/dashboard."""
    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('''
        SELECT
            COUNT(*) as total_projects,
            SUM(current_amount) as total_budget,
            SUM(total_paid) as total_spent,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count
        FROM contracts WHERE is_deleted = 0
    ''')
    row = cursor.fetchone()
    return jsonify(dict(row) if row else {
        'total_projects': 0, 'total_budget': 0, 'total_spent': 0,
        'delayed_count': 0, 'over_budget_count': 0
    })


@api_bp.route('/watchlist/projects')
def watchlist_projects():
    """Return project data for given contract_ids (used by client-side watchlist)."""
    ids = request.args.get('ids', '')
    if not ids:
        return jsonify([])

    contract_ids = [i.strip() for i in ids.split(',') if i.strip()]
    if not contract_ids:
        return jsonify([])

    db = get_db()
    cursor = get_cursor(db)
    placeholders = ','.join(['%s'] * len(contract_ids))
    cursor.execute(f'''
        SELECT contract_id, title, vendor_name, surtax_category, school_name,
               status, current_amount, total_paid, percent_complete,
               overall_health_score, risk_level, is_delayed, delay_days,
               is_over_budget, budget_variance_pct
        FROM contracts
        WHERE is_deleted = 0 AND contract_id IN ({placeholders})
        ORDER BY overall_health_score ASC
    ''', contract_ids)
    projects = [dict(row) for row in cursor.fetchall()]
    return jsonify(projects)


@api_bp.route('/export/contracts')
def export_contracts():
    """Export contracts to CSV."""
    db = get_db()
    cursor = get_cursor(db)

    surtax_only = request.args.get('surtax', '0') == '1'
    where = "WHERE is_deleted = 0"
    if surtax_only:
        where += " AND surtax_category IS NOT NULL"

    cursor.execute(f'''
        SELECT contract_id, title, vendor_name, surtax_category, school_name,
               status, original_amount, current_amount, total_paid,
               percent_complete, overall_health_score,
               start_date, is_delayed, is_over_budget
        FROM contracts {where}
        ORDER BY current_amount DESC
    ''')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row[col] for col in columns])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=contracts_export.csv'}
    )


@api_bp.route('/export/vendors')
def export_vendors():
    """Export vendor performance to CSV."""
    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('''
        SELECT v.name, v.headquarters_city, v.headquarters_state, v.vendor_size,
               COUNT(c.contract_id) as contract_count,
               SUM(c.current_amount) as total_value,
               SUM(c.total_paid) as total_paid,
               AVG(c.overall_health_score) as avg_health,
               SUM(CASE WHEN c.is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
               SUM(CASE WHEN c.is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count
        FROM vendors v
        LEFT JOIN contracts c ON v.vendor_id = c.vendor_id AND c.is_deleted = 0
        GROUP BY v.vendor_id, v.name, v.headquarters_city, v.headquarters_state, v.vendor_size
        HAVING COUNT(c.contract_id) > 0
        ORDER BY total_value DESC
    ''')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row[col] for col in columns])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=vendors_export.csv'}
    )


@api_bp.route('/export/change-orders')
def export_change_orders():
    """Export change orders to CSV."""
    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('''
        SELECT c.title as contract_title, co.description, co.change_value,
               co.status, co.requested_date, co.approved_date, co.reason
        FROM change_orders co
        JOIN contracts c ON co.contract_id = c.contract_id
        WHERE c.is_deleted = 0
        ORDER BY co.requested_date DESC
    ''')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row[col] for col in columns])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=change_orders_export.csv'}
    )
