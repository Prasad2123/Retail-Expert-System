# Retail Expert System: A Rule-Based Intelligent Decision Support System

An undergraduate Artificial Intelligence mini-project demonstrating **Knowledge Representation**, **Forward-Chaining Inference**, and **Transparent Decision Support** for retail shopkeepers using Python 3 and the `rich` terminal library.

---

## 1. Project Title & Abstract

### Title
**Retail Expert System: A Rule-Based Intelligent Decision Support System**

### Abstract
Small and medium-sized retail businesses frequently struggle with stockouts, overstocking, tied-up working capital, and unintended loss-making pricing. While modern large enterprises employ complex predictive machine-learning pipelines, independent retailers require transparent, deterministic, and easily interpretable decision support that can operate completely offline without external cloud dependencies. 

This project implements a classical Artificial Intelligence **Rule-Based Expert System (RBES)** designed to assist retail store managers in making inventory replenishment, promotional discount, and pricing decisions. By structuring domain expertise into declarative **IF–THEN rules** and applying a **forward-chaining inference engine** with an integrated **explanation facility**, the system audits inventory health, calculates precise reorder quantities, enforces cost-floor constraints on promotions, and flags financial risks in real time.

---

## 2. Problem Statement & Objectives

### Problem Statement
Retail managers must continuously track hundreds of stock-keeping units (SKUs) across multiple categories. In manual retail management:
1. **Stockouts occur unnoticed**, leading to lost customer goodwill and forfeited revenue.
2. **Capital gets locked** in slow-moving or obsolete inventory.
3. **Discount decisions are arbitrary**, occasionally selling products below purchase cost and causing cash losses.
4. **Calculations lack transparency**, as staff cannot easily explain why a specific reorder quantity or discount was chosen.

### Objectives
- Model retail business knowledge as formal declarative rules (Knowledge Base).
- Implement an automated Forward-Chaining Inference Engine to evaluate inventory working memory.
- Provide a Transparent Explanation Facility showing exact facts evaluated and rules triggered.
- Enforce strict business constraints (e.g., promotional discounts must never fall below purchase cost).
- Offer interactive decision support: inventory CRUD, product search, rule testing, customer product recommendations, and report export.
- Deliver an interactive, professional Command-Line Interface (CLI) using the `rich` library.

---

## 3. Scope & Boundaries

- **In Scope:**
  - Deterministic IF–THEN rule evaluation.
  - Forward chaining from facts to conclusions.
  - Multi-category inventory management (Groceries, Electronics, Clothing, Personal Care).
  - Financial risk detection (selling below cost, razor-thin margins).
  - Reorder quantity estimation based on lead demand and safety stock formulas.
  - Customer recommendation matching by budget and category.
  - Local JSON persistence and timestamped text audit reports.
- **Out of Scope (By Design):**
  - Machine learning models, neural networks, or probabilistic black-box models.
  - Cloud APIs, external web scrapers, or database servers.
  - Graphical web/mobile frontends.
  - Automatic purchasing or real-time payment gateway processing.

---

## 4. Technologies Used

| Technology | Purpose | Justification |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Programming Language | Clean syntax, native standard library support, and beginner-friendly readability. |
| **`rich` Library** | Terminal User Interface | Renders colorful tables, styled panels, status badges, and interactive prompts. |
| **JSON** | Local Persistence | Human-readable, structured, lightweight, and offline storage for inventory facts. |
| **Python Standard Library** | Architecture & Math | Modules used: `os`, `sys`, `json`, `datetime`, `typing`, `math`, `tempfile`. |
| **`unittest`** | Automated Verification | Python's native test framework verifying all rules, edge cases, and mathematical models. |

---

## 5. System Architecture

The project strictly follows the classical Artificial Intelligence Expert System paradigm:

```
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
               |  - Domain Thresholds & Formulas                |
               |  - Declarative Rules (RULE-01 to RULE-08)      |
               +------------------------------------------------+
                                  |
                                  v
                    +---------------------------+
                    | JSON Storage (data/*.json)|
                    +---------------------------+
```

