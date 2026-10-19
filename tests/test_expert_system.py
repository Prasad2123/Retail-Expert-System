"""
test_expert_system.py - Unit Test Suite for Retail Expert System
================================================================
Comprehensive test suite validating:
1. Out-of-stock detection (Rule 2)
2. Low-stock detection (Rule 1)
3. Reorder quantity calculation (Rule 3)
4. High-demand classification (Rule 4)
5. Slow-moving classification (Rule 5)
6. Discount recommendation respecting purchase cost floor (Rule 6)
7. Profit margin calculation & division-by-zero protection (Rule 7)
8. Invalid inventory data handling (Validation)
9. Rule explanation generation (Explanation Facility)
10. Product recommendation based on category and budget constraints
11. Overlapping rule priority and classification integrity
"""

import sys
import os
import unittest
import tempfile
import json

# Ensure parent directory is on sys.path for direct or discovery execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from inventory import (
    validate_product_data,
    calculate_profit,
    calculate_profit_margin,
    load_inventory,
    save_inventory,
    add_product,
    update_stock,
    get_product_by_id
)
from knowledge_base import (
    RULE_01,
    RULE_02,
    RULE_03,
    RULE_04,
    RULE_05,
    RULE_06,
    RULE_07,
    RULE_08,
    calculate_target_stock,
    calculate_reorder_quantity,
    calculate_safe_discount,
    classify_performance,
    get_rule_by_id,
    get_all_rules,
    HIGH_DEMAND_SALES_THRESHOLD,
    SLOW_MOVING_SALES_THRESHOLD
)
from inference_engine import InferenceEngine, ExplanationFacility
from recommendations import recommend_products, generate_promotional_discount_candidates
from reports import generate_inventory_summary, export_analysis_report


