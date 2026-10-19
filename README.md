# Retail Expert System: A Rule-Based Intelligent Decision Support System

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![UI Library](https://img.shields.io/badge/CLI_UI-Rich-cyan.svg)
![AI Architecture](https://img.shields.io/badge/AI-Rule--Based%20Expert%20System-green.svg)
![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)
![Currency](https://img.shields.io/badge/Currency-INR%20(%E2%82%B9)-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

An interactive, offline Artificial Intelligence mini-project demonstrating **Knowledge Representation**, **Forward-Chaining Inference**, and **Transparent Decision Support** for retail shopkeepers using Python 3 and the `rich` terminal library.

---

## Table of Contents

- [1. Project Title and Introduction](#1-project-title-and-introduction)
- [2. Abstract](#2-abstract)
- [3. Problem Statement](#3-problem-statement)
- [4. Project Objectives](#4-project-objectives)
- [5. Key Features](#5-key-features)
- [6. Technologies Used](#6-technologies-used)
- [7. System Architecture](#7-system-architecture)
- [8. Rule-Based Knowledge Base](#8-rule-based-knowledge-base)
- [9. IF–THEN Rules Table](#9-ifthen-rules-table)
- [10. Inference Engine and Forward-Chaining Process](#10-inference-engine-and-forward-chaining-process)
- [11. Installation Instructions](#11-installation-instructions)
- [12. How to Run the Application](#12-how-to-run-the-application)
- [13. Application Menu and Sample Output](#13-application-menu-and-sample-output)
- [14. Example Expert Analysis](#14-example-expert-analysis)
- [15. Testing Instructions](#15-testing-instructions)
- [16. Project Folder Structure](#16-project-folder-structure)
- [17. Advantages](#17-advantages)
- [18. Limitations](#18-limitations)
- [19. Future Enhancements](#19-future-enhancements)
- [20. Conclusion](#20-conclusion)

---

## 1. Project Title and Introduction

### Project Title
**Retail Expert System: A Rule-Based Intelligent Decision Support System**

### Introduction
The **Retail Expert System** is a terminal-based decision support system designed to assist independent shopkeepers and retail inventory managers. Built with clean, beginner-friendly Python 3 and the `rich` terminal UI library, the system models the reasoning of an experienced retail consultant. 

Rather than relying on opaque probabilistic black-box models, this application employs a classical, deterministic **Rule-Based Expert System (RBES)** architecture. It monitors inventory levels, identifies stockouts, estimates optimal replenishment quantities, recommends promotional discounts while strictly guarding cost floors, and audits profit margins—all displayed with structured visual formatting and full step-by-step reasoning transparency.

---

## 2. Abstract

Small and medium-scale retail operations often struggle with balancing inventory: holding too much stock locks up capital and risks product obsolescence, while holding too little leads to lost sales and dissatisfied customers. Furthermore, ad-hoc discounting strategies can inadvertently sell items below cost price, resulting in cash losses.

This project implements an artificial intelligence decision support system founded on declarative knowledge representation and forward chaining. The system stores retail domain knowledge as structured **IF–THEN rules** and evaluates current stock facts in working memory. It flags low and zero-stock conditions, calculates precise reorder targets using safety stock formulas, identifies fast- and slow-moving items, and generates auditable recommendations. The entire workflow runs completely offline in any terminal, displaying all monetary amounts in **Indian Rupees (₹ / INR)**.

---

## 3. Problem Statement

Retail store managers face recurring operational challenges:

1. **Unnoticed Stockouts**: Running out of critical stock-keeping units (SKUs) causes immediate revenue loss and pushes customers to competitors.
2. **Capital Inefficiency**: Capital remains tied up in slow-moving merchandise that lingers on shelves for months.
3. **Risky Discount Decisions**: Unstructured markdowns risk selling products below wholesale purchase cost.
4. **Lack of Explainability**: Most modern analytics software functions as a black box, giving recommendations without stating *why* an action should be taken.
5. **Connectivity and Cost Barriers**: Small retailers need offline solutions that do not incur cloud hosting fees or require internet connectivity.

---

## 4. Project Objectives

- **Model Domain Knowledge**: Encode retail principles into modular, declarative IF–THEN rules.
- **Implement Forward Chaining**: Develop an inference engine that evaluates product facts and infers actionable conclusions.
- **Enforce Business Constraints**: Guarantee that suggested promotional discounts never fall below the purchase cost floor.
- **Provide an Explanation Facility**: Enable shopkeepers and presentation evaluators to inspect the exact evaluated facts and rule premises behind any recommendation.
- **Build an Attractive Terminal UI**: Use the `rich` library to deliver clean tables, colored status badges, and styled panels.
- **Maintain Local Data Persistence**: Provide reliable JSON loading and saving with robust input validation.
- **Support Indian Commerce**: Standardize all currency formatting, pricing, and budget filters in Indian Rupees (`₹`).

---

## 5. Key Features

- **Interactive Terminal Dashboard**: Displays date, time, total products, out-of-stock count, low-stock warnings, and reorder alerts at a glance.
- **Inventory Catalog Management**: Complete CRUD operations (Add, View, Search, Update Stock) with validation against negative prices and duplicate IDs.
- **Forward-Chaining Rule Engine**: Automatically evaluates the entire inventory against 8 domain rules in order of priority.
- **Priority-Ranked Recommendations**: Categorizes every suggestion into `HIGH`, `MEDIUM`, or `LOW` priority.
- **Automated Reorder Quantity Math**: Calculates reorder batches based on target stock and monthly sales demand.
- **Promotional Discount Advisor**: Proposes safe clearance discounts for slow-moving products while guaranteeing zero loss-making sales.
- **Customer Product Recommender**: Interactive multi-attribute filtering by product category, budget ceiling (in ₹), and demand preferences.
- **Custom Rule Tester (Explanation Facility)**: Test any rule interactively against active inventory items or custom hypothetical facts.
- **Executive Retail Valuation**: Aggregates total inventory cost value, retail value, and potential gross profit in `₹`.
- **Text Audit Report Exporter**: Exports timestamped, formatted analysis reports directly to disk.

---

## 6. Technologies Used

| Technology | Role | Justification |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Programming Language | Clean syntax, native standard library, and high cross-platform compatibility. |
| **`rich` Library** | Terminal User Interface | Formats colorful tables, panels, status badges, and interactive prompts. |
| **JSON** | Working Memory Persistence | Lightweight, human-readable, offline file storage without external database overhead. |
| **`unittest`** | Verification Framework | Python's built-in testing tool used to validate all 12 operational scenarios. |
| **Standard Library** | System Operations | Standard modules used: `sys`, `os`, `json`, `datetime`, `typing`, `math`, `tempfile`. |

---

## 7. System Architecture

The project strictly follows the classical Artificial Intelligence Expert System architecture:

```text
+-------------------------------------------------------------------------+
|                              USER (Shopkeeper)                          |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  USER INTERFACE & DASHBOARD (main.py)                   |
|   - Terminal Tables   - Input Prompts   - Menus   - Colored Status Cards|
+-------------------------------------------------------------------------+
         |                                                 ^
         v                                                 |
+------------------------------------+   +--------------------------------+
|    WORKING MEMORY (inventory.py)   |   |  EXPLANATION FACILITY & REPORT |
|  - Active Product Facts            |   |  - Step-by-step Audit Traces   |
|  - Inferred Attributes (Margin,    |   |  - Formatted Text File Exporter|
|    Stock Coverage, Loss Status)    |   |    (inference_engine, reports) |
+------------------------------------+   +--------------------------------+
         |                                                 ^
         +------------------------+                        |
                                  v                        |
               +------------------------------------------------+
               |        INFERENCE ENGINE (inference_engine.py)  |
               |  - Forward Chaining Matching Cycle             |
               |  - Conflict Resolution & Precedence (OOS > Low)|
               |  - Generates Recommendation Objects            |
               +------------------------------------------------+
                                  ^
                                  | Rules & Constants
               +------------------------------------------------+
               |        KNOWLEDGE BASE (knowledge_base.py)      |
               |  - Domain Thresholds & Retail Formulas         |
               |  - Declarative Rules (RULE-01 to RULE-08)      |
               +------------------------------------------------+
                                  |
                                  v
                    +---------------------------+
                    | JSON Storage (data/*.json)|
                    +---------------------------+
```

### Architectural Subsystems:
1. **Knowledge Base (`knowledge_base.py`)**: Repository of domain thresholds, mathematical formulas, and declarative `Rule` instances.
2. **Working Memory (`inventory.py`)**: In-memory representation of product facts loaded from `data/inventory.json`.
3. **Inference Engine (`inference_engine.py`)**: Matches facts against rules, applies priority order, and instantiates `Recommendation` objects.
4. **Explanation Facility (`inference_engine.py` / `main.py`)**: Audits why a rule condition succeeded or failed, providing full factual justification.
5. **Report Generator (`reports.py`)**: Creates executive summaries and exports permanent text audit logs.

---

## 8. Rule-Based Knowledge Base

### Domain Thresholds
- **High-Demand Sales Threshold**: `monthly_sales >= 30` units/month
- **Slow-Moving Sales Threshold**: `monthly_sales <= 5` units/month
- **Slow-Moving Inventory Level**: `stock >= 15` units (or `stock >= 2 * min_stock`)
- **Promotional Clearance Discount**: `10.0%`
- **Low Margin Warning Threshold**: `profit_margin < 15.0%`

### Core Retail Formulas
- **Target Stock Formula**:
  `Target Stock = max(2 * Min Stock, Monthly Sales + Min Stock)`
- **Reorder Quantity Formula**:
  `Reorder Quantity = max(0, Target Stock - Current Stock)`
- **Profit Per Unit**:
  `Profit Per Unit = Selling Price - Purchase Cost`
- **Profit Margin Percentage**:
  `Profit Margin (%) = ((Selling Price - Purchase Cost) / Selling Price) * 100`  *(for Selling Price > 0)*
- **Safe Promotional Discount**:
  `Discounted Price = Selling Price * (1 - Discount% / 100)`
  *Constraint:* `Discounted Price >= Purchase Cost`
  `Max Safe Discount (%) = ((Selling Price - Purchase Cost) / Selling Price) * 100`

---

## 9. IF–THEN Rules Table

| Rule ID | Rule Name | Formal IF Condition | Formal THEN Action | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **RULE-01** | Low Stock Alert | `0 < stock <= min_stock` | Classify as **LOW STOCK**; recommend restocking to target stock level. | `HIGH` |
| **RULE-02** | Out-of-Stock Alert | `stock == 0` | Classify as **OUT OF STOCK**; trigger emergency reorder (takes priority over Rule 1). | `HIGH` |
| **RULE-03** | Reorder Recommendation | `stock <= min_stock AND monthly_sales > 0` | Compute reorder quantity: `max(0, Target Stock - Current Stock)`. | `HIGH` |
| **RULE-04** | High-Demand Product | `monthly_sales >= 30` | Classify as **HIGH DEMAND**; maintain safety stock and negotiate supplier volume terms. | `MEDIUM` |
| **RULE-05** | Slow-Moving Product | `monthly_sales <= 5 AND (stock >= 15 OR stock >= 2*min_stock)` | Classify as **SLOW MOVING**; warn of stagnant capital and advise promotional bundling. | `MEDIUM` |
| **RULE-06** | Discount Recommendation | `is_slow_moving AND selling_price > purchase_cost` | Propose up to 10% clearance discount, capped to ensure price never drops below cost. | `MEDIUM` |
| **RULE-07** | Profit Margin Analysis | `selling_price < purchase_cost OR profit_margin < 15%` | Flag pricing risk: if selling below cost, immediately advise raising price to at least cost or 20% margin. | `HIGH` / `LOW` |
| **RULE-08** | Performance Classification | Multi-attribute evaluation | Classify product performance as `HIGH PERFORMING`, `NORMAL`, or `NEEDS REVIEW`. | `LOW` |

---

## 10. Inference Engine and Forward-Chaining Process

The system uses a **data-driven forward-chaining cycle**:

```text
[ Current Facts in Working Memory ]
                │
                ▼
[ Evaluate Rule Condition Premises in Priority Order ]
                │
                ├─► Condition TRUE  ──► Fire Rule Action ──► Add Recommendation to Agenda
                │
                └─► Condition FALSE ──► Rule Does Not Fire
                │
                ▼
[ Conflict Resolution: Rule 2 Precedes Rule 1 for Zero Stock ]
                │
                ▼
[ Sort Inferred Recommendations by Priority: HIGH ──► MEDIUM ──► LOW ]
```

### Forward Chaining Pseudocode

```python
def evaluate_inventory(working_memory, knowledge_base):
    recommendations = []
    
    for product in working_memory:
        facts = extract_and_derive_facts(product)
        
        for rule in knowledge_base.get_rules():
            satisfied, details = rule.evaluate(facts)
            
            if satisfied:
                # Rule precedence conflict resolution:
                if rule.rule_id == "RULE-01" and facts["stock"] == 0:
                    continue  # Handled exclusively by RULE-02
                
                rec = Recommendation(
                    product_id=facts["product_id"],
                    product_name=facts["name"],
                    condition=details["condition"],
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    reason=details["reason"],
                    recommendation=details["recommendation"],
                    priority=details["priority"]
                )
                recommendations.append(rec)
                
    sort_by_priority(recommendations, order=["HIGH", "MEDIUM", "LOW"])
    return recommendations
```

---

## 11. Installation Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your system.
- Git (optional, for cloning).

### Step 1: Clone or Download the Repository
```bash
git clone https://github.com/Prasad2123/Retail-Expert-System.git
cd Retail-Expert-System
```

### Step 2: Install Dependencies
Install the required `rich` library:
```bash
pip install -r requirements.txt
```

---

## 12. How to Run the Application

Launch the application directly from the repository root:

```bash
python main.py
```

The application runs inside Windows Command Prompt (`cmd.exe`), Windows PowerShell, macOS Terminal, Linux Bash, or the integrated terminal in VS Code.

---

## 13. Application Menu and Sample Output

### Main Dashboard
```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ★ STORE INTELLIGENCE CONSOLE ★                         ║
║                            RETAIL EXPERT SYSTEM                              ║
║              Rule-Based AI Intelligent Decision Support System               ║
║              Current Time: Monday, Oct 19, 2026 | 07:30 AM                   ║
║                     Forward-Chaining Inference Engine                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

╭──────────────────────────────────────────────────────────────────────────────╮
│ INVENTORY OVERVIEW: Total Products: 12 │ Low Stock: 2 │ Out of Stock: 1      │
│                     Reorders Needed: 3                                       │
╰──────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────────────── MAIN MENU ─────────────────────────────────╮
│ [1] View Product Inventory                                                   │
│ [2] Search Product                                                           │
│ [3] Add New Product                                                          │
│ [4] Update Stock                                                             │
│ [5] Run Expert Analysis                                                      │
│ [6] Product Recommendations                                                  │
│ [7] Test a Rule (AI Explanation Facility)                                    │
│ [8] View Retail Summary                                                      │
│ [9] Export Analysis Report                                                   │
│ [0] Exit Application                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 14. Example Expert Analysis

When selecting **Option [5] (Run Expert Analysis)**, the inference engine evaluates all products and renders formatted recommendation cards:

### Case 1: Out of Stock Alert (`RULE-02` & `RULE-03`)
```text
╭────────────────── [ PRIORITY: HIGH ] Recommendation #01 ─────────────────────╮
│ Artisan Sourdough Bread (ID: P003)                                           │
│ • Condition Triggered : OUT OF STOCK                                         │
│ • Rule Fired          : RULE-02 - Out-of-Stock Alert                         │
│ • Inference Reason    : Available stock is completely depleted (0 units).    │
│                         Immediate stockout in progress.                      │
│ • Expert Action       : Place urgent purchase order for at least 50 units to │
│                         restore inventory to 50 units.                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Case 2: Low Stock Replenishment (`RULE-01` & `RULE-03`)
```text
╭────────────────── [ PRIORITY: HIGH ] Recommendation #04 ─────────────────────╮
│ Wireless Ergonomic Mouse (ID: P004)                                          │
│ • Condition Triggered : LOW STOCK                                            │
│ • Rule Fired          : RULE-01 - Low Stock Alert                            │
│ • Inference Reason    : Current stock (4) is below the minimum threshold (10).│
│ • Expert Action       : Replenish at least 16 units to reach the target      │
│                         stock level (20 units).                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Case 3: Sold Below Cost Financial Anomaly (`RULE-07`)
```text
╭────────────────── [ PRIORITY: HIGH ] Recommendation #10 ─────────────────────╮
│ Clearance Travel Sunscreen SPF 50 (ID: P012)                                 │
│ • Condition Triggered : NEGATIVE MARGIN / SOLD BELOW COST                    │
│ • Rule Fired          : RULE-07 - Profit Margin & Cost Safety Analysis       │
│ • Inference Reason    : Product is selling at ₹199.00, which is below its    │
│                         purchase cost of ₹299.00. Every sale loses ₹100.00   │
│                         per unit.                                            │
│ • Expert Action       : Immediately adjust selling price to at least ₹299.00 │
│                         (break-even) or ₹373.75 to achieve a healthy 20%     │
│                         margin.                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Case 4: Cost-Guarded Promotional Discount (`RULE-06`)
```text
╭───────────────── [ PRIORITY: MEDIUM ] Recommendation #17 ────────────────────╮
│ Noise-Cancelling Headphones (ID: P006)                                       │
│ • Condition Triggered : PROMOTIONAL DISCOUNT RECOMMENDED                     │
│ • Rule Fired          : RULE-06 - Discount Recommendation                    │
│ • Inference Reason    : High inventory (22 units) with sluggish sales (3/mo) │
│                         ties up working capital.                             │
│ • Expert Action       : Apply a 10.0% clearance discount: reduce price from  │
│                         ₹3,999.00 to ₹3,599.10. Preserves ₹1,399.10/unit     │
│                         profit (38.9% margin).                               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 15. Testing Instructions

The repository includes a comprehensive unit test suite in `tests/test_expert_system.py` using Python's built-in `unittest` module.

### Run Tests
```bash
python -m unittest discover -s tests -v
```

### Test Coverage Summary
- `test_01_out_of_stock_detection`: Verifies `stock == 0` fires `RULE-02` and suppresses `RULE-01`.
- `test_02_low_stock_detection`: Verifies `0 < stock <= min_stock` fires `RULE-01`.
- `test_03_reorder_quantity_calculation`: Verifies target stock and reorder quantity mathematics.
- `test_04_high_demand_classification`: Verifies high sales trigger `RULE-04`.
- `test_05_slow_moving_classification`: Verifies low sales and high stock trigger `RULE-05`.
- `test_06_discount_recommendation_respects_cost`: Verifies discounts never reduce price below cost.
- `test_07_profit_margin_calculation`: Verifies profit per unit, margin percentages, and safe division by zero.
- `test_08_invalid_inventory_data_handling`: Verifies rejection of negative numbers and duplicate IDs.
- `test_09_rule_explanation_facility`: Verifies transparent rule audit generation.
- `test_10_product_recommendation_filtering`: Verifies multi-attribute filtering by category and budget.
- `test_11_performance_classification`: Verifies classification into `HIGH PERFORMING`, `NORMAL`, and `NEEDS REVIEW`.
- `test_12_json_persistence`: Verifies safe read/write operations using temporary test files.

All 12 tests pass cleanly in under 0.05 seconds.

---

## 16. Project Folder Structure

```text
Retail-Expert-System/
├── .gitignore                  # Git ignore rules for Python bytecode and caches
├── requirements.txt            # Python dependencies (rich)
├── README.md                   # Comprehensive project documentation
├── main.py                     # CLI entry point, ASCII dashboard, and menus
├── inventory.py                # Working memory, JSON persistence, and validation
├── knowledge_base.py           # Declarative rules (RULE-01 to 08), constants, and formulas
├── inference_engine.py         # Forward-chaining engine and AI explanation facility
├── recommendations.py          # Category/budget advisor and discount calculations
├── reports.py                  # Inventory analytics summary and text report exporter
│
├── data/
│   └── inventory.json          # Persistent catalog of 12 sample products in INR (₹)
│
├── reports/
│   ├── .gitkeep                # Directory marker for exported reports
│   └── expert_analysis_*.txt   # Generated timestamped audit reports
│
└── tests/
    ├── __init__.py             # Test package marker
    └── test_expert_system.py   # Complete 12-scenario test suite
```

---

## 17. Advantages

- **100% Deterministic & Traceable**: Every decision traces back to a specific, auditable IF–THEN rule.
- **Guaranteed Cost-Floor Safety**: Prohibits clearance discounts that would sell items below wholesale cost.
- **Completely Offline**: Requires no cloud services, API tokens, or external network connectivity.
- **Zero Hallucinations**: Eliminates the unpredictability and false facts common in generative AI models.
- **Lightweight & Fast**: Executes complete inventory evaluations in milliseconds.
- **Native Indian Rupee Support**: Built specifically with `₹` currency formatting and sensible Indian retail price points.

---

## 18. Limitations

- **Static Rule Base**: The knowledge base does not automatically discover or derive new rules from raw transaction logs.
- **Independent SKU Modeling**: Rules evaluate each product independently without modeling cross-product purchase affinities (e.g., bread and butter bundled together).
- **Single-Location Scope**: Designed for a single storefront rather than distributed multi-warehouse supply chains.

---

## 19. Future Enhancements

- **Backward-Chaining Diagnostic Facility**: Implement goal-driven reasoning (e.g., *"Why did net profit fall by 15% this quarter?"*).
- **Fuzzy Logic Membership**: Introduce fuzzy sets to smoothly categorize items between "borderline stock" and "adequate stock".
- **Hardware Barcode Integration**: Connect with USB/Bluetooth handheld barcode scanners for real-time checkout updates.
- **Seasonal Demand Coefficients**: Include seasonal weighting factors for festival and holiday demand surges.

---

## 20. Conclusion

The **Retail Expert System** successfully demonstrates the core principles of Artificial Intelligence knowledge engineering. By decoupling the **Knowledge Base** from the **Inference Engine** and backing every conclusion with a transparent **Explanation Facility**, the application provides practical, reliable decision support for retail store owners. The project meets all academic requirements for an undergraduate AI mini-project, offering robust test coverage, professional terminal aesthetics, and strict mathematical data integrity.