### Components:
1. **Knowledge Base (`knowledge_base.py`)**: Stores domain rules, thresholds (e.g., high-demand sales >= 30, slow-moving sales <= 5), and mathematical formulas.
2. **Working Memory (`inventory.py`)**: Represents the current state of facts (product attributes, current stock, monthly sales, calculated margins).
3. **Inference Engine (`inference_engine.py`)**: Forward chains from product facts, matches rule conditions, resolves priority conflicts, and infers recommendations.
4. **Explanation Facility (`inference_engine.py` / `main.py`)**: Explains *why* a rule was satisfied by revealing the underlying mathematical conditions and factual inputs.
5. **Recommendation & Strategy (`recommendations.py`)**: Multi-attribute filtering for customer recommendations and cost-constrained discount planning.
6. **Report Generator (`reports.py`)**: Generates timestamped, readable audit files for store accounting.

---

## 6. Formal IF–THEN Rule Catalog

The expert system encodes 8 core retail rules:

| Rule ID | Rule Name | Formal IF Condition | Formal THEN Action | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **RULE-01** | Low Stock Alert | `0 < stock <= min_stock` | Classify product as **LOW STOCK** and recommend replenishment. | `HIGH` |
| **RULE-02** | Out-of-Stock Alert | `stock == 0` | Classify product as **OUT OF STOCK** and trigger immediate emergency purchase order (takes priority over Rule 1). | `HIGH` |
| **RULE-03** | Reorder Recommendation | `stock <= min_stock AND monthly_sales > 0` | Calculate optimal reorder quantity: `max(0, Target Stock - Stock)` where `Target Stock = max(2*min_stock, monthly_sales + min_stock)`. | `HIGH` |
| **RULE-04** | High-Demand Product | `monthly_sales >= 30` | Classify product as **HIGH DEMAND**; advise safety stock buffer and volume supplier discounts. | `MEDIUM` |
| **RULE-05** | Slow-Moving Product | `monthly_sales <= 5 AND (stock >= 15 OR stock >= 2*min_stock)` | Classify product as **SLOW MOVING**; warn of tied-up capital and suggest promotional review. | `MEDIUM` |
| **RULE-06** | Discount Recommendation | `is_slow_moving AND selling_price > purchase_cost` | Recommend up to 10% clearance discount, strictly capped such that `discounted_price >= purchase_cost`. | `MEDIUM` |
| **RULE-07** | Profit Margin Analysis | `selling_price < purchase_cost OR profit_margin < 15%` | Flag pricing risk: if selling below cost, immediately recommend price increase to break-even or 20% margin. | `HIGH` / `LOW` |
| **RULE-08** | Performance Classification | Multi-attribute evaluation of sales, stock, and margins | Classify product as `HIGH PERFORMING`, `NORMAL`, or `NEEDS REVIEW`. | `LOW` |

---

## 7. Algorithms & Mathematical Formulas

### Forward-Chaining Inference Algorithm (Pseudocode)

```python
# Forward Chaining Algorithm for Retail Decision Support
function EVALUATE_INVENTORY(WorkingMemory, KnowledgeBase):
    Recommendations = []

    for each Product in WorkingMemory:
        # Step 1: Compute derived facts
        Facts = ExtractFacts(Product)
        Facts['profit'] = Facts['selling_price'] - Facts['purchase_cost']
        Facts['margin'] = (Facts['profit'] / Facts['selling_price']) * 100

        # Step 2: Forward Match against Knowledge Base Rules
        for each Rule in KnowledgeBase.Rules:
            Satisfied, Details = Rule.Evaluate(Facts)
            if Satisfied:
                # Step 3: Conflict Resolution & Rule Precedence
                if Rule.ID == 'RULE-01' and Facts['stock'] == 0:
                    continue  # Rule 2 handles zero stock
                
                # Step 4: Add inferred action to working agenda
                Rec = CreateRecommendation(Product, Rule, Details)
                Recommendations.Append(Rec)

    # Step 5: Prioritize Recommendations (HIGH -> MEDIUM -> LOW)
    SortByPriority(Recommendations)
    return Recommendations
```

### Core Mathematical Formulas

1. **Target Stock Formula:**
   $$\text{Target Stock} = \max(2 \times \text{Min Stock},\ \text{Monthly Sales} + \text{Min Stock})$$

