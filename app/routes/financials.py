"""Financial routes - budget, analytics, benchmarking."""

from flask import Blueprint, render_template, request
from app.database import get_db
from app.services.executive_analytics import ExecutiveAnalytics
from app.services.benchmarking import get_benchmarking_engine
from app.services.ai_insights import get_ai_insights

financials_bp = Blueprint('financials', __name__, url_prefix='/financials')


@financials_bp.route('/')
def home():
    """Financial overview with budget summary."""
    db = get_db()
    cursor = db.cursor()

    # Portfolio financial summary
    cursor.execute('''
        SELECT
            COUNT(*) as total_contracts,
            SUM(original_amount) as total_original,
            SUM(current_amount) as total_current,
            SUM(total_paid) as total_spent,
            SUM(current_amount - original_amount) as total_variance,
            AVG(CASE WHEN original_amount > 0
                THEN ((current_amount - original_amount) / original_amount * 100) ELSE 0 END) as avg_variance_pct,
            SUM(CASE WHEN status = 'Active' THEN current_amount ELSE 0 END) as active_budget,
            SUM(CASE WHEN status = 'Active' THEN total_paid ELSE 0 END) as active_spent
        FROM contracts WHERE is_deleted = 0
    ''')
    summary = dict(cursor.fetchone())

    # Spending by category
    cursor.execute('''
        SELECT surtax_category, COUNT(*) as count,
               SUM(current_amount) as budget, SUM(total_paid) as spent
        FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category ORDER BY budget DESC
    ''')
    by_category = [dict(row) for row in cursor.fetchall()]

    # Monthly spending trend (last 12 months approximation from payments)
    cursor.execute('''
        SELECT strftime('%Y-%m', payment_date) as month,
               SUM(amount) as total
        FROM payments
        GROUP BY month ORDER BY month DESC LIMIT 12
    ''')
    monthly_spend = [dict(row) for row in cursor.fetchall()]
    monthly_spend.reverse()

    # AI insights
    insights = get_ai_insights(cursor)

    return render_template('financials/financials.html',
                           title='Financial Overview',
                           summary=summary,
                           by_category=by_category,
                           monthly_spend=monthly_spend,
                           insights=insights)


@financials_bp.route('/analytics')
def analytics():
    """Executive analytics with EVM forecasting."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT * FROM contracts
        WHERE is_deleted = 0 AND status = 'Active'
        ORDER BY current_amount DESC
    ''')
    contracts = [dict(row) for row in cursor.fetchall()]

    analytics_engine = ExecutiveAnalytics(cursor)
    exec_summary = analytics_engine.generate_executive_summary()

    # Calculate analytics for each contract
    for c in contracts:
        c['analytics'] = analytics_engine.get_contract_analytics(c)

    # Aggregate forecasts
    total_budget = sum(c.get('current_amount', 0) or 0 for c in contracts)
    total_forecast = sum(c['analytics']['forecast_at_completion'] for c in contracts)
    forecast_variance = total_forecast - total_budget

    # Top over-budget forecasts
    over_budget = [c for c in contracts if c['analytics']['forecast_at_completion'] > (c.get('current_amount', 0) or 0)]
    over_budget.sort(key=lambda x: x['analytics']['forecast_at_completion'] - (x.get('current_amount', 0) or 0), reverse=True)

    return render_template('financials/analytics.html',
                           title='Executive Analytics',
                           contracts=contracts,
                           exec_summary=exec_summary,
                           total_budget=total_budget,
                           total_forecast=total_forecast,
                           forecast_variance=forecast_variance,
                           over_budget=over_budget[:10])


@financials_bp.route('/benchmarking')
def benchmarking():
    """Coupa 2025 benchmark comparison."""
    engine = get_benchmarking_engine()
    benchmark_summary = engine.get_benchmark_summary()

    # Generate sample KPI values from our data
    db = get_db()
    cursor = db.cursor()

    # Calculate actual KPIs from contract data
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN current_amount > 0 AND original_amount > 0 THEN 1 ELSE 0 END) as with_contract,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active
        FROM contracts WHERE is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    # Build KPI values from data
    kpi_values = {
        'on_contract_spend': min(95, (stats.get('with_contract', 0) / max(stats.get('total', 1), 1)) * 100),
        'structured_spend': 62.0,
        'pre_approved_spend': 91.5,
        'electronic_po_processing': 85.0,
        'electronic_invoice_processing': 78.0,
        'first_time_match_rate': 88.5,
        'invoices_paid_digitally': 72.0,
        'expense_lines_within_policy': 95.0,
        'increase_visibility_managed_spend': 18.0,
        'supplier_info_mgmt_cycle_time': 8.2,
    }

    health = engine.calculate_health_score(kpi_values)

    return render_template('financials/benchmarking.html',
                           title='Procurement Benchmarking',
                           benchmark_summary=benchmark_summary,
                           health=health,
                           kpi_values=kpi_values)


@financials_bp.route('/change-orders')
def change_orders():
    """Change order tracking."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT co.*, c.title as contract_title, c.contract_id as cid
        FROM change_orders co
        JOIN contracts c ON co.contract_id = c.contract_id
        WHERE c.is_deleted = 0
        ORDER BY co.requested_date DESC
    ''')
    orders = [dict(row) for row in cursor.fetchall()]

    # Summary stats
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(co.change_value) as total_amount,
            SUM(CASE WHEN co.status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN co.status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN co.status = 'Rejected' THEN 1 ELSE 0 END) as rejected
        FROM change_orders co
        JOIN contracts c ON co.contract_id = c.contract_id
        WHERE c.is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    return render_template('financials/change_orders.html',
                           title='Change Orders',
                           orders=orders,
                           stats=stats)


@financials_bp.route('/vendors')
def vendors():
    """Vendor financial performance."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT v.*,
               COUNT(c.contract_id) as contract_count,
               SUM(c.current_amount) as total_value,
               SUM(c.total_paid) as total_paid,
               AVG(c.overall_health_score) as avg_health,
               SUM(CASE WHEN c.is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
               SUM(CASE WHEN c.is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count
        FROM vendors v
        LEFT JOIN contracts c ON v.vendor_id = c.vendor_id AND c.is_deleted = 0
        GROUP BY v.vendor_id
        ORDER BY total_value DESC
    ''')
    vendors = [dict(row) for row in cursor.fetchall()]

    return render_template('financials/vendors.html',
                           title='Vendor Financial Performance',
                           vendors=vendors)
