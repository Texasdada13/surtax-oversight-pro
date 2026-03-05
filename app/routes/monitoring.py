"""Monitoring routes - risk, watchlist, audit, alerts."""

from flask import Blueprint, render_template, request
from app.database import get_db
from app.services.scoring_engine import ContractScoringEngine, AlertGenerator
from app.services.executive_analytics import ExecutiveAnalytics

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')


@monitoring_bp.route('/risk')
def risk():
    """Risk dashboard with scored contracts."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT * FROM contracts
        WHERE is_deleted = 0 AND status = 'Active'
        ORDER BY overall_health_score ASC
    ''')
    contracts = [dict(row) for row in cursor.fetchall()]

    engine = ContractScoringEngine()
    scored = [engine.score_contract(c) for c in contracts]

    # Risk distribution
    risk_dist = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for c in scored:
        level = c.get('risk_level', 'Low')
        risk_dist[level] = risk_dist.get(level, 0) + 1

    # Top risk contracts
    top_risk = [c for c in scored if c.get('risk_level') in ('Critical', 'High')][:10]

    # Analytics for top risk
    analytics = ExecutiveAnalytics(cursor)
    for c in top_risk:
        c['analytics'] = analytics.get_contract_analytics(c)

    avg_health = sum(c.get('overall_health_score', 0) for c in scored) / len(scored) if scored else 0
    total_at_risk = risk_dist.get('Critical', 0) + risk_dist.get('High', 0)
    total_value_at_risk = sum(
        c.get('current_amount', 0) or 0 for c in scored
        if c.get('risk_level') in ('Critical', 'High')
    )

    return render_template('monitoring/risk_dashboard.html',
                           title='Risk Dashboard',
                           contracts=scored,
                           risk_distribution=risk_dist,
                           top_risk=top_risk,
                           avg_health=avg_health,
                           total_at_risk=total_at_risk,
                           total_value_at_risk=total_value_at_risk,
                           total_contracts=len(scored))


@monitoring_bp.route('/watchlist')
def watchlist():
    """Contracts on watchlist (health < 60 or flagged)."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT * FROM contracts
        WHERE is_deleted = 0
          AND (overall_health_score < 60
               OR is_delayed = 1
               OR is_over_budget = 1)
        ORDER BY overall_health_score ASC
    ''')
    contracts = [dict(row) for row in cursor.fetchall()]

    engine = ContractScoringEngine()
    scored = [engine.score_contract(c) for c in contracts]

    return render_template('monitoring/watchlist.html',
                           title='Watchlist',
                           contracts=scored,
                           total=len(scored))


@monitoring_bp.route('/audit')
def audit():
    """Audit trail from audit_log table."""
    db = get_db()
    cursor = db.cursor()

    page = request.args.get('page', 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page

    cursor.execute('SELECT COUNT(*) as cnt FROM audit_log')
    total = cursor.fetchone()['cnt']

    cursor.execute('''
        SELECT a.*,
               CASE WHEN a.table_name = 'contracts'
                    THEN (SELECT title FROM contracts WHERE contract_id = a.record_id)
                    ELSE NULL END as contract_title
        FROM audit_log a
        ORDER BY a.changed_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    logs = [dict(row) for row in cursor.fetchall()]

    total_pages = (total + per_page - 1) // per_page

    return render_template('monitoring/audit_trail.html',
                           title='Audit Trail',
                           logs=logs,
                           page=page,
                           total_pages=total_pages,
                           total=total)


@monitoring_bp.route('/alerts')
def alerts():
    """Generated alerts from AlertGenerator."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM contracts WHERE is_deleted = 0')
    contracts = [dict(row) for row in cursor.fetchall()]

    engine = ContractScoringEngine()
    scored = [engine.score_contract(c) for c in contracts]

    alert_gen = AlertGenerator()
    all_alerts = alert_gen.generate_alerts(scored)

    severity_counts = {}
    for a in all_alerts:
        sev = a['severity']
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return render_template('monitoring/alerts.html',
                           title='Alerts',
                           alerts=all_alerts,
                           severity_counts=severity_counts,
                           total=len(all_alerts))
