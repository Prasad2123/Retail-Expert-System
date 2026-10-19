"""
knowledge_base.py - Knowledge Base for Retail Expert System
===========================================================
This module represents the KNOWLEDGE BASE component of the expert system.
It encapsulates:
1. Domain Thresholds & Business Constants
2. Mathematical Formulas for Inventory & Retail Decisions
3. Formal Declarative Rule Definitions (IF-THEN Logic)
4. Explanations and Priority Ratings for Decision Support
"""

import math
from typing import Dict, Any, List, Optional, Tuple, Callable

# ==============================================================================
# 1. DOMAIN THRESHOLDS & CONFIGURABLE BUSINESS CONSTANTS
# ==============================================================================
# Products with monthly sales at or above this are classified as HIGH DEMAND
HIGH_DEMAND_SALES_THRESHOLD: int = 30

# Products with monthly sales at or below this are candidates for SLOW MOVING
SLOW_MOVING_SALES_THRESHOLD: int = 5

# High stock threshold for slow-moving products (units in inventory)
SLOW_MOVING_MIN_STOCK: int = 15

# Default promotional discount percentage recommended for slow-moving inventory
DEFAULT_DISCOUNT_PERCENT: float = 10.0

# Products with a profit margin percentage below this are flagged as LOW MARGIN
LOW_MARGIN_THRESHOLD: float = 15.0

# Minimum healthy profit margin target
HEALTHY_MARGIN_THRESHOLD: float = 30.0


# ==============================================================================
# 2. DOMAIN FORMULAS & CALCULATION HELPERS
# ==============================================================================
def calculate_profit(product: Dict[str, Any]) -> float:
    """Calculate profit per unit: Selling price - Purchase cost."""
    selling = float(product.get("selling_price", 0.0))
    cost = float(product.get("purchase_cost", 0.0))
    return round(selling - cost, 2)


def calculate_profit_margin(product: Dict[str, Any]) -> float:
    """
    Calculate profit margin percentage:
    Profit margin % = ((Selling price - Purchase cost) / Selling price) * 100
    Safely handles zero or negative selling prices without division by zero.
    """
    selling = float(product.get("selling_price", 0.0))
    cost = float(product.get("purchase_cost", 0.0))
    if selling <= 0:
        return 0.0
    margin = ((selling - cost) / selling) * 100.0
    return round(margin, 2)


def calculate_target_stock(min_stock: int, monthly_sales: int) -> int:
    """
    Calculate the target optimal inventory level.
    Business Logic:
    - Target stock covers expected demand plus safety buffer.
    - Safety Stock Buffer = min_stock
    - Target Stock = max(min_stock * 2, monthly_sales + min_stock)
    
    Example:
    If min_stock = 10 and monthly_sales = 10:
    Target Stock = max(20, 20) = 20 units.
    """
    min_stock = max(0, int(min_stock))
    monthly_sales = max(0, int(monthly_sales))
    return max(min_stock * 2, monthly_sales + min_stock)


def calculate_reorder_quantity(current_stock: int, min_stock: int, monthly_sales: int) -> int:
    """
    Calculate recommended reorder quantity:
    Reorder Quantity = max(0, target_stock - current_stock)
    
    Example:
    Current Stock = 4, Min Stock = 10, Monthly Sales = 10.
    Target Stock = 20.
    Reorder Quantity = max(0, 20 - 4) = 16 units.
    """
    target = calculate_target_stock(min_stock, monthly_sales)
    return max(0, target - max(0, int(current_stock)))


def format_currency(amount: float) -> str:
    """
    Format numeric monetary amount into Indian Rupee (INR) currency string.
    Example: format_currency(1499) -> '₹1,499.00'
    """
    return f"₹{float(amount):,.2f}"


