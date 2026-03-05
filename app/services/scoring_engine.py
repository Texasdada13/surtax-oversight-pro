"""
Contract Scoring Engine
Calculates performance scores, risk levels, and health metrics.
Copied from contract-oversight-system with minimal changes (stateless).
"""

from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ContractScoringEngine:
    """Calculates contract performance and health scores."""

    def __init__(self):
        self.health_weights = {
            'cost_variance': 0.30,
            'schedule_variance': 0.25,
            'performance': 0.25,
            'compliance': 0.20
        }
        self.risk_thresholds = {'critical': 30, 'high': 50, 'medium': 70, 'low': 100}

    def calculate_cost_variance_score(self, contract: Dict) -> float:
        original = contract.get('original_amount', 0) or 0
        current = contract.get('current_amount', 0) or 0
        if original <= 0:
            return 50
        variance_pct = ((current - original) / original) * 100
        if variance_pct <= 0:
            return 100
        elif variance_pct <= 5:
            return 95
        elif variance_pct <= 10:
            return 85
        elif variance_pct <= 15:
            return 70
        elif variance_pct <= 20:
            return 55
        elif variance_pct <= 30:
            return 40
        else:
            return max(20, 40 - (variance_pct - 30))

    def calculate_schedule_variance_score(self, contract: Dict) -> float:
        original_end = contract.get('original_end_date')
        current_end = contract.get('current_end_date')
        start_date = contract.get('start_date')
        if not original_end or not start_date:
            return 50
        try:
            original_end_dt = datetime.fromisoformat(str(original_end)[:10])
            current_end_dt = datetime.fromisoformat(str(current_end or original_end)[:10])
            start_dt = datetime.fromisoformat(str(start_date)[:10])
            original_duration = (original_end_dt - start_dt).days
            if original_duration <= 0:
                return 50
            extension_days = (current_end_dt - original_end_dt).days
            extension_pct = (extension_days / original_duration) * 100
            if extension_pct <= 0:
                return 100
            elif extension_pct <= 5:
                return 90
            elif extension_pct <= 10:
                return 80
            elif extension_pct <= 20:
                return 65
            elif extension_pct <= 30:
                return 50
            else:
                return max(20, 50 - (extension_pct - 30))
        except (ValueError, TypeError):
            return 50

    def calculate_performance_score(self, contract: Dict) -> float:
        return (contract.get('percent_complete', 0) or 0) * 0.7 + 50 * 0.3

    def calculate_compliance_score(self, contract: Dict) -> float:
        score = 100
        if contract.get('requires_insurance') and not contract.get('insurance_verified'):
            score -= 20
        if contract.get('requires_bond') and not contract.get('bond_verified'):
            score -= 15
        if contract.get('award_date') and not contract.get('board_approval_date'):
            if (contract.get('current_amount', 0) or 0) > 50000:
                score -= 25
        if contract.get('is_sole_source') and not contract.get('justification'):
            score -= 15
        return max(0, score)

    def calculate_overall_health(self, contract: Dict) -> float:
        cost = self.calculate_cost_variance_score(contract)
        schedule = self.calculate_schedule_variance_score(contract)
        performance = self.calculate_performance_score(contract)
        compliance = self.calculate_compliance_score(contract)
        health = (
            cost * self.health_weights['cost_variance'] +
            schedule * self.health_weights['schedule_variance'] +
            performance * self.health_weights['performance'] +
            compliance * self.health_weights['compliance']
        )
        return round(health, 1)

    def determine_risk_level(self, health_score: float) -> str:
        if health_score < self.risk_thresholds['critical']:
            return 'Critical'
        elif health_score < self.risk_thresholds['high']:
            return 'High'
        elif health_score < self.risk_thresholds['medium']:
            return 'Medium'
        return 'Low'

    def score_contract(self, contract: Dict) -> Dict:
        contract['cost_variance_score'] = self.calculate_cost_variance_score(contract)
        contract['schedule_variance_score'] = self.calculate_schedule_variance_score(contract)
        contract['performance_score'] = self.calculate_performance_score(contract)
        contract['compliance_score'] = self.calculate_compliance_score(contract)
        contract['overall_health_score'] = self.calculate_overall_health(contract)
        contract['risk_level'] = self.determine_risk_level(contract['overall_health_score'])
        return contract


class AlertGenerator:
    """Generates alerts and warnings for contracts."""

    def __init__(self):
        self.alert_rules = [
            {'id': 'cost_overrun_warning', 'name': 'Cost Overrun Warning', 'severity': 'High',
             'condition': lambda c: self._cost_overrun(c, 10, 20)},
            {'id': 'cost_overrun_critical', 'name': 'Critical Cost Overrun', 'severity': 'Critical',
             'condition': lambda c: self._cost_overrun(c, 20, 100)},
            {'id': 'schedule_delay_warning', 'name': 'Schedule Delay Warning', 'severity': 'Medium',
             'condition': lambda c: (c.get('is_delayed') and (c.get('delay_days', 0) or 0) < 60)},
            {'id': 'schedule_delay_critical', 'name': 'Critical Schedule Delay', 'severity': 'High',
             'condition': lambda c: (c.get('is_delayed') and (c.get('delay_days', 0) or 0) >= 60)},
            {'id': 'expiring_soon', 'name': 'Contract Expiring Soon', 'severity': 'Medium',
             'condition': lambda c: self._expiring_soon(c, 30)},
            {'id': 'low_health_score', 'name': 'Low Health Score', 'severity': 'High',
             'condition': lambda c: (c.get('overall_health_score', 100) or 100) < 50},
            {'id': 'multiple_change_orders', 'name': 'Excessive Change Orders', 'severity': 'Medium',
             'condition': lambda c: (c.get('change_order_count', 0) or 0) >= 3},
        ]

    def _cost_overrun(self, contract: Dict, min_pct: float, max_pct: float) -> bool:
        original = contract.get('original_amount', 0) or 0
        current = contract.get('current_amount', 0) or 0
        if original <= 0:
            return False
        variance_pct = ((current - original) / original) * 100
        return min_pct <= variance_pct < max_pct

    def _expiring_soon(self, contract: Dict, days: int) -> bool:
        end_date = contract.get('current_end_date') or contract.get('original_end_date')
        if not end_date:
            return False
        try:
            end_dt = datetime.fromisoformat(str(end_date)[:10])
            days_until = (end_dt - datetime.now()).days
            return 0 < days_until <= days
        except (ValueError, TypeError):
            return False

    def generate_alerts(self, contracts: List[Dict]) -> List[Dict]:
        alerts = []
        for contract in contracts:
            for rule in self.alert_rules:
                try:
                    if rule['condition'](contract):
                        alerts.append({
                            'contract_id': contract.get('contract_id'),
                            'contract_title': contract.get('title'),
                            'vendor_name': contract.get('vendor_name'),
                            'alert_type': rule['id'],
                            'title': rule['name'],
                            'severity': rule['severity'],
                        })
                except Exception as e:
                    logger.error(f"Error checking rule {rule['id']}: {e}")

        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        alerts.sort(key=lambda a: severity_order.get(a['severity'], 4))
        return alerts
