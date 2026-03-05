"""Write Phase 4 monitoring and financials templates."""
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'app', 'templates')

templates = {}

# ── MONITORING TEMPLATES ──

templates['monitoring/risk_dashboard.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Risk Dashboard</h1>
            <p class="text-gray-500">Real-time risk assessment across all active contracts</p>
        </div>
        <div class="flex items-center gap-2 text-sm">
            <span class="px-3 py-1 bg-gray-100 rounded-full">{{ total_contracts }} Active Contracts</span>
        </div>
    </div>

    <!-- KPI Row -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Avg Health Score</p>
            <p class="text-3xl font-bold {% if avg_health >= 70 %}text-green-600{% elif avg_health >= 50 %}text-yellow-600{% else %}text-red-600{% endif %}">{{ "%.0f"|format(avg_health) }}</p>
            <p class="text-xs text-gray-400">out of 100</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Contracts at Risk</p>
            <p class="text-3xl font-bold text-red-600">{{ total_at_risk }}</p>
            <p class="text-xs text-gray-400">Critical + High</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Value at Risk</p>
            <p class="text-3xl font-bold text-red-600">{{ total_value_at_risk|currency_short }}</p>
            <p class="text-xs text-gray-400">total exposure</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Risk Distribution</p>
            <div class="flex gap-1 mt-2">
                {% for level, count in risk_distribution.items() %}
                {% if count > 0 %}
                <span class="px-2 py-0.5 text-xs rounded-full
                    {% if level == 'Critical' %}bg-red-100 text-red-700
                    {% elif level == 'High' %}bg-orange-100 text-orange-700
                    {% elif level == 'Medium' %}bg-yellow-100 text-yellow-700
                    {% else %}bg-green-100 text-green-700{% endif %}">
                    {{ count }} {{ level }}
                </span>
                {% endif %}
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- Risk Distribution Bar -->
    <div class="bg-white rounded-xl shadow-sm border p-5">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Risk Distribution</h3>
        <div class="flex h-6 rounded-full overflow-hidden">
            {% set total = total_contracts or 1 %}
            {% if risk_distribution.get('Critical', 0) > 0 %}
            <div class="bg-red-500" style="width: {{ (risk_distribution['Critical'] / total * 100)|round }}%" title="Critical: {{ risk_distribution['Critical'] }}"></div>
            {% endif %}
            {% if risk_distribution.get('High', 0) > 0 %}
            <div class="bg-orange-500" style="width: {{ (risk_distribution['High'] / total * 100)|round }}%" title="High: {{ risk_distribution['High'] }}"></div>
            {% endif %}
            {% if risk_distribution.get('Medium', 0) > 0 %}
            <div class="bg-yellow-400" style="width: {{ (risk_distribution['Medium'] / total * 100)|round }}%" title="Medium: {{ risk_distribution['Medium'] }}"></div>
            {% endif %}
            {% if risk_distribution.get('Low', 0) > 0 %}
            <div class="bg-green-500" style="width: {{ (risk_distribution['Low'] / total * 100)|round }}%" title="Low: {{ risk_distribution['Low'] }}"></div>
            {% endif %}
        </div>
        <div class="flex justify-between mt-2 text-xs text-gray-500">
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500"></span> Critical</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-orange-500"></span> High</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-yellow-400"></span> Medium</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500"></span> Low</span>
        </div>
    </div>

    <!-- Top Risk Contracts -->
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b">
            <h3 class="font-semibold text-gray-900">High Risk Contracts</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Contract</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Vendor</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Health</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Risk</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Budget</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Cost Score</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Schedule</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Forecast</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for c in top_risk %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                            <a href="{{ url_for('contracts.contract_detail', contract_id=c.contract_id) }}" class="text-blue-600 hover:underline font-medium">{{ c.title|truncate(40) }}</a>
                            <p class="text-xs text-gray-400">{{ c.contract_id }}</p>
                        </td>
                        <td class="px-4 py-3 text-gray-600">{{ c.vendor_name or 'N/A' }}</td>
                        <td class="px-4 py-3 text-center">
                            <span class="inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold
                                {% if c.overall_health_score >= 70 %}bg-green-100 text-green-700
                                {% elif c.overall_health_score >= 50 %}bg-yellow-100 text-yellow-700
                                {% else %}bg-red-100 text-red-700{% endif %}">
                                {{ c.overall_health_score|round|int }}
                            </span>
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="px-2 py-1 text-xs rounded-full
                                {% if c.risk_level == 'Critical' %}bg-red-100 text-red-700
                                {% elif c.risk_level == 'High' %}bg-orange-100 text-orange-700
                                {% else %}bg-yellow-100 text-yellow-700{% endif %}">
                                {{ c.risk_level }}
                            </span>
                        </td>
                        <td class="px-4 py-3 text-right">{{ (c.current_amount or 0)|currency_short }}</td>
                        <td class="px-4 py-3 text-center">{{ c.cost_variance_score|round|int }}</td>
                        <td class="px-4 py-3 text-center">{{ c.schedule_variance_score|round|int }}</td>
                        <td class="px-4 py-3 text-right">
                            {% if c.analytics %}
                            {{ c.analytics.forecast_at_completion|currency_short }}
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                    {% if not top_risk %}
                    <tr><td colspan="8" class="px-4 py-8 text-center text-gray-400">No high-risk contracts found</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
'''

templates['monitoring/watchlist.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Watchlist</h1>
            <p class="text-gray-500">Contracts requiring attention — delayed, over budget, or low health score</p>
        </div>
        <span class="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">{{ total }} items</span>
    </div>

    <div class="space-y-3">
        {% for c in contracts %}
        <div class="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition-shadow
            {% if c.risk_level == 'Critical' %}border-l-4 border-l-red-500
            {% elif c.risk_level == 'High' %}border-l-4 border-l-orange-500
            {% else %}border-l-4 border-l-yellow-400{% endif %}">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center gap-3">
                        <a href="{{ url_for('contracts.contract_detail', contract_id=c.contract_id) }}" class="text-lg font-semibold text-blue-600 hover:underline">{{ c.title }}</a>
                        <span class="px-2 py-0.5 text-xs rounded-full
                            {% if c.risk_level == 'Critical' %}bg-red-100 text-red-700
                            {% elif c.risk_level == 'High' %}bg-orange-100 text-orange-700
                            {% elif c.risk_level == 'Medium' %}bg-yellow-100 text-yellow-700
                            {% else %}bg-green-100 text-green-700{% endif %}">{{ c.risk_level }}</span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">{{ c.vendor_name or 'No vendor' }} &bull; {{ c.contract_id }}</p>
                    <div class="flex gap-4 mt-2 text-sm">
                        {% if c.is_delayed %}
                        <span class="text-red-600">Delayed {{ c.delay_days or 0 }} days</span>
                        {% endif %}
                        {% if c.is_over_budget %}
                        <span class="text-orange-600">Over budget {{ "%.1f"|format(c.budget_variance_pct or 0) }}%</span>
                        {% endif %}
                        <span class="text-gray-500">Health: {{ c.overall_health_score|round|int }}/100</span>
                        <span class="text-gray-500">Budget: {{ (c.current_amount or 0)|currency_short }}</span>
                    </div>
                </div>
                <div class="text-right">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-full text-lg font-bold
                        {% if c.overall_health_score >= 70 %}bg-green-100 text-green-700
                        {% elif c.overall_health_score >= 50 %}bg-yellow-100 text-yellow-700
                        {% else %}bg-red-100 text-red-700{% endif %}">
                        {{ c.overall_health_score|round|int }}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
        {% if not contracts %}
        <div class="bg-white rounded-xl shadow-sm border p-12 text-center text-gray-400">
            <p class="text-lg">No contracts on watchlist</p>
            <p class="text-sm mt-1">All contracts are performing within acceptable parameters</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
'''

templates['monitoring/audit_trail.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Audit Trail</h1>
            <p class="text-gray-500">Complete history of system actions and changes</p>
        </div>
        <span class="px-3 py-1 bg-gray-100 rounded-full text-sm">{{ total }} entries</span>
    </div>

    <div class="bg-white rounded-xl shadow-sm border">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Date/Time</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Action</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Contract</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">User</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Details</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for log in logs %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ log.created_at|date }}</td>
                        <td class="px-4 py-3">
                            <span class="px-2 py-0.5 text-xs rounded-full
                                {% if log.action == 'CREATE' %}bg-green-100 text-green-700
                                {% elif log.action == 'UPDATE' %}bg-blue-100 text-blue-700
                                {% elif log.action == 'DELETE' %}bg-red-100 text-red-700
                                {% else %}bg-gray-100 text-gray-700{% endif %}">
                                {{ log.action or 'UNKNOWN' }}
                            </span>
                        </td>
                        <td class="px-4 py-3">
                            {% if log.contract_id %}
                            <a href="{{ url_for('contracts.contract_detail', contract_id=log.contract_id) }}" class="text-blue-600 hover:underline">{{ log.contract_title|truncate(30) if log.contract_title else log.contract_id }}</a>
                            {% else %}
                            <span class="text-gray-400">—</span>
                            {% endif %}
                        </td>
                        <td class="px-4 py-3 text-gray-600">{{ log.user_id or 'System' }}</td>
                        <td class="px-4 py-3 text-gray-500 max-w-xs truncate">{{ log.details or '' }}</td>
                    </tr>
                    {% endfor %}
                    {% if not logs %}
                    <tr><td colspan="5" class="px-4 py-8 text-center text-gray-400">No audit log entries</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>

        {% if total_pages > 1 %}
        <div class="flex justify-center gap-2 p-4 border-t">
            {% if page > 1 %}
            <a href="?page={{ page - 1 }}" class="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200">Prev</a>
            {% endif %}
            <span class="px-3 py-1 text-sm text-gray-500">Page {{ page }} of {{ total_pages }}</span>
            {% if page < total_pages %}
            <a href="?page={{ page + 1 }}" class="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200">Next</a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
'''

templates['monitoring/alerts.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Alerts</h1>
            <p class="text-gray-500">Auto-generated alerts based on contract performance rules</p>
        </div>
        <div class="flex gap-2">
            {% for sev, count in severity_counts.items() %}
            <span class="px-3 py-1 text-sm rounded-full
                {% if sev == 'Critical' %}bg-red-100 text-red-700
                {% elif sev == 'High' %}bg-orange-100 text-orange-700
                {% else %}bg-yellow-100 text-yellow-700{% endif %}">
                {{ count }} {{ sev }}
            </span>
            {% endfor %}
        </div>
    </div>

    {% if not alerts %}
    <div class="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
        <svg class="w-12 h-12 text-green-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="text-green-800 font-medium">All Clear</p>
        <p class="text-green-600 text-sm mt-1">No alerts at this time</p>
    </div>
    {% else %}
    <div class="space-y-3">
        {% for alert in alerts %}
        <div class="bg-white rounded-xl shadow-sm border p-4
            {% if alert.severity == 'Critical' %}border-l-4 border-l-red-500
            {% elif alert.severity == 'High' %}border-l-4 border-l-orange-500
            {% else %}border-l-4 border-l-yellow-400{% endif %}">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <span class="px-2 py-0.5 text-xs font-medium rounded-full
                        {% if alert.severity == 'Critical' %}bg-red-100 text-red-700
                        {% elif alert.severity == 'High' %}bg-orange-100 text-orange-700
                        {% else %}bg-yellow-100 text-yellow-700{% endif %}">
                        {{ alert.severity }}
                    </span>
                    <span class="font-medium text-gray-900">{{ alert.title }}</span>
                </div>
                <a href="{{ url_for('contracts.contract_detail', contract_id=alert.contract_id) }}" class="text-sm text-blue-600 hover:underline">View Contract</a>
            </div>
            <p class="text-sm text-gray-500 mt-1">
                {{ alert.contract_title or alert.contract_id }}
                {% if alert.vendor_name %} &bull; {{ alert.vendor_name }}{% endif %}
            </p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
        <strong>About Alerts:</strong> Alerts are generated automatically based on contract health scoring rules.
        They include cost overrun warnings (&gt;10%), schedule delays, expiring contracts, low health scores, and excessive change orders.
    </div>
</div>
{% endblock %}
'''

# ── FINANCIAL TEMPLATES ──

templates['financials/financials.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Financial Overview</h1>
        <p class="text-gray-500">Portfolio-wide budget and spending analysis</p>
    </div>

    <!-- KPI Row -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Total Portfolio Budget</p>
            <p class="text-2xl font-bold text-gray-900">{{ (summary.total_current or 0)|currency_short }}</p>
            <p class="text-xs text-gray-400">across {{ summary.total_contracts }} contracts</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Total Spent</p>
            <p class="text-2xl font-bold text-blue-600">{{ (summary.total_spent or 0)|currency_short }}</p>
            {% set spend_pct = ((summary.total_spent or 0) / (summary.total_current or 1) * 100) %}
            <p class="text-xs text-gray-400">{{ "%.1f"|format(spend_pct) }}% of budget</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Budget Variance</p>
            <p class="text-2xl font-bold {% if (summary.total_variance or 0) > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                {{ (summary.total_variance or 0)|currency_short }}
            </p>
            <p class="text-xs text-gray-400">{{ "%.1f"|format(summary.avg_variance_pct or 0) }}% avg variance</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Active Budget Remaining</p>
            {% set remaining = (summary.active_budget or 0) - (summary.active_spent or 0) %}
            <p class="text-2xl font-bold text-gray-900">{{ remaining|currency_short }}</p>
            <p class="text-xs text-gray-400">active contracts only</p>
        </div>
    </div>

    <!-- Budget Utilization Bar -->
    <div class="bg-white rounded-xl shadow-sm border p-5">
        <h3 class="text-sm font-medium text-gray-700 mb-3">Budget Utilization</h3>
        <div class="w-full bg-gray-200 rounded-full h-4">
            <div class="bg-blue-600 h-4 rounded-full" style="width: {{ [spend_pct, 100]|min }}%"></div>
        </div>
        <div class="flex justify-between mt-1 text-xs text-gray-500">
            <span>{{ (summary.total_spent or 0)|currency_short }} spent</span>
            <span>{{ (summary.total_current or 0)|currency_short }} budget</span>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Spending by Category -->
        <div class="bg-white rounded-xl shadow-sm border">
            <div class="p-5 border-b">
                <h3 class="font-semibold text-gray-900">Spending by Category</h3>
            </div>
            <div class="p-5 space-y-3">
                {% for cat in by_category %}
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-gray-700">{{ cat.surtax_category }}</span>
                        <span class="text-gray-500">{{ (cat.spent or 0)|currency_short }} / {{ (cat.budget or 0)|currency_short }}</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        {% set pct = ((cat.spent or 0) / (cat.budget or 1) * 100) %}
                        <div class="h-2 rounded-full {% if pct > 90 %}bg-red-500{% elif pct > 70 %}bg-yellow-500{% else %}bg-blue-500{% endif %}" style="width: {{ [pct, 100]|min }}%"></div>
                    </div>
                </div>
                {% endfor %}
                {% if not by_category %}
                <p class="text-gray-400 text-sm">No category data available</p>
                {% endif %}
            </div>
        </div>

        <!-- AI Insights -->
        <div class="bg-white rounded-xl shadow-sm border">
            <div class="p-5 border-b">
                <h3 class="font-semibold text-gray-900">AI Insights</h3>
            </div>
            <div class="p-5 space-y-3">
                {% for insight in insights %}
                <div class="p-3 rounded-lg
                    {% if insight.severity == 'critical' %}bg-red-50 border border-red-200
                    {% elif insight.severity == 'warning' %}bg-yellow-50 border border-yellow-200
                    {% elif insight.severity == 'success' %}bg-green-50 border border-green-200
                    {% else %}bg-blue-50 border border-blue-200{% endif %}">
                    <p class="font-medium text-sm
                        {% if insight.severity == 'critical' %}text-red-800
                        {% elif insight.severity == 'warning' %}text-yellow-800
                        {% elif insight.severity == 'success' %}text-green-800
                        {% else %}text-blue-800{% endif %}">{{ insight.title }}</p>
                    <p class="text-xs mt-1
                        {% if insight.severity == 'critical' %}text-red-600
                        {% elif insight.severity == 'warning' %}text-yellow-600
                        {% elif insight.severity == 'success' %}text-green-600
                        {% else %}text-blue-600{% endif %}">{{ insight.description }}</p>
                </div>
                {% endfor %}
                {% if not insights %}
                <p class="text-gray-400 text-sm">No insights generated — all metrics within normal range</p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Monthly Spending -->
    {% if monthly_spend %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b">
            <h3 class="font-semibold text-gray-900">Monthly Spending Trend</h3>
        </div>
        <div class="p-5">
            <div class="flex items-end gap-2 h-40">
                {% set max_val = monthly_spend|map(attribute='total')|max or 1 %}
                {% for m in monthly_spend %}
                <div class="flex-1 flex flex-col items-center gap-1">
                    <div class="w-full bg-blue-500 rounded-t" style="height: {{ (m.total / max_val * 120)|round }}px" title="{{ (m.total or 0)|currency_short }}"></div>
                    <span class="text-xs text-gray-400">{{ m.month[-2:] }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

templates['financials/analytics.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Executive Analytics</h1>
        <p class="text-gray-500">Earned Value Management forecasting and predictive analytics</p>
    </div>

    <!-- Executive Summary -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white">
        <h3 class="text-sm font-medium text-blue-200 mb-2">Executive Summary</h3>
        <p class="text-lg">{{ exec_summary }}</p>
    </div>

    <!-- Forecast KPIs -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Total Budget (BAC)</p>
            <p class="text-2xl font-bold text-gray-900">{{ total_budget|currency_short }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Forecast at Completion (EAC)</p>
            <p class="text-2xl font-bold {% if total_forecast > total_budget %}text-red-600{% else %}text-green-600{% endif %}">
                {{ total_forecast|currency_short }}
            </p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Forecast Variance</p>
            <p class="text-2xl font-bold {% if forecast_variance > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                {{ forecast_variance|currency_short }}
            </p>
            {% if total_budget > 0 %}
            <p class="text-xs text-gray-400">{{ "%.1f"|format(forecast_variance / total_budget * 100) }}%</p>
            {% endif %}
        </div>
    </div>

    <!-- Over Budget Forecasts -->
    {% if over_budget %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b">
            <h3 class="font-semibold text-gray-900">Contracts Forecasted Over Budget</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Contract</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Budget</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Spent</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Forecast (EAC)</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Overrun</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">CPI</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Progress</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for c in over_budget %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                            <a href="{{ url_for('contracts.contract_detail', contract_id=c.contract_id) }}" class="text-blue-600 hover:underline">{{ c.title|truncate(35) }}</a>
                        </td>
                        <td class="px-4 py-3 text-right">{{ (c.current_amount or 0)|currency_short }}</td>
                        <td class="px-4 py-3 text-right">{{ (c.total_paid or 0)|currency_short }}</td>
                        <td class="px-4 py-3 text-right text-red-600 font-medium">{{ c.analytics.forecast_at_completion|currency_short }}</td>
                        <td class="px-4 py-3 text-right text-red-600">
                            {{ (c.analytics.forecast_at_completion - (c.current_amount or 0))|currency_short }}
                        </td>
                        <td class="px-4 py-3 text-center">{{ c.analytics.cost_performance_index }}</td>
                        <td class="px-4 py-3 text-center">{{ c.percent_complete or 0 }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- All Active Contracts Analytics -->
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b">
            <h3 class="font-semibold text-gray-900">Active Contract Analytics</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Contract</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Burn Rate/mo</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Forecast</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">CPI</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Risk</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Est. Completion</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for c in contracts[:20] %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                            <a href="{{ url_for('contracts.contract_detail', contract_id=c.contract_id) }}" class="text-blue-600 hover:underline">{{ c.title|truncate(35) }}</a>
                        </td>
                        <td class="px-4 py-3 text-right">{{ c.analytics.burn_rate_monthly|currency_short }}</td>
                        <td class="px-4 py-3 text-right">{{ c.analytics.forecast_at_completion|currency_short }}</td>
                        <td class="px-4 py-3 text-center">{{ c.analytics.cost_performance_index }}</td>
                        <td class="px-4 py-3 text-center">
                            <span class="px-2 py-0.5 text-xs rounded-full
                                {% if c.analytics.risk_category == 'High' %}bg-red-100 text-red-700
                                {% elif c.analytics.risk_category == 'Medium' %}bg-yellow-100 text-yellow-700
                                {% else %}bg-green-100 text-green-700{% endif %}">
                                {{ c.analytics.risk_category }}
                            </span>
                        </td>
                        <td class="px-4 py-3 text-gray-600">{{ c.analytics.expected_completion_date or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
'''

templates['financials/benchmarking.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Procurement Benchmarking</h1>
        <p class="text-gray-500">Performance compared to Coupa 2025 Total Spend Management benchmarks</p>
    </div>

    <!-- Overall Health Score -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
        <div class="flex items-center gap-6">
            <div class="w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold
                {% if health.grade == 'A' %}bg-green-100 text-green-700
                {% elif health.grade == 'B' %}bg-blue-100 text-blue-700
                {% elif health.grade == 'C' %}bg-yellow-100 text-yellow-700
                {% else %}bg-red-100 text-red-700{% endif %}">
                {{ health.grade }}
            </div>
            <div>
                <h3 class="text-xl font-semibold text-gray-900">Overall Score: {{ health.overall_score }}/100</h3>
                <p class="text-gray-500">Rating: {{ health.rating }} &bull; {{ health.total_kpis }} KPIs evaluated</p>
                {% if health.strengths %}
                <p class="text-sm text-green-600 mt-1">Strengths: {{ health.strengths|join(', ') }}</p>
                {% endif %}
                {% if health.improvements %}
                <p class="text-sm text-red-600 mt-1">Needs Improvement: {{ health.improvements|join(', ') }}</p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Category Breakdown -->
    {% for cat_id, cat in health.categories.items() %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">{{ cat.name }}</h3>
            <span class="px-3 py-1 rounded-full text-sm font-medium
                {% if cat.score >= 90 %}bg-green-100 text-green-700
                {% elif cat.score >= 75 %}bg-blue-100 text-blue-700
                {% elif cat.score >= 60 %}bg-yellow-100 text-yellow-700
                {% else %}bg-red-100 text-red-700{% endif %}">
                {{ cat.score }}/100
            </span>
        </div>
        <div class="p-5 space-y-4">
            {% for kpi in cat.kpis %}
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-700">{{ kpi.name }}</span>
                    <span class="text-gray-500">
                        Actual: <strong>{{ kpi.actual_value }}{{ '%' if kpi.unit == 'percent' else ' hrs' if kpi.unit == 'business_hours' else '' }}</strong>
                        &bull; Benchmark: {{ kpi.benchmark_value }}{{ '%' if kpi.unit == 'percent' else ' hrs' if kpi.unit == 'business_hours' else '' }}
                    </span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-2">
                        <div class="h-2 rounded-full
                            {% if kpi.rating == 'Excellent' %}bg-green-500
                            {% elif kpi.rating == 'Good' %}bg-blue-500
                            {% elif kpi.rating == 'Fair' %}bg-yellow-500
                            {% else %}bg-red-500{% endif %}"
                            style="width: {{ [kpi.score, 100]|min }}%"></div>
                    </div>
                    <span class="text-xs px-2 py-0.5 rounded-full
                        {% if kpi.rating == 'Excellent' %}bg-green-100 text-green-700
                        {% elif kpi.rating == 'Good' %}bg-blue-100 text-blue-700
                        {% elif kpi.rating == 'Fair' %}bg-yellow-100 text-yellow-700
                        {% else %}bg-red-100 text-red-700{% endif %}">
                        {{ kpi.rating }}
                    </span>
                </div>
                <p class="text-xs text-gray-400 mt-1">{{ kpi.description }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}

    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
        <strong>Source:</strong> Coupa 2025 Total Spend Management Benchmark Report. Benchmarks represent median values across surveyed organizations.
    </div>
</div>
{% endblock %}
'''

templates['financials/change_orders.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Change Orders</h1>
            <p class="text-gray-500">Track all contract modifications and change orders</p>
        </div>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Total Change Orders</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total or 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Net Amount Impact</p>
            <p class="text-2xl font-bold {% if (stats.total_amount or 0) > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                {{ (stats.total_amount or 0)|currency_short }}
            </p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Approved</p>
            <p class="text-2xl font-bold text-green-600">{{ stats.approved or 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Pending</p>
            <p class="text-2xl font-bold text-yellow-600">{{ stats.pending or 0 }}</p>
        </div>
    </div>

    <!-- Change Orders Table -->
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Contract</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Description</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Amount</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Status</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Submitted</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Reason</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for co in orders %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                            <a href="{{ url_for('contracts.contract_detail', contract_id=co.cid) }}" class="text-blue-600 hover:underline">{{ co.contract_title|truncate(30) }}</a>
                        </td>
                        <td class="px-4 py-3 text-gray-600 max-w-xs truncate">{{ co.description or 'N/A' }}</td>
                        <td class="px-4 py-3 text-right font-medium {% if (co.amount_change or 0) > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                            {{ (co.amount_change or 0)|currency }}
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="px-2 py-0.5 text-xs rounded-full
                                {% if co.status == 'Approved' %}bg-green-100 text-green-700
                                {% elif co.status == 'Pending' %}bg-yellow-100 text-yellow-700
                                {% elif co.status == 'Rejected' %}bg-red-100 text-red-700
                                {% else %}bg-gray-100 text-gray-700{% endif %}">
                                {{ co.status }}
                            </span>
                        </td>
                        <td class="px-4 py-3 text-gray-500">{{ co.date_submitted|date if co.date_submitted else 'N/A' }}</td>
                        <td class="px-4 py-3 text-gray-500">{{ co.reason or '' }}</td>
                    </tr>
                    {% endfor %}
                    {% if not orders %}
                    <tr><td colspan="6" class="px-4 py-8 text-center text-gray-400">No change orders found</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
'''

templates['financials/vendors.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Vendor Financial Performance</h1>
        <p class="text-gray-500">Financial health and performance metrics by vendor</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {% for v in vendors %}
        <div class="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between mb-3">
                <div>
                    <h3 class="font-semibold text-gray-900">{{ v.vendor_name }}</h3>
                    <p class="text-sm text-gray-500">{{ v.contract_count or 0 }} contract{{ 's' if (v.contract_count or 0) != 1 }}</p>
                </div>
                {% if v.avg_health %}
                <span class="inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold
                    {% if v.avg_health >= 70 %}bg-green-100 text-green-700
                    {% elif v.avg_health >= 50 %}bg-yellow-100 text-yellow-700
                    {% else %}bg-red-100 text-red-700{% endif %}">
                    {{ v.avg_health|round|int }}
                </span>
                {% endif %}
            </div>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="text-gray-500">Total Value</span>
                    <span class="font-medium">{{ (v.total_value or 0)|currency_short }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-500">Total Paid</span>
                    <span class="font-medium">{{ (v.total_paid or 0)|currency_short }}</span>
                </div>
                {% if v.total_value and v.total_paid %}
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                    {% set pct = ((v.total_paid or 0) / (v.total_value or 1) * 100) %}
                    <div class="bg-blue-500 h-1.5 rounded-full" style="width: {{ [pct, 100]|min }}%"></div>
                </div>
                {% endif %}
                <div class="flex gap-3 pt-1">
                    {% if v.delayed_count %}
                    <span class="text-red-600 text-xs">{{ v.delayed_count }} delayed</span>
                    {% endif %}
                    {% if v.over_budget_count %}
                    <span class="text-orange-600 text-xs">{{ v.over_budget_count }} over budget</span>
                    {% endif %}
                    {% if not v.delayed_count and not v.over_budget_count %}
                    <span class="text-green-600 text-xs">On track</span>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
        {% if not vendors %}
        <div class="col-span-full bg-white rounded-xl shadow-sm border p-12 text-center text-gray-400">
            No vendor data available
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
'''

# Write all templates
for path, content in templates.items():
    full_path = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Wrote {path}")

print(f"\nDone! Wrote {len(templates)} templates.")
