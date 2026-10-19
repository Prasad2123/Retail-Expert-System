"""
recommendations.py - Product Recommendation & Promotional Strategy Module
=========================================================================
This module implements the customer-facing and shopkeeper decision-support
recommendation logic based on transparent rules:
1. Category Filtering
2. Budget Constraints (selling_price <= max_budget)
3. Positive Stock Availability (stock > 0)
4. Sales Demand / Product Performance
5. Feasible Discount Proposals respecting Cost Floors
"""

from typing import List, Dict, Any, Optional, Tuple
from knowledge_base import calculate_safe_discount, classify_performance, calculate_profit_margin, format_currency


def recommend_products(
    inventory: List[Dict[str, Any]],
    category: Optional[str] = None,
    max_budget: Optional[float] = None,
    min_stock: int = 1,
    demand_preference: Optional[str] = None,  # 'high_demand', 'any'
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Recommend products matching user criteria using deterministic rules.
    
    Rules applied:
    - Rule A: Category must match (if specified and not 'ALL')
    - Rule B: Selling price must be <= max_budget (if specified)
    - Rule C: Available stock must be >= min_stock (positive availability)
    - Rule D: If demand_preference == 'high_demand', monthly_sales >= 25
    
    Returns:
    (recommended_items, explanatory_summary)
    """
    if not inventory:
        return [], "Inventory is currently empty. No products available to recommend."

    matched_items = []
    
    # Track statistics for failure explanations
    out_of_budget_count = 0
    out_of_stock_count = 0
    category_match_count = 0

    norm_category = category.strip().lower() if category and category.strip().upper() != "ALL" else None

    for product in inventory:
        prod_cat = str(product.get("category", "")).strip().lower()
        price = float(product.get("selling_price", 0.0))
        stock = int(product.get("stock", 0))
        sales = int(product.get("monthly_sales", 0))

        # Check Category
        if norm_category:
            if prod_cat != norm_category:
                continue
            category_match_count += 1

        # Check Stock
        if stock < min_stock:
            out_of_stock_count += 1
            continue

        # Check Budget
        if max_budget is not None and max_budget > 0:
            if price > max_budget:
                out_of_budget_count += 1
                continue

        # Check Demand Preference
        if demand_preference == "high_demand" and sales < 25:
            continue

        # Construct Transparent Recommendation Reason
        margin = calculate_profit_margin(product)
        perf_label, _ = classify_performance(product)

        reasons = []
        if max_budget is not None and max_budget > 0:
            savings = max_budget - price
            if savings > 0:
                reasons.append(f"{format_currency(savings)} under budget")
            else:
                reasons.append("exactly matches budget")

        if sales >= 30:
            reasons.append(f"bestseller with high demand ({sales} units sold/mo)")
        elif sales >= 15:
            reasons.append(f"popular product ({sales} units sold/mo)")

        reasons.append(f"{stock} units ready for immediate fulfillment")

        if margin >= 30:
            reasons.append(f"healthy retailer margin ({margin}%)")

        full_reason = "; ".join(reasons).capitalize() + "."

        matched_items.append({
            "product_id": product.get("product_id"),
            "name": product.get("name"),
            "category": product.get("category"),
            "selling_price": price,
            "purchase_cost": float(product.get("purchase_cost", 0.0)),
            "stock": stock,
            "monthly_sales": sales,
            "margin_pct": margin,
            "performance": perf_label,
            "recommendation_reason": full_reason
        })

    # Sort matching products by sales (highest first), then by margin
    matched_items.sort(key=lambda x: (x["monthly_sales"], x["margin_pct"]), reverse=True)

    # Explanation if no products matched
    if not matched_items:
        reasons_list = []
        if norm_category and category_match_count == 0:
            reasons_list.append(f"No products found in category '{category}'.")
        else:
            if out_of_stock_count > 0:
                reasons_list.append(f"{out_of_stock_count} item(s) matched criteria but are currently out of stock.")
            if max_budget is not None and out_of_budget_count > 0:
                reasons_list.append(f"{out_of_budget_count} item(s) in this category exceeded budget of {format_currency(max_budget)}.")
        
        explanation = "No suitable products found. " + " ".join(reasons_list)
        return [], explanation

    summary = f"Found {len(matched_items)} matching product(s) satisfying all constraints."
    return matched_items, summary


def generate_promotional_discount_candidates(
    inventory: List[Dict[str, Any]],
    requested_discount_pct: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Identifies all slow-moving or overstocked products eligible for a promotional
    clearance discount according to Rule 6, ensuring the price never falls below cost.
    """
    candidates = []

    for product in inventory:
        stock = int(product.get("stock", 0))
        min_stock = int(product.get("min_stock", 0))
        sales = int(product.get("monthly_sales", 0))
        price = float(product.get("selling_price", 0.0))
        cost = float(product.get("purchase_cost", 0.0))

        # Check slow moving conditions
        is_slow = (sales <= 5 and (stock >= 15 or (min_stock > 0 and stock >= min_stock * 2)))

        if is_slow and price > cost:
            analysis = calculate_safe_discount(price, cost, requested_discount_pct)
            candidates.append({
                "product_id": product.get("product_id"),
                "name": product.get("name"),
                "category": product.get("category"),
                "current_price": price,
                "purchase_cost": cost,
                "stock": stock,
                "monthly_sales": sales,
                "discount_analysis": analysis
            })

    return candidates
