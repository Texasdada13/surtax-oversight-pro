"""
Procurement Benchmarking Module
Based on Coupa 2025 Total Spend Management Benchmark Report.
Copied from contract-oversight-system (stateless).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BENCHMARK_CATEGORIES = {
    'spend_analysis': 'Spend Analysis',
    'supplier_management': 'Supplier Risk & Performance Management',
    'source_to_contract': 'Source-to-Contract',
    'procurement': 'Procurement',
    'cash_liquidity': 'Cash & Liquidity Management',
    'e_invoicing': 'E-Invoicing',
    'expenses': 'Expenses',
    'payments': 'Payments'
}

COUPA_BENCHMARKS = {
    'increase_visibility_managed_spend': {
        'name': 'Increase in Visibility of Managed Spend', 'category': 'spend_analysis',
        'benchmark_value': 24.4, 'unit': 'percent', 'direction': 'higher', 'importance': 'high',
        'description': 'Percentage increase in spend visibility after implementation'
    },
    'supplier_info_mgmt_cycle_time': {
        'name': 'Supplier Onboarding Cycle Time', 'category': 'supplier_management',
        'benchmark_value': 6.6, 'unit': 'business_hours', 'direction': 'lower', 'importance': 'medium',
        'description': 'Time to complete supplier onboarding/updates'
    },
    'on_contract_spend': {
        'name': 'On-Contract Spend', 'category': 'source_to_contract',
        'benchmark_value': 81.1, 'unit': 'percent', 'direction': 'higher', 'importance': 'high',
        'description': 'Percentage of spend under contract coverage'
    },
    'structured_spend': {
        'name': 'Structured Spend', 'category': 'procurement',
        'benchmark_value': 55.3, 'unit': 'percent', 'direction': 'higher', 'importance': 'high',
        'description': 'Spend processed through structured procurement channels'
    },
    'pre_approved_spend': {
        'name': 'Pre-Approved Spend', 'category': 'procurement',
        'benchmark_value': 96.4, 'unit': 'percent', 'direction': 'higher', 'importance': 'critical',
        'description': 'Spend through proper approval workflows'
    },
    'electronic_po_processing': {
        'name': 'Electronic PO Processing Rate', 'category': 'procurement',
        'benchmark_value': 98.8, 'unit': 'percent', 'direction': 'higher', 'importance': 'medium',
        'description': 'Purchase orders processed electronically'
    },
    'electronic_invoice_processing': {
        'name': 'Electronic Invoice Processing Rate', 'category': 'e_invoicing',
        'benchmark_value': 86.2, 'unit': 'percent', 'direction': 'higher', 'importance': 'high',
        'description': 'Invoices processed electronically'
    },
    'first_time_match_rate': {
        'name': 'First-Time Match Rate', 'category': 'e_invoicing',
        'benchmark_value': 97.1, 'unit': 'percent', 'direction': 'higher', 'importance': 'high',
        'description': 'Invoices that match PO on first attempt'
    },
    'invoices_paid_digitally': {
        'name': 'Invoices Paid Digitally', 'category': 'payments',
        'benchmark_value': 96.0, 'unit': 'percent', 'direction': 'higher', 'importance': 'medium',
        'description': 'Payments made through digital channels'
    },
    'expense_lines_within_policy': {
        'name': 'Expense Lines Within Policy', 'category': 'expenses',
        'benchmark_value': 98.9, 'unit': 'percent', 'direction': 'higher', 'importance': 'high',
        'description': 'Expense line items compliant with policy'
    },
}

IMPORTANCE_WEIGHTS = {'critical': 2.0, 'high': 1.5, 'medium': 1.0, 'low': 0.5}


class BenchmarkingEngine:
    """Engine for calculating procurement benchmarks and health scores."""

    def __init__(self):
        self.benchmarks = COUPA_BENCHMARKS
        self.categories = BENCHMARK_CATEGORIES

    def score_kpi(self, kpi_id: str, actual_value: float) -> Dict:
        """Score a single KPI against its benchmark."""
        kpi = self.benchmarks[kpi_id]
        benchmark = kpi['benchmark_value']
        direction = kpi['direction']

        if direction == 'higher':
            gap = actual_value - benchmark
            gap_pct = (gap / benchmark * 100) if benchmark > 0 else 0
            score = min(100, (actual_value / benchmark) * 100) if actual_value < benchmark else min(100, 100 + gap_pct * 0.1)
        else:
            gap = benchmark - actual_value
            gap_pct = (gap / benchmark * 100) if benchmark > 0 else 0
            score = min(100, (benchmark / actual_value) * 100) if actual_value > benchmark else min(100, 100 + gap_pct * 0.1)

        if score >= 90:
            rating = 'Excellent'
        elif score >= 75:
            rating = 'Good'
        elif score >= 60:
            rating = 'Fair'
        elif score >= 40:
            rating = 'Poor'
        else:
            rating = 'Critical'

        return {
            'kpi_id': kpi_id, 'name': kpi['name'], 'category': kpi['category'],
            'actual_value': actual_value, 'benchmark_value': benchmark,
            'unit': kpi['unit'], 'direction': direction,
            'score': round(score, 1), 'gap': round(gap, 2), 'gap_percent': round(gap_pct, 1),
            'rating': rating, 'importance': kpi.get('importance', 'medium'),
            'description': kpi.get('description', ''),
        }

    def calculate_health_score(self, kpi_values: Dict[str, float]) -> Dict:
        """Calculate overall procurement health score."""
        all_scores = []
        category_results = {}

        for cat_id, cat_name in self.categories.items():
            cat_kpis = {k: v for k, v in self.benchmarks.items() if v['category'] == cat_id}
            cat_scores = []
            for kpi_id in cat_kpis:
                if kpi_id in kpi_values:
                    result = self.score_kpi(kpi_id, kpi_values[kpi_id])
                    cat_scores.append(result)
                    all_scores.append(result)

            if cat_scores:
                avg = sum(s['score'] for s in cat_scores) / len(cat_scores)
                category_results[cat_id] = {
                    'name': cat_name, 'score': round(avg, 1),
                    'kpi_count': len(cat_scores), 'kpis': cat_scores
                }

        overall = sum(s['score'] for s in all_scores) / len(all_scores) if all_scores else 0

        if overall >= 90:
            grade, rating = 'A', 'Excellent'
        elif overall >= 80:
            grade, rating = 'B', 'Good'
        elif overall >= 70:
            grade, rating = 'C', 'Fair'
        elif overall >= 60:
            grade, rating = 'D', 'Poor'
        else:
            grade, rating = 'F', 'Critical'

        strengths = [s['name'] for s in sorted(all_scores, key=lambda x: x['score'], reverse=True)
                     if s['rating'] in ('Excellent', 'Good')][:5]
        improvements = [s['name'] for s in sorted(all_scores, key=lambda x: x['score'])
                       if s['rating'] in ('Poor', 'Critical')][:5]

        return {
            'overall_score': round(overall, 1), 'grade': grade, 'rating': rating,
            'categories': category_results,
            'strengths': strengths, 'improvements': improvements,
            'total_kpis': len(all_scores),
        }

    def get_benchmark_summary(self) -> Dict:
        """Get summary of all benchmarks for display."""
        summary = {'total_kpis': len(self.benchmarks), 'categories': {}}
        for cat_id, cat_name in self.categories.items():
            kpis = [
                {'id': k, 'name': v['name'], 'benchmark': v['benchmark_value'],
                 'unit': v['unit'], 'direction': v['direction'],
                 'importance': v.get('importance', 'medium'), 'description': v.get('description', '')}
                for k, v in self.benchmarks.items() if v['category'] == cat_id
            ]
            summary['categories'][cat_id] = {'name': cat_name, 'kpi_count': len(kpis), 'kpis': kpis}
        return summary


_engine = None

def get_benchmarking_engine() -> BenchmarkingEngine:
    global _engine
    if _engine is None:
        _engine = BenchmarkingEngine()
    return _engine
