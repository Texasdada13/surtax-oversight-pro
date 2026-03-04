"""Financial routes - budget, analytics, benchmarking."""

from flask import Blueprint, render_template

financials_bp = Blueprint('financials', __name__, url_prefix='/financials')


@financials_bp.route('/')
def home():
    """Financial overview."""
    return render_template('financials/financials.html', title='Financials')


@financials_bp.route('/analytics')
def analytics():
    """Detailed analytics."""
    return render_template('financials/analytics.html', title='Analytics')


@financials_bp.route('/benchmarking')
def benchmarking():
    """Coupa benchmark comparison."""
    return render_template('financials/benchmarking.html', title='Benchmarking')


@financials_bp.route('/change-orders')
def change_orders():
    """Change order tracking."""
    return render_template('financials/change_orders.html', title='Change Orders')


@financials_bp.route('/vendors')
def vendors():
    """Vendor performance (surtax context)."""
    return render_template('financials/vendors.html', title='Vendors')
