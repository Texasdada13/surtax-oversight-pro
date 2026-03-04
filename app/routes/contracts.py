"""General contract management routes."""

from flask import Blueprint, render_template, request, g
from app.database import get_db

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')


@contracts_bp.route('/')
def dashboard():
    """Contract management dashboard."""
    from app.services.stats import get_all_contract_stats

    db = get_db()
    cursor = db.cursor()
    stats = get_all_contract_stats(cursor)

    # Spending by type (contracts with vs without surtax category)
    cursor.execute('''
        SELECT
            CASE WHEN surtax_category IS NOT NULL THEN 'Surtax Capital' ELSE 'General' END as contract_type,
            COUNT(*) as count,
            COALESCE(SUM(current_amount), 0) as total_budget,
            COALESCE(SUM(total_paid), 0) as total_spent
        FROM contracts WHERE is_deleted = 0
        GROUP BY contract_type
        ORDER BY total_budget DESC
    ''')
    by_type = [dict(row) for row in cursor.fetchall()]

    # Risk distribution
    cursor.execute('''
        SELECT risk_level, COUNT(*) as count
        FROM contracts WHERE is_deleted = 0
        GROUP BY risk_level
        ORDER BY CASE risk_level
            WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3 WHEN 'Low' THEN 4 ELSE 5 END
    ''')
    risk_dist = [dict(row) for row in cursor.fetchall()]

    # Top contracts by budget
    cursor.execute('''
        SELECT contract_id, title, vendor_name, current_amount, total_paid,
               percent_complete, status, risk_level, overall_health_score,
               surtax_category, school_name
        FROM contracts WHERE is_deleted = 0
        ORDER BY current_amount DESC LIMIT 10
    ''')
    top_contracts = [dict(row) for row in cursor.fetchall()]

    # Recent concerns
    cursor.execute('''
        SELECT contract_id, title, vendor_name, current_amount,
               is_delayed, delay_days, is_over_budget, budget_variance_pct,
               risk_level
        FROM contracts
        WHERE is_deleted = 0 AND (is_delayed = 1 OR is_over_budget = 1)
        ORDER BY overall_health_score ASC LIMIT 5
    ''')
    recent_concerns = [dict(row) for row in cursor.fetchall()]

    return render_template('contracts/dashboard.html',
                          title='Contract Dashboard',
                          stats=stats,
                          by_type=by_type,
                          risk_dist=risk_dist,
                          top_contracts=top_contracts,
                          recent_concerns=recent_concerns)


@contracts_bp.route('/executive')
def executive():
    """Executive contract dashboard with analytics."""
    from app.services.stats import get_all_contract_stats

    db = get_db()
    cursor = db.cursor()
    stats = get_all_contract_stats(cursor)

    # Vendor performance summary
    cursor.execute('''
        SELECT vendor_name,
               COUNT(*) as contract_count,
               COALESCE(SUM(current_amount), 0) as total_value,
               AVG(overall_health_score) as avg_health,
               SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count
        FROM contracts WHERE is_deleted = 0 AND vendor_name IS NOT NULL
        GROUP BY vendor_name
        ORDER BY total_value DESC
    ''')
    vendor_summary = [dict(row) for row in cursor.fetchall()]

    # Status breakdown
    cursor.execute('''
        SELECT status, COUNT(*) as count,
               COALESCE(SUM(current_amount), 0) as total_value
        FROM contracts WHERE is_deleted = 0
        GROUP BY status
    ''')
    status_breakdown = [dict(row) for row in cursor.fetchall()]

    # Monthly spending trend (approximate from start dates)
    cursor.execute('''
        SELECT strftime('%Y-%m', start_date) as month,
               COUNT(*) as contracts_started,
               COALESCE(SUM(current_amount), 0) as value_started
        FROM contracts WHERE is_deleted = 0 AND start_date IS NOT NULL
        GROUP BY month ORDER BY month DESC LIMIT 12
    ''')
    monthly_trend = [dict(row) for row in cursor.fetchall()]
    monthly_trend.reverse()

    return render_template('contracts/executive_dashboard.html',
                          title='Executive Dashboard',
                          stats=stats,
                          vendor_summary=vendor_summary,
                          status_breakdown=status_breakdown,
                          monthly_trend=monthly_trend)


