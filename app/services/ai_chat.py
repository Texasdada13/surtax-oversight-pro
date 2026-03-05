"""
Claude API-powered AI Chat Service.
Provides intelligent Q&A about contract and surtax data.
"""

import os
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI assistant for the Surtax Oversight Pro dashboard, a government contract and surtax oversight tool for Marion County, Florida.

You help committee members and district staff understand:
- Contract status, budgets, and spending patterns
- Project delays and risk levels
- Vendor performance and compliance
- Surtax revenue and capital project oversight
- Financial trends and forecasting

When answering:
- Be concise and data-driven
- Reference specific numbers when available
- Flag concerning trends or risks
- Suggest follow-up actions when appropriate
- Use professional but accessible language

You have access to the following portfolio data context:
{context}
"""

GUIDED_PROMPTS = [
    {'label': 'Budget Summary', 'question': 'What is the overall budget status of the portfolio?'},
    {'label': 'Delayed Projects', 'question': 'Which projects are currently delayed and by how much?'},
    {'label': 'Vendor Performance', 'question': 'Summarize vendor performance across all contracts.'},
    {'label': 'Risk Assessment', 'question': 'What are the highest risk contracts and why?'},
    {'label': 'Spending Trends', 'question': 'What are the current spending trends and any concerns?'},
    {'label': 'Compliance Status', 'question': 'Are there any compliance issues or missing documentation?'},
]


def get_data_context(cursor) -> str:
    """Build a data context string from the database for Claude."""
    context_parts = []

    # Portfolio overview
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
               SUM(current_amount) as total_budget,
               SUM(total_paid) as total_spent,
               AVG(overall_health_score) as avg_health,
               SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
               SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget
        FROM contracts WHERE is_deleted = 0
    ''')
    row = cursor.fetchone()
    if row:
        stats = dict(row)
        context_parts.append(
            f"Portfolio: {stats['total']} contracts ({stats['active']} active), "
            f"Total budget: ${stats['total_budget'] or 0:,.0f}, "
            f"Total spent: ${stats['total_spent'] or 0:,.0f}, "
            f"Avg health: {stats['avg_health'] or 0:.0f}/100, "
            f"Delayed: {stats['delayed']}, Over budget: {stats['over_budget']}"
        )

    # Top risk contracts
    cursor.execute('''
        SELECT title, vendor_name, current_amount, overall_health_score, risk_level,
               is_delayed, delay_days, is_over_budget, budget_variance_pct
        FROM contracts WHERE is_deleted = 0 AND overall_health_score < 60
        ORDER BY overall_health_score ASC LIMIT 5
    ''')
    risk_contracts = [dict(r) for r in cursor.fetchall()]
    if risk_contracts:
        context_parts.append("High-risk contracts:")
        for c in risk_contracts:
            context_parts.append(
                f"  - {c['title']}: health {c['overall_health_score']:.0f}, "
                f"risk={c['risk_level']}, budget=${c['current_amount'] or 0:,.0f}"
                + (f", delayed {c['delay_days']}d" if c['is_delayed'] else "")
                + (f", {c['budget_variance_pct']:.1f}% over budget" if c['is_over_budget'] else "")
            )

    # Category breakdown
    cursor.execute('''
        SELECT surtax_category, COUNT(*) as count, SUM(current_amount) as budget,
               SUM(total_paid) as spent
        FROM contracts WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category ORDER BY budget DESC
    ''')
    categories = [dict(r) for r in cursor.fetchall()]
    if categories:
        context_parts.append("Spending by category:")
        for c in categories:
            context_parts.append(
                f"  - {c['surtax_category']}: {c['count']} projects, "
                f"budget ${c['budget'] or 0:,.0f}, spent ${c['spent'] or 0:,.0f}"
            )

    return "\n".join(context_parts)


def ask_claude(question: str, cursor, conversation_history: Optional[List] = None) -> Dict:
    """Send a question to Claude API with portfolio data context."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        return {
            'answer': 'Claude API is not configured. Set ANTHROPIC_API_KEY in your .env file to enable AI-powered responses.',
            'suggestions': [p['question'] for p in GUIDED_PROMPTS[:3]],
            'source': 'fallback'
        }

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        context = get_data_context(cursor)
        system = SYSTEM_PROMPT.format(context=context)

        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({'role': 'user', 'content': question})

        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1024,
            system=system,
            messages=messages,
        )

        answer = response.content[0].text

        return {
            'answer': answer,
            'suggestions': [p['question'] for p in GUIDED_PROMPTS[:3]],
            'source': 'claude'
        }

    except ImportError:
        return {
            'answer': 'The anthropic Python package is not installed. Run: pip install anthropic',
            'suggestions': [],
            'source': 'error'
        }
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return {
            'answer': f'Error communicating with Claude API: {str(e)}',
            'suggestions': [],
            'source': 'error'
        }


def get_guided_prompts() -> List[Dict]:
    """Return list of guided prompts for the UI."""
    return GUIDED_PROMPTS
