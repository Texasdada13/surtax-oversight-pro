"""Tools routes - meeting mode, AI chat, compliance, map, public portal."""

from flask import Blueprint, render_template

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')


@tools_bp.route('/ask')
def ask():
    """AI chat interface."""
    return render_template('tools/ask.html', title='Ask AI')


@tools_bp.route('/meeting')
def meeting():
    """Meeting mode."""
    return render_template('tools/meeting.html', title='Meeting Mode')


@tools_bp.route('/meeting/present')
def meeting_present():
    """Full-screen presentation mode."""
    return render_template('tools/meeting_present.html', title='Presentation')


@tools_bp.route('/compliance')
def compliance():
    """Compliance dashboard."""
    return render_template('tools/compliance.html', title='Compliance')


@tools_bp.route('/map')
def map_view():
    """Geographic map view."""
    return render_template('tools/map_view.html', title='Map View')


@tools_bp.route('/public')
def public_portal():
    """Public transparency portal."""
    return render_template('tools/public_portal.html', title='Public Portal')