@contracts_bp.route('/list')
def contract_list():
    """List all contracts."""
    db = get_db()
    cursor = db.cursor()

    # Get filter params
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')  # 'surtax' or 'general'
    risk_filter = request.args.get('risk', '')
    sort_by = request.args.get('sort', 'title')
    search = request.args.get('q', '')

    query = '''
        SELECT contract_id, title, vendor_name, current_amount, total_paid,
               percent_complete, status, risk_level, overall_health_score,
               surtax_category, school_name, is_delayed, delay_days,
               is_over_budget, budget_variance_pct, start_date, current_end_date
        FROM contracts WHERE is_deleted = 0
    '''
    params = []

    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    if type_filter == 'surtax':
        query += ' AND surtax_category IS NOT NULL'
    elif type_filter == 'general':
        query += ' AND surtax_category IS NULL'
    if risk_filter:
        query += ' AND risk_level = ?'
        params.append(risk_filter)
    if search:
        query += ' AND (title LIKE ? OR vendor_name LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    sort_map = {
        'title': 'title ASC',
        'budget': 'current_amount DESC',
        'progress': 'percent_complete DESC',
        'health': 'overall_health_score ASC',
        'vendor': 'vendor_name ASC',
        'status': 'status ASC',
    }
    query += f' ORDER BY {sort_map.get(sort_by, "title ASC")}'

    cursor.execute(query, params)
    contracts = [dict(row) for row in cursor.fetchall()]

    return render_template('contracts/contracts.html',
                          title='All Contracts',
                          contracts=contracts,
                          current_status=status_filter,
                          current_type=type_filter,
                          current_risk=risk_filter,
                          current_sort=sort_by,
                          current_search=search)


@contracts_bp.route('/<contract_id>')
def contract_detail(contract_id):
    """Contract detail view."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM contracts WHERE contract_id = ? AND is_deleted = 0', (contract_id,))
    contract = cursor.fetchone()

    if not contract:
        return render_template('errors/404.html', title='Contract Not Found'), 404

    contract = dict(contract)

    # Change orders
    cursor.execute('SELECT * FROM change_orders WHERE contract_id = ? ORDER BY requested_date DESC', (contract_id,))
    change_orders = [dict(row) for row in cursor.fetchall()]

    # Milestones
    cursor.execute('SELECT * FROM milestones WHERE contract_id = ? ORDER BY planned_date', (contract_id,))
    milestones = [dict(row) for row in cursor.fetchall()]

    # Payments
    cursor.execute('SELECT * FROM payments WHERE contract_id = ? ORDER BY payment_date DESC', (contract_id,))
    payments = [dict(row) for row in cursor.fetchall()]

    # If it's a surtax project, also get phases and inspections
    phases = []
    inspections = []
    if contract.get('surtax_category'):
        cursor.execute('SELECT * FROM project_phases WHERE contract_id = ? ORDER BY phase_order', (contract_id,))
        phases = [dict(row) for row in cursor.fetchall()]
        cursor.execute('SELECT * FROM inspection_log WHERE contract_id = ? ORDER BY inspection_date DESC', (contract_id,))
        inspections = [dict(row) for row in cursor.fetchall()]

    return render_template('contracts/contract_detail.html',
                          title=contract['title'],
                          contract=contract,
                          change_orders=change_orders,
                          milestones=milestones,
                          payments=payments,
                          phases=phases,
                          inspections=inspections)


@contracts_bp.route('/vendors')
def vendors():
    """Vendor directory."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT v.*,
               COUNT(c.contract_id) as active_contracts,
               COALESCE(SUM(c.current_amount), 0) as total_contract_value,
               AVG(c.overall_health_score) as avg_project_health
        FROM vendors v
        LEFT JOIN contracts c ON v.name = c.vendor_name AND c.is_deleted = 0
        GROUP BY v.vendor_id
        ORDER BY total_contract_value DESC
    ''')
    vendors_list = [dict(row) for row in cursor.fetchall()]

    return render_template('contracts/vendors.html',
                          title='Vendors',
                          vendors=vendors_list)


@contracts_bp.route('/vendors/<vendor_id>')
def vendor_detail(vendor_id):
    """Vendor detail view."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM vendors WHERE vendor_id = ?', (vendor_id,))
    vendor = cursor.fetchone()

    if not vendor:
        return render_template('errors/404.html', title='Vendor Not Found'), 404

    vendor = dict(vendor)

    # Get vendor's contracts
    cursor.execute('''
        SELECT contract_id, title, current_amount, total_paid, percent_complete,
               status, risk_level, overall_health_score, surtax_category, school_name,
               start_date, current_end_date
        FROM contracts
        WHERE vendor_name = ? AND is_deleted = 0
        ORDER BY current_amount DESC
    ''', (vendor['name'],))
    contracts = [dict(row) for row in cursor.fetchall()]

    # Summary stats
    cursor.execute('''
        SELECT COUNT(*) as total_contracts,
               COALESCE(SUM(current_amount), 0) as total_value,
               COALESCE(SUM(total_paid), 0) as total_paid,
               AVG(percent_complete) as avg_completion,
               AVG(overall_health_score) as avg_health,
               SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
               SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count
        FROM contracts WHERE vendor_name = ? AND is_deleted = 0
    ''', (vendor['name'],))
    stats = dict(cursor.fetchone())

    return render_template('contracts/vendor_detail.html',
                          title=vendor['name'],
                          vendor=vendor,
                          contracts=contracts,
                          stats=stats)