def calculate_safe_discount(
    selling_price: float,
    purchase_cost: float,
    requested_discount_pct: float = DEFAULT_DISCOUNT_PERCENT
) -> Dict[str, Any]:
    """
    Evaluate promotional discount feasibility subject to business constraint:
    RULE: 'Never recommend a discount that reduces selling price below purchase cost.'
    
    Returns a dictionary with:
    - safe: bool (whether requested discount is safe)
    - recommended_pct: float (discount percentage)
    - discounted_price: float
    - profit_after_discount: float
    - margin_after_discount: float
    - max_safe_discount_pct: float
    - reason: str
    """
    selling_price = float(selling_price)
    purchase_cost = float(purchase_cost)

    if selling_price <= 0:
        return {
            "safe": False,
            "recommended_pct": 0.0,
            "discounted_price": 0.0,
            "profit_after_discount": 0.0,
            "margin_after_discount": 0.0,
            "max_safe_discount_pct": 0.0,
            "reason": "Selling price is zero or negative."
        }

    # Absolute floor price allowed without incurring a loss
    floor_price = purchase_cost
    max_safe_discount_amount = max(0.0, selling_price - floor_price)
    max_safe_discount_pct = round((max_safe_discount_amount / selling_price) * 100.0, 1)

    proposed_discount_amount = round(selling_price * (requested_discount_pct / 100.0), 2)
    proposed_discounted_price = round(selling_price - proposed_discount_amount, 2)

    if proposed_discounted_price >= floor_price:
        profit = round(proposed_discounted_price - purchase_cost, 2)
        margin = round((profit / proposed_discounted_price) * 100.0, 1) if proposed_discounted_price > 0 else 0.0
        return {
            "safe": True,
            "recommended_pct": requested_discount_pct,
            "discounted_price": proposed_discounted_price,
            "profit_after_discount": profit,
            "margin_after_discount": margin,
            "max_safe_discount_pct": max_safe_discount_pct,
            "reason": f"Safe {requested_discount_pct}% discount leaves profit of {format_currency(profit)} ({margin}% margin)."
        }
    else:
        # Proposed discount would violate the constraint
        if max_safe_discount_pct > 0:
            discounted_price = round(selling_price * (1 - max_safe_discount_pct / 100.0), 2)
            profit = round(discounted_price - purchase_cost, 2)
            margin = round((profit / discounted_price) * 100.0, 1) if discounted_price > 0 else 0.0
            return {
                "safe": False,
                "recommended_pct": max_safe_discount_pct,
                "discounted_price": discounted_price,
                "profit_after_discount": profit,
                "margin_after_discount": margin,
                "max_safe_discount_pct": max_safe_discount_pct,
                "reason": (
                    f"Requested {requested_discount_pct}% discount violates cost floor ({format_currency(purchase_cost)}). "
                    f"Capped at max break-even discount of {max_safe_discount_pct}% ({format_currency(discounted_price)})."
                )
            }
        else:
            return {
                "safe": False,
                "recommended_pct": 0.0,
                "discounted_price": selling_price,
                "profit_after_discount": round(selling_price - purchase_cost, 2),
                "margin_after_discount": 0.0,
                "max_safe_discount_pct": 0.0,
                "reason": f"Current price ({format_currency(selling_price)}) is already at or below purchase cost ({format_currency(purchase_cost)}). No discount allowed."
            }


def classify_performance(product: Dict[str, Any]) -> Tuple[str, str]:
    """
    Rule 8 Performance Classification Logic:
    Classifies a product as 'HIGH PERFORMING', 'NORMAL', or 'NEEDS REVIEW'.
    
    Returns:
    (classification_label, explanation_text)
    """
    stock = int(product.get("stock", 0))
    min_stock = int(product.get("min_stock", 0))
    monthly_sales = int(product.get("monthly_sales", 0))
    selling_price = float(product.get("selling_price", 0.0))
    purchase_cost = float(product.get("purchase_cost", 0.0))

    # Condition A: Sold below cost -> Needs Review
    if selling_price < purchase_cost:
        return "NEEDS REVIEW", f"Product sold below cost (Loss: {format_currency(purchase_cost - selling_price)}/unit)."

    # Condition B: Out of stock -> Needs Review
    if stock == 0:
        return "NEEDS REVIEW", "Stock is completely depleted (0 units), missing potential customer sales."

    # Condition C: Slow moving with excessive inventory -> Needs Review
    if monthly_sales <= SLOW_MOVING_SALES_THRESHOLD and stock >= SLOW_MOVING_MIN_STOCK:
        return "NEEDS REVIEW", f"Slow moving ({monthly_sales} sold/mo) with high inventory ({stock} units)."

    # Condition D: High sales with healthy stock -> High Performing
    if monthly_sales >= HIGH_DEMAND_SALES_THRESHOLD:
        return "HIGH PERFORMING", f"Strong sales volume ({monthly_sales} units/mo) and positive profit contribution."

    # Default: Normal performance
    return "NORMAL", f"Balanced sales ({monthly_sales} units/mo) and manageable inventory ({stock} units)."


