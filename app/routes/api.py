"""API routes - JSON endpoints for AJAX, persona/view switching."""

from flask import Blueprint, jsonify, request, session
from app.database import get_db

api_bp = Blueprint('api', __name__)


@api_bp.route('/set-persona', methods=['POST'])
def set_persona():
    """Switch user persona."""
    from config.personas import PERSONAS
    data = request.get_json() or {}
    persona = data.get('persona', 'committee')
    if persona in PERSONAS:
        session['persona'] = persona
    return jsonify({'success': True, 'persona': session.get('persona')})


@api_bp.route('/set-view-mode', methods=['POST'])
def set_view_mode():
    """Switch view mode (surtax/contracts)."""
    from config.personas import VIEW_MODES
    data = request.get_json() or {}
    view_mode = data.get('view_mode', 'surtax')
    if view_mode in VIEW_MODES:
        session['view_mode'] = view_mode
    return jsonify({'success': True, 'view_mode': session.get('view_mode')})


@api_bp.route('/ask', methods=['POST'])
def ask():
    """Process AI question via Claude API."""
    from app.services.ai_chat import ask_claude

    data = request.get_json() or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    db = get_db()
    cursor = db.cursor()
    result = ask_claude(question, cursor)
    return jsonify(result)


@api_bp.route('/stats')
def stats():
    """Summary stats for sidebar/dashboard."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT
            COUNT(*) as total_projects,
            SUM(current_amount) as total_budget,
            SUM(total_paid) as total_spent,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count
        FROM contracts WHERE is_deleted = 0
    ''')
    row = cursor.fetchone()
    return jsonify(dict(row) if row else {
        'total_projects': 0, 'total_budget': 0, 'total_spent': 0,
        'delayed_count': 0, 'over_budget_count': 0
    })
