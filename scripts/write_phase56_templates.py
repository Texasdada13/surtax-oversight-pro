"""Write Phase 5+6 templates: tools and documents."""
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'app', 'templates')
templates = {}

# ── TOOLS TEMPLATES ──

templates['tools/ask.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6" x-data="askAI()">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Ask AI Assistant</h1>
        <p class="text-gray-500">Get AI-powered answers about contracts, budgets, and project performance</p>
    </div>

    <!-- Guided Prompts -->
    <div class="flex flex-wrap gap-2">
        {% for p in guided_prompts %}
        <button @click="askQuestion('{{ p.question }}')"
                class="px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors border border-blue-200">
            {{ p.label }}
        </button>
        {% endfor %}
    </div>

    <!-- Chat Messages -->
    <div class="bg-white rounded-xl shadow-sm border min-h-[300px] max-h-[500px] overflow-y-auto p-4 space-y-4" id="chat-messages">
        <template x-for="msg in messages" :key="msg.id">
            <div :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
                <div :class="msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'"
                     class="rounded-xl px-4 py-3 max-w-[80%] text-sm whitespace-pre-wrap" x-text="msg.content"></div>
            </div>
        </template>
        <div x-show="loading" class="flex justify-start">
            <div class="bg-gray-100 rounded-xl px-4 py-3 text-sm text-gray-500">
                <span class="animate-pulse">Thinking...</span>
            </div>
        </div>
        <div x-show="messages.length === 0 && !loading" class="text-center py-12 text-gray-400">
            <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
            </svg>
            <p>Ask a question or click a guided prompt above</p>
        </div>
    </div>

    <!-- Input -->
    <div class="flex gap-2">
        <input type="text" x-model="question" @keydown.enter="askQuestion()"
               placeholder="Ask about contracts, budgets, vendors..."
               class="flex-1 px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
        <button @click="askQuestion()" :disabled="loading || !question.trim()"
                class="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 text-sm font-medium">
            Send
        </button>
    </div>
</div>

<script>
function askAI() {
    return {
        question: '',
        messages: [],
        loading: false,
        msgId: 0,
        askQuestion(q) {
            const text = q || this.question.trim();
            if (!text || this.loading) return;
            this.question = '';
            this.messages.push({id: ++this.msgId, role: 'user', content: text});
            this.loading = true;
            this.$nextTick(() => {
                document.getElementById('chat-messages').scrollTop = 99999;
            });
            fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: text})
            })
            .then(r => r.json())
            .then(data => {
                this.messages.push({id: ++this.msgId, role: 'assistant', content: data.answer || data.error || 'No response'});
                this.loading = false;
                this.$nextTick(() => {
                    document.getElementById('chat-messages').scrollTop = 99999;
                });
            })
            .catch(err => {
                this.messages.push({id: ++this.msgId, role: 'assistant', content: 'Error: ' + err.message});
                this.loading = false;
            });
        }
    }
}
</script>
{% endblock %}
'''

templates['tools/meeting.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Meeting Preparation</h1>
            <p class="text-gray-500">Key data points and talking points for your next committee meeting</p>
        </div>
        <a href="{{ url_for('tools.meeting_present') }}" target="_blank"
           class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path></svg>
            Present Full Screen
        </a>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
            <p class="text-3xl font-bold text-gray-900">{{ stats.active or 0 }}</p>
            <p class="text-sm text-gray-500">Active Projects</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
            <p class="text-3xl font-bold text-blue-600">{{ (stats.total_budget or 0)|currency_short }}</p>
            <p class="text-sm text-gray-500">Total Budget</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
            <p class="text-3xl font-bold {% if (stats.delayed or 0) > 0 %}text-red-600{% else %}text-green-600{% endif %}">{{ stats.delayed or 0 }}</p>
            <p class="text-sm text-gray-500">Delayed</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
            <p class="text-3xl font-bold {% if (stats.avg_health or 0) >= 70 %}text-green-600{% elif (stats.avg_health or 0) >= 50 %}text-yellow-600{% else %}text-red-600{% endif %}">{{ "%.0f"|format(stats.avg_health or 0) }}</p>
            <p class="text-sm text-gray-500">Avg Health</p>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Open Concerns -->
        <div class="bg-white rounded-xl shadow-sm border">
            <div class="p-4 border-b"><h3 class="font-semibold text-gray-900">Open Concerns</h3></div>
            <div class="p-4 space-y-2">
                {% for c in concerns %}
                <div class="p-3 rounded-lg bg-{{ 'red' if c.severity == 'Critical' else 'yellow' if c.severity == 'High' else 'gray' }}-50 border">
                    <p class="font-medium text-sm text-gray-900">{{ c.title }}</p>
                    <p class="text-xs text-gray-500">{{ c.contract_title or '' }} &bull; {{ c.severity }} &bull; {{ c.created_date|date if c.created_date else '' }}</p>
                </div>
                {% endfor %}
                {% if not concerns %}
                <p class="text-gray-400 text-sm py-4 text-center">No open concerns</p>
                {% endif %}
            </div>
        </div>

        <!-- Action Items -->
        <div class="bg-white rounded-xl shadow-sm border">
            <div class="p-4 border-b"><h3 class="font-semibold text-gray-900">Open Action Items</h3></div>
            <div class="p-4 space-y-2">
                {% for a in actions %}
                <div class="p-3 rounded-lg bg-gray-50 border flex justify-between items-start">
                    <div>
                        <p class="font-medium text-sm text-gray-900">{{ a.action_item }}</p>
                        <p class="text-xs text-gray-500">{{ a.assignee or 'Unassigned' }} &bull; Due: {{ a.due_date|date if a.due_date else 'TBD' }}</p>
                    </div>
                    <span class="px-2 py-0.5 text-xs rounded-full
                        {% if a.priority == 'High' %}bg-red-100 text-red-700
                        {% elif a.priority == 'Medium' %}bg-yellow-100 text-yellow-700
                        {% else %}bg-gray-100 text-gray-600{% endif %}">{{ a.priority }}</span>
                </div>
                {% endfor %}
                {% if not actions %}
                <p class="text-gray-400 text-sm py-4 text-center">No open action items</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

templates['tools/meeting_present.html'] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Surtax Oversight - Meeting Presentation</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen">
    <div class="max-w-6xl mx-auto p-8">
        <!-- Header -->
        <div class="text-center mb-12">
            <h1 class="text-4xl font-bold mb-2">Surtax Oversight Pro</h1>
            <p class="text-xl text-slate-400">Marion County Portfolio Overview</p>
            <p class="text-sm text-slate-500 mt-2">{{ now().strftime('%B %d, %Y') if now is defined else '' }}</p>
        </div>

        <!-- KPI Cards -->
        <div class="grid grid-cols-4 gap-6 mb-12">
            <div class="bg-slate-800 rounded-2xl p-6 text-center border border-slate-700">
                <p class="text-5xl font-bold text-white">{{ stats.active or 0 }}</p>
                <p class="text-slate-400 mt-2">Active Projects</p>
            </div>
            <div class="bg-slate-800 rounded-2xl p-6 text-center border border-slate-700">
                <p class="text-5xl font-bold text-blue-400">${{ "%.1f"|format((stats.total_budget or 0) / 1000000) }}M</p>
                <p class="text-slate-400 mt-2">Total Budget</p>
            </div>
            <div class="bg-slate-800 rounded-2xl p-6 text-center border border-slate-700">
                <p class="text-5xl font-bold {% if (stats.delayed or 0) > 0 %}text-red-400{% else %}text-green-400{% endif %}">{{ stats.delayed or 0 }}</p>
                <p class="text-slate-400 mt-2">Delayed</p>
            </div>
            <div class="bg-slate-800 rounded-2xl p-6 text-center border border-slate-700">
                <p class="text-5xl font-bold {% if (stats.avg_health or 0) >= 70 %}text-green-400{% elif (stats.avg_health or 0) >= 50 %}text-yellow-400{% else %}text-red-400{% endif %}">
                    {{ "%.0f"|format(stats.avg_health or 0) }}
                </p>
                <p class="text-slate-400 mt-2">Avg Health Score</p>
            </div>
        </div>

        <!-- Budget Utilization -->
        <div class="bg-slate-800 rounded-2xl p-6 mb-8 border border-slate-700">
            <h3 class="text-lg font-semibold mb-4">Budget Utilization</h3>
            {% set spend_pct = ((stats.total_spent or 0) / (stats.total_budget or 1) * 100) %}
            <div class="w-full bg-slate-700 rounded-full h-6">
                <div class="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-3 text-sm font-medium" style="width: {{ [spend_pct, 100]|min }}%">
                    {{ "%.0f"|format(spend_pct) }}%
                </div>
            </div>
            <div class="flex justify-between mt-2 text-sm text-slate-400">
                <span>${{ "%.1f"|format((stats.total_spent or 0) / 1000000) }}M spent</span>
                <span>${{ "%.1f"|format((stats.total_budget or 0) / 1000000) }}M budget</span>
            </div>
        </div>

        <!-- Category Breakdown -->
        {% if categories %}
        <div class="bg-slate-800 rounded-2xl p-6 border border-slate-700">
            <h3 class="text-lg font-semibold mb-4">By Category</h3>
            <div class="grid grid-cols-2 gap-4">
                {% for cat in categories %}
                <div class="flex justify-between items-center p-3 bg-slate-700/50 rounded-lg">
                    <div>
                        <p class="font-medium">{{ cat.surtax_category }}</p>
                        <p class="text-sm text-slate-400">{{ cat.count }} projects</p>
                    </div>
                    <p class="text-xl font-bold text-blue-400">${{ "%.1f"|format((cat.budget or 0) / 1000000) }}M</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div class="text-center mt-8 text-sm text-slate-600">
            Press ESC or click to close
        </div>
    </div>
</body>
</html>
'''