# ==============================================================================
# 3. DECLARATIVE RULE STRUCTURE & SPECIFICATION
# ==============================================================================
class Rule:
    """
    Represents a single IF-THEN rule in the Expert System Knowledge Base.
    
    Attributes:
    - rule_id: Unique rule identifier (e.g., 'RULE-01')
    - name: Human-readable name of the rule
    - condition_text: Formal specification of the IF condition
    - action_text: Formal specification of the THEN action
    - priority: Priority rating ('HIGH', 'MEDIUM', 'LOW')
    - evaluate_fn: Function accepting product facts dict, returning (satisfied: bool, details: dict)
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        condition_text: str,
        action_text: str,
        priority: str,
        evaluate_fn: Callable[[Dict[str, Any]], Tuple[bool, Dict[str, Any]]]
    ):
        self.rule_id = rule_id
        self.name = name
        self.condition_text = condition_text
        self.action_text = action_text
        self.priority = priority
        self.evaluate_fn = evaluate_fn

    def evaluate(self, facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate this rule against the working memory facts."""
        return self.evaluate_fn(facts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule metadata to dictionary for display or academic documentation."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "if_condition": self.condition_text,
            "then_action": self.action_text,
            "priority": self.priority
        }


# ==============================================================================
# 4. RULE DEFINITIONS (RULES 1 THROUGH 8)
# ==============================================================================

# --- RULE-01: Low Stock Alert ---
def _eval_rule_01(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    stock = int(facts.get("stock", 0))
    min_stock = int(facts.get("min_stock", 0))
    # Rule 1 applies when 0 < stock <= min_stock (Rule 2 handles stock == 0)
    satisfied = (0 < stock <= min_stock)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": f"Current stock: {stock}, Minimum stock threshold: {min_stock}",
        "condition_detail": f"0 < stock ({stock}) <= min_stock ({min_stock})"
    }
    
    if satisfied:
        monthly_sales = int(facts.get("monthly_sales", 0))
        target_stock = calculate_target_stock(min_stock, monthly_sales)
        reorder_qty = calculate_reorder_quantity(stock, min_stock, monthly_sales)
        details.update({
            "condition": "LOW STOCK",
            "reason": f"Current stock ({stock}) is below the minimum threshold ({min_stock}).",
            "recommendation": f"Replenish at least {reorder_qty} units to reach the target stock level ({target_stock} units).",
            "priority": "HIGH"
        })
    return satisfied, details


RULE_01 = Rule(
    rule_id="RULE-01",
    name="Low Stock Alert",
    condition_text="IF 0 < available_stock <= minimum_stock_threshold",
    action_text="THEN classify product as LOW STOCK and recommend replenishment.",
    priority="HIGH",
    evaluate_fn=_eval_rule_01
)


# --- RULE-02: Out-of-Stock Alert ---
def _eval_rule_02(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    stock = int(facts.get("stock", 0))
    min_stock = int(facts.get("min_stock", 0))
    monthly_sales = int(facts.get("monthly_sales", 0))
    satisfied = (stock == 0)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": f"Current stock: {stock}, Minimum stock: {min_stock}",
        "condition_detail": f"stock ({stock}) == 0"
    }
    
    if satisfied:
        target_stock = calculate_target_stock(min_stock, monthly_sales)
        reorder_qty = calculate_reorder_quantity(stock, min_stock, monthly_sales)
        details.update({
            "condition": "OUT OF STOCK",
            "reason": "Available stock is completely depleted (0 units). Immediate stockout in progress.",
            "recommendation": f"Place urgent purchase order for at least {reorder_qty} units to restore inventory to {target_stock} units.",
            "priority": "HIGH"
        })
    return satisfied, details


RULE_02 = Rule(
    rule_id="RULE-02",
    name="Out-of-Stock Alert",
    condition_text="IF available_stock == 0",
    action_text="THEN classify product as OUT OF STOCK and recommend immediate urgent restocking (takes priority over ordinary low stock).",
    priority="HIGH",
    evaluate_fn=_eval_rule_02
)