class TestRetailExpertSystem(unittest.TestCase):
    """Test cases covering all expert system modules and business rules."""

    def setUp(self):
        """Set up isolated sample test data."""
        self.sample_product_low_stock = {
            "product_id": "T001",
            "name": "Test Wireless Mouse",
            "category": "Electronics",
            "purchase_cost": 450.00,
            "selling_price": 899.00,
            "stock": 4,
            "min_stock": 10,
            "monthly_sales": 10
        }

        self.sample_product_out_of_stock = {
            "product_id": "T002",
            "name": "Test Organic Bread",
            "category": "Groceries",
            "purchase_cost": 65.00,
            "selling_price": 120.00,
            "stock": 0,
            "min_stock": 10,
            "monthly_sales": 30
        }

        self.sample_product_high_demand = {
            "product_id": "T003",
            "name": "Fast Charger",
            "category": "Electronics",
            "purchase_cost": 650.00,
            "selling_price": 1299.00,
            "stock": 50,
            "min_stock": 10,
            "monthly_sales": 45
        }

        self.sample_product_slow_moving = {
            "product_id": "T004",
            "name": "Winter Parka Coat",
            "category": "Clothing",
            "purchase_cost": 1100.00,
            "selling_price": 2200.00,
            "stock": 25,
            "min_stock": 5,
            "monthly_sales": 2
        }

        self.sample_product_below_cost = {
            "product_id": "T005",
            "name": "Loss Leader Sunscreen",
            "category": "Personal Care",
            "purchase_cost": 299.00,
            "selling_price": 199.00,
            "stock": 10,
            "min_stock": 5,
            "monthly_sales": 5
        }

        self.engine = InferenceEngine()

    # --------------------------------------------------------------------------
    # 1. OUT-OF-STOCK DETECTION & PRECEDENCE (RULE 2 vs RULE 1)
    # --------------------------------------------------------------------------
    def test_01_out_of_stock_detection(self):
        """Verify stock == 0 triggers RULE-02 (OUT OF STOCK) and NOT ordinary LOW STOCK."""
        facts = self.engine.build_working_memory(self.sample_product_out_of_stock)
        
        # Rule 2 must fire
        satisfied_r2, details_r2 = RULE_02.evaluate(facts)
        self.assertTrue(satisfied_r2)
        self.assertEqual(details_r2["condition"], "OUT OF STOCK")
        self.assertEqual(details_r2["priority"], "HIGH")

        # Rule 1 must NOT fire for zero stock (rule precedence)
        satisfied_r1, details_r1 = RULE_01.evaluate(facts)
        self.assertFalse(satisfied_r1, "Zero stock must not trigger ordinary low-stock alert.")

    # --------------------------------------------------------------------------
    # 2. LOW-STOCK DETECTION (RULE 1)
    # --------------------------------------------------------------------------
    def test_02_low_stock_detection(self):
        """Verify 0 < stock <= min_stock triggers RULE-01 (LOW STOCK)."""
        facts = self.engine.build_working_memory(self.sample_product_low_stock)
        
        satisfied, details = RULE_01.evaluate(facts)
        self.assertTrue(satisfied)
        self.assertEqual(details["condition"], "LOW STOCK")
        self.assertIn("Current stock (4) is below the minimum threshold (10)", details["reason"])

        # Counter test: Stock well above threshold should not trigger Rule 1
        facts_healthy = dict(facts, stock=20)
        satisfied_healthy, _ = RULE_01.evaluate(facts_healthy)
        self.assertFalse(satisfied_healthy)

    # --------------------------------------------------------------------------
    # 3. REORDER QUANTITY CALCULATION (RULE 3)
    # --------------------------------------------------------------------------
    def test_03_reorder_quantity_calculation(self):
        """Verify target stock formula and reorder quantity math."""
        # Scenario from prompt: stock=4, min_stock=10, monthly_sales=10
        # Target stock = max(10*2, 10+10) = 20
        # Reorder = max(0, 20 - 4) = 16 units
        target = calculate_target_stock(min_stock=10, monthly_sales=10)
        reorder = calculate_reorder_quantity(current_stock=4, min_stock=10, monthly_sales=10)
        self.assertEqual(target, 20)
        self.assertEqual(reorder, 16)

        # Evaluate via RULE_03
        facts = self.engine.build_working_memory(self.sample_product_low_stock)
        satisfied, details = RULE_03.evaluate(facts)
        self.assertTrue(satisfied)
        self.assertIn("Reorder 16 units", details["recommendation"])

        # Edge case: If stock is already abundant, reorder should be 0
        reorder_zero = calculate_reorder_quantity(current_stock=50, min_stock=10, monthly_sales=10)
        self.assertEqual(reorder_zero, 0)

    # --------------------------------------------------------------------------
    # 4. HIGH-DEMAND CLASSIFICATION (RULE 4)
    # --------------------------------------------------------------------------
    def test_04_high_demand_classification(self):
        """Verify products with sales >= threshold trigger RULE-04."""
        facts = self.engine.build_working_memory(self.sample_product_high_demand)
        satisfied, details = RULE_04.evaluate(facts)
        self.assertTrue(satisfied)
        self.assertEqual(details["condition"], "HIGH DEMAND")

        # Below threshold should not fire
        facts_low = dict(facts, monthly_sales=HIGH_DEMAND_SALES_THRESHOLD - 5)
        satisfied_low, _ = RULE_04.evaluate(facts_low)
        self.assertFalse(satisfied_low)

    # --------------------------------------------------------------------------
    # 5. SLOW-MOVING CLASSIFICATION (RULE 5)
    # --------------------------------------------------------------------------
    def test_05_slow_moving_classification(self):
        """Verify low sales + high stock triggers RULE-05."""
        facts = self.engine.build_working_memory(self.sample_product_slow_moving)
        satisfied, details = RULE_05.evaluate(facts)
        self.assertTrue(satisfied)
        self.assertEqual(details["condition"], "SLOW MOVING")

        # Fast moving product with high stock must NOT trigger slow-moving
        facts_fast = dict(facts, monthly_sales=40)
        satisfied_fast, _ = RULE_05.evaluate(facts_fast)
        self.assertFalse(satisfied_fast)

    # --------------------------------------------------------------------------
    # 6. DISCOUNT RECOMMENDATION RESPECTING PURCHASE COST FLOOR (RULE 6)
    # --------------------------------------------------------------------------
    def test_06_discount_recommendation_respects_cost(self):
        """Verify discount recommendation never allows selling below purchase cost."""
        # Case A: Substantial margin (Cost: ₹1,100, Price: ₹2,200) -> 10% discount is safe
        # Discounted price = ₹1,980.00 >= ₹1,100.00
        analysis_safe = calculate_safe_discount(selling_price=2200.00, purchase_cost=1100.00, requested_discount_pct=10.0)
        self.assertTrue(analysis_safe["safe"])
        self.assertEqual(analysis_safe["discounted_price"], 1980.00)
        self.assertEqual(analysis_safe["profit_after_discount"], 880.00)

        # Case B: Razor-thin margin (Cost: ₹950.00, Price: ₹1,000.00)
        # 10% discount would give ₹900.00 (< ₹950.00 cost) -> Must NOT allow 10% discount!
        analysis_unsafe = calculate_safe_discount(selling_price=1000.00, purchase_cost=950.00, requested_discount_pct=10.0)
        self.assertFalse(analysis_unsafe["safe"])
        self.assertGreaterEqual(analysis_unsafe["discounted_price"], 950.00)
        self.assertEqual(analysis_unsafe["max_safe_discount_pct"], 5.0)

        # Case C: Product already selling at or below cost
        analysis_below = calculate_safe_discount(selling_price=1000.00, purchase_cost=1500.00, requested_discount_pct=10.0)
        self.assertFalse(analysis_below["safe"])
        self.assertEqual(analysis_below["recommended_pct"], 0.0)

    # --------------------------------------------------------------------------
    # 7. PROFIT MARGIN CALCULATION & DIVISION BY ZERO SAFETY (RULE 7)
    # --------------------------------------------------------------------------
    def test_07_profit_margin_calculation(self):
        """Verify profit calculations, margin percentages, and safe division."""
        # Normal calculation
        prod = {"selling_price": 200.00, "purchase_cost": 150.00}
        self.assertEqual(calculate_profit(prod), 50.00)
        self.assertEqual(calculate_profit_margin(prod), 25.0)

        # Zero selling price edge case (division by zero safety)
        prod_zero = {"selling_price": 0.0, "purchase_cost": 50.00}
        self.assertEqual(calculate_profit_margin(prod_zero), 0.0)

        # Below cost / loss making test (RULE-07 trigger)
        facts_loss = self.engine.build_working_memory(self.sample_product_below_cost)
        satisfied, details = RULE_07.evaluate(facts_loss)
        self.assertTrue(satisfied)
        self.assertEqual(details["condition"], "NEGATIVE MARGIN / SOLD BELOW COST")
        self.assertEqual(details["priority"], "HIGH")

    # --------------------------------------------------------------------------
    # 8. INVALID INVENTORY DATA HANDLING (VALIDATION)
    # --------------------------------------------------------------------------
    def test_08_invalid_inventory_data_handling(self):
        """Verify input validation rejects invalid fields and malformed records."""
        # Negative price
        bad_price = {"product_id": "X1", "name": "Item", "category": "Cat", "purchase_cost": 10, "selling_price": -5, "stock": 5, "min_stock": 2, "monthly_sales": 10}
        is_valid, msg = validate_product_data(bad_price)
        self.assertFalse(is_valid)
        self.assertIn("cannot be negative", msg)

        # Negative stock
        bad_stock = {"product_id": "X2", "name": "Item", "category": "Cat", "purchase_cost": 10, "selling_price": 20, "stock": -2, "min_stock": 2, "monthly_sales": 10}
        is_valid, msg = validate_product_data(bad_stock)
        self.assertFalse(is_valid)
        self.assertIn("cannot be negative", msg)

        # Empty Product ID
        empty_id = {"product_id": "", "name": "Item", "category": "Cat", "purchase_cost": 10, "selling_price": 20, "stock": 5, "min_stock": 2, "monthly_sales": 10}
        is_valid, msg = validate_product_data(empty_id)
        self.assertFalse(is_valid)
        self.assertIn("empty", msg.lower())

        # Duplicate Product ID
        duplicate_id = {"product_id": "P001", "name": "Item", "category": "Cat", "purchase_cost": 10, "selling_price": 20, "stock": 5, "min_stock": 2, "monthly_sales": 10}
        is_valid, msg = validate_product_data(duplicate_id, existing_ids=["P001", "P002"])
        self.assertFalse(is_valid)
        self.assertIn("already exists", msg)

    # --------------------------------------------------------------------------
    # 9. RULE EXPLANATION GENERATION (EXPLANATION FACILITY)
    # --------------------------------------------------------------------------
    def test_09_rule_explanation_facility(self):
        """Verify Explanation Facility generates transparent IF-THEN audit traces."""
        facts = self.engine.build_working_memory(self.sample_product_low_stock)
        explanation = ExplanationFacility.explain_rule_evaluation(RULE_01, facts)

        self.assertEqual(explanation["rule_id"], "RULE-01")
        self.assertIn("IF", explanation["if_condition"])
        self.assertIn("THEN", explanation["then_action"])
        self.assertTrue(explanation["condition_satisfied"])
        self.assertIn("Current stock: 4", explanation["evaluated_values"])
        self.assertIn("Replenish at least 16 units", explanation["generated_recommendation"])

    # --------------------------------------------------------------------------
    # 10. PRODUCT RECOMMENDATION BASED ON CATEGORY AND BUDGET
    # --------------------------------------------------------------------------
    def test_10_product_recommendation_filtering(self):
        """Verify recommendation engine enforces category, budget, and positive stock."""
        test_catalog = [
            {"product_id": "C1", "name": "Affordable USB Cable", "category": "Electronics", "purchase_cost": 150, "selling_price": 299.00, "stock": 15, "min_stock": 5, "monthly_sales": 50},
            {"product_id": "C2", "name": "Premium Keyboard", "category": "Electronics", "purchase_cost": 2500, "selling_price": 4999.00, "stock": 10, "min_stock": 5, "monthly_sales": 20},
            {"product_id": "C3", "name": "Out of Stock Mouse", "category": "Electronics", "purchase_cost": 300, "selling_price": 599.00, "stock": 0, "min_stock": 5, "monthly_sales": 30},
            {"product_id": "C4", "name": "Cotton T-Shirt", "category": "Clothing", "purchase_cost": 250, "selling_price": 499.00, "stock": 20, "min_stock": 5, "monthly_sales": 25},
        ]

        # Filter: Electronics within budget of ₹1,000
        results, summary = recommend_products(test_catalog, category="Electronics", max_budget=1000.00, min_stock=1)
        
        # Only C1 satisfies all constraints
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["product_id"], "C1")
        self.assertIn("under budget", results[0]["recommendation_reason"])

        # Filter: Clothing under ₹200 (None match)
        empty_results, empty_msg = recommend_products(test_catalog, category="Clothing", max_budget=200.00)
        self.assertEqual(len(empty_results), 0)
        self.assertIn("No suitable products found", empty_msg)

    # --------------------------------------------------------------------------
    # 11. PRODUCT PERFORMANCE CLASSIFICATION (RULE 8)
    # --------------------------------------------------------------------------
    def test_11_performance_classification(self):
        """Verify performance classification into HIGH PERFORMING, NORMAL, and NEEDS REVIEW."""
        # High Demand -> HIGH PERFORMING
        label_high, _ = classify_performance(self.sample_product_high_demand)
        self.assertEqual(label_high, "HIGH PERFORMING")

        # Out of Stock -> NEEDS REVIEW
        label_oos, _ = classify_performance(self.sample_product_out_of_stock)
        self.assertEqual(label_oos, "NEEDS REVIEW")

        # Sold Below Cost -> NEEDS REVIEW
        label_loss, _ = classify_performance(self.sample_product_below_cost)
        self.assertEqual(label_loss, "NEEDS REVIEW")

    # --------------------------------------------------------------------------
    # 12. JSON PERSISTENCE & FILE INTEGRITY
    # --------------------------------------------------------------------------
    def test_12_json_persistence(self):
        """Verify inventory loading and saving to a temporary JSON file."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        try:
            sample_data = [self.sample_product_low_stock]
            # Save
            saved = save_inventory(sample_data, tmp_path)
            self.assertTrue(saved)

            # Load
            loaded = load_inventory(tmp_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["product_id"], "T001")

            # Update Stock
            ok, msg = update_stock(loaded, "T001", 12, mode="set", file_path=tmp_path)
            self.assertTrue(ok)
            reloaded = load_inventory(tmp_path)
            self.assertEqual(reloaded[0]["stock"], 12)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
