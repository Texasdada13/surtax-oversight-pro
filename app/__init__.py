"""
Surtax Oversight Pro
A unified government oversight dashboard combining surtax project tracking
and general contract management with persona-based UI simplification.
"""

from flask import Flask, session, g, redirect, url_for
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Add project root to path so config/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / '.env')


def create_app(county: str = None, config_override: dict = None):
    """
    Application factory for creating Flask app instances.

    Args:
        county: County name (e.g., 'marion'). Defaults to SURTAX_COUNTY env var or 'marion'
        config_override: Optional dict to override config values (useful for testing)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Determine which county config to load
    county = county or os.environ.get('SURTAX_COUNTY', 'marion')

    # Load configuration
    from app.config import load_config
    config = load_config(county)

    # Apply any overrides
    if config_override:
        config.update(config_override)

    # Store config in app
    app.config.update(config)
    app.config['COUNTY'] = county

    # Set secret key - use env var, then config, then fallback
    secret_key = os.environ.get('SECRET_KEY') or config.get('app', {}).get('secret_key') or 'dev-key-change-in-production'
    app.secret_key = secret_key

    # Initialize extensions
    _init_extensions(app)

    # Register template filters
    _register_filters(app)

    # Register persona hooks
    _register_persona_hooks(app)

    # Register blueprints (routes)
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register root route
    @app.route('/')
    def index():
        view_mode = session.get('view_mode', 'surtax')
        if view_mode == 'contracts':
            return redirect(url_for('contracts.dashboard'))
        return redirect(url_for('surtax.overview'))

    # Persona switch route
    @app.route('/switch-persona/<persona_id>')
    def switch_persona(persona_id):
        from config.personas import PERSONAS
        if persona_id in PERSONAS:
            session['persona'] = persona_id
        return redirect(url_for('index'))

    # View mode switch route
    @app.route('/switch-view/<view_mode>')
    def switch_view(view_mode):
        from config.personas import VIEW_MODES
        if view_mode in VIEW_MODES:
            session['view_mode'] = view_mode
        return redirect(url_for('index'))

    return app


def _init_extensions(app):
    """Initialize Flask extensions."""
    from app.database import init_app
    init_app(app)


def _register_filters(app):
    """Register Jinja2 template filters."""

    @app.template_filter('currency')
    def currency_filter(value):
        """Format as currency."""
        if value is None:
            return '$0'
        try:
            value = float(value)
        except (TypeError, ValueError):
            return '$0'
        if abs(value) >= 1_000_000:
            return f'${value/1_000_000:,.1f}M'
        elif abs(value) >= 1_000:
            return f'${value/1_000:,.0f}K'
        return f'${value:,.0f}'

    @app.template_filter('currency_full')
    def currency_full_filter(value):
        """Format as full currency (no abbreviation)."""
        if value is None:
            return '$0'
        try:
            value = float(value)
        except (TypeError, ValueError):
            return '$0'
        return f'${value:,.0f}'

    @app.template_filter('currency_short')
    def currency_short_filter(value):
        """Format as abbreviated currency for large displays."""
        if value is None:
            return '$0'
        try:
            value = float(value)
        except (TypeError, ValueError):
            return '$0'
        if abs(value) >= 1_000_000_000:
            return f'${value/1_000_000_000:,.1f}B'
        elif abs(value) >= 1_000_000:
            return f'${value/1_000_000:,.1f}M'
        elif abs(value) >= 1_000:
            return f'${value/1_000:,.0f}K'
        return f'${value:,.0f}'

    @app.template_filter('percent')
    def percent_filter(value):
        """Format as percentage."""
        if value is None:
            return '0%'
        try:
            value = float(value)
        except (TypeError, ValueError):
            return '0%'
        return f'{value:.1f}%'

    @app.template_filter('date')
    def date_filter(value, format='%b %d, %Y'):
        """Format date string."""
        if value is None:
            return ''
        if isinstance(value, str):
            from datetime import datetime
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
        return value.strftime(format)


def _register_persona_hooks(app):
    """Register persona and view mode context injection."""
    from config.personas import ENABLE_PERSONA_SYSTEM, PERSONAS, VIEW_MODES, get_visible_navigation, GUIDED_AI_PROMPTS

    @app.before_request
    def inject_persona_context():
        if not ENABLE_PERSONA_SYSTEM:
            return

        # Set persona
        if 'persona' not in session:
            session['persona'] = 'committee'
        g.persona = session.get('persona', 'committee')
        g.persona_config = PERSONAS.get(g.persona, PERSONAS['committee'])

        # Set view mode
        if 'view_mode' not in session:
            session['view_mode'] = 'surtax'
        g.view_mode = session.get('view_mode', 'surtax')
        g.view_mode_config = VIEW_MODES.get(g.view_mode, VIEW_MODES['surtax'])

        # Get filtered navigation
        g.navigation = get_visible_navigation(g.persona, g.view_mode)
        g.hide_sidebar = False

    @app.context_processor
    def inject_template_globals():
        """Make persona/view data available in all templates."""
        from app.utils.persona_helpers import get_icon_path

        # Get concerns count for badge
        concerns_count = 0
        try:
            from app.database import get_db, get_cursor
            db = get_db()
            cursor = get_cursor(db)
            cursor.execute('''
                SELECT COUNT(*) FROM contracts
                WHERE is_deleted = 0
                AND (is_delayed = 1 OR is_over_budget = 1)
            ''')
            row = cursor.fetchone()
            if row:
                concerns_count = row[0]
        except Exception:
            pass

        return {
            'current_persona': g.get('persona', 'committee'),
            'persona_config': g.get('persona_config', PERSONAS['committee']),
            'personas_list': PERSONAS,
            'current_view_mode': g.get('view_mode', 'surtax'),
            'view_mode_config': g.get('view_mode_config', VIEW_MODES['surtax']),
            'view_modes_list': VIEW_MODES,
            'navigation_config': g.get('navigation', {}),
            'hide_sidebar': g.get('hide_sidebar', False),
            'concerns_count': concerns_count,
            'guided_prompts': GUIDED_AI_PROMPTS,
            'get_icon_path': get_icon_path,
        }


def _register_blueprints(app):
    """Register route blueprints."""
    from app.routes.surtax import surtax_bp
    from app.routes.contracts import contracts_bp
    from app.routes.monitoring import monitoring_bp
    from app.routes.financials import financials_bp
    from app.routes.documents import documents_bp
    from app.routes.tools import tools_bp
    from app.routes.api import api_bp

    app.register_blueprint(surtax_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(financials_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(api_bp, url_prefix='/api')


def _register_error_handlers(app):
    """Register error handlers."""
    import traceback
    import sys

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        print(f"500 ERROR: {error}", file=sys.stderr, flush=True)
        traceback.print_exc()
        return render_template('errors/500.html', title='Server Error'), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        from flask import render_template
        print(f"UNHANDLED EXCEPTION: {error}", file=sys.stderr, flush=True)
        traceback.print_exc()
        return render_template('errors/500.html', title='Server Error'), 500