2. **Reorder Quantity Formula:**
   $$\text{Reorder Quantity} = \max(0,\ \text{Target Stock} - \text{Current Stock})$$

3. **Profit Per Unit:**
   $$\text{Profit} = \text{Selling Price} - \text{Purchase Cost}$$

4. **Profit Margin Percentage:**
   $$\text{Margin } (\%) = \left(\frac{\text{Selling Price} - \text{Purchase Cost}}{\text{Selling Price}}\right) \times 100 \quad (\text{for Selling Price} > 0)$$

5. **Safe Promotional Discount Constraint:**
   $$\text{Discounted Price} = \text{Selling Price} \times \left(1 - \frac{\text{Discount } \%}{100}\right)$$
   $$\text{Condition: } \text{Discounted Price} \ge \text{Purchase Cost}$$
   $$\text{Max Safe Discount } (\%) = \left(\frac{\text{Selling Price} - \text{Purchase Cost}}{\text{Selling Price}}\right) \times 100$$

---

## 8. Project Structure

```
Retail Expert System/
│
├── main.py                     # Entry point & interactive Rich terminal interface
├── inventory.py                # Working memory facts, JSON CRUD, and validation
├── knowledge_base.py           # Knowledge base: business constants, formulas, and rules
├── inference_engine.py         # Forward-chaining engine & explanation facility
├── recommendations.py          # Category/budget recommendation & discount strategy
├── reports.py                  # Retail analytics summary & text audit report exporter
│
├── data/
│   └── inventory.json          # Persistent JSON inventory data (12 sample products)
│
├── reports/
│   └── .gitkeep                # Directory for generated timestamped analysis reports
│
├── tests/
│   ├── __init__.py             # Test package marker
│   └── test_expert_system.py   # Comprehensive 12-scenario unit test suite
│
├── requirements.txt            # Python dependencies (rich)
└── README.md                   # Complete academic documentation & presentation guide
```

---

## 9. Installation & Execution Guide

### Prerequisites
- Python 3.10 or higher.
- Windows Command Prompt, Windows PowerShell, Linux Terminal, or macOS Terminal.

### Step 1: Clone or Navigate to the Workspace
```bash
cd "D:\Retail Expert System"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python main.py
```

### Step 4: Run Automated Unit Tests
```bash
python -m unittest discover -s tests -v
```

---

## 10. Sample Terminal Output

### Main Dashboard Screen
```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ★ STORE INTELLIGENCE CONSOLE ★                         ║
║                            RETAIL EXPERT SYSTEM                              ║
║              Rule-Based AI Intelligent Decision Support System               ║
║              Current Time: Monday, Oct 19, 2026 | 06:45 AM                   ║
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

### Expert Analysis Trace Example (Low Stock)
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

### Expert Analysis Trace Example (Loss-Making Product & Discount Recommendation)
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

### Explanation Facility Audit Output (Option [7])
```text
╭─────────────────────── Rule Inference Audit: RULE-01 ────────────────────────╮
│ Rule Evaluated : RULE-01 - Low Stock Alert                                   │
│ Formal IF Rule : IF 0 < available_stock <= minimum_stock_threshold           │
│ THEN Action    : THEN classify product as LOW STOCK and recommend            │
│                  replenishment.                                              │
│                                                                              │
│ Evaluated Facts:                                                             │
│ Current stock: 4, Minimum stock threshold: 10                                │
│                                                                              │
│ Condition Status: [ YES - CONDITION SATISFIED ]                              │
│ Reason / Justification:                                                      │
│ Current stock (4) is below the minimum threshold (10).                       │
│                                                                              │
│ Generated Action / Recommendation:                                           │
│ Replenish at least 16 units to reach the target stock level (20 units).      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 11. Testing & Verification

