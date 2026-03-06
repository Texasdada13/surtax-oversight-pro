"""
Persona-based UI configuration and view mode system.
Defines which features are visible to which user personas and in which view mode.
"""

# Feature flag to enable/disable entire persona system
ENABLE_PERSONA_SYSTEM = True

# Available personas
PERSONAS = {
    'committee': {
        'id': 'committee',
        'name': 'Committee Member',
        'description': 'Simplified view for oversight committee members',
        'is_default': True
    },
    'staff': {
        'id': 'staff',
        'name': 'District Staff',
        'description': 'Full access to all features and analytics',
        'is_default': False
    }
}

# View modes - toggle between surtax-specific and general contract views
VIEW_MODES = {
    'surtax': {
        'id': 'surtax',
        'name': 'Surtax Oversight',
        'description': 'School capital outlay surtax projects',
        'icon': 'school'
    },
    'contracts': {
        'id': 'contracts',
        'name': 'Contract Management',
        'description': 'General contract oversight & analytics',
        'icon': 'briefcase'
    }
}

# Navigation configuration with visibility rules
# Each item has: view_modes (which view modes it appears in) + visible_to (which personas see it)
NAVIGATION = {
    # === SURTAX VIEW - Committee Main ===
    'surtax_main': {
        'label': 'Surtax',
        'view_modes': ['surtax'],
        'visible_to': ['committee'],
        'collapsible': False,
        'items': [
            {'id': 'surtax_overview', 'label': 'Overview', 'path': '/surtax/', 'icon': 'home', 'visible_to': ['committee']},
            {'id': 'ask_ai', 'label': 'Ask AI', 'path': '/tools/ask', 'icon': 'chat', 'visible_to': ['committee']},
            {'id': 'surtax_concerns', 'label': 'Concerns', 'path': '/surtax/concerns', 'icon': 'alert', 'badge': 'concerns_count', 'visible_to': ['committee']},
            {'id': 'monitoring_risk', 'label': 'Risk Dashboard', 'path': '/monitoring/risk', 'icon': 'shield', 'visible_to': ['committee']},
            {'id': 'surtax_vendors', 'label': 'Vendors', 'path': '/financials/vendors', 'icon': 'users', 'visible_to': ['committee']}
        ]
    },
    'surtax_more': {
        'label': 'More Tools',
        'view_modes': ['surtax'],
        'visible_to': ['committee'],
        'collapsible': True,
        'default_collapsed': True,
        'items': [
            {'id': 'surtax_projects', 'label': 'Projects', 'path': '/surtax/projects', 'icon': 'folder', 'visible_to': ['committee']},
            {'id': 'surtax_capital', 'label': 'Capital Projects', 'path': '/surtax/capital-projects', 'icon': 'building', 'visible_to': ['committee']},
            {'id': 'surtax_schools', 'label': 'Schools', 'path': '/surtax/schools', 'icon': 'school', 'visible_to': ['committee']},
            {'id': 'monitoring_watchlist', 'label': 'Watchlist', 'path': '/monitoring/watchlist', 'icon': 'star', 'visible_to': ['committee']},
            {'id': 'financials_home', 'label': 'Financials', 'path': '/financials/', 'icon': 'dollarSign', 'visible_to': ['committee']},
            {'id': 'financials_change_orders', 'label': 'Change Orders', 'path': '/financials/change-orders', 'icon': 'document', 'visible_to': ['committee']},
            {'id': 'documents_home', 'label': 'Documents', 'path': '/documents/', 'icon': 'collection', 'visible_to': ['committee']},
            {'id': 'documents_minutes', 'label': 'Meeting Minutes', 'path': '/documents/minutes', 'icon': 'clipboard', 'visible_to': ['committee']},
            {'id': 'documents_report', 'label': 'Annual Report', 'path': '/documents/report', 'icon': 'document', 'visible_to': ['committee']},
            {'id': 'tools_meeting', 'label': 'Meeting Mode', 'path': '/tools/meeting', 'icon': 'presentation', 'visible_to': ['committee']},
            {'id': 'financials_analytics', 'label': 'Analytics', 'path': '/financials/analytics', 'icon': 'chartBar', 'visible_to': ['committee']},
            {'id': 'tools_compliance', 'label': 'Compliance', 'path': '/tools/compliance', 'icon': 'checkCircle', 'visible_to': ['committee']},
            {'id': 'tools_map', 'label': 'Map View', 'path': '/tools/map', 'icon': 'map', 'visible_to': ['committee']},
            {'id': 'tools_public', 'label': 'Public Portal', 'path': '/tools/public', 'icon': 'globe', 'visible_to': ['committee']},
            {'id': 'monitoring_alerts', 'label': 'Alerts', 'path': '/monitoring/alerts', 'icon': 'bell', 'visible_to': ['committee']},
            {'id': 'monitoring_audit', 'label': 'Audit Trail', 'path': '/monitoring/audit', 'icon': 'clock', 'visible_to': ['committee']},
            {'id': 'tools_help', 'label': 'Help', 'path': '/tools/help', 'icon': 'questionMark', 'visible_to': ['committee']},
            {'id': 'tools_settings', 'label': 'Settings', 'path': '/tools/settings', 'icon': 'settings', 'visible_to': ['committee']}
        ]
    },

    # === SURTAX VIEW - Staff Navigation ===
    'surtax_staff_main': {
        'label': 'Surtax',
        'view_modes': ['surtax'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'surtax_overview', 'label': 'Overview', 'path': '/surtax/', 'icon': 'home', 'visible_to': ['staff']},
            {'id': 'surtax_projects', 'label': 'Projects', 'path': '/surtax/projects', 'icon': 'folder', 'visible_to': ['staff']},
            {'id': 'surtax_capital', 'label': 'Capital Projects', 'path': '/surtax/capital-projects', 'icon': 'building', 'visible_to': ['staff']},
            {'id': 'surtax_schools', 'label': 'Schools', 'path': '/surtax/schools', 'icon': 'school', 'visible_to': ['staff']},
            {'id': 'ask_ai', 'label': 'Ask AI', 'path': '/tools/ask', 'icon': 'chat', 'visible_to': ['staff']}
        ]
    },
    'surtax_staff_monitoring': {
        'label': 'Monitoring',
        'view_modes': ['surtax'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'surtax_concerns', 'label': 'Concerns', 'path': '/surtax/concerns', 'icon': 'alert', 'badge': 'concerns_count', 'visible_to': ['staff']},
            {'id': 'monitoring_watchlist', 'label': 'Watchlist', 'path': '/monitoring/watchlist', 'icon': 'star', 'visible_to': ['staff']},
            {'id': 'monitoring_risk', 'label': 'Risk Dashboard', 'path': '/monitoring/risk', 'icon': 'shield', 'visible_to': ['staff']},
            {'id': 'monitoring_audit', 'label': 'Audit Trail', 'path': '/monitoring/audit', 'icon': 'clock', 'visible_to': ['staff']},
            {'id': 'monitoring_alerts', 'label': 'Alerts', 'path': '/monitoring/alerts', 'icon': 'bell', 'visible_to': ['staff']}
        ]
    },
    'surtax_staff_financials': {
        'label': 'Financials',
        'view_modes': ['surtax'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'financials_home', 'label': 'Financials', 'path': '/financials/', 'icon': 'dollarSign', 'visible_to': ['staff']},
            {'id': 'financials_change_orders', 'label': 'Change Orders', 'path': '/financials/change-orders', 'icon': 'document', 'visible_to': ['staff']},
            {'id': 'surtax_vendors', 'label': 'Vendors', 'path': '/financials/vendors', 'icon': 'users', 'visible_to': ['staff']},
            {'id': 'financials_analytics', 'label': 'Analytics', 'path': '/financials/analytics', 'icon': 'chartBar', 'visible_to': ['staff']},
            {'id': 'financials_benchmarking', 'label': 'Benchmarking', 'path': '/financials/benchmarking', 'icon': 'trendingUp', 'visible_to': ['staff']}
        ]
    },
    'surtax_staff_documents': {
        'label': 'Documents',
        'view_modes': ['surtax'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'documents_home', 'label': 'Document Library', 'path': '/documents/', 'icon': 'collection', 'visible_to': ['staff']},
            {'id': 'documents_minutes', 'label': 'Meeting Minutes', 'path': '/documents/minutes', 'icon': 'clipboard', 'visible_to': ['staff']},
            {'id': 'documents_report', 'label': 'Annual Report', 'path': '/documents/report', 'icon': 'document', 'visible_to': ['staff']}
        ]
    },
    'surtax_staff_tools': {
        'label': 'Tools',
        'view_modes': ['surtax'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'tools_meeting', 'label': 'Meeting Mode', 'path': '/tools/meeting', 'icon': 'presentation', 'visible_to': ['staff']},
            {'id': 'tools_compliance', 'label': 'Compliance', 'path': '/tools/compliance', 'icon': 'checkCircle', 'visible_to': ['staff']},
            {'id': 'tools_map', 'label': 'Map View', 'path': '/tools/map', 'icon': 'map', 'visible_to': ['staff']},
            {'id': 'tools_public', 'label': 'Public Portal', 'path': '/tools/public', 'icon': 'globe', 'visible_to': ['staff']},
            {'id': 'tools_help', 'label': 'Help', 'path': '/tools/help', 'icon': 'questionMark', 'visible_to': ['staff']},
            {'id': 'tools_settings', 'label': 'Settings', 'path': '/tools/settings', 'icon': 'settings', 'visible_to': ['staff']}
        ]
    },

    # === CONTRACTS VIEW - Committee Main ===
    'contracts_main': {
        'label': 'Contracts',
        'view_modes': ['contracts'],
        'visible_to': ['committee'],
        'collapsible': False,
        'items': [
            {'id': 'contracts_dashboard', 'label': 'Dashboard', 'path': '/contracts/', 'icon': 'home', 'visible_to': ['committee']},
            {'id': 'ask_ai', 'label': 'Ask AI', 'path': '/tools/ask', 'icon': 'chat', 'visible_to': ['committee']},
            {'id': 'contracts_list', 'label': 'All Contracts', 'path': '/contracts/list', 'icon': 'folder', 'visible_to': ['committee']},
            {'id': 'monitoring_risk', 'label': 'Risk Dashboard', 'path': '/monitoring/risk', 'icon': 'shield', 'visible_to': ['committee']},
            {'id': 'contracts_vendors', 'label': 'Vendors', 'path': '/contracts/vendors', 'icon': 'users', 'visible_to': ['committee']}
        ]
    },

    # === CONTRACTS VIEW - Staff Navigation ===
    'contracts_staff_main': {
        'label': 'Contracts',
        'view_modes': ['contracts'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'contracts_dashboard', 'label': 'Dashboard', 'path': '/contracts/', 'icon': 'home', 'visible_to': ['staff']},
            {'id': 'contracts_executive', 'label': 'Executive View', 'path': '/contracts/executive', 'icon': 'chartBar', 'visible_to': ['staff']},
            {'id': 'contracts_list', 'label': 'All Contracts', 'path': '/contracts/list', 'icon': 'folder', 'visible_to': ['staff']},
            {'id': 'ask_ai', 'label': 'Ask AI', 'path': '/tools/ask', 'icon': 'chat', 'visible_to': ['staff']}
        ]
    },
    'contracts_staff_monitoring': {
        'label': 'Monitoring',
        'view_modes': ['contracts'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'monitoring_risk', 'label': 'Risk Dashboard', 'path': '/monitoring/risk', 'icon': 'shield', 'visible_to': ['staff']},
            {'id': 'monitoring_watchlist', 'label': 'Watchlist', 'path': '/monitoring/watchlist', 'icon': 'star', 'visible_to': ['staff']},
            {'id': 'monitoring_alerts', 'label': 'Alerts', 'path': '/monitoring/alerts', 'icon': 'bell', 'visible_to': ['staff']},
            {'id': 'monitoring_audit', 'label': 'Audit Trail', 'path': '/monitoring/audit', 'icon': 'clock', 'visible_to': ['staff']}
        ]
    },
    'contracts_staff_financials': {
        'label': 'Financials',
        'view_modes': ['contracts'],
        'visible_to': ['staff'],
        'collapsible': False,
        'items': [
            {'id': 'financials_home', 'label': 'Financials', 'path': '/financials/', 'icon': 'dollarSign', 'visible_to': ['staff']},
            {'id': 'contracts_vendors', 'label': 'Vendors', 'path': '/contracts/vendors', 'icon': 'users', 'visible_to': ['staff']},
            {'id': 'financials_benchmarking', 'label': 'Benchmarking', 'path': '/financials/benchmarking', 'icon': 'trendingUp', 'visible_to': ['staff']},
            {'id': 'financials_analytics', 'label': 'Analytics', 'path': '/financials/analytics', 'icon': 'chartBar', 'visible_to': ['staff']}
        ]
    },
}


