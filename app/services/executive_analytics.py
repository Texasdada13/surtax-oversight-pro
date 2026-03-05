"""
Executive Analytics Service
Provides predictive analytics, risk scoring, and executive-level insights.
Adapted from contract-oversight-system to use Flask's request-scoped DB.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ExecutiveAnalytics:
    """Provides executive-level analytics and predictions."""

    def __init__(self, cursor):
        self.cursor = cursor

    def calculate_burn_rate(self, contract: Dict) -> float:
        """Calculate monthly burn rate (spending rate)."""
        total_paid = contract.get('total_paid', 0) or 0
        start_date_str = contract.get('start_date')

        if not start_date_str or total_paid == 0:
            return 0.0

        try:
            start_date = datetime.strptime(str(start_date_str)[:10], '%Y-%m-%d')
        except (ValueError, TypeError):
            return 0.0

        months_elapsed = max((datetime.now().year - start_date.year) * 12 +
                           (datetime.now().month - start_date.month), 1)
        return round(total_paid / months_elapsed, 2)

    def forecast_budget_at_completion(self, contract: Dict) -> float:
        """
        Forecast final budget using EVM: EAC = BAC / CPI
        where CPI = Earned Value / Actual Cost.
        """
        bac = contract.get('current_amount', 0) or 0
        total_paid = contract.get('total_paid', 0) or 0
        pct = (contract.get('percent_complete', 0) or 0) / 100.0

        if pct == 0 or total_paid == 0:
            return bac

        earned_value = bac * pct
        cpi = earned_value / total_paid if total_paid > 0 else 1.0
        forecast = bac / cpi if cpi > 0 else bac

        return round(forecast, 2)

    def predict_completion_date(self, contract: Dict) -> Optional[str]:
        """Predict completion date based on current velocity."""
        start_str = contract.get('start_date')
        pct = contract.get('percent_complete', 0) or 0
        planned_end = contract.get('current_end_date')

        if not start_str or pct == 0:
            return planned_end

        try:
            start = datetime.strptime(str(start_str)[:10], '%Y-%m-%d')
        except (ValueError, TypeError):
            return planned_end

        days_elapsed = (datetime.now() - start).days
        if days_elapsed <= 0:
            return planned_end

        velocity = pct / days_elapsed
        if velocity <= 0:
            return planned_end

        remaining_days = (100 - pct) / velocity
        expected = datetime.now() + timedelta(days=remaining_days)
        return expected.strftime('%Y-%m-%d')

    def calculate_risk_probability(self, contract: Dict) -> Tuple[float, str]:
        """Calculate risk probability score (0-100) using weighted factors."""
        health = contract.get('overall_health_score', 50) or 50
        cost_var = contract.get('cost_variance_score', 50) or 50
        sched_var = contract.get('schedule_variance_score', 50) or 50
        co_count = contract.get('change_order_count', 0) or 0
        value = contract.get('current_amount', 0) or 0
        pct = contract.get('percent_complete', 0) or 0

        health_risk = 100 - health
        cost_risk = 100 - cost_var
        schedule_risk = 100 - sched_var
        co_risk = min(co_count * 15, 100)

        if value > 10_000_000:
            complexity_risk = 80
        elif value > 5_000_000:
            complexity_risk = 60
        elif value > 1_000_000:
            complexity_risk = 40
        else:
            complexity_risk = 20

        if pct < 25:
            progress_risk = 60
        elif pct < 50:
            progress_risk = 40
        elif pct < 75:
            progress_risk = 20
        else:
            progress_risk = 10

        risk_score = (
            health_risk * 0.30 +
            cost_risk * 0.20 +
            schedule_risk * 0.20 +
            co_risk * 0.10 +
            complexity_risk * 0.10 +
            progress_risk * 0.10
        )

        if risk_score >= 70:
            category = 'High'
        elif risk_score >= 50:
            category = 'Medium'
        elif risk_score >= 30:
            category = 'Low'
        else:
            category = 'Very Low'

        return round(risk_score, 1), category

    def generate_executive_summary(self) -> str:
        """Generate auto-generated executive summary text."""
        self.cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
                SUM(current_amount) as total_value,
                SUM(total_paid) as total_paid,
                AVG(overall_health_score) as avg_health,
                SUM(CASE WHEN overall_health_score < 50 THEN 1 ELSE 0 END) as at_risk,
                SUM(CASE WHEN overall_health_score < 30 THEN 1 ELSE 0 END) as critical
            FROM contracts WHERE is_deleted = 0
        ''')
        stats = self.cursor.fetchone()
        if not stats:
            return "No contract data available."

        stats = dict(stats)
        avg_health = stats.get('avg_health', 0) or 0
        at_risk = stats.get('at_risk', 0) or 0
        critical = stats.get('critical', 0) or 0
        total_value = stats.get('total_value', 0) or 0

        # Budget variance
        self.cursor.execute('''
            SELECT SUM(current_amount - original_amount) as variance
            FROM contracts WHERE is_deleted = 0 AND original_amount > 0
        ''')
        var_row = self.cursor.fetchone()
        variance = (dict(var_row).get('variance', 0) or 0) if var_row else 0
        var_pct = (variance / total_value * 100) if total_value > 0 else 0

        parts = []

        if avg_health >= 70:
            parts.append(f"Portfolio health is healthy at {avg_health:.0f}/100.")
        elif avg_health >= 50:
            parts.append(f"Portfolio health is stable with some concerns at {avg_health:.0f}/100.")
        else:
            parts.append(f"Portfolio health is at significant risk at {avg_health:.0f}/100.")

        if critical > 0:
            parts.append(f"{critical} project{'s' if critical != 1 else ''} in critical status requiring immediate action.")
        elif at_risk > 0:
            parts.append(f"{at_risk} project{'s' if at_risk != 1 else ''} at risk and requiring monitoring.")
        else:
            parts.append("All projects are on track.")

        if var_pct > 10:
            parts.append(f"Portfolio is {var_pct:.1f}% over budget—cost controls needed.")
        elif var_pct > 5:
            parts.append(f"Portfolio is {var_pct:.1f}% over budget—monitoring recommended.")
        else:
            parts.append("Budget performance is on target.")

        return " ".join(parts)

    def get_contract_analytics(self, contract: Dict) -> Dict:
        """Get all analytics for a single contract."""
        burn_rate = self.calculate_burn_rate(contract)
        forecast = self.forecast_budget_at_completion(contract)
        expected_date = self.predict_completion_date(contract)
        risk_score, risk_cat = self.calculate_risk_probability(contract)

        return {
            'burn_rate_monthly': burn_rate,
            'forecast_at_completion': forecast,
            'expected_completion_date': expected_date,
            'risk_probability_score': risk_score,
            'risk_category': risk_cat,
            'cost_performance_index': round(
                ((contract.get('current_amount', 0) or 0) * (contract.get('percent_complete', 0) or 0) / 100) /
                max(contract.get('total_paid', 1) or 1, 1), 2
            ),
        }
