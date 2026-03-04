#!/usr/bin/env python
"""Write the contract detail template."""
import os

template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            'app', 'templates', 'contracts')

content = r'''{% extends "base.html" %}

{% block content %}
<!-- Breadcrumb -->
<div class="mb-4 flex items-center gap-2 text-sm text-gray-500">
    <a href="{{ url_for('contracts.dashboard') }}" class="hover:text-blue-600">Home</a>
    <span>/</span>
    <a href="{{ url_for('contracts.contract_list') }}" class="hover:text-blue-600">Contracts</a>
    <span>/</span>
    <span class="text-gray-900 font-medium">{{ contract.title[:40] }}{% if contract.title|length > 40 %}...{% endif %}</span>
</div>

<!-- Contract Header -->
<div class="bg-white rounded-xl shadow-sm p-6 mb-6">
    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
                <h1 class="text-2xl font-bold text-gray-900">{{ contract.title }}</h1>
                {% if contract.surtax_category %}
                <span class="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-700 rounded-full">Surtax</span>
                {% endif %}
            </div>
            <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                <span class="font-medium text-gray-700">{{ contract.contract_id }}</span>
                {% if contract.vendor_name %}
                <span>&middot; {{ contract.vendor_name }}</span>
                {% endif %}
                {% if contract.school_name %}
                <span>&middot; {{ contract.school_name }}</span>
                {% endif %}
                <span class="px-2 py-0.5 text-xs rounded-full
                    {% if contract.status == 'Active' %}bg-green-100 text-green-700
                    {% elif contract.status == 'Completed' %}bg-blue-100 text-blue-700
                    {% else %}bg-gray-100 text-gray-700{% endif %}">
                    {{ contract.status }}
                </span>
                {% if contract.is_delayed %}
                <span class="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full">Delayed {{ contract.delay_days }}d</span>
                {% endif %}
                {% if contract.is_over_budget %}
                <span class="px-2 py-0.5 text-xs bg-orange-100 text-orange-700 rounded-full">+{{ contract.budget_variance_pct }}% Over Budget</span>
                {% endif %}
            </div>
        </div>
        <div class="flex items-center gap-4">
            <!-- Health Score -->
            <div class="text-center">
                <div class="w-16 h-16 rounded-full flex items-center justify-center border-4
                    {% if contract.overall_health_score and contract.overall_health_score >= 70 %}border-green-500
                    {% elif contract.overall_health_score and contract.overall_health_score >= 50 %}border-yellow-500
                    {% else %}border-red-500{% endif %}">
                    <span class="text-lg font-bold text-gray-900">{{ contract.overall_health_score|int if contract.overall_health_score else '-' }}</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">Health</p>
            </div>
            <!-- Risk Badge -->
            <div class="text-center">
                <span class="inline-block px-3 py-2 text-sm font-bold rounded-lg
                    {% if contract.risk_level == 'Critical' %}bg-red-100 text-red-700
                    {% elif contract.risk_level == 'High' %}bg-orange-100 text-orange-700
                    {% elif contract.risk_level == 'Medium' %}bg-yellow-100 text-yellow-700
                    {% else %}bg-green-100 text-green-700{% endif %}">
                    {{ contract.risk_level }} Risk
                </span>
            </div>
        </div>
    </div>
</div>

<!-- Financial Bar -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
    <div class="bg-white rounded-xl shadow-sm p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wider">Original Amount</p>
        <p class="text-xl font-bold text-gray-900 mt-1">{{ contract.original_amount|currency_full }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wider">Current Amount</p>
        <p class="text-xl font-bold text-gray-900 mt-1">{{ contract.current_amount|currency_full }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wider">Total Paid</p>
        <p class="text-xl font-bold text-blue-600 mt-1">{{ contract.total_paid|currency_full }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wider">Remaining</p>
        <p class="text-xl font-bold text-green-600 mt-1">{{ contract.remaining_balance|currency_full }}</p>
    </div>
</div>

<!-- Progress Bar -->
<div class="bg-white rounded-xl shadow-sm p-6 mb-6">
    <div class="flex justify-between items-center mb-2">
        <h2 class="text-sm font-bold text-gray-700">Overall Progress</h2>
        <span class="text-lg font-bold text-gray-900">{{ contract.percent_complete|int }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-4">
        <div class="h-4 rounded-full transition-all
            {% if contract.percent_complete >= 75 %}bg-green-500
            {% elif contract.percent_complete >= 50 %}bg-blue-500
            {% elif contract.percent_complete >= 25 %}bg-yellow-500
            {% else %}bg-gray-400{% endif %}"
             style="width: {{ contract.percent_complete }}%;"></div>
    </div>
</div>

<!-- Tabs -->
<div x-data="{ tab: 'overview' }" class="mb-6">
    <div class="flex gap-1 bg-white rounded-xl shadow-sm p-1 mb-4">
        <button @click="tab = 'overview'" :class="tab === 'overview' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">Overview</button>
        <button @click="tab = 'financials'" :class="tab === 'financials' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">Financials</button>
        {% if phases %}
        <button @click="tab = 'phases'" :class="tab === 'phases' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">Phases</button>
        {% endif %}
        {% if milestones %}
        <button @click="tab = 'milestones'" :class="tab === 'milestones' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">Milestones</button>
        {% endif %}
        {% if inspections %}
        <button @click="tab = 'inspections'" :class="tab === 'inspections' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">Inspections</button>
        {% endif %}
    </div>

    <!-- Overview Tab -->
    <div x-show="tab === 'overview'">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white rounded-xl shadow-sm p-6">
                <h3 class="text-lg font-bold text-gray-900 mb-4">Contract Details</h3>
                <div class="space-y-3 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-500">Contract ID</span>
                        <span class="text-gray-900 font-medium">{{ contract.contract_id }}</span>
                    </div>
                    {% if contract.contract_number %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Contract Number</span>
                        <span class="text-gray-900 font-medium">{{ contract.contract_number }}</span>
                    </div>
                    {% endif %}
                    {% if contract.type %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Type</span>
                        <span class="text-gray-900">{{ contract.type }}</span>
                    </div>
                    {% endif %}
                    {% if contract.surtax_category %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Surtax Category</span>
                        <span class="text-gray-900">{{ contract.surtax_category }}</span>
                    </div>
                    {% endif %}
                    {% if contract.vendor_name %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Vendor</span>
                        <span class="text-gray-900 font-medium">{{ contract.vendor_name }}</span>
                    </div>
                    {% endif %}
                    {% if contract.school_name %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">School</span>
                        <span class="text-gray-900">{{ contract.school_name }}</span>
                    </div>
                    {% endif %}
                    {% if contract.description %}
                    <div class="pt-3 border-t border-gray-200">
                        <p class="text-gray-500 mb-1">Description</p>
                        <p class="text-gray-900">{{ contract.description }}</p>
                    </div>
                    {% endif %}
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm p-6">
                <h3 class="text-lg font-bold text-gray-900 mb-4">Schedule</h3>
                <div class="space-y-3 text-sm">
                    {% if contract.start_date %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Start Date</span>
                        <span class="text-gray-900">{{ contract.start_date|date }}</span>
                    </div>
                    {% endif %}
                    {% if contract.original_end_date %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Original End Date</span>
                        <span class="text-gray-900">{{ contract.original_end_date|date }}</span>
                    </div>
                    {% endif %}
                    {% if contract.current_end_date %}
                    <div class="flex justify-between">
                        <span class="text-gray-500">Current End Date</span>
                        <span class="text-gray-900 font-medium">{{ contract.current_end_date|date }}</span>
                    </div>
                    {% endif %}
                    {% if contract.is_delayed %}
                    <div class="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
                        <p class="text-sm font-medium text-red-700">{{ contract.delay_days }} days behind schedule</p>
                        {% if contract.delay_reason %}
                        <p class="text-sm text-red-600 mt-1">{{ contract.delay_reason }}</p>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>

                {% if contract.procurement_method or contract.bid_count %}
                <div class="mt-6 pt-4 border-t border-gray-200">
                    <h4 class="text-sm font-bold text-gray-700 mb-3">Procurement</h4>
                    <div class="space-y-2 text-sm">
                        {% if contract.procurement_method %}
                        <div class="flex justify-between">
                            <span class="text-gray-500">Method</span>
                            <span class="text-gray-900">{{ contract.procurement_method }}</span>
                        </div>
                        {% endif %}
                        {% if contract.bid_count %}
                        <div class="flex justify-between">
                            <span class="text-gray-500">Bids Received</span>
                            <span class="text-gray-900">{{ contract.bid_count }}</span>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Financials Tab -->
    <div x-show="tab === 'financials'" style="display: none;">
        <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Budget Breakdown</h3>
            <div class="space-y-4">
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-gray-600">Spent</span>
                        <span class="font-bold text-blue-600">{{ contract.total_paid|currency_full }}</span>
                    </div>
                    {% set spent_pct = (contract.total_paid / contract.current_amount * 100) if contract.current_amount else 0 %}
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="h-2.5 rounded-full bg-blue-500" style="width: {{ spent_pct|round }}%;"></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ spent_pct|round(1) }}% of budget spent</p>
                </div>
                {% if contract.original_amount != contract.current_amount %}
                <div class="p-3 bg-orange-50 rounded-lg border border-orange-200">
                    <p class="text-sm text-orange-700">
                        Budget changed from {{ contract.original_amount|currency_full }} to {{ contract.current_amount|currency_full }}
                        ({% if contract.current_amount > contract.original_amount %}+{% endif %}{{ ((contract.current_amount - contract.original_amount) / contract.original_amount * 100)|round(1) if contract.original_amount else 0 }}%)
                    </p>
                </div>
                {% endif %}
            </div>
        </div>

        {% if change_orders %}
        <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Change Orders ({{ change_orders|length }})</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-200">
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">#</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Description</th>
                            <th class="text-right py-2 text-xs text-gray-500 font-medium">Amount</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Status</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for co in change_orders %}
                        <tr class="border-b border-gray-100">
                            <td class="py-2 font-medium">{{ co.change_order_number or loop.index }}</td>
                            <td class="py-2 text-gray-600">{{ co.description or '-' }}</td>
                            <td class="py-2 text-right font-medium {% if co.change_value > 0 %}text-red-600{% else %}text-green-600{% endif %}">
                                {% if co.change_value > 0 %}+{% endif %}{{ co.change_value|currency_full }}
                            </td>
                            <td class="py-2">
                                <span class="px-2 py-0.5 text-xs rounded-full
                                    {% if co.status == 'Approved' %}bg-green-100 text-green-700
                                    {% elif co.status == 'Pending' %}bg-yellow-100 text-yellow-700
                                    {% else %}bg-gray-100 text-gray-700{% endif %}">
                                    {{ co.status }}
                                </span>
                            </td>
                            <td class="py-2 text-gray-500">{{ co.requested_date|date if co.requested_date else '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        {% if payments %}
        <div class="bg-white rounded-xl shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Payments ({{ payments|length }})</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-200">
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Invoice</th>
                            <th class="text-right py-2 text-xs text-gray-500 font-medium">Amount</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Status</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in payments %}
                        <tr class="border-b border-gray-100">
                            <td class="py-2 font-medium text-gray-900">{{ p.invoice_number or '-' }}</td>
                            <td class="py-2 text-right font-medium">{{ p.amount|currency_full }}</td>
                            <td class="py-2">
                                <span class="px-2 py-0.5 text-xs rounded-full
                                    {% if p.status == 'Paid' %}bg-green-100 text-green-700
                                    {% elif p.status == 'Pending' %}bg-yellow-100 text-yellow-700
                                    {% else %}bg-gray-100 text-gray-700{% endif %}">
                                    {{ p.status }}
                                </span>
                            </td>
                            <td class="py-2 text-gray-500">{{ p.payment_date|date if p.payment_date else '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Phases Tab -->
    {% if phases %}
    <div x-show="tab === 'phases'" style="display: none;">
        <div class="space-y-4">
            {% for phase in phases %}
            <div class="bg-white rounded-xl shadow-sm p-5">
                <div class="flex items-center justify-between mb-3">
                    <div>
                        <h3 class="font-semibold text-gray-900">{{ phase.phase_name }}</h3>
                        {% if phase.start_date or phase.end_date %}
                        <p class="text-sm text-gray-500">
                            {{ phase.start_date|date if phase.start_date else 'TBD' }} &mdash; {{ phase.end_date|date if phase.end_date else 'TBD' }}
                        </p>
                        {% endif %}
                    </div>
                    <span class="px-2 py-1 text-xs font-medium rounded-full
                        {% if phase.status == 'Completed' %}bg-green-100 text-green-700
                        {% elif phase.status == 'In Progress' %}bg-blue-100 text-blue-700
                        {% else %}bg-gray-100 text-gray-700{% endif %}">
                        {{ phase.status }}
                    </span>
                </div>
                <div class="flex items-center gap-3">
                    <div class="flex-1 bg-gray-200 rounded-full h-2">
                        <div class="h-2 rounded-full {% if phase.percent_complete >= 100 %}bg-green-500{% elif phase.percent_complete >= 50 %}bg-blue-500{% else %}bg-yellow-500{% endif %}"
                             style="width: {{ phase.percent_complete }}%;"></div>
                    </div>
                    <span class="text-sm font-medium text-gray-700">{{ phase.percent_complete|int }}%</span>
                </div>
                {% if phase.notes %}
                <p class="text-sm text-gray-500 mt-2">{{ phase.notes }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Milestones Tab -->
    {% if milestones %}
    <div x-show="tab === 'milestones'" style="display: none;">
        <div class="bg-white rounded-xl shadow-sm p-6">
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-200">
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Milestone</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Planned Date</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Actual Date</th>
                            <th class="text-right py-2 text-xs text-gray-500 font-medium">Progress</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in milestones %}
                        <tr class="border-b border-gray-100">
                            <td class="py-2 font-medium text-gray-900">{{ m.title }}</td>
                            <td class="py-2 text-gray-600">{{ m.planned_date|date if m.planned_date else '-' }}</td>
                            <td class="py-2 text-gray-600">{{ m.actual_date|date if m.actual_date else '-' }}</td>
                            <td class="py-2 text-right font-medium">{{ m.percent_complete|int }}%</td>
                            <td class="py-2">
                                <span class="px-2 py-0.5 text-xs rounded-full
                                    {% if m.status == 'Completed' %}bg-green-100 text-green-700
                                    {% elif m.status == 'In Progress' %}bg-blue-100 text-blue-700
                                    {% else %}bg-gray-100 text-gray-700{% endif %}">
                                    {{ m.status }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Inspections Tab -->
    {% if inspections %}
    <div x-show="tab === 'inspections'" style="display: none;">
        <div class="bg-white rounded-xl shadow-sm p-6">
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-gray-200">
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Date</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Type</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Inspector</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Result</th>
                            <th class="text-right py-2 text-xs text-gray-500 font-medium">Deficiencies</th>
                            <th class="text-left py-2 text-xs text-gray-500 font-medium">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for i in inspections %}
                        <tr class="border-b border-gray-100">
                            <td class="py-2 text-gray-600">{{ i.inspection_date|date if i.inspection_date else '-' }}</td>
                            <td class="py-2 text-gray-900">{{ i.inspection_type or '-' }}</td>
                            <td class="py-2 text-gray-600">{{ i.inspector_name or '-' }}</td>
                            <td class="py-2">
                                <span class="px-2 py-0.5 text-xs rounded-full
                                    {% if i.status == 'Pass' %}bg-green-100 text-green-700
                                    {% elif i.status == 'Fail' %}bg-red-100 text-red-700
                                    {% else %}bg-yellow-100 text-yellow-700{% endif %}">
                                    {{ i.status }}
                                </span>
                            </td>
                            <td class="py-2 text-right">{{ i.deficiency_count }}</td>
                            <td class="py-2 text-gray-500 max-w-xs truncate">{{ i.notes or '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

with open(os.path.join(template_dir, 'contract_detail.html'), 'w', encoding='utf-8') as f:
    f.write(content)

print("contract_detail.html written successfully")
