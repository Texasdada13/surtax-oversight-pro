"""Monitoring routes - risk, watchlist, audit, alerts."""

from flask import Blueprint, render_template

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')


@monitoring_bp.route('/risk')
def risk():
    """Risk dashboard."""
    return render_template('monitoring/risk_dashboard.html', title='Risk Dashboard')


@monitoring_bp.route('/watchlist')
def watchlist():
    """User watchlist."""
    return render_template('monitoring/watchlist.html', title='Watchlist')


@monitoring_bp.route('/audit')
def audit():
    """Audit trail."""
    return render_template('monitoring/audit_trail.html', title='Audit Trail')


@monitoring_bp.route('/alerts')
def alerts():
    """Alerts dashboard."""
    return render_template('monitoring/alerts.html', title='Alerts')
