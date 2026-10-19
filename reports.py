"""
reports.py - Retail Analytics Summary & Report Export Module
============================================================
This module computes high-level inventory statistics and exports comprehensive,
traceable text reports of expert system findings to the local filesystem.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from knowledge_base import (
    HIGH_DEMAND_SALES_THRESHOLD,
    SLOW_MOVING_SALES_THRESHOLD,
    SLOW_MOVING_MIN_STOCK,
    classify_performance,
    get_all_rules,
    format_currency
)
from inference_engine import Recommendation

DEFAULT_REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def generate_inventory_summary(inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute comprehensive inventory metrics and retail indicators.
    All financial values are strictly labeled as estimates based on inventory data.
    """
    total_products = len(inventory)
    total_units = sum(int(p.get("stock", 0)) for p in inventory)

    total_cost_value = sum(int(p.get("stock", 0)) * float(p.get("purchase_cost", 0.0)) for p in inventory)
    total_retail_value = sum(int(p.get("stock", 0)) * float(p.get("selling_price", 0.0)) for p in inventory)
    total_potential_profit = total_retail_value - total_cost_value

    out_of_stock = []
    low_stock = []
    high_demand = []
    slow_moving = []
    below_cost = []
    
    category_summary: Dict[str, Dict[str, Any]] = {}
    performance_summary: Dict[str, int] = {"HIGH PERFORMING": 0, "NORMAL": 0, "NEEDS REVIEW": 0}

    for p in inventory:
        stock = int(p.get("stock", 0))
        min_stock = int(p.get("min_stock", 0))
        sales = int(p.get("monthly_sales", 0))
        cost = float(p.get("purchase_cost", 0.0))
        price = float(p.get("selling_price", 0.0))
        cat = str(p.get("category", "General")).strip()

        # Stock status
        if stock == 0:
            out_of_stock.append(p)
        elif stock <= min_stock:
            low_stock.append(p)

        # Demand status
        if sales >= HIGH_DEMAND_SALES_THRESHOLD:
            high_demand.append(p)

        # Slow moving status
        if sales <= SLOW_MOVING_SALES_THRESHOLD and (stock >= SLOW_MOVING_MIN_STOCK or (min_stock > 0 and stock >= min_stock * 2)):
            slow_moving.append(p)

        # Financial risk
        if price < cost:
            below_cost.append(p)

        # Performance classification
        perf_label, _ = classify_performance(p)
        performance_summary[perf_label] = performance_summary.get(perf_label, 0) + 1

        # Category breakdown
        if cat not in category_summary:
            category_summary[cat] = {"count": 0, "units": 0, "retail_value": 0.0}
        category_summary[cat]["count"] += 1
        category_summary[cat]["units"] += stock
        category_summary[cat]["retail_value"] += stock * price

    return {
        "total_products": total_products,
        "total_units": total_units,
        "total_cost_value": round(total_cost_value, 2),
        "total_retail_value": round(total_retail_value, 2),
        "total_potential_profit": round(total_potential_profit, 2),
        "out_of_stock_products": out_of_stock,
        "low_stock_products": low_stock,
        "high_demand_products": high_demand,
        "slow_moving_products": slow_moving,
        "below_cost_products": below_cost,
        "category_summary": category_summary,
        "performance_summary": performance_summary,
    }


def export_analysis_report(
    inventory: List[Dict[str, Any]],
    recommendations: List[Recommendation],
    reports_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Export a comprehensive, professional academic report of expert analysis to a text file.
    Includes timestamps, inventory summaries, triggered rules, justifications, and priorities.
    """
    target_dir = reports_dir or DEFAULT_REPORTS_DIR
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as e:
        return False, f"Could not create reports directory: {e}"

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"expert_analysis_{timestamp_str}.txt"
    filepath = os.path.join(target_dir, filename)

    summary = generate_inventory_summary(inventory)
    now_formatted = datetime.now().strftime("%A, %B %d, %Y at %I:%M:%S %p")

    lines = []
    lines.append("=" * 80)
    lines.append("       RETAIL EXPERT SYSTEM: AI DECISION SUPPORT AUDIT REPORT")
    lines.append("        Rule-Based Knowledge Representation & Forward Chaining")
    lines.append("=" * 80)
    lines.append(f"Generated On  : {now_formatted}")
    lines.append(f"Output File   : {filename}")
    lines.append(f"Total Products: {summary['total_products']}")
    lines.append(f"Total Rules   : {len(get_all_rules())}")
    lines.append("-" * 80)
    lines.append("")

    lines.append("1. EXECUTIVE INVENTORY SUMMARY (ESTIMATED METRICS)")
    lines.append("-" * 80)
    lines.append(f"  • Total Products in Catalog : {summary['total_products']}")
    lines.append(f"  • Total Inventory Units     : {summary['total_units']} units")
    lines.append(f"  • Estimated Inventory Cost  : {format_currency(summary['total_cost_value'])}")
    lines.append(f"  • Estimated Retail Value    : {format_currency(summary['total_retail_value'])}")
    lines.append(f"  • Estimated Potential Profit: {format_currency(summary['total_potential_profit'])}")
    lines.append("")
    lines.append("  Inventory Health Breakdown:")
    lines.append(f"  • Out-of-Stock Items        : {len(summary['out_of_stock_products'])} product(s)")
    lines.append(f"  • Low-Stock Items           : {len(summary['low_stock_products'])} product(s)")
    lines.append(f"  • High-Demand Products      : {len(summary['high_demand_products'])} product(s)")
    lines.append(f"  • Slow-Moving Products      : {len(summary['slow_moving_products'])} product(s)")
    lines.append(f"  • Sold Below Cost (Deficit) : {len(summary['below_cost_products'])} product(s)")
    lines.append("")
    lines.append("  Product Performance Classification:")
    for perf_type, count in summary["performance_summary"].items():
        lines.append(f"  • {perf_type:<16}: {count} product(s)")
    lines.append("")
    lines.append("  [NOTE: Financial values are estimates based on active inventory data.]")
    lines.append("")

    lines.append("2. DETAILED RULE-BASED RECOMMENDATIONS")
    lines.append("-" * 80)

    if not recommendations:
        lines.append("  No active alerts or recommendations generated. Inventory is balanced.")
    else:
        for idx, rec in enumerate(recommendations, 1):
            lines.append(f"[{idx:02d}] Product       : {rec.product_name} (ID: {rec.product_id})")
            lines.append(f"     Priority      : {rec.priority}")
            lines.append(f"     Condition     : {rec.condition}")
            lines.append(f"     Rule Triggered: {rec.rule_id} - {rec.rule_name}")
            lines.append(f"     Reason        : {rec.reason}")
            lines.append(f"     Recommendation: {rec.recommendation}")
            lines.append("-" * 80)

    lines.append("")
    lines.append("3. KNOWLEDGE BASE RULE SPECIFICATIONS")
    lines.append("-" * 80)
    for rule in get_all_rules():
        lines.append(f"  [{rule.rule_id}] {rule.name} (Priority: {rule.priority})")
        lines.append(f"    IF   : {rule.condition_text}")
        lines.append(f"    THEN : {rule.action_text}")
        lines.append("")

    lines.append("=" * 80)
    lines.append("                   END OF EXPERT SYSTEM AUDIT REPORT")
    lines.append("=" * 80)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True, filepath
    except (IOError, OSError) as e:
        return False, f"Failed to write report file: {e}"
