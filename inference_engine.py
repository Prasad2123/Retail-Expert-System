"""
inference_engine.py - Forward-Chaining Inference Engine and Explanation Facility
================================================================================
This module implements the INFERENCE ENGINE and EXPLANATION FACILITY:
- Forward Chaining: Starts with known product facts in Working Memory,
  evaluates rule premises against facts, and infers actionable recommendations.
- Rule Conflict & Priority Handling: Out-of-stock takes precedence over low-stock;
  financial risk rules are prioritized.
- Explanation Facility: Provides step-by-step transparency into why each rule
  was satisfied or not satisfied.
"""

from typing import List, Dict, Any, Optional, Tuple
from knowledge_base import (
    Rule,
    get_all_rules,
    get_rule_by_id,
    calculate_profit,
    calculate_profit_margin,
    RULES_REGISTRY
)


class Recommendation:
    """
    Encapsulates an inferred recommendation produced by firing an IF-THEN rule.
    """
    def __init__(
        self,
        product_id: str,
        product_name: str,
        condition: str,
        rule_id: str,
        rule_name: str,
        reason: str,
        recommendation: str,
        priority: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.product_id = product_id
        self.product_name = product_name
        self.condition = condition
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.reason = reason
        self.recommendation = recommendation
        self.priority = priority.upper()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "condition": self.condition,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "reason": self.reason,
            "recommendation": self.recommendation,
            "priority": self.priority,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        return (
            f"<Recommendation {self.rule_id} for {self.product_id} "
            f"[{self.priority}]: {self.condition}>"
        )


class InferenceEngine:
    """
    The Forward-Chaining Inference Engine for Retail Decision Support.
    """

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = rules if rules is not None else get_all_rules()

    def build_working_memory(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare working memory facts from raw product dictionary:
        Extracts fields, ensures numeric types, and computes derived facts
        (profit, profit margin, stock coverage).
        """
        selling = float(product.get("selling_price", 0.0))
        cost = float(product.get("purchase_cost", 0.0))
        stock = int(product.get("stock", 0))
        min_stock = int(product.get("min_stock", 0))
        monthly_sales = int(product.get("monthly_sales", 0))

        profit_per_unit = round(selling - cost, 2)
        profit_margin = round(((profit_per_unit / selling) * 100.0), 2) if selling > 0 else 0.0

        facts = {
            "product_id": str(product.get("product_id", "")).strip(),
            "name": str(product.get("name", "")).strip(),
            "category": str(product.get("category", "")).strip(),
            "selling_price": selling,
            "purchase_cost": cost,
            "stock": stock,
            "min_stock": min_stock,
            "monthly_sales": monthly_sales,
            "profit_per_unit": profit_per_unit,
            "profit_margin": profit_margin,
            "is_out_of_stock": (stock == 0),
            "is_low_stock": (0 < stock <= min_stock),
            "is_sold_below_cost": (selling < cost)
        }
        return facts

    def evaluate_product(
        self,
        product: Dict[str, Any],
        include_normal_performance: bool = False
    ) -> List[Recommendation]:
        """
        Run forward chaining on a single product's working memory facts.
        
        Parameters:
        - product: raw product dictionary
        - include_normal_performance: if True, includes Rule 8 even if NORMAL.
          By default, Expert Analysis highlights actionable issues and high performance.
        
        Returns:
        List of generated Recommendation objects for rules that fired.
        """
        facts = self.build_working_memory(product)
        recommendations: List[Recommendation] = []

        for rule in self.rules:
            # Evaluate rule condition against working memory
            satisfied, details = rule.evaluate(facts)

            if satisfied:
                # If evaluating Rule 8, only include if NOT 'NORMAL' unless requested
                if rule.rule_id == "RULE-08":
                    classification = details.get("classification", "")
                    if classification == "NORMAL" and not include_normal_performance:
                        continue

                rec = Recommendation(
                    product_id=facts["product_id"],
                    product_name=facts["name"],
                    condition=details.get("condition", rule.name),
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    reason=details.get("reason", ""),
                    recommendation=details.get("recommendation", ""),
                    priority=details.get("priority", rule.priority),
                    metadata=details
                )
                recommendations.append(rec)

        return recommendations

    def evaluate_inventory(
        self,
        inventory: List[Dict[str, Any]],
        include_normal_performance: bool = False
    ) -> List[Recommendation]:
        """
        Forward chaining evaluation across entire inventory working memory.
        Returns list of all recommendations, ordered by priority:
        HIGH -> MEDIUM -> LOW.
        """
        all_recommendations: List[Recommendation] = []

        for product in inventory:
            recs = self.evaluate_product(product, include_normal_performance=include_normal_performance)
            all_recommendations.extend(recs)

        # Sort recommendations by priority weight
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))

        return all_recommendations

    def get_analysis_summary(
        self,
        inventory: List[Dict[str, Any]],
        recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        """
        Summarize the results of the expert analysis.
        """
        total_products = len(inventory)
        affected_product_ids = set(r.product_id for r in recommendations)
        
        high_count = sum(1 for r in recommendations if r.priority == "HIGH")
        medium_count = sum(1 for r in recommendations if r.priority == "MEDIUM")
        low_count = sum(1 for r in recommendations if r.priority == "LOW")

        rule_breakdown: Dict[str, int] = {}
        for r in recommendations:
            rule_breakdown[r.rule_id] = rule_breakdown.get(r.rule_id, 0) + 1

        return {
            "total_products": total_products,
            "total_recommendations": len(recommendations),
            "affected_products_count": len(affected_product_ids),
            "high_priority_count": high_count,
            "medium_priority_count": medium_count,
            "low_priority_count": low_count,
            "rule_breakdown": rule_breakdown
        }


class ExplanationFacility:
    """
    Transparent Explanation Facility:
    Allows inspection and auditing of rule evaluations for academic transparency.
    """

    @staticmethod
    def explain_rule_evaluation(rule: Rule, facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a transparent audit of a single rule against working memory facts.
        
        Returns detailed reasoning structure:
        - rule_id, rule_name
        - if_condition
        - evaluated_values
        - condition_satisfied: bool
        - then_action
        - generated_reason
        - generated_recommendation
        """
        satisfied, details = rule.evaluate(facts)

        return {
            "rule_id": rule.rule_id,
            "rule_name": rule.name,
            "if_condition": rule.condition_text,
            "then_action": rule.action_text,
            "priority": rule.priority,
            "evaluated_values": details.get("evaluated_values", ""),
            "condition_detail": details.get("condition_detail", ""),
            "condition_satisfied": satisfied,
            "generated_reason": details.get("reason", "Condition not met; rule did not fire."),
            "generated_recommendation": details.get("recommendation", "None"),
        }