The project includes an automated test suite in [tests/test_expert_system.py](file:///d:/Retail%20Expert%20System/tests/test_expert_system.py) covering 12 critical verification scenarios:

```bash
python -m unittest discover -s tests -v
```

```text
test_01_out_of_stock_detection ... ok
test_02_low_stock_detection ... ok
test_03_reorder_quantity_calculation ... ok
test_04_high_demand_classification ... ok
test_05_slow_moving_classification ... ok
test_06_discount_recommendation_respects_cost ... ok
test_07_profit_margin_calculation ... ok
test_08_invalid_inventory_data_handling ... ok
test_09_rule_explanation_facility ... ok
test_10_product_recommendation_filtering ... ok
test_11_performance_classification ... ok
test_12_json_persistence ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.027s

OK
```

All tests operate on isolated in-memory or temporary files to ensure active product data is never contaminated during automated testing.

---

## 12. College Project Viva & 3–5 Minute Presentation Guide

If demonstrating this project for a faculty evaluation or mini-project viva, follow this structured walkthrough:

### Minute 1: Introduction & Architecture (30–60 seconds)
- State the title: *"Retail Expert System: A Rule-Based Intelligent Decision Support System"*.
- Explain the motivation: Small shopkeepers need transparent, deterministic decision support in Indian Rupees (₹) rather than opaque black-box machine learning.
- Highlight the **AI Architecture**: **Knowledge Base** (declarative rules), **Working Memory** (inventory facts), **Inference Engine** (forward chaining), and **Explanation Facility** (rule auditing).

### Minute 2: Running the System & Live Inventory (60 seconds)
- Launch the application: `python main.py`.
- Select **Option [1]** to display the colorful catalog of 12 realistic retail products with prices in Indian Rupees (₹) spanning Groceries, Electronics, Clothing, and Personal Care.
- Point out the status badges: **IN STOCK** (green), **LOW STOCK** (yellow), and **OUT OF STOCK** (red).

### Minute 3: Running Expert Analysis & Forward Chaining (60 seconds)
- Select **Option [5] (Run Expert Analysis)**.
- Demonstrate how the inference engine evaluates all rules forward from product facts.
- Highlight three specific recommendations:
  1. **Stockout (P003 Artisan Bread)**: Handled by `RULE-02` taking priority over `RULE-01`.
  2. **Low Stock (P004 Wireless Mouse)**: `RULE-01` and `RULE-03` calculate exact reorder of 16 units using $\text{Target Stock} - \text{Current Stock}$.
  3. **Loss-Making Risk (P012 Travel Sunscreen)**: `RULE-07` flags a negative margin item selling at ₹199.00 with purchase cost of ₹299.00.
- Show the option to export the timestamped text audit report to `reports/`.

### Minute 4: Demonstrating the AI Explanation Facility (60 seconds)
- Select **Option [7] (Test a Rule)**.
- Choose **RULE-06 (Discount Recommendation)**.
- Show that the system verifies whether a 10% discount would cause the product to sell below its purchase cost floor in ₹.
- Switch to manual mode: enter custom stock and sales to prove that the rule engine dynamically derives the correct conclusion with a full transparency trace.

### Minute 5: Automated Testing & Conclusion (30 seconds)
- Exit to the shell and run `python -m unittest discover -s tests -v`.
- Show that all 12 test suites pass with 100% test coverage.
- Conclude: *"This project demonstrates a production-grade, transparent expert system adhering strictly to classical AI knowledge engineering principles configured for Indian retail commerce."*

---

## 13. Strengths, Limitations, and Future Enhancements

### Strengths
- **100% Deterministic & Traceable:** Every piece of advice is linked to a concrete IF–THEN rule.
- **Cost-Floor Safety:** Guaranteed financial safety against selling at a loss during clearance promotions.
- **Completely Offline:** Runs without internet access, external API keys, or heavy model weights.
- **Zero Hallucination:** Eliminates probabilistic guessing present in Large Language Models.

### Limitations
- **Fixed Rule Base:** Does not automatically learn new retail rules from historical big data.
- **Independent SKU Evaluation:** Does not currently model cross-product cannibalization or market basket affinity (e.g., buying milk and bread together).

### Future Enhancements
- Integration of **Backward Chaining** for diagnostic goal analysis (e.g., *"Why did net profit fall by 12% this month?"*).
- Support for **Fuzzy Logic** to model gradual transitions between "low stock" and "adequate stock".
- Barcode scanner integration via USB serial emulation.

---

## 14. Academic Declaration

This project is an original software engineering and artificial intelligence implementation developed for educational assessment. All business rules, formulas, and software modules have been implemented cleanly with comprehensive comments and documentation.
#   R e t a i l - E x p e r t - S y s t e m  
 