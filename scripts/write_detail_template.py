#!/usr/bin/env python
"""Write the project_detail_enhanced.html template."""
import os

template = r'''{% extends "base.html" %}

{% block content %}
<!-- Breadcrumb -->
<nav class="flex items-center text-sm text-gray-500 mb-6">
    <a href="{{ url_for('surtax.overview') }}" class="hover:text-gray-700">Home</a>
    <svg class="w-4 h-4 mx-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
    <a href="{{ url_for('surtax.projects') }}" class="hover:text-gray-700">Projects</a>
    <svg class="w-4 h-4 mx-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
    <span class="text-gray-900 font-medium">{{ project.title[:50] }}{% if project.title|length > 50 %}...{% endif %}</span>
</nav>

<!-- Project Header -->
<div class="bg-white rounded-xl shadow-sm p-6 mb-6">
    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
                <h1 class="text-2xl font-bold text-gray-900">{{ project.title }}</h1>
                {% if project.is_delayed %}<span class="px-2 py-1 text-xs font-semibold bg-red-100 text-red-700 rounded-full">Delayed</span>{% endif %}
                {% if project.is_over_budget %}<span class="px-2 py-1 text-xs font-semibold bg-orange-100 text-orange-700 rounded-full">Over Budget</span>{% endif %}
            </div>
            <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                <span class="font-medium text-gray-700">{{ project.contract_id }}</span>
                {% if project.surtax_category %}<span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded">{{ project.surtax_category }}</span>{% endif %}
                <span class="px-2 py-0.5 rounded {% if project.status == 'Active' %}bg-green-50 text-green-700{% elif project.status == 'Completed' %}bg-blue-50 text-blue-700{% else %}bg-gray-100 text-gray-600{% endif %}">{{ project.status }}</span>
                {% if project.school_name %}<a href="{{ url_for('surtax.school_detail', school_name=project.school_name) }}" class="text-blue-600 hover:text-blue-700">{{ project.school_name }}</a>{% endif %}
            </div>
        </div>
        <div class="flex items-center gap-4">
            <div class="text-center">
                <div class="w-16 h-16 rounded-full flex items-center justify-center text-white text-xl font-bold {% if project.overall_health_score >= 70 %}bg-green-500{% elif project.overall_health_score >= 50 %}bg-yellow-500{% elif project.overall_health_score >= 30 %}bg-orange-500{% else %}bg-red-500{% endif %}">{{ project.overall_health_score }}</div>
                <p class="text-xs text-gray-500 mt-1">Health</p>
            </div>
            <div class="text-center px-3 py-2 rounded-lg {% if project.risk_level == 'Critical' %}bg-red-50 text-red-700{% elif project.risk_level == 'High' %}bg-orange-50 text-orange-700{% elif project.risk_level == 'Medium' %}bg-yellow-50 text-yellow-700{% else %}bg-green-50 text-green-700{% endif %}">
                <p class="text-sm font-bold">{{ project.risk_level }}</p><p class="text-xs">Risk Level</p>
            </div>
        </div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
        <div><p class="text-xs text-gray-500">Original Budget</p><p class="text-lg font-bold text-gray-900">{{ project.original_amount|currency }}</p></div>
        <div><p class="text-xs text-gray-500">Current Budget</p><p class="text-lg font-bold {% if project.is_over_budget %}text-orange-600{% else %}text-gray-900{% endif %}">{{ project.current_amount|currency }}</p></div>
        <div><p class="text-xs text-gray-500">Total Spent</p><p class="text-lg font-bold text-blue-600">{{ project.total_paid|currency }}</p></div>
        <div><p class="text-xs text-gray-500">Remaining</p><p class="text-lg font-bold text-green-600">{{ project.remaining_balance|currency }}</p></div>
    </div>
    <div class="mt-4">
        <div class="flex justify-between text-sm mb-1"><span class="text-gray-600">Overall Progress</span><span class="font-medium">{{ project.percent_complete }}%</span></div>
        <div class="w-full bg-gray-200 rounded-full h-3">
            <div class="h-3 rounded-full transition-all {% if project.percent_complete >= 75 %}bg-green-500{% elif project.percent_complete >= 50 %}bg-blue-500{% elif project.percent_complete >= 25 %}bg-yellow-500{% else %}bg-gray-400{% endif %}" style="width: {{ project.percent_complete }}%;"></div>
        </div>
    </div>
</div>

<!-- Tabbed Content -->
<div x-data="{ activeTab: 'overview' }">
    <div class="bg-white rounded-t-xl shadow-sm border-b border-gray-200">
        <div class="flex overflow-x-auto">
            <button @click="activeTab = 'overview'" :class="activeTab === 'overview' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'" class="px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap">Overview</button>
            <button @click="activeTab = 'financials'" :class="activeTab === 'financials' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'" class="px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap">Financials</button>
            <button @click="activeTab = 'schedule'" :class="activeTab === 'schedule' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'" class="px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap">Schedule & Phases</button>
            <button @click="activeTab = 'quality'" :class="activeTab === 'quality' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'" class="px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap">Quality & Safety</button>
            <button @click="activeTab = 'contractor'" :class="activeTab === 'contractor' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'" class="px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap">Contractor</button>
        </div>
    </div>
    <div class="bg-white rounded-b-xl shadow-sm p-6">
        <!-- Overview Tab -->
        <div x-show="activeTab === 'overview'">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-semibold text-gray-900 mb-3">Project Details</h3>
                    <dl class="space-y-3">
                        <div><dt class="text-xs text-gray-500">Description</dt><dd class="text-sm text-gray-900">{{ project.description or 'No description available' }}</dd></div>
                        <div><dt class="text-xs text-gray-500">Category</dt><dd class="text-sm text-gray-900">{{ project.surtax_category or 'N/A' }}</dd></div>
                        <div><dt class="text-xs text-gray-500">Expenditure Type</dt><dd class="text-sm text-gray-900">{{ project.expenditure_type or 'N/A' }}</dd></div>
                        <div><dt class="text-xs text-gray-500">Contract ID</dt><dd class="text-sm text-gray-900">{{ project.contract_id }}</dd></div>
                    </dl>
                </div>
                <div>
                    <h3 class="font-semibold text-gray-900 mb-3">Schedule</h3>
                    <dl class="space-y-3">
                        <div><dt class="text-xs text-gray-500">Start Date</dt><dd class="text-sm text-gray-900">{{ project.start_date|date if project.start_date else 'TBD' }}</dd></div>
                        <div><dt class="text-xs text-gray-500">Original End Date</dt><dd class="text-sm text-gray-900">{{ project.original_end_date|date if project.original_end_date else 'TBD' }}</dd></div>
                        <div><dt class="text-xs text-gray-500">Current End Date</dt><dd class="text-sm text-gray-900">{{ project.current_end_date|date if project.current_end_date else 'TBD' }}</dd></div>
                        {% if project.is_delayed %}<div><dt class="text-xs text-gray-500">Delay</dt><dd class="text-sm text-red-600 font-medium">{{ project.delay_days }} days &mdash; {{ project.delay_reason or 'Reason not specified' }}</dd></div>{% endif %}
                    </dl>
                </div>
            </div>
        </div>

        <!-- Financials Tab -->
        <div x-show="activeTab === 'financials'" style="display: none;">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                    <h3 class="font-semibold text-gray-900 mb-3">Budget Breakdown</h3>
                    <dl class="space-y-3">
                        <div class="flex justify-between"><dt class="text-sm text-gray-500">Original Amount</dt><dd class="text-sm font-medium text-gray-900">{{ project.original_amount|currency_full }}</dd></div>
                        <div class="flex justify-between"><dt class="text-sm text-gray-500">Current Amount</dt><dd class="text-sm font-medium {% if project.is_over_budget %}text-orange-600{% else %}text-gray-900{% endif %}">{{ project.current_amount|currency_full }}</dd></div>
                        <div class="flex justify-between border-t pt-2"><dt class="text-sm text-gray-500">Total Paid</dt><dd class="text-sm font-medium text-blue-600">{{ project.total_paid|currency_full }}</dd></div>
                        <div class="flex justify-between"><dt class="text-sm text-gray-500">Remaining</dt><dd class="text-sm font-medium text-green-600">{{ project.remaining_balance|currency_full }}</dd></div>
                        {% if project.is_over_budget %}<div class="flex justify-between border-t pt-2"><dt class="text-sm text-gray-500">Budget Variance</dt><dd class="text-sm font-bold text-orange-600">+{{ project.budget_variance_pct }}%</dd></div>{% endif %}
                    </dl>
                </div>
                <div>
                    <h3 class="font-semibold text-gray-900 mb-3">Spending Progress</h3>
                    {% set spend_pct = (project.total_paid / project.current_amount * 100) if project.current_amount else 0 %}
                    <div class="mb-4">
                        <div class="flex justify-between text-sm mb-1"><span class="text-gray-600">Budget Utilization</span><span class="font-medium">{{ spend_pct|round(1) }}%</span></div>
                        <div class="w-full bg-gray-200 rounded-full h-3"><div class="h-3 rounded-full bg-blue-500" style="width: {{ [spend_pct, 100]|min }}%;"></div></div>
                    </div>
                    <div class="mb-4">
                        <div class="flex justify-between text-sm mb-1"><span class="text-gray-600">Work Completion</span><span class="font-medium">{{ project.percent_complete }}%</span></div>
                        <div class="w-full bg-gray-200 rounded-full h-3"><div class="h-3 rounded-full bg-green-500" style="width: {{ project.percent_complete }}%;"></div></div>
                    </div>
                </div>
            </div>
            {% if change_orders %}
            <h3 class="font-semibold text-gray-900 mb-3 mt-6">Change Orders</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead><tr class="border-b border-gray-200"><th class="text-left py-2 text-xs text-gray-500 font-medium">Date</th><th class="text-left py-2 text-xs text-gray-500 font-medium">Description</th><th class="text-right py-2 text-xs text-gray-500 font-medium">Amount</th><th class="text-left py-2 text-xs text-gray-500 font-medium">Status</th></tr></thead>
                    <tbody>{% for co in change_orders %}<tr class="border-b border-gray-100"><td class="py-2">{{ co.requested_date|date if co.requested_date else 'N/A' }}</td><td class="py-2">{{ co.description or 'No description' }}</td><td class="py-2 text-right font-medium">{{ co.amount|currency if co.amount else 'N/A' }}</td><td class="py-2"><span class="px-2 py-0.5 text-xs rounded-full {% if co.status == 'Approved' %}bg-green-100 text-green-700{% elif co.status == 'Pending' %}bg-yellow-100 text-yellow-700{% else %}bg-gray-100 text-gray-600{% endif %}">{{ co.status or 'Unknown' }}</span></td></tr>{% endfor %}</tbody>
                </table>
            </div>
            {% endif %}
        </div>

        <!-- Schedule & Phases Tab -->
        <div x-show="activeTab === 'schedule'" style="display: none;">
            {% if phases %}
            <h3 class="font-semibold text-gray-900 mb-4">Project Phases</h3>
            <div class="space-y-4">
                {% for phase in phases %}
                <div class="border border-gray-200 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold {% if phase.status == 'Completed' %}bg-green-100 text-green-700{% elif phase.status == 'Active' %}bg-blue-100 text-blue-700{% else %}bg-gray-100 text-gray-500{% endif %}">{{ phase.phase_order or loop.index }}</div>
                            <div><h4 class="font-medium text-gray-900">{{ phase.phase_name }}</h4><p class="text-xs text-gray-500">{{ phase.status or 'Pending' }}</p></div>
                        </div>
                        <span class="text-sm font-medium">{{ phase.percent_complete or 0 }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2"><div class="h-2 rounded-full {% if phase.percent_complete == 100 %}bg-green-500{% else %}bg-blue-500{% endif %}" style="width: {{ phase.percent_complete or 0 }}%;"></div></div>
                    {% if phase.start_date or phase.end_date %}<p class="text-xs text-gray-500 mt-2">{{ phase.start_date|date if phase.start_date else '?' }} &mdash; {{ phase.end_date|date if phase.end_date else '?' }}</p>{% endif %}
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="text-center py-8"><p class="text-gray-500">No phase data available for this project</p></div>
            {% endif %}
        </div>

        <!-- Quality & Safety Tab -->
        <div x-show="activeTab === 'quality'" style="display: none;">
            {% if inspections %}
            <h3 class="font-semibold text-gray-900 mb-4">Inspection Log</h3>
            <div class="space-y-3">
                {% for insp in inspections %}
                <div class="border border-gray-200 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-1">
                        <div class="flex items-center gap-3">
                            <span class="px-2 py-1 text-xs font-medium rounded-full {% if insp.result == 'Pass' %}bg-green-100 text-green-700{% elif insp.result == 'Fail' %}bg-red-100 text-red-700{% else %}bg-yellow-100 text-yellow-700{% endif %}">{{ insp.result or 'Pending' }}</span>
                            <span class="text-sm font-medium text-gray-900">{{ insp.inspection_type or 'General Inspection' }}</span>
                        </div>
                        <span class="text-sm text-gray-500">{{ insp.inspection_date|date if insp.inspection_date else 'N/A' }}</span>
                    </div>
                    {% if insp.notes %}<p class="text-sm text-gray-600 mt-2">{{ insp.notes }}</p>{% endif %}
                    {% if insp.inspector_name %}<p class="text-xs text-gray-400 mt-1">Inspector: {{ insp.inspector_name }}</p>{% endif %}
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="text-center py-8"><p class="text-gray-500">No inspection records available</p></div>
            {% endif %}
        </div>

        <!-- Contractor Tab -->
        <div x-show="activeTab === 'contractor'" style="display: none;">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-semibold text-gray-900 mb-3">Contractor Information</h3>
                    <dl class="space-y-3">
                        <div><dt class="text-xs text-gray-500">Vendor Name</dt><dd class="text-sm font-medium text-gray-900">{{ project.vendor_name or 'Not assigned' }}</dd></div>
                        <div><dt class="text-xs text-gray-500">Contract ID</dt><dd class="text-sm text-gray-900">{{ project.contract_id }}</dd></div>
                    </dl>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('app/templates/surtax/project_detail_enhanced.html', 'w', encoding='utf-8') as f:
    f.write(template)
print(f"Written {len(template)} chars")
