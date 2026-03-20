"""Surtax-specific routes for school capital outlay project oversight."""

from flask import Blueprint, render_template, g, request

surtax_bp = Blueprint('surtax', __name__, url_prefix='/surtax')


@surtax_bp.route('/')
def overview():
    """Surtax overview dashboard - persona-aware."""
    from app.utils.persona_helpers import get_overview_template_for_persona
    from app.database import get_db, get_cursor
    from app.services.stats import get_overview_stats, get_spending_by_category, get_concerns_list

    persona = g.get('persona', 'committee')
    template = get_overview_template_for_persona(persona, 'surtax')

    db = get_db()
    cursor = get_cursor(db)
    stats = get_overview_stats(cursor)
    categories = get_spending_by_category(cursor)
    concerns = get_concerns_list(cursor)

    # Compute percent_of_total for each category
    total_budget = stats.get('total_budget', 0) or 0
    for cat in categories:
        cat_budget = cat.get('total_budget', 0) or 0
        cat['percent_of_total'] = round(cat_budget / total_budget * 100, 1) if total_budget > 0 else 0

    # Get specific delayed/overbudget project details for the overview cards
    delayed_details = [c for c in concerns if c.get('is_delayed')]
    overbudget_details = [c for c in concerns if c.get('is_over_budget')]

    # Budget utilization percent
    total_spent = stats.get('total_spent', 0) or 0
    budget_pct = round(total_spent / total_budget * 100, 1) if total_budget > 0 else 0

    return render_template(template,
                          title='Oversight Committee Portal',
                          stats=stats,
                          categories=categories,
                          concerns=concerns,
                          delayed_projects=stats.get('delayed_count', 0),
                          overbudget_projects=stats.get('over_budget_count', 0),
                          delayed_details=delayed_details,
                          overbudget_details=overbudget_details,
                          budget_pct=budget_pct,
                          quick_stats={
                              'active_projects': stats.get('active_projects', 0),
                              'total_budget': f"${stats.get('total_budget', 0)/1_000_000:,.1f}M" if stats.get('total_budget') else '$0'
                          })


@surtax_bp.route('/projects')
def projects():
    """List all surtax-funded projects with rich filtering."""
    from app.database import get_db, get_cursor

    db = get_db()
    cursor = get_cursor(db)

    # Get filter params
    search_q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    type_filter = request.args.get('type', '')
    school_filter = request.args.get('school', '')
    delayed_only = request.args.get('delayed', '')
    overbudget_only = request.args.get('overbudget', '')
    sort_by = request.args.get('sort', 'budget')

    query = '''
        SELECT contract_id, title, school_name, surtax_category, vendor_name,
               current_amount, total_paid, percent_complete, status, type,
               is_delayed, delay_days, is_over_budget, budget_variance_pct,
               overall_health_score, risk_level, start_date, current_end_date, purpose
        FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
    '''
    params = []

    if search_q:
        query += ' AND (title ILIKE %s OR vendor_name ILIKE %s OR purpose ILIKE %s)'
        like = f'%{search_q}%'
        params.extend([like, like, like])
    if status_filter:
        query += ' AND status = %s'
        params.append(status_filter)
    if category_filter:
        query += ' AND surtax_category = %s'
        params.append(category_filter)
    if type_filter:
        query += ' AND type = %s'
        params.append(type_filter)
    if school_filter:
        query += ' AND school_name = %s'
        params.append(school_filter)
    if delayed_only:
        query += ' AND is_delayed = 1'
    if overbudget_only:
        query += ' AND is_over_budget = 1'

    sort_map = {
        'title': 'title ASC',
        'budget': 'current_amount DESC',
        'progress': 'percent_complete DESC',
        'health': 'overall_health_score ASC',
        'school': 'school_name ASC',
    }
    query += f' ORDER BY {sort_map.get(sort_by, "current_amount DESC")}'

    cursor.execute(query, params)
    projects_list = [dict(row) for row in cursor.fetchall()]

    # Get filter dropdown options
    cursor.execute('''
        SELECT DISTINCT surtax_category FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        ORDER BY surtax_category
    ''')
    categories = [row['surtax_category'] for row in cursor.fetchall()]

    cursor.execute('''
        SELECT DISTINCT type FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL AND type IS NOT NULL
        ORDER BY type
    ''')
    types = [row['type'] for row in cursor.fetchall()]

    cursor.execute('''
        SELECT DISTINCT school_name FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL AND school_name IS NOT NULL
        ORDER BY school_name
    ''')
    schools = [row['school_name'] for row in cursor.fetchall()]

    # Build active filters list for badge display
    active_filters = []
    if category_filter:
        active_filters.append(category_filter)
    if type_filter:
        active_filters.append(type_filter)
    if status_filter:
        active_filters.append(status_filter)
    if school_filter:
        active_filters.append(school_filter)
    if delayed_only:
        active_filters.append('Delayed')
    if overbudget_only:
        active_filters.append('Over Budget')

    return render_template('surtax/projects.html',
                          title='Projects',
                          projects=projects_list,
                          categories=categories,
                          types=types,
                          schools=schools,
                          search_q=search_q,
                          current_status=status_filter,
                          current_category=category_filter,
                          current_type=type_filter,
                          current_school=school_filter,
                          delayed_only=delayed_only,
                          overbudget_only=overbudget_only,
                          current_sort=sort_by,
                          active_filters=active_filters)


