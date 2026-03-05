"""Tools routes - meeting mode, AI chat, compliance, map, public portal."""

from flask import Blueprint, render_template
from app.database import get_db
from app.services.ai_chat import get_guided_prompts

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')


@tools_bp.route('/ask')
def ask():
    """AI chat interface."""
    prompts = get_guided_prompts()
    return render_template('tools/ask.html', title='Ask AI', guided_prompts=prompts)


@tools_bp.route('/meeting')
def meeting():
    """Meeting preparation mode with key stats."""
    db = get_db()
    cursor = db.cursor()

    # Key stats for meeting
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(current_amount) as total_budget,
            SUM(total_paid) as total_spent,
            AVG(overall_health_score) as avg_health,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget,
            SUM(CASE WHEN overall_health_score < 50 THEN 1 ELSE 0 END) as critical
        FROM contracts WHERE is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    # Concerns for meeting
    cursor.execute('''
        SELECT c.*, ct.title as contract_title
        FROM concerns c
        LEFT JOIN contracts ct ON c.contract_id = ct.contract_id
        WHERE c.status = 'Open'
        ORDER BY c.severity DESC, c.created_date DESC LIMIT 10
    ''')
    concerns = [dict(row) for row in cursor.fetchall()]

    # Action items
    cursor.execute('''
        SELECT * FROM committee_actions
        WHERE status = 'Open'
        ORDER BY priority DESC, due_date ASC LIMIT 10
    ''')
    actions = [dict(row) for row in cursor.fetchall()]

    return render_template('tools/meeting.html',
                           title='Meeting Preparation',
                           stats=stats, concerns=concerns, actions=actions)


@tools_bp.route('/meeting/present')
def meeting_present():
    """Full-screen presentation mode."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(current_amount) as total_budget,
            SUM(total_paid) as total_spent,
            AVG(overall_health_score) as avg_health,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget
        FROM contracts WHERE is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    # Category breakdown
    cursor.execute('''
        SELECT surtax_category, COUNT(*) as count, SUM(current_amount) as budget,
               SUM(total_paid) as spent
        FROM contracts WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category ORDER BY budget DESC
    ''')
    categories = [dict(row) for row in cursor.fetchall()]

    return render_template('tools/meeting_present.html',
                           title='Presentation',
                           stats=stats, categories=categories)


@tools_bp.route('/compliance')
def compliance():
    """Compliance dashboard."""
    db = get_db()
    cursor = db.cursor()

    # Compliance issues
    cursor.execute('''
        SELECT contract_id, title, vendor_name, current_amount, surtax_category,
               requires_insurance, insurance_verified,
               requires_bond, bond_verified,
               is_sole_source, justification,
               board_approval_date, award_date
        FROM contracts
        WHERE is_deleted = 0 AND status = 'Active'
        ORDER BY current_amount DESC
    ''')
    contracts = [dict(row) for row in cursor.fetchall()]

    # Flag compliance issues and compute area scores
    issues = []
    ins_required = ins_verified = 0
    bond_required = bond_verified = 0
    board_required = board_approved = 0
    sole_source = sole_justified = 0

    for c in contracts:
        if c.get('requires_insurance'):
            ins_required += 1
            if c.get('insurance_verified'):
                ins_verified += 1
            else:
                issues.append({'contract': c['title'], 'contract_id': c['contract_id'],
                              'surtax_category': c.get('surtax_category'),
                              'issue': 'Insurance not verified', 'area': 'Insurance', 'severity': 'High'})
        if c.get('requires_bond'):
            bond_required += 1
            if c.get('bond_verified'):
                bond_verified += 1
            else:
                issues.append({'contract': c['title'], 'contract_id': c['contract_id'],
                              'surtax_category': c.get('surtax_category'),
                              'issue': 'Bond not verified', 'area': 'Bonding', 'severity': 'High'})
        if (c.get('current_amount', 0) or 0) > 50000:
            board_required += 1
            if c.get('board_approval_date'):
                board_approved += 1
            elif c.get('award_date'):
                issues.append({'contract': c['title'], 'contract_id': c['contract_id'],
                              'surtax_category': c.get('surtax_category'),
                              'issue': 'Missing board approval (>$50K)', 'area': 'Board Approval', 'severity': 'Critical'})
        if c.get('is_sole_source'):
            sole_source += 1
            if c.get('justification'):
                sole_justified += 1
            else:
                issues.append({'contract': c['title'], 'contract_id': c['contract_id'],
                              'surtax_category': c.get('surtax_category'),
                              'issue': 'Sole source without justification', 'area': 'Procurement', 'severity': 'Medium'})

    non_compliant_ids = set(i['contract_id'] for i in issues)
    compliant = len(contracts) - len(non_compliant_ids)
    compliance_pct = round(compliant / len(contracts) * 100) if contracts else 100

    areas = {
        'insurance': {
            'required': ins_required, 'verified': ins_verified,
            'pct': round(ins_verified / ins_required * 100) if ins_required else 100
        },
        'bonding': {
            'required': bond_required, 'verified': bond_verified,
            'pct': round(bond_verified / bond_required * 100) if bond_required else 100
        },
        'board': {
            'required': board_required, 'approved': board_approved,
            'pct': round(board_approved / board_required * 100) if board_required else 100
        },
        'procurement': {
            'sole_source': sole_source, 'justified': sole_justified,
            'pct': round(sole_justified / sole_source * 100) if sole_source else 100
        },
    }

    return render_template('tools/compliance.html',
                           title='Compliance',
                           contracts=contracts,
                           issues=issues,
                           total=len(contracts),
                           compliant=compliant,
                           non_compliant=len(non_compliant_ids),
                           compliance_pct=compliance_pct,
                           areas=areas)


@tools_bp.route('/map')
def map_view():
    """Geographic map view of projects."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT contract_id, title, project_location, latitude, longitude,
               current_amount, status, surtax_category, overall_health_score
        FROM contracts
        WHERE is_deleted = 0 AND latitude IS NOT NULL AND longitude IS NOT NULL
    ''')
    projects = [dict(row) for row in cursor.fetchall()]

    return render_template('tools/map_view.html',
                           title='Map View',
                           projects=projects)


@tools_bp.route('/public')
def public_portal():
    """Public transparency portal (read-only)."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as completed,
            SUM(current_amount) as total_budget,
            SUM(total_paid) as total_spent
        FROM contracts WHERE is_deleted = 0
    ''')
    stats = dict(cursor.fetchone())

    cursor.execute('''
        SELECT contract_id, title, vendor_name, surtax_category,
               current_amount, total_paid, percent_complete, status
        FROM contracts
        WHERE is_deleted = 0
        ORDER BY current_amount DESC
    ''')
    projects = [dict(row) for row in cursor.fetchall()]

    return render_template('tools/public_portal.html',
                           title='Public Portal',
                           stats=stats, projects=projects)