# --- RULE-03: Reorder Recommendation ---
def _eval_rule_03(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    stock = int(facts.get("stock", 0))
    min_stock = int(facts.get("min_stock", 0))
    monthly_sales = int(facts.get("monthly_sales", 0))
    
    # Reorder applies when stock <= min_stock AND monthly_sales > 0
    satisfied = (stock <= min_stock and monthly_sales > 0)
    
    target_stock = calculate_target_stock(min_stock, monthly_sales)
    reorder_qty = calculate_reorder_quantity(stock, min_stock, monthly_sales)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": f"Current stock: {stock}, Min stock: {min_stock}, Monthly sales: {monthly_sales}, Target stock: {target_stock}",
        "condition_detail": f"stock ({stock}) <= min_stock ({min_stock}) AND monthly_sales ({monthly_sales}) > 0"
    }
    
    if satisfied:
        details.update({
            "condition": "REORDER REQUIRED",
            "reason": f"Inventory is at or below reorder threshold ({min_stock}) with active demand ({monthly_sales} units/mo).",
            "recommendation": (
                f"Reorder {reorder_qty} units based on formula: "
                f"max(0, Target Stock [{target_stock}] - Current Stock [{stock}])."
            ),
            "priority": "HIGH"
        })
    return satisfied, details


RULE_03 = Rule(
    rule_id="RULE-03",
    name="Reorder Recommendation",
    condition_text="IF available_stock <= minimum_stock_threshold AND monthly_sales > 0",
    action_text="THEN recommend reorder quantity = max(0, target_stock - current_stock).",
    priority="HIGH",
    evaluate_fn=_eval_rule_03
)


# --- RULE-04: High-Demand Product ---
def _eval_rule_04(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    monthly_sales = int(facts.get("monthly_sales", 0))
    satisfied = (monthly_sales >= HIGH_DEMAND_SALES_THRESHOLD)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": f"Monthly sales: {monthly_sales}, High demand threshold: {HIGH_DEMAND_SALES_THRESHOLD}",
        "condition_detail": f"monthly_sales ({monthly_sales}) >= threshold ({HIGH_DEMAND_SALES_THRESHOLD})"
    }
    
    if satisfied:
        details.update({
            "condition": "HIGH DEMAND",
            "reason": f"Monthly sales of {monthly_sales} units exceeds high-demand threshold ({HIGH_DEMAND_SALES_THRESHOLD}).",
            "recommendation": "Maintain buffer inventory, avoid stockouts, and negotiate volume discounts with suppliers.",
            "priority": "MEDIUM"
        })
    return satisfied, details


RULE_04 = Rule(
    rule_id="RULE-04",
    name="High-Demand Product",
    condition_text=f"IF monthly_sales >= {HIGH_DEMAND_SALES_THRESHOLD}",
    action_text="THEN classify product as HIGH DEMAND and recommend maintaining sufficient inventory buffer.",
    priority="MEDIUM",
    evaluate_fn=_eval_rule_04
)


# --- RULE-05: Slow-Moving Product ---
def _eval_rule_05(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    stock = int(facts.get("stock", 0))
    min_stock = int(facts.get("min_stock", 0))
    monthly_sales = int(facts.get("monthly_sales", 0))
    
    # Slow moving if sales <= SLOW_MOVING_SALES_THRESHOLD and stock is relatively high
    # (either stock >= SLOW_MOVING_MIN_STOCK or stock >= min_stock * 2)
    stock_is_high = (stock >= SLOW_MOVING_MIN_STOCK or (min_stock > 0 and stock >= min_stock * 2))
    satisfied = (monthly_sales <= SLOW_MOVING_SALES_THRESHOLD and stock_is_high)
    
    months_supply = round(stock / max(1, monthly_sales), 1)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": f"Monthly sales: {monthly_sales} (threshold <= {SLOW_MOVING_SALES_THRESHOLD}), Stock: {stock} (threshold >= {SLOW_MOVING_MIN_STOCK})",
        "condition_detail": f"monthly_sales ({monthly_sales}) <= {SLOW_MOVING_SALES_THRESHOLD} AND stock ({stock}) is high ({months_supply} months of supply)"
    }
    
    if satisfied:
        details.update({
            "condition": "SLOW MOVING",
            "reason": f"Low turnover ({monthly_sales} sold/month) with {stock} units in inventory (~{months_supply} months of supply).",
            "recommendation": "Review replenishment schedule, reallocate shelf space, or introduce a promotional bundle.",
            "priority": "MEDIUM"
        })
    return satisfied, details