@surtax_bp.route('/projects/<contract_id>')
def project_detail(contract_id):
    """Detailed view of a surtax project."""
    from app.database import get_db, get_cursor

    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('SELECT * FROM contracts WHERE contract_id = %s AND is_deleted = 0', (contract_id,))
    project = cursor.fetchone()

    if not project:
        return render_template('errors/404.html', title='Project Not Found'), 404

    project = dict(project)

    # Get phases
    cursor.execute('SELECT * FROM project_phases WHERE contract_id = %s ORDER BY phase_order', (contract_id,))
    phases = [dict(row) for row in cursor.fetchall()]

    # Get change orders
    cursor.execute('SELECT * FROM change_orders WHERE contract_id = %s ORDER BY requested_date DESC', (contract_id,))
    change_orders = [dict(row) for row in cursor.fetchall()]

    # Get inspections
    cursor.execute('SELECT * FROM inspection_log WHERE contract_id = %s ORDER BY inspection_date DESC', (contract_id,))
    inspections = [dict(row) for row in cursor.fetchall()]

    # Get community engagement
    cursor.execute('SELECT * FROM community_engagement WHERE contract_id = %s ORDER BY meeting_date DESC', (contract_id,))
    community = [dict(row) for row in cursor.fetchall()]

    # Get committee actions
    cursor.execute('SELECT * FROM committee_actions WHERE contract_id = %s ORDER BY due_date DESC', (contract_id,))
    actions = [dict(row) for row in cursor.fetchall()]

    # Get contractor performance
    cursor.execute('SELECT * FROM contractor_performance WHERE contract_id = %s', (contract_id,))
    perf_row = cursor.fetchone()
    contractor_perf = dict(perf_row) if perf_row else None

    # Get documents
    cursor.execute('SELECT * FROM documents WHERE contract_id = %s AND is_deleted = 0 ORDER BY uploaded_date DESC', (contract_id,))
    documents = [dict(row) for row in cursor.fetchall()]

    return render_template('surtax/project_detail_enhanced.html',
                          title=project['title'],
                          project=project,
                          phases=phases,
                          change_orders=change_orders,
                          inspections=inspections,
                          community=community,
                          actions=actions,
                          contractor_perf=contractor_perf,
                          documents=documents)


@surtax_bp.route('/schools')
def schools():
    """List schools with surtax project summaries."""
    from app.database import get_db, get_cursor
    from app.services.stats import get_projects_by_school

    db = get_db()
    cursor = get_cursor(db)
    schools_list = get_projects_by_school(cursor)

    return render_template('surtax/schools.html',
                          title='Schools',
                          schools=schools_list)


@surtax_bp.route('/schools/<path:school_name>')
def school_detail(school_name):
    """Detail view for a specific school's projects."""
    from app.database import get_db, get_cursor

    db = get_db()
    cursor = get_cursor(db)

    cursor.execute('''
        SELECT contract_id, title, surtax_category, vendor_name,
               current_amount, total_paid, percent_complete, status,
               is_delayed, delay_days, is_over_budget, budget_variance_pct,
               overall_health_score, risk_level
        FROM contracts
        WHERE is_deleted = 0 AND school_name = %s
        ORDER BY current_amount DESC
    ''', (school_name,))
    projects_list = [dict(row) for row in cursor.fetchall()]

    # Summary stats for this school
    cursor.execute('''
        SELECT COUNT(*) as total, COALESCE(SUM(current_amount), 0) as budget,
               COALESCE(SUM(total_paid), 0) as spent, AVG(percent_complete) as avg_completion
        FROM contracts WHERE is_deleted = 0 AND school_name = %s
    ''', (school_name,))
    stats = dict(cursor.fetchone())

    return render_template('surtax/school_detail.html',
                          title=school_name,
                          school_name=school_name,
                          projects=projects_list,
                          stats=stats)


@surtax_bp.route('/capital-projects')
def capital_projects():
    """Capital projects overview grouped by category."""
    from app.database import get_db, get_cursor

    db = get_db()
    cursor = get_cursor(db)

    # Overall capital stats
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as completed,
            SUM(current_amount) as total_budget,
            SUM(total_paid) as total_spent,
            AVG(percent_complete) as avg_progress,
            AVG(overall_health_score) as avg_health,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget
        FROM contracts WHERE is_deleted = 0 AND surtax_category IS NOT NULL
    ''')
    stats = dict(cursor.fetchone())

    # By category with detail
    cursor.execute('''
        SELECT surtax_category,
               COUNT(*) as count,
               SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
               SUM(CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as completed,
               SUM(current_amount) as budget,
               SUM(total_paid) as spent,
               AVG(percent_complete) as avg_progress,
               AVG(overall_health_score) as avg_health,
               SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
               SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget
        FROM contracts WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category ORDER BY budget DESC
    ''')
    categories = [dict(row) for row in cursor.fetchall()]

    # All capital projects for the table
    cursor.execute('''
        SELECT contract_id, title, school_name, surtax_category, vendor_name,
               current_amount, total_paid, percent_complete, status,
               is_delayed, is_over_budget, overall_health_score, risk_level
        FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        ORDER BY current_amount DESC
    ''')
    projects = [dict(row) for row in cursor.fetchall()]

    return render_template('surtax/capital_projects.html',
                          title='Capital Projects',
                          stats=stats,
                          categories=categories,
                          projects=projects)


@surtax_bp.route('/concerns')
def concerns():
    """Concerns dashboard - delayed and over-budget projects."""
    from app.database import get_db, get_cursor
    from app.services.stats import get_concerns_list

    db = get_db()
    cursor = get_cursor(db)
    concerns_list = get_concerns_list(cursor)

    # Split by type
    delayed = [c for c in concerns_list if c['is_delayed']]
    over_budget = [c for c in concerns_list if c['is_over_budget']]

    return render_template('surtax/concerns.html',
                          title='Concerns',
                          concerns=concerns_list,
                          delayed=delayed,
                          over_budget=over_budget)