def get_visible_navigation(persona='committee', view_mode='surtax'):
    """Filter navigation based on persona and view mode."""
    if not ENABLE_PERSONA_SYSTEM:
        return NAVIGATION

    filtered_nav = {}
    for section_key, section in NAVIGATION.items():
        # Check view mode
        if view_mode not in section.get('view_modes', []):
            continue
        # Check persona
        if persona not in section.get('visible_to', []):
            continue
        # Filter items by persona
        filtered_items = [
            item for item in section['items']
            if persona in item.get('visible_to', [])
        ]
        if filtered_items:
            filtered_nav[section_key] = {
                **section,
                'items': filtered_items
            }
    return filtered_nav


# Guided AI Prompts for Committee Members
GUIDED_AI_PROMPTS = [
    {
        'category': 'Financial Oversight',
        'button_text': 'Compare revenue to projections',
        'icon': 'dollarSign',
        'prompt': 'Compare the year-to-date surtax revenue collections against the approved projections. Highlight any significant variances and explain potential impacts on the approved project timeline.'
    },
    {
        'category': 'Compliance',
        'button_text': 'Verify ballot language compliance',
        'icon': 'checkCircle',
        'prompt': 'Review the current surtax expenditures and verify that all spending aligns with the ballot language approved by voters. Identify any concerns about compliance with the capital outlay statutory requirements.'
    },
    {
        'category': 'Project Status',
        'button_text': 'Explain projects behind schedule',
        'icon': 'clock',
        'prompt': 'Identify all projects that are currently behind schedule. For each delayed project, explain the root cause of the delay, the expected impact, and any mitigation plans in place.'
    },
    {
        'category': 'Budget Concerns',
        'button_text': 'Identify projects over budget',
        'icon': 'alert',
        'prompt': 'List all projects that are currently over budget or trending toward budget overruns. For each, summarize the cost drivers and whether additional funding sources are needed.'
    },
    {
        'category': 'Meeting Prep',
        'button_text': 'Prepare 3-bullet meeting summary',
        'icon': 'document',
        'prompt': 'Create a 3-bullet executive summary for the upcoming committee meeting that highlights: (1) key financial metrics, (2) major project updates, and (3) critical issues requiring committee attention.'
    },
    {
        'category': 'Public Transparency',
        'button_text': 'Review public communication efforts',
        'icon': 'globe',
        'prompt': "Assess the district's current public communication and transparency efforts regarding surtax-funded projects. Identify any gaps in public reporting or opportunities to improve community awareness."
    },
    {
        'category': 'Financial Planning',
        'button_text': 'Explain forecast & contingency',
        'icon': 'chart',
        'prompt': "Explain the current multi-year surtax revenue forecast and the district's contingency plans if collections fall short of projections. Include any recommended adjustments to the project pipeline."
    },
    {
        'category': 'Vendor Oversight',
        'button_text': 'Summarize vendor performance',
        'icon': 'users',
        'prompt': 'Summarize the performance of the top contractors working on surtax-funded projects. Highlight any quality concerns, delays, or exemplary performance that the committee should be aware of.'
    },
    {
        'category': 'Risk Assessment',
        'button_text': 'Highlight top 3 risks',
        'icon': 'shield',
        'prompt': 'Identify the top 3 risks currently facing the surtax program (financial, operational, or compliance-related). For each risk, explain the potential impact and recommended mitigation strategies.'
    },
    {
        'category': 'Public Communication',
        'button_text': 'Turn into public summary',
        'icon': 'presentation',
        'prompt': 'Convert the current dashboard data into a brief, plain-language summary suitable for public presentation. Focus on accomplishments, current status, and fiscal responsibility in 2-3 short paragraphs or 5-6 bullet points.'
    }
]