RULE_05 = Rule(
    rule_id="RULE-05",
    name="Slow-Moving Product",
    condition_text=f"IF monthly_sales <= {SLOW_MOVING_SALES_THRESHOLD} AND stock is high (stock >= {SLOW_MOVING_MIN_STOCK} or stock >= 2*min_stock)",
    action_text="THEN classify product as SLOW MOVING and suggest reviewing purchasing or running promotional campaign.",
    priority="MEDIUM",
    evaluate_fn=_eval_rule_05
)


# --- RULE-06: Discount Recommendation ---
def _eval_rule_06(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    stock = int(facts.get("stock", 0))
    min_stock = int(facts.get("min_stock", 0))
    monthly_sales = int(facts.get("monthly_sales", 0))
    selling_price = float(facts.get("selling_price", 0.0))
    purchase_cost = float(facts.get("purchase_cost", 0.0))
    
    stock_is_high = (stock >= SLOW_MOVING_MIN_STOCK or (min_stock > 0 and stock >= min_stock * 2))
    is_slow = (monthly_sales <= SLOW_MOVING_SALES_THRESHOLD and stock_is_high)
    
    discount_analysis = calculate_safe_discount(selling_price, purchase_cost, DEFAULT_DISCOUNT_PERCENT)
    
    # Rule triggers if product is slow-moving and has room for discount without violating cost floor
    satisfied = (is_slow and selling_price > purchase_cost)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": (
            f"Slow moving: {is_slow}, Selling price: {format_currency(selling_price)}, Purchase cost: {format_currency(purchase_cost)}, "
            f"Safe discount possible: {discount_analysis['safe']}"
        ),
        "condition_detail": f"is_slow_moving ({is_slow}) AND selling_price ({format_currency(selling_price)}) > purchase_cost ({format_currency(purchase_cost)})"
    }
    
    if satisfied:
        if discount_analysis["safe"]:
            rec_text = (
                f"Apply a {DEFAULT_DISCOUNT_PERCENT}% clearance discount: reduce price from {format_currency(selling_price)} "
                f"to {format_currency(discount_analysis['discounted_price'])}. "
                f"Preserves {format_currency(discount_analysis['profit_after_discount'])}/unit profit ({discount_analysis['margin_after_discount']}% margin)."
            )
        else:
            rec_text = (
                f"Standard 10% discount violates cost floor. Apply max safe break-even discount of "
                f"{discount_analysis['max_safe_discount_pct']}% ({format_currency(discount_analysis['discounted_price'])}) "
                f"to liquidate stock without incurring a cash loss."
            )
            
        details.update({
            "condition": "PROMOTIONAL DISCOUNT RECOMMENDED",
            "reason": f"High inventory ({stock} units) with sluggish sales ({monthly_sales}/mo) ties up working capital.",
            "recommendation": rec_text,
            "priority": "MEDIUM"
        })
    return satisfied, details


RULE_06 = Rule(
    rule_id="RULE-06",
    name="Discount Recommendation",
    condition_text="IF product is SLOW MOVING AND selling_price > purchase_cost",
    action_text=(
        "THEN suggest a modest discount (up to 10%) without allowing discounted price to fall below purchase cost."
    ),
    priority="MEDIUM",
    evaluate_fn=_eval_rule_06
)


