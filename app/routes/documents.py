"""Document management routes."""

from flask import Blueprint, render_template

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


@documents_bp.route('/')
def home():
    """Document library."""
    return render_template('documents/documents.html', title='Documents')


@documents_bp.route('/minutes')
def minutes():
    """Meeting minutes."""
    return render_template('documents/meeting_minutes.html', title='Meeting Minutes')


@documents_bp.route('/report')
def report():
    """Annual report."""
    return render_template('documents/annual_report.html', title='Annual Report')
