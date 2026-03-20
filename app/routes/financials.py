"""Financial routes - budget, analytics, benchmarking."""

from flask import Blueprint, render_template, request
from app.database import get_db, get_cursor
from app.services.executive_analytics import ExecutiveAnalytics
from app.services.benchmarking import get_benchmarking_engine
from app.services.ai_insights import get_ai_insights

financials_bp = Blueprint('financials', __name__, url_prefix='/financials')


@financials_bp.route('/')
def home():
    """Financial summary — county CAFR revenue/expenditure overview."""
    # Demo CAFR data (would come from a cafr_data table in production)
    revenue_sources = [
        {'name': 'Ad Valorem Taxes', 'amount': 412500000},
        {'name': 'Sales Surtax (Half-Cent)', 'amount': 98700000},
        {'name': 'State Revenue Sharing', 'amount': 67300000},
        {'name': 'Intergovernmental Revenue', 'amount': 54200000},
        {'name': 'Charges for Services', 'amount': 42100000},
        {'name': 'Special Assessments', 'amount': 31800000},
        {'name': 'Licenses & Permits', 'amount': 28500000},
        {'name': 'Investment Earnings', 'amount': 18900000},
        {'name': 'Fines & Forfeitures', 'amount': 12400000},
        {'name': 'Miscellaneous Revenue', 'amount': 8600000},
    ]
    expenditure_categories = [
        {'name': 'Instruction & Education', 'amount': 285000000},
        {'name': 'Capital Outlay & Construction', 'amount': 178500000},
        {'name': 'General Government Services', 'amount': 98700000},
        {'name': 'Financial & Administrative', 'amount': 67200000},
        {'name': 'Student Transportation', 'amount': 45300000},
        {'name': 'Maintenance & Operations', 'amount': 38100000},
        {'name': 'Debt Service', 'amount': 32600000},
        {'name': 'Technology Services', 'amount': 24800000},
        {'name': 'Safety & Security', 'amount': 18200000},
        {'name': 'Community Services', 'amount': 12500000},
    ]
    revenue_by_fund = [
        {'fund': 'General Fund', 'amount': 425000000, 'pct': 55.0},
        {'fund': 'Special Revenue', 'amount': 148000000, 'pct': 19.2},
        {'fund': 'Capital Projects', 'amount': 112000000, 'pct': 14.5},
        {'fund': 'Debt Service', 'amount': 52000000, 'pct': 6.7},
        {'fund': 'Enterprise Fund', 'amount': 35000000, 'pct': 4.6},
    ]
    expenditure_by_fund = [
        {'fund': 'General Fund', 'amount': 398000000, 'pct': 49.6},
        {'fund': 'Special Revenue', 'amount': 142000000, 'pct': 17.7},
        {'fund': 'Capital Projects', 'amount': 155000000, 'pct': 19.3},
        {'fund': 'Debt Service', 'amount': 58000000, 'pct': 7.2},
        {'fund': 'Enterprise Fund', 'amount': 49900000, 'pct': 6.2},
    ]

    total_revenue = sum(r['amount'] for r in revenue_sources)
    total_expenditure = sum(e['amount'] for e in expenditure_categories)
    net_position = total_revenue - total_expenditure
    budget_health = round(min((total_revenue / total_expenditure * 100), 100), 1) if total_expenditure else 100

    return render_template('financials/financials.html',
                           title='Financial Summary',
                           revenue_sources=revenue_sources,
                           expenditure_categories=expenditure_categories,
                           revenue_by_fund=revenue_by_fund,
                           expenditure_by_fund=expenditure_by_fund,
                           total_revenue=total_revenue,
                           total_expenditure=total_expenditure,
                           net_position=net_position,
                           budget_health=budget_health)


@financials_bp.route('/analytics')
def analytics():
    """Executive analytics with EVM forecasting."""
    db = get_db()
    cursor = get_cursor(db)

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

    # Risk distribution
    risk_dist = {'High': 0, 'Medium': 0, 'Low': 0}
    for c in contracts:
        cat = c['analytics'].get('risk_category', 'Low')
        risk_dist[cat] = risk_dist.get(cat, 0) + 1

    # Portfolio health by category
    cursor.execute('''
        SELECT surtax_category, COUNT(*) as count,
               AVG(overall_health_score) as avg_health,
               SUM(current_amount) as budget
        FROM contracts
        WHERE is_deleted = 0 AND status = 'Active' AND surtax_category IS NOT NULL
        GROUP BY surtax_category ORDER BY budget DESC
    ''')
    category_health = [dict(row) for row in cursor.fetchall()]

    return render_template('financials/analytics.html',
                           title='Executive Analytics',
                           contracts=contracts,
                           exec_summary=exec_summary,
                           total_budget=total_budget,
                           total_forecast=total_forecast,
                           forecast_variance=forecast_variance,
                           over_budget=over_budget[:10],
                           risk_dist=risk_dist,
                           category_health=category_health)


