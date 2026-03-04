"""API routes - JSON endpoints for AJAX, persona/view switching."""

from flask import Blueprint, jsonify, request, session

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
    """Process AI question (stub - will be wired to Claude API in Phase 5)."""
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    return jsonify({
        'answer': f'AI chat will be available once Claude API is configured. Your question: "{question}"',
        'suggestions': ['What is the total budget?', 'Which projects are delayed?', 'Summarize vendor performance'],
        'ask_staff': False
    })


@api_bp.route('/stats')
def stats():
    """Summary stats for sidebar/dashboard."""
    return jsonify({
        'total_projects': 0,
        'total_budget': 0,
        'total_spent': 0,
        'delayed_count': 0,
        'over_budget_count': 0
    })