# --- RULE-07: Profit Margin & Below-Cost Analysis ---
def _eval_rule_07(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    selling_price = float(facts.get("selling_price", 0.0))
    purchase_cost = float(facts.get("purchase_cost", 0.0))
    
    profit_per_unit = round(selling_price - purchase_cost, 2)
    margin_pct = round(((profit_per_unit / selling_price) * 100.0), 2) if selling_price > 0 else 0.0
    
    # This rule triggers if sold below cost OR low margin
    is_below_cost = (selling_price < purchase_cost)
    is_low_margin = (not is_below_cost and margin_pct < LOW_MARGIN_THRESHOLD)
    satisfied = (is_below_cost or is_low_margin)
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": (
            f"Selling price: {format_currency(selling_price)}, Purchase cost: {format_currency(purchase_cost)}, "
            f"Profit/unit: {format_currency(profit_per_unit)}, Margin: {margin_pct}%"
        ),
        "condition_detail": f"selling_price < purchase_cost OR margin ({margin_pct}%) < {LOW_MARGIN_THRESHOLD}%"
    }
    
    if satisfied:
        if is_below_cost:
            details.update({
                "condition": "NEGATIVE MARGIN / SOLD BELOW COST",
                "reason": (
                    f"Product is selling at {format_currency(selling_price)}, which is below its purchase cost of {format_currency(purchase_cost)}. "
                    f"Every sale loses {format_currency(abs(profit_per_unit))} per unit."
                ),
                "recommendation": (
                    f"Immediately adjust selling price to at least {format_currency(purchase_cost)} (break-even) "
                    f"or {format_currency(round(purchase_cost * 1.25, 2))} to achieve a healthy 20% margin."
                ),
                "priority": "HIGH"
            })
        else:
            details.update({
                "condition": "LOW PROFIT MARGIN",
                "reason": f"Current profit margin of {margin_pct}% is below the target threshold ({LOW_MARGIN_THRESHOLD}%).",
                "recommendation": "Review supplier purchasing contracts or consider modest price adjustment to improve unit profitability.",
                "priority": "LOW"
            })
    return satisfied, details


RULE_07 = Rule(
    rule_id="RULE-07",
    name="Profit Margin & Cost Safety Analysis",
    condition_text=f"IF selling_price < purchase_cost OR profit_margin < {LOW_MARGIN_THRESHOLD}%",
    action_text="THEN flag pricing anomaly, prevent loss-making sales, and recommend price adjustment.",
    priority="HIGH",
    evaluate_fn=_eval_rule_07
)


# --- RULE-08: Product Performance Classification ---
def _eval_rule_08(facts: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    classification, reason = classify_performance(facts)
    # Rule 8 always provides a classification for every product
    satisfied = True
    
    priority_map = {
        "NEEDS REVIEW": "HIGH",
        "HIGH PERFORMING": "LOW",
        "NORMAL": "LOW"
    }
    
    recommendation_map = {
        "NEEDS REVIEW": "Action required: inspect stock, pricing, or demand drivers to resolve performance bottleneck.",
        "HIGH PERFORMING": "Maintain optimal supply continuity; this product is a core revenue driver.",
        "NORMAL": "Maintain current operating parameters and standard replenishment cycles."
    }
    
    details = {
        "condition_satisfied": satisfied,
        "evaluated_values": f"Classification: {classification}, Reason: {reason}",
        "condition_detail": "Evaluated all sales, stock, and margin dimensions",
        "condition": f"PERFORMANCE: {classification}",
        "reason": reason,
        "recommendation": recommendation_map.get(classification, "Monitor metrics."),
        "priority": priority_map.get(classification, "LOW"),
        "classification": classification
    }
    return satisfied, details


RULE_08 = Rule(
    rule_id="RULE-08",
    name="Product Performance Classification",
    condition_text="IF sales, stock, and margins are analyzed against business benchmarks",
    action_text="THEN classify product into HIGH PERFORMING, NORMAL, or NEEDS REVIEW.",
    priority="LOW",
    evaluate_fn=_eval_rule_08
)


# ==============================================================================
# 5. KNOWLEDGE BASE REGISTRY & ACCESSORS
# ==============================================================================
RULES_REGISTRY: List[Rule] = [
    RULE_02,  # Out-of-Stock takes highest precedence over low stock
    RULE_01,  # Low Stock Alert
    RULE_03,  # Reorder Recommendation
    RULE_07,  # Profit Margin / Loss Making (High financial priority)
    RULE_04,  # High Demand
    RULE_05,  # Slow Moving
    RULE_06,  # Discount Recommendation
    RULE_08,  # Overall Performance Classification
]


def get_rule_by_id(rule_id: str) -> Optional[Rule]:
    """Retrieve a rule object by its rule ID (case-insensitive)."""
    rid = rule_id.strip().upper()
    for rule in RULES_REGISTRY:
        if rule.rule_id == rid:
            return rule
    return None


def get_all_rules() -> List[Rule]:
    """Return a list of all registered rules in the knowledge base."""
    return list(RULES_REGISTRY)