@financials_bp.route('/benchmarking')
def benchmarking():
    """Coupa 2025 benchmark comparison."""
    engine = get_benchmarking_engine()
    benchmark_summary = engine.get_benchmark_summary()

    # Generate sample KPI values from our data
    db = get_db()
    cursor = get_cursor(db)

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
    """Change order tracking — contract-level view."""
    db = get_db()
    cursor = get_cursor(db)

    # Individual change orders (for detail reference)
    cursor.execute('''
        SELECT co.*, c.title as contract_title, c.contract_id as cid
        FROM change_orders co
        JOIN contracts c ON co.contract_id = c.contract_id
        WHERE c.is_deleted = 0
        ORDER BY co.requested_date DESC
    ''')
    orders = [dict(row) for row in cursor.fetchall()]

    # Contract-level aggregated view
    cursor.execute('''
        SELECT c.contract_id, c.title, c.vendor_name, c.original_amount, c.current_amount,
               c.surtax_category, c.status as contract_status,
               COUNT(co.change_order_id) as change_count,
               SUM(co.change_value) as net_change,
               SUM(CASE WHEN co.change_value > 0 THEN 1 ELSE 0 END) as increases,
               SUM(CASE WHEN co.change_value < 0 THEN 1 ELSE 0 END) as decreases
        FROM contracts c
        JOIN change_orders co ON c.contract_id = co.contract_id
        WHERE c.is_deleted = 0
        GROUP BY c.contract_id, c.title, c.vendor_name, c.original_amount,
                 c.current_amount, c.surtax_category, c.status
        ORDER BY ABS(SUM(co.change_value)) DESC
    ''')
    contract_changes = [dict(row) for row in cursor.fetchall()]
    for cc in contract_changes:
        orig = cc.get('original_amount') or 0
        cc['pct_change'] = round(((cc.get('net_change') or 0) / orig * 100), 1) if orig > 0 else 0

    # Summary stats
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(co.change_value) as total_amount,
            SUM(CASE WHEN co.change_value > 0 THEN 1 ELSE 0 END) as budget_increases,
            SUM(CASE WHEN co.change_value < 0 THEN 1 ELSE 0 END) as budget_decreases,
            SUM(CASE WHEN co.status = 'Approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN co.status = 'Pending' THEN 1 ELSE 0 END) as pending
        FROM change_orders co
        JOIN contracts c ON co.contract_id = c.contract_id
        WHERE c.is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    return render_template('financials/change_orders.html',
                           title='Change Orders',
                           orders=orders,
                           contract_changes=contract_changes,
                           stats=stats)


@financials_bp.route('/vendors')
def vendors():
    """Vendor performance dashboard with KPIs and tiers."""
    db = get_db()
    cursor = get_cursor(db)

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
        GROUP BY v.vendor_id, v.name, v.dba_name, v.contact_name, v.email,
                 v.phone, v.address, v.city, v.state, v.zip_code, v.vendor_type,
                 v.vendor_size, v.headquarters_city, v.headquarters_state, v.tax_id,
                 v.registration_date, v.status, v.performance_score, v.total_contracts,
                 v.total_awarded, v.minority_owned, v.woman_owned, v.small_business,
                 v.local_business, v.years_in_business, v.bonding_capacity,
                 v.certifications, v.license_number, v.insurance_expiry, v.notes
        ORDER BY total_value DESC
    ''')
    vendors_list = [dict(row) for row in cursor.fetchall()]

    # Compute performance tiers
    for v in vendors_list:
        health = v.get('avg_health') or 0
        delayed = v.get('delayed_count') or 0
        over_budget = v.get('over_budget_count') or 0
        if health >= 75 and delayed == 0 and over_budget == 0:
            v['tier'] = 'Excellent'
        elif health >= 60 and delayed <= 1:
            v['tier'] = 'Good'
        elif health >= 40:
            v['tier'] = 'Fair'
        else:
            v['tier'] = 'At Risk'

    # Summary stats
    active_vendors = [v for v in vendors_list if v.get('contract_count', 0) > 0]
    vendor_summary = {
        'total': len(vendors_list),
        'active': len(active_vendors),
        'total_value': sum(v.get('total_value', 0) or 0 for v in vendors_list),
        'avg_health': sum(v.get('avg_health', 0) or 0 for v in active_vendors) / max(len(active_vendors), 1),
        'excellent': sum(1 for v in vendors_list if v.get('tier') == 'Excellent'),
        'good': sum(1 for v in vendors_list if v.get('tier') == 'Good'),
        'fair': sum(1 for v in vendors_list if v.get('tier') == 'Fair'),
        'at_risk': sum(1 for v in vendors_list if v.get('tier') == 'At Risk'),
        'with_delays': sum(1 for v in vendors_list if (v.get('delayed_count') or 0) > 0),
        'with_overruns': sum(1 for v in vendors_list if (v.get('over_budget_count') or 0) > 0),
    }

    return render_template('financials/vendors.html',
                           title='Vendor Performance Dashboard',
                           vendors=vendors_list,
                           summary=vendor_summary)
