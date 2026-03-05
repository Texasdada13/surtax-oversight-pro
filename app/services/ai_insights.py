"""
AI-powered insights and predictions.
Generates rule-based insights from project data.
Adapted from florida-school-surtax-oversight (fixed column names).
"""

import sqlite3
from typing import Dict, Any, List


def get_ai_insights(cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
    """Generate AI-powered insights from project data."""
    insights = []
    for fn in [_analyze_budget_trends, _analyze_delay_patterns,
               _analyze_vendor_performance, _analyze_spending_efficiency]:
        result = fn(cursor)
        if result:
            insights.append(result)
    return insights


def _analyze_budget_trends(cursor: sqlite3.Cursor) -> Dict[str, Any]:
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN current_amount > original_amount THEN 1 ELSE 0 END) as increased,
               AVG(CASE WHEN original_amount > 0
                   THEN ((current_amount - original_amount) / original_amount * 100) ELSE 0 END) as avg_change
        FROM contracts
        WHERE is_deleted = 0 AND original_amount IS NOT NULL AND original_amount > 0
    ''')
    row = cursor.fetchone()
    if row and row['total'] > 0:
        pct_increased = (row['increased'] / row['total']) * 100
        avg_change = row['avg_change'] or 0
        if pct_increased > 50:
            return {
                'type': 'trend', 'icon': 'trending-up',
                'title': 'Budget Increases Common',
                'description': f"{pct_increased:.0f}% of projects have seen budget increases, "
                              f"averaging {avg_change:.1f}% above original estimates.",
                'severity': 'warning' if avg_change > 10 else 'info'
            }
    return None


def _analyze_delay_patterns(cursor: sqlite3.Cursor) -> Dict[str, Any]:
    cursor.execute('''
        SELECT surtax_category, COUNT(*) as total,
               SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed,
               AVG(CASE WHEN is_delayed = 1 THEN delay_days ELSE 0 END) as avg_delay
        FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category HAVING total >= 2
        ORDER BY (delayed * 1.0 / total) DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    if row and row['delayed'] > 0:
        delay_rate = (row['delayed'] / row['total']) * 100
        if delay_rate > 30:
            return {
                'type': 'pattern', 'icon': 'clock',
                'title': f"Delays Common in {row['surtax_category']}",
                'description': f"{delay_rate:.0f}% of {row['surtax_category']} projects are delayed, "
                              f"averaging {row['avg_delay']:.0f} days.",
                'severity': 'warning'
            }
    return None


def _analyze_vendor_performance(cursor: sqlite3.Cursor) -> Dict[str, Any]:
    cursor.execute('''
        SELECT vendor_name, COUNT(*) as projects,
               AVG(CASE WHEN is_delayed = 1 THEN 1.0 ELSE 0.0 END) * 100 as delay_rate,
               AVG(CASE WHEN is_over_budget = 1 THEN 1.0 ELSE 0.0 END) * 100 as overbudget_rate
        FROM contracts
        WHERE is_deleted = 0 AND vendor_name IS NOT NULL
        GROUP BY vendor_name HAVING projects >= 2
        ORDER BY (delay_rate + overbudget_rate) DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    if row and (row['delay_rate'] > 50 or row['overbudget_rate'] > 50):
        return {
            'type': 'vendor', 'icon': 'alert-triangle',
            'title': 'Vendor Performance Concern',
            'description': f"{row['vendor_name']} has a {row['delay_rate']:.0f}% delay rate "
                          f"and {row['overbudget_rate']:.0f}% over-budget rate across {row['projects']} projects.",
            'severity': 'critical'
        }
    return None


def _analyze_spending_efficiency(cursor: sqlite3.Cursor) -> Dict[str, Any]:
    cursor.execute('''
        SELECT SUM(current_amount) as budget, SUM(total_paid) as spent,
               AVG(percent_complete) as progress
        FROM contracts WHERE is_deleted = 0 AND status = 'Active'
    ''')
    row = cursor.fetchone()
    if row and row['budget'] and row['budget'] > 0:
        spend_rate = (row['spent'] or 0) / row['budget'] * 100
        progress = row['progress'] or 0
        if spend_rate > progress + 20:
            return {
                'type': 'efficiency', 'icon': 'alert-circle',
                'title': 'Spending Outpacing Progress',
                'description': f"Active projects are {spend_rate:.0f}% through budget "
                              f"but only {progress:.0f}% complete.",
                'severity': 'warning'
            }
        elif progress > spend_rate + 10:
            return {
                'type': 'efficiency', 'icon': 'check-circle',
                'title': 'Good Cost Control',
                'description': f"Active projects are {progress:.0f}% complete "
                              f"with only {spend_rate:.0f}% of budget spent.",
                'severity': 'success'
            }
    return None