templates['tools/compliance.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Compliance Dashboard</h1>
        <p class="text-gray-500">Monitor insurance, bonding, board approvals, and procurement compliance</p>
    </div>

    <!-- Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Total Active Contracts</p>
            <p class="text-3xl font-bold text-gray-900">{{ total }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Fully Compliant</p>
            <p class="text-3xl font-bold text-green-600">{{ compliant }}</p>
            <p class="text-xs text-gray-400">{{ "%.0f"|format(compliant / (total or 1) * 100) }}% compliance rate</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <p class="text-sm text-gray-500">Issues Found</p>
            <p class="text-3xl font-bold text-red-600">{{ issues|length }}</p>
        </div>
    </div>

    <!-- Issues -->
    {% if issues %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b"><h3 class="font-semibold text-gray-900">Compliance Issues</h3></div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Contract</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Issue</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Severity</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for i in issues %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3">
                            <a href="{{ url_for('contracts.contract_detail', contract_id=i.contract_id) }}" class="text-blue-600 hover:underline">{{ i.contract }}</a>
                        </td>
                        <td class="px-4 py-3 text-gray-600">{{ i.issue }}</td>
                        <td class="px-4 py-3 text-center">
                            <span class="px-2 py-0.5 text-xs rounded-full
                                {% if i.severity == 'Critical' %}bg-red-100 text-red-700
                                {% elif i.severity == 'High' %}bg-orange-100 text-orange-700
                                {% else %}bg-yellow-100 text-yellow-700{% endif %}">
                                {{ i.severity }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% else %}
    <div class="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
        <p class="text-green-800 font-medium text-lg">All Contracts Compliant</p>
        <p class="text-green-600 text-sm mt-1">No compliance issues found across active contracts</p>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

templates['tools/map_view.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Project Map</h1>
        <p class="text-gray-500">Geographic view of project locations</p>
    </div>

    {% if projects %}
    <div class="bg-white rounded-xl shadow-sm border p-5">
        <div class="bg-gray-100 rounded-lg" style="height: 500px; position: relative;">
            <div id="map" style="width: 100%; height: 100%; border-radius: 0.5rem;"></div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {% for p in projects %}
        <div class="bg-white rounded-lg border p-3 text-sm hover:shadow-sm">
            <a href="{{ url_for('contracts.contract_detail', contract_id=p.contract_id) }}" class="font-medium text-blue-600 hover:underline">{{ p.title|truncate(40) }}</a>
            <p class="text-xs text-gray-500">{{ p.project_location or 'No address' }}</p>
            <div class="flex gap-2 mt-1">
                <span class="text-xs text-gray-400">{{ p.surtax_category or 'General' }}</span>
                <span class="text-xs text-gray-400">{{ (p.current_amount or 0)|currency_short }}</span>
            </div>
        </div>
        {% endfor %}
    </div>

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const map = L.map('map').setView([29.1872, -82.1301], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        }).addTo(map);
        const projects = {{ projects|tojson }};
        projects.forEach(p => {
            if (p.latitude && p.longitude) {
                const color = (p.overall_health_score || 50) >= 70 ? '#22c55e' : (p.overall_health_score || 50) >= 50 ? '#eab308' : '#ef4444';
                L.circleMarker([p.latitude, p.longitude], {radius: 8, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.8})
                    .addTo(map)
                    .bindPopup('<strong>' + p.title + '</strong><br>' + (p.project_location || '') + '<br>' + (p.surtax_category || ''));
            }
        });
    </script>
    {% else %}
    <div class="bg-gray-50 border rounded-xl p-12 text-center text-gray-400">
        <p class="text-lg">No projects with location data</p>
        <p class="text-sm mt-1">Add latitude/longitude to contracts to see them on the map</p>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

templates['tools/public_portal.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-8 text-white">
        <h1 class="text-3xl font-bold">Marion County Surtax Transparency Portal</h1>
        <p class="text-blue-200 mt-2">Public access to project information, budgets, and progress</p>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-gray-900">{{ stats.total or 0 }}</p>
            <p class="text-sm text-gray-500">Total Projects</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-green-600">{{ stats.active or 0 }}</p>
            <p class="text-sm text-gray-500">Active</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-blue-600">{{ stats.completed or 0 }}</p>
            <p class="text-sm text-gray-500">Completed</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-gray-900">{{ (stats.total_budget or 0)|currency_short }}</p>
            <p class="text-sm text-gray-500">Total Budget</p>
        </div>
    </div>

    <!-- Budget Progress -->
    <div class="bg-white rounded-xl shadow-sm border p-5">
        <h3 class="font-semibold text-gray-900 mb-3">Budget Utilization</h3>
        {% set spend_pct = ((stats.total_spent or 0) / (stats.total_budget or 1) * 100) %}
        <div class="w-full bg-gray-200 rounded-full h-4">
            <div class="bg-blue-600 h-4 rounded-full" style="width: {{ [spend_pct, 100]|min }}%"></div>
        </div>
        <div class="flex justify-between mt-1 text-sm text-gray-500">
            <span>{{ (stats.total_spent or 0)|currency_short }} spent ({{ "%.0f"|format(spend_pct) }}%)</span>
            <span>{{ (stats.total_budget or 0)|currency_short }} total</span>
        </div>
    </div>

    <!-- Project List -->
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b"><h3 class="font-semibold text-gray-900">All Projects</h3></div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Project</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Category</th>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Vendor</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Budget</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Progress</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for p in projects %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3 font-medium text-gray-900">{{ p.title|truncate(40) }}</td>
                        <td class="px-4 py-3 text-gray-500">{{ p.surtax_category or 'General' }}</td>
                        <td class="px-4 py-3 text-gray-500">{{ p.vendor_name or 'N/A' }}</td>
                        <td class="px-4 py-3 text-right">{{ (p.current_amount or 0)|currency_short }}</td>
                        <td class="px-4 py-3">
                            <div class="flex items-center gap-2">
                                <div class="flex-1 bg-gray-200 rounded-full h-1.5">
                                    <div class="bg-blue-500 h-1.5 rounded-full" style="width: {{ p.percent_complete or 0 }}%"></div>
                                </div>
                                <span class="text-xs text-gray-500">{{ p.percent_complete or 0 }}%</span>
                            </div>
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="px-2 py-0.5 text-xs rounded-full
                                {% if p.status == 'Active' %}bg-green-100 text-green-700
                                {% elif p.status == 'Complete' %}bg-blue-100 text-blue-700
                                {% else %}bg-gray-100 text-gray-600{% endif %}">
                                {{ p.status }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="text-center text-sm text-gray-400 py-4">
        Data provided in compliance with Florida Sunshine Law. Updated regularly.
    </div>
</div>
{% endblock %}
'''

# ── DOCUMENT TEMPLATES ──

templates['documents/documents.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-2xl font-bold text-gray-900">Document Library</h1>
            <p class="text-gray-500">Contracts, reports, and supporting documentation</p>
        </div>
        <span class="px-3 py-1 bg-gray-100 rounded-full text-sm">{{ total }} documents</span>
    </div>

    {% if doc_types %}
    {% for dtype, docs in doc_types.items() %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-4 border-b flex items-center justify-between">
            <h3 class="font-semibold text-gray-900">{{ dtype }}</h3>
            <span class="text-sm text-gray-400">{{ docs|length }} files</span>
        </div>
        <div class="divide-y">
            {% for d in docs %}
            <div class="p-4 flex items-center justify-between hover:bg-gray-50">
                <div class="flex items-center gap-3">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                    </svg>
                    <div>
                        <p class="font-medium text-gray-900 text-sm">{{ d.title }}</p>
                        <p class="text-xs text-gray-500">
                            {{ d.contract_title or 'General' }}
                            {% if d.uploaded_date %} &bull; {{ d.uploaded_date|date }}{% endif %}
                            {% if d.file_size %} &bull; {{ "%.1f"|format(d.file_size / 1024) }} KB{% endif %}
                        </p>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}
    {% else %}
    <div class="bg-white rounded-xl shadow-sm border p-12 text-center text-gray-400">
        <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
        </svg>
        <p class="text-lg">No documents uploaded yet</p>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

templates['documents/meeting_minutes.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div>
        <h1 class="text-2xl font-bold text-gray-900">Meeting Minutes</h1>
        <p class="text-gray-500">Committee meeting records and decisions</p>
    </div>

    {% if meetings %}
    <div class="space-y-4">
        {% for m in meetings %}
        <div class="bg-white rounded-xl shadow-sm border p-5">
            <div class="flex items-start justify-between">
                <div>
                    <h3 class="font-semibold text-gray-900">{{ m.meeting_type or 'Regular' }} Meeting</h3>
                    <p class="text-sm text-gray-500">{{ m.meeting_date|date if m.meeting_date else 'No date' }}{% if m.location %} &bull; {{ m.location }}{% endif %}</p>
                </div>
                <span class="px-2 py-0.5 text-xs rounded-full
                    {% if m.status == 'Approved' %}bg-green-100 text-green-700
                    {% elif m.status == 'Draft' %}bg-yellow-100 text-yellow-700
                    {% else %}bg-gray-100 text-gray-600{% endif %}">
                    {{ m.status or 'Draft' }}
                </span>
            </div>
            {% if m.agenda %}
            <div class="mt-3 text-sm text-gray-600">
                <p class="font-medium text-gray-700">Agenda:</p>
                <p>{{ m.agenda|truncate(200) }}</p>
            </div>
            {% endif %}
            {% if m.decisions %}
            <div class="mt-2 text-sm text-gray-600">
                <p class="font-medium text-gray-700">Decisions:</p>
                <p>{{ m.decisions|truncate(200) }}</p>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="bg-white rounded-xl shadow-sm border p-12 text-center text-gray-400">
        <p class="text-lg">No meeting minutes recorded yet</p>
    </div>
    {% endif %}
</div>
{% endblock %}
'''

templates['documents/annual_report.html'] = '''{% extends "base.html" %}
{% block content %}
<div class="space-y-6">
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-8 text-white">
        <h1 class="text-3xl font-bold">Annual Report</h1>
        <p class="text-blue-200 mt-1">Marion County Surtax Oversight — Portfolio Summary</p>
    </div>

    <!-- Portfolio Overview -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-gray-900">{{ stats.total_contracts or 0 }}</p>
            <p class="text-sm text-gray-500">Total Contracts</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-green-600">{{ stats.active or 0 }}</p>
            <p class="text-sm text-gray-500">Active</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-blue-600">{{ stats.completed or 0 }}</p>
            <p class="text-sm text-gray-500">Completed</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-3xl font-bold text-gray-900">{{ (stats.total_current or 0)|currency_short }}</p>
            <p class="text-sm text-gray-500">Total Budget</p>
        </div>
    </div>

    <!-- Financial Summary -->
    <div class="bg-white rounded-xl shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Financial Summary</h3>
        <div class="grid grid-cols-3 gap-6">
            <div>
                <p class="text-sm text-gray-500">Original Budget</p>
                <p class="text-xl font-bold">{{ (stats.total_original or 0)|currency_short }}</p>
            </div>
            <div>
                <p class="text-sm text-gray-500">Current Budget</p>
                <p class="text-xl font-bold">{{ (stats.total_current or 0)|currency_short }}</p>
            </div>
            <div>
                <p class="text-sm text-gray-500">Total Spent</p>
                <p class="text-xl font-bold text-blue-600">{{ (stats.total_spent or 0)|currency_short }}</p>
            </div>
        </div>
        <div class="mt-4">
            {% set spend_pct = ((stats.total_spent or 0) / (stats.total_current or 1) * 100) %}
            <div class="w-full bg-gray-200 rounded-full h-3">
                <div class="bg-blue-600 h-3 rounded-full" style="width: {{ [spend_pct, 100]|min }}%"></div>
            </div>
            <p class="text-xs text-gray-400 mt-1">{{ "%.1f"|format(spend_pct) }}% of budget spent</p>
        </div>
    </div>

    <!-- Health & Risk -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-sm text-gray-500">Avg Health Score</p>
            <p class="text-4xl font-bold {% if (stats.avg_health or 0) >= 70 %}text-green-600{% elif (stats.avg_health or 0) >= 50 %}text-yellow-600{% else %}text-red-600{% endif %}">
                {{ "%.0f"|format(stats.avg_health or 0) }}
            </p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-sm text-gray-500">Delayed Projects</p>
            <p class="text-4xl font-bold text-red-600">{{ stats.delayed or 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 text-center">
            <p class="text-sm text-gray-500">Over Budget</p>
            <p class="text-4xl font-bold text-orange-600">{{ stats.over_budget or 0 }}</p>
        </div>
    </div>

    <!-- By Category -->
    {% if categories %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b"><h3 class="font-semibold text-gray-900">Spending by Category</h3></div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Category</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Projects</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Budget</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Spent</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Avg Health</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for c in categories %}
                    <tr>
                        <td class="px-4 py-3 font-medium">{{ c.surtax_category }}</td>
                        <td class="px-4 py-3 text-center">{{ c.count }}</td>
                        <td class="px-4 py-3 text-right">{{ (c.budget or 0)|currency_short }}</td>
                        <td class="px-4 py-3 text-right">{{ (c.spent or 0)|currency_short }}</td>
                        <td class="px-4 py-3 text-center">{{ "%.0f"|format(c.avg_health or 0) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Top Vendors -->
    {% if top_vendors %}
    <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-5 border-b"><h3 class="font-semibold text-gray-900">Top 10 Vendors by Value</h3></div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left font-medium text-gray-600">Vendor</th>
                        <th class="px-4 py-3 text-center font-medium text-gray-600">Contracts</th>
                        <th class="px-4 py-3 text-right font-medium text-gray-600">Total Value</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    {% for v in top_vendors %}
                    <tr>
                        <td class="px-4 py-3 font-medium">{{ v.vendor_name }}</td>
                        <td class="px-4 py-3 text-center">{{ v.contracts }}</td>
                        <td class="px-4 py-3 text-right">{{ (v.total_value or 0)|currency_short }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
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
