"""
main.py - Retail Expert System Terminal User Interface
======================================================
Application entry point and interactive terminal user interface powered by Rich.
Simulates an AI Retail Decision Support Expert System for shopkeepers.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

# Import domain modules
from inventory import (
    load_inventory,
    save_inventory,
    get_product_by_id,
    search_products,
    add_product,
    update_stock,
    get_categories,
    calculate_profit,
    calculate_profit_margin,
    format_currency,
    DEFAULT_DATA_PATH
)
from knowledge_base import (
    get_all_rules,
    get_rule_by_id,
    calculate_target_stock,
    calculate_reorder_quantity,
    calculate_safe_discount,
    HIGH_DEMAND_SALES_THRESHOLD,
    SLOW_MOVING_SALES_THRESHOLD,
    SLOW_MOVING_MIN_STOCK
)
from inference_engine import InferenceEngine, ExplanationFacility, Recommendation
from recommendations import recommend_products, generate_promotional_discount_candidates
from reports import generate_inventory_summary, export_analysis_report

# Initialize Rich Console
console = Console()

# Storefront ASCII Art Logo
STOREFRONT_LOGO = r"""
  ___  ___ _____ ___  _____ _      ___ _  ______  ___ _____ _____ 
  | _ \/ _ \_   _/ _ \_   _| |    | __\ \/ / _ \/ _ \_   _/ ____/ 
  |   /  __/ | || (_) || | | |__  | _| >  <|  _/  __/ | | \____ \ 
  |_|_\\___| |_| \___/ |_| |____| |___/_/\_\_|  \___| |_| /_____/ 
                 [ AI RULE-BASED DECISION SUPPORT ]
"""

ASCII_BASKET = r"""
     \======/
      \____/   RETAIL EXPERT SYSTEM
     (______\  Rule-Based AI Decision Support
"""


def clear_screen():
    """Clear terminal screen in a cross-platform manner."""
    os.system("cls" if os.name == "nt" else "clear")


def pause_for_user():
    """Prompt user to press Enter before returning to the main menu."""
    console.print()
    Prompt.ask("[bold dim]Press [cyan]Enter[/cyan] to return to the menu[/bold dim]")


def prompt_int(prompt_text: str, default: Optional[int] = None, min_val: Optional[int] = None) -> Optional[int]:
    """Safely prompt user for an integer with validation."""
    while True:
        default_str = str(default) if default is not None else None
        res = Prompt.ask(prompt_text, default=default_str)
        if res.strip().lower() in ("b", "back", "cancel"):
            return None
        try:
            val = int(res.strip())
            if min_val is not None and val < min_val:
                console.print(f"[bold red]Value cannot be less than {min_val}. Try again.[/bold red]")
                continue
            return val
        except ValueError:
            console.print("[bold red]Invalid number. Please enter an integer (or 'b' to cancel).[/bold red]")


def prompt_float(prompt_text: str, default: Optional[float] = None, min_val: Optional[float] = None) -> Optional[float]:
    """Safely prompt user for a float with validation."""
    while True:
        default_str = f"{default:.2f}" if default is not None else None
        res = Prompt.ask(prompt_text, default=default_str)
        if res.strip().lower() in ("b", "back", "cancel"):
            return None
        try:
            val = float(res.strip())
            if min_val is not None and val < min_val:
                console.print(f"[bold red]Value cannot be less than {min_val}. Try again.[/bold red]")
                continue
            return round(val, 2)
        except ValueError:
            console.print("[bold red]Invalid number. Please enter a valid decimal number (or 'b' to cancel).[/bold red]")


def display_header(inventory: List[Dict[str, Any]]):
    """Render the dashboard header and quick status cards."""
    now_str = datetime.now().strftime("%A, %b %d, %Y | %I:%M %p")

    # Quick metric calculations
    total = len(inventory)
    out_of_stock = sum(1 for p in inventory if int(p.get("stock", 0)) == 0)
    low_stock = sum(1 for p in inventory if 0 < int(p.get("stock", 0)) <= int(p.get("min_stock", 0)))
    reorder_needed = out_of_stock + low_stock

    # ASCII Header Panel
    header_text = Text()
    header_text.append("RETAIL EXPERT SYSTEM\n", style="bold cyan")
    header_text.append("Rule-Based AI Intelligent Decision Support System\n", style="italic white")
    header_text.append(f"Current Time: {now_str}", style="dim")

    console.print(Panel(
        header_text,
        title="[bold yellow]★ STORE INTELLIGENCE CONSOLE ★[/bold yellow]",
        subtitle="[dim]Forward-Chaining Inference Engine[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))

    # Metric summary line
    summary_line = (
        f"[bold white]INVENTORY OVERVIEW:[/bold white] "
        f"Total Products: [bold cyan]{total}[/bold cyan] │ "
        f"Low Stock: [bold yellow]{low_stock}[/bold yellow] │ "
        f"Out of Stock: [bold red]{out_of_stock}[/bold red] │ "
        f"Reorders Needed: [bold magenta]{reorder_needed}[/bold magenta]"
    )
    console.print(Panel(summary_line, border_style="blue", box=box.ROUNDED))


def view_inventory_view(inventory: List[Dict[str, Any]]):
    """Display product inventory in a formatted Rich table."""
    console.print("\n[bold cyan]=== PRODUCT INVENTORY CATALOG ===[/bold cyan]\n")

    if not inventory:
        console.print("[yellow]Inventory is currently empty.[/yellow]")
        pause_for_user()
        return

    table = Table(
        title="Active Retail Inventory Records",
        border_style="blue",
        header_style="bold cyan",
        box=box.ROUNDED,
        show_lines=True
    )

    table.add_column("ID", style="bold yellow", justify="center", width=7)
    table.add_column("Product Name", style="white", min_width=24)
    table.add_column("Category", style="cyan", justify="center")
    table.add_column("Cost (₹)", justify="right")
    table.add_column("Price (₹)", justify="right")
    table.add_column("Margin", justify="right")
    table.add_column("Stock", justify="right")
    table.add_column("Min", justify="right")
    table.add_column("Sales/Mo", justify="right")
    table.add_column("Status", justify="center")

    for p in inventory:
        stock = int(p.get("stock", 0))
        min_stock = int(p.get("min_stock", 0))
        cost = float(p.get("purchase_cost", 0.0))
        price = float(p.get("selling_price", 0.0))
        margin = calculate_profit_margin(p)

        # Status Badge
        if stock == 0:
            status = "[bold white on red] OUT OF STOCK [/bold white on red]"
            stock_style = "bold red"
        elif stock <= min_stock:
            status = "[bold black on yellow] LOW STOCK [/bold black on yellow]"
            stock_style = "bold yellow"
        else:
            status = "[bold green]IN STOCK[/bold green]"
            stock_style = "green"

        margin_style = "red" if margin < 0 else ("yellow" if margin < 15 else "green")

        table.add_row(
            p.get("product_id", ""),
            p.get("name", ""),
            p.get("category", ""),
            format_currency(cost),
            format_currency(price),
            f"[{margin_style}]{margin:.1f}%[/{margin_style}]",
            f"[{stock_style}]{stock}[/{stock_style}]",
            str(min_stock),
            str(p.get("monthly_sales", 0)),
            status
        )

    console.print(table)
    pause_for_user()


def search_product_view(inventory: List[Dict[str, Any]]):
    """Search for products by ID, name, or category."""
    console.print("\n[bold cyan]=== SEARCH PRODUCT INVENTORY ===[/bold cyan]")
    query = Prompt.ask("[bold]Enter Product ID, Name, or Category[/bold] (or 'b' to back)")
    
    if query.strip().lower() in ("b", "back", "cancel") or not query.strip():
        return

    results = search_products(inventory, query)

    if not results:
        console.print(f"[bold yellow]No products found matching '{query}'.[/bold yellow]")
        pause_for_user()
        return

    console.print(f"\n[green]Found {len(results)} matching product(s):[/green]\n")

    for p in results:
        margin = calculate_profit_margin(p)
        profit = calculate_profit(p)
        stock = int(p.get("stock", 0))
        min_stock = int(p.get("min_stock", 0))
        sales = int(p.get("monthly_sales", 0))

        status_text = (
            "[bold red]OUT OF STOCK[/bold red]" if stock == 0 else
            ("[bold yellow]LOW STOCK[/bold yellow]" if stock <= min_stock else "[bold green]IN STOCK[/bold green]")
        )

        card_content = (
            f"[bold white]{p.get('name')}[/bold white]  [dim]({p.get('category')})[/dim]\n"
            f"• Product ID     : [cyan]{p.get('product_id')}[/cyan]\n"
            f"• Stock Level    : {stock} units (Min Threshold: {min_stock}) → {status_text}\n"
            f"• Monthly Sales  : {sales} units/month\n"
            f"• Cost Price     : {format_currency(float(p.get('purchase_cost', 0)))}\n"
            f"• Selling Price  : {format_currency(float(p.get('selling_price', 0)))}\n"
            f"• Profit / Unit  : {format_currency(profit)} (Margin: {margin:.1f}%)"
        )

        console.print(Panel(
            card_content,
            title=f"[bold cyan]Product: {p.get('product_id')}[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        ))

    pause_for_user()


def add_product_view(inventory: List[Dict[str, Any]]):
    """Interactive guided form for adding a new product record."""
    console.print("\n[bold cyan]=== ADD NEW PRODUCT RECORD ===[/bold cyan]")
    console.print("[dim]Fill in the product details. Type 'b' at any prompt to cancel.[/dim]\n")

    # Unique Product ID
    existing_ids = [str(p.get("product_id", "")).strip().upper() for p in inventory]
    while True:
        pid = Prompt.ask("[bold]Product ID[/bold] (e.g. P013)").strip().upper()
        if pid.lower() in ("b", "back", "cancel"):
            return
        if not pid:
            console.print("[bold red]Product ID cannot be empty.[/bold red]")
            continue
        if pid in existing_ids:
            console.print(f"[bold red]Product ID '{pid}' already exists. Choose a unique ID.[/bold red]")
            continue
        break

    # Product Name
    while True:
        name = Prompt.ask("[bold]Product Name[/bold]").strip()
        if name.lower() in ("b", "back", "cancel"):
            return
        if not name:
            console.print("[bold red]Product name cannot be empty.[/bold red]")
            continue
        break

    # Category selection
    categories = get_categories(inventory)
    console.print(f"[dim]Existing categories: {', '.join(categories)}[/dim]")
    cat = Prompt.ask("[bold]Category[/bold] (pick existing or type new)").strip()
    if cat.lower() in ("b", "back", "cancel") or not cat:
        cat = "General"

    # Numeric inputs with validation
    cost = prompt_float("[bold]Purchase Cost (₹)[/bold]", min_val=0.0)
    if cost is None:
        return

    price = prompt_float("[bold]Selling Price (₹)[/bold]", min_val=0.0)
    if price is None:
        return

    if price < cost:
        console.print(f"[bold yellow]Warning: Selling price ({format_currency(price)}) is below cost ({format_currency(cost)}). This product will operate at a loss.[/bold yellow]")

    stock = prompt_int("[bold]Initial Stock Quantity[/bold]", min_val=0)
    if stock is None:
        return

    min_stock = prompt_int("[bold]Minimum Stock Threshold[/bold]", min_val=0)
    if min_stock is None:
        return

    sales = prompt_int("[bold]Estimated Monthly Sales[/bold]", min_val=0)
    if sales is None:
        return

    new_prod = {
        "product_id": pid,
        "name": name,
        "category": cat,
        "purchase_cost": cost,
        "selling_price": price,
        "stock": stock,
        "min_stock": min_stock,
        "monthly_sales": sales
    }

    # Confirmation
    console.print()
    console.print(Panel(
        f"ID: [bold]{pid}[/bold] | Name: [bold]{name}[/bold] | Category: {cat}\n"
        f"Cost: {format_currency(cost)} | Price: {format_currency(price)} | Stock: {stock} | Min: {min_stock} | Sales: {sales}",
        title="[bold green]Confirm New Product[/bold green]",
        border_style="green"
    ))

    confirm = Confirm.ask("Do you want to save this product to inventory?")
    if confirm:
        success, msg = add_product(inventory, new_prod)
        if success:
            console.print(f"\n[bold green]✔ {msg}[/bold green]")
        else:
            console.print(f"\n[bold red]✖ Error: {msg}[/bold red]")
    else:
        console.print("[yellow]Product addition cancelled.[/yellow]")

    pause_for_user()


def update_stock_view(inventory: List[Dict[str, Any]]):
    """Update stock quantity for an existing product."""
    console.print("\n[bold cyan]=== UPDATE PRODUCT STOCK LEVEL ===[/bold cyan]")
    pid = Prompt.ask("[bold]Enter Product ID to update[/bold] (or 'b' to back)").strip().upper()
    if pid.lower() in ("b", "back", "cancel") or not pid:
        return

    product = get_product_by_id(inventory, pid)
    if not product:
        console.print(f"[bold red]Product with ID '{pid}' was not found.[/bold red]")
        pause_for_user()
        return

    current_stock = int(product.get("stock", 0))
    console.print(f"\nProduct: [bold white]{product.get('name')}[/bold white]")
    console.print(f"Current Stock: [bold cyan]{current_stock}[/bold cyan] units (Min threshold: {product.get('min_stock')})\n")

    console.print("[1] Set exact stock quantity")
    console.print("[2] Add stock (+ replenishment)")
    console.print("[3] Deduct stock (- sales / wastage)")
    console.print("[0] Cancel")

    choice = Prompt.ask("[bold]Select update mode[/bold]", choices=["1", "2", "3", "0"], default="1")

    if choice == "0":
        return
    elif choice == "1":
        new_qty = prompt_int("Enter new exact stock count", min_val=0)
        if new_qty is None:
            return
        success, msg = update_stock(inventory, pid, new_qty, mode="set")
    elif choice == "2":
        add_qty = prompt_int("Enter number of units received", min_val=1)
        if add_qty is None:
            return
        success, msg = update_stock(inventory, pid, add_qty, mode="delta")
    elif choice == "3":
        deduct_qty = prompt_int("Enter number of units sold/removed", min_val=1)
        if deduct_qty is None:
            return
        success, msg = update_stock(inventory, pid, -deduct_qty, mode="delta")

    if success:
        console.print(f"\n[bold green]✔ {msg}[/bold green]")
    else:
        console.print(f"\n[bold red]✖ {msg}[/bold red]")

    pause_for_user()


def run_expert_analysis_view(inventory: List[Dict[str, Any]]):
    """
    Run forward-chaining expert analysis over current inventory working memory.
    Displays all triggered rules, priorities, reasons, and recommendations.
    """
    console.print("\n[bold cyan]=== RUNNING FORWARD-CHAINING EXPERT ANALYSIS ===[/bold cyan]")
    console.print("[dim]Evaluating inventory facts against Knowledge Base rules...[/dim]\n")

    engine = InferenceEngine()
    recommendations = engine.evaluate_inventory(inventory, include_normal_performance=False)
    summary = engine.get_analysis_summary(inventory, recommendations)

    if not recommendations:
        console.print(Panel(
            "[bold green]All products meet operational standards. No critical rules triggered.[/bold green]",
            title="[bold green]Expert Analysis Result[/bold green]",
            border_style="green"
        ))
        pause_for_user()
        return

    # Render recommendations
    for idx, rec in enumerate(recommendations, 1):
        if rec.priority == "HIGH":
            border_color = "red"
            priority_tag = "[bold white on red] PRIORITY: HIGH [/bold white on red]"
        elif rec.priority == "MEDIUM":
            border_color = "yellow"
            priority_tag = "[bold black on yellow] PRIORITY: MEDIUM [/bold black on yellow]"
        else:
            border_color = "cyan"
            priority_tag = "[bold black on cyan] PRIORITY: LOW [/bold black on cyan]"

        content = (
            f"[bold white]{rec.product_name}[/bold white] [dim](ID: {rec.product_id})[/dim]\n"
            f"• [bold]Condition Triggered :[/bold] [bold {border_color}]{rec.condition}[/bold {border_color}]\n"
            f"• [bold]Rule Fired          :[/bold] [cyan]{rec.rule_id} - {rec.rule_name}[/cyan]\n"
            f"• [bold]Inference Reason    :[/bold] {rec.reason}\n"
            f"• [bold]Expert Action       :[/bold] [bold white]{rec.recommendation}[/bold white]"
        )

        console.print(Panel(
            content,
            title=f"{priority_tag} [bold]Recommendation #{idx:02d}[/bold]",
            border_style=border_color,
            box=box.ROUNDED
        ))

    # Summary Panel
    summary_text = (
        f"Total Rules Fired: [bold cyan]{summary['total_recommendations']}[/bold cyan] across "
        f"[bold white]{summary['affected_products_count']}[/bold white] product(s).\n"
        f"• [bold red]High Priority (Immediate Action)[/bold red]   : {summary['high_priority_count']}\n"
        f"• [bold yellow]Medium Priority (Tactical Review)[/bold yellow] : {summary['medium_priority_count']}\n"
        f"• [bold cyan]Low Priority (Routine Advisory)[/bold cyan]    : {summary['low_priority_count']}"
    )

    console.print(Panel(
        summary_text,
        title="[bold yellow]Analysis Summary[/bold yellow]",
        border_style="yellow",
        box=box.DOUBLE
    ))

    # Prompt to export report directly
    export_now = Confirm.ask("Would you like to export this full report to a text file now?", default=False)
    if export_now:
        success, res = export_analysis_report(inventory, recommendations)
        if success:
            console.print(f"\n[bold green]✔ Report saved successfully to:[/bold green] [cyan]{res}[/cyan]")
        else:
            console.print(f"\n[bold red]✖ Failed to export report: {res}[/bold red]")

    pause_for_user()


def product_recommendations_view(inventory: List[Dict[str, Any]]):
    """Shopkeeper / customer-facing product recommendation assistant."""
    console.print("\n[bold cyan]=== PRODUCT RECOMMENDATION ADVISOR ===[/bold cyan]")
    console.print("[dim]Filter inventory to discover the best products based on budget and demand.[/dim]\n")

    # Category Filter
    categories = get_categories(inventory)
    console.print("[bold]Available Categories:[/bold] " + ", ".join(f"[cyan]{c}[/cyan]" for c in categories))
    category_choice = Prompt.ask("Enter category to filter (or 'ALL' for any)", default="ALL").strip()

    # Budget Filter
    budget_input = Prompt.ask("Enter maximum budget (₹) (or 0 for no limit)", default="0").strip()
    try:
        max_budget = float(budget_input)
        if max_budget <= 0:
            max_budget = None
    except ValueError:
        max_budget = None

    # Demand preference
    high_demand_only = Confirm.ask("Only recommend bestsellers / high-demand items?", default=False)
    demand_pref = "high_demand" if high_demand_only else None

    # Run recommendation rules
    matched, message = recommend_products(
        inventory,
        category=category_choice,
        max_budget=max_budget,
        min_stock=1,
        demand_preference=demand_pref
    )

    if not matched:
        console.print(Panel(
            f"[bold yellow]{message}[/bold yellow]",
            title="[bold yellow]No Products Found[/bold yellow]",
            border_style="yellow"
        ))
        pause_for_user()
        return

    console.print(f"\n[bold green]✔ {message}[/bold green]\n")

    table = Table(
        title="Recommended Product Matches",
        border_style="green",
        header_style="bold green",
        box=box.ROUNDED
    )
    table.add_column("Product", style="bold white", min_width=22)
    table.add_column("Category", style="cyan")
    table.add_column("Price", justify="right")
    table.add_column("Stock", justify="right", style="green")
    table.add_column("Monthly Sales", justify="right")
    table.add_column("Recommendation Reason", style="italic")

    for item in matched:
        table.add_row(
            item["name"],
            item["category"],
            format_currency(item["selling_price"]),
            str(item["stock"]),
            str(item["monthly_sales"]),
            item["recommendation_reason"]
        )

    console.print(table)
    pause_for_user()


def test_rule_view(inventory: List[Dict[str, Any]]):
    """
    Custom Rule Tester module:
    Designed for college project presentations and viva questions!
    Allows interactive inspection of knowledge base rules and working memory reasoning.
    """
    console.print("\n[bold cyan]=== CUSTOM RULE TESTER (AI EXPLANATION FACILITY) ===[/bold cyan]")
    console.print("[dim]Select a knowledge base rule to inspect its conditions and reasoning.[/dim]\n")

    rules = get_all_rules()
    for idx, rule in enumerate(rules, 1):
        console.print(f"[{idx}] [bold cyan]{rule.rule_id}[/bold cyan]: {rule.name} (Priority: {rule.priority})")

    rule_choice = Prompt.ask("\nSelect rule number to test (or '0' to back)", default="1")
    if rule_choice == "0" or not rule_choice.isdigit():
        return

    idx = int(rule_choice) - 1
    if idx < 0 or idx >= len(rules):
        console.print("[bold red]Invalid rule choice.[/bold red]")
        pause_for_user()
        return

    selected_rule = rules[idx]

    console.print(f"\nSelected: [bold yellow]{selected_rule.rule_id} - {selected_rule.name}[/bold yellow]")
    console.print("[1] Test against an existing product from inventory")
    console.print("[2] Enter custom hypothetical facts interactively")

    mode = Prompt.ask("Choose testing method", choices=["1", "2"], default="1")

    if mode == "1":
        # Select product
        pid = Prompt.ask("Enter Product ID from inventory", default="P004").strip().upper()
        prod = get_product_by_id(inventory, pid)
        if not prod:
            console.print(f"[bold red]Product '{pid}' not found.[/bold red]")
            pause_for_user()
            return
        facts = InferenceEngine().build_working_memory(prod)
    else:
        # Enter custom test facts
        console.print("\n[dim]Enter hypothetical working memory facts:[/dim]")
        stock = prompt_int("Stock quantity", default=4, min_val=0)
        min_stock = prompt_int("Minimum stock threshold", default=10, min_val=0)
        sales = prompt_int("Monthly sales volume", default=10, min_val=0)
        cost = prompt_float("Purchase cost (₹)", default=450.0, min_val=0.0)
        price = prompt_float("Selling price (₹)", default=899.0, min_val=0.0)

        if any(x is None for x in (stock, min_stock, sales, cost, price)):
            return

        facts = {
            "product_id": "TEST-PROD",
            "name": "Hypothetical Demo Item",
            "category": "Testing",
            "stock": stock,
            "min_stock": min_stock,
            "monthly_sales": sales,
            "purchase_cost": cost,
            "selling_price": price
        }

    # Evaluate using Explanation Facility
    explanation = ExplanationFacility.explain_rule_evaluation(selected_rule, facts)

    # Display reasoning trace
    result_style = "bold green" if explanation["condition_satisfied"] else "bold red"
    result_badge = "[bold white on green] YES - CONDITION SATISFIED [/bold white on green]" if explanation["condition_satisfied"] else "[bold white on red] NO - CONDITION NOT MET [/bold white on red]"

    audit_text = (
        f"[bold]Rule Evaluated :[/bold] [cyan]{explanation['rule_id']} - {explanation['rule_name']}[/cyan]\n"
        f"[bold]Formal IF Rule :[/bold] {explanation['if_condition']}\n"
        f"[bold]THEN Action    :[/bold] {explanation['then_action']}\n\n"
        f"[bold]Evaluated Facts:[/bold]\n{explanation['evaluated_values']}\n\n"
        f"[bold]Condition Status:[/bold] {result_badge}\n"
        f"[bold]Reason / Justification:[/bold]\n{explanation['generated_reason']}\n\n"
        f"[bold]Generated Action / Recommendation:[/bold]\n[{result_style}]{explanation['generated_recommendation']}[/{result_style}]"
    )

    console.print(Panel(
        audit_text,
        title=f"[bold yellow]Rule Inference Audit: {explanation['rule_id']}[/bold yellow]",
        border_style="cyan" if explanation["condition_satisfied"] else "red",
        box=box.ROUNDED
    ))

    pause_for_user()


def retail_summary_view(inventory: List[Dict[str, Any]]):
    """Executive retail summary dashboard."""
    console.print("\n[bold cyan]=== RETAIL EXECUTIVE SUMMARY & ANALYTICS ===[/bold cyan]\n")

    summary = generate_inventory_summary(inventory)

    # Financial Estimates Panel
    fin_text = (
        f"• Total Active Products in Catalog : [bold cyan]{summary['total_products']}[/bold cyan]\n"
        f"• Total Inventory Units in Stock   : [bold cyan]{summary['total_units']:,}[/bold cyan] units\n"
        f"• Total Estimated Inventory Cost   : [bold yellow]{format_currency(summary['total_cost_value'])}[/bold yellow]\n"
        f"• Total Estimated Retail Value     : [bold green]{format_currency(summary['total_retail_value'])}[/bold green]\n"
        f"• Estimated Potential Gross Profit : [bold green]{format_currency(summary['total_potential_profit'])}[/bold green]\n\n"
        f"[dim italic]* Note: Financial figures are estimates calculated from active catalog units.[/dim italic]"
    )
    console.print(Panel(
        fin_text,
        title="[bold yellow]Estimated Financial Valuation[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    ))

    # Health & Risk Indicators Table
    health_table = Table(
        title="Inventory Health & Anomaly Indicators",
        border_style="cyan",
        header_style="bold cyan",
        box=box.ROUNDED
    )
    health_table.add_column("Retail Indicator", style="bold white")
    health_table.add_column("Count", justify="center")
    health_table.add_column("Status / Urgency")

    out_cnt = len(summary["out_of_stock_products"])
    low_cnt = len(summary["low_stock_products"])
    loss_cnt = len(summary["below_cost_products"])
    high_cnt = len(summary["high_demand_products"])
    slow_cnt = len(summary["slow_moving_products"])

    health_table.add_row(
        "Out of Stock (Zero Inventory)",
        str(out_cnt),
        "[bold red]CRITICAL (Stockout In Progress)[/bold red]" if out_cnt > 0 else "[green]Optimal[/green]"
    )
    health_table.add_row(
        "Low Stock (At/Below Threshold)",
        str(low_cnt),
        "[bold yellow]WARNING (Reorder Needed)[/bold yellow]" if low_cnt > 0 else "[green]Optimal[/green]"
    )
    health_table.add_row(
        "Sold Below Cost (Negative Margin)",
        str(loss_cnt),
        "[bold red]HIGH FINANCIAL RISK[/bold red]" if loss_cnt > 0 else "[green]None[/green]"
    )
    health_table.add_row(
        "High-Demand Bestsellers",
        str(high_cnt),
        "[bold cyan]Revenue Drivers[/bold cyan]"
    )
    health_table.add_row(
        "Slow-Moving (Stagnant Capital)",
        str(slow_cnt),
        "[bold yellow]Promotions / Discount Candidates[/bold yellow]" if slow_cnt > 0 else "[green]None[/green]"
    )

    console.print(health_table)

    # Category Breakdown
    cat_table = Table(
        title="Category Distribution",
        border_style="blue",
        header_style="bold blue",
        box=box.ROUNDED
    )
    cat_table.add_column("Category", style="bold cyan")
    cat_table.add_column("Product Types", justify="center")
    cat_table.add_column("Units in Stock", justify="right")
    cat_table.add_column("Est. Retail Value (₹)", justify="right")

    for cat_name, cat_data in summary["category_summary"].items():
        cat_table.add_row(
            cat_name,
            str(cat_data["count"]),
            str(cat_data["units"]),
            format_currency(cat_data['retail_value'])
        )

    console.print(cat_table)
    pause_for_user()


def export_report_view(inventory: List[Dict[str, Any]]):
    """Export expert analysis report to a text file."""
    console.print("\n[bold cyan]=== EXPORT EXPERT ANALYSIS REPORT ===[/bold cyan]")
    console.print("[dim]Generating comprehensive report with all triggered rules and inventory metrics...[/dim]\n")

    engine = InferenceEngine()
    recommendations = engine.evaluate_inventory(inventory, include_normal_performance=False)
    
    success, filepath = export_analysis_report(inventory, recommendations)

    if success:
        console.print(Panel(
            f"[bold green]✔ Report successfully exported![/bold green]\n\n"
            f"• File Location: [cyan]{filepath}[/cyan]\n"
            f"• Total Recommendations Documented: [bold white]{len(recommendations)}[/bold white]",
            title="[bold green]Report Generated[/bold green]",
            border_style="green",
            box=box.ROUNDED
        ))
    else:
        console.print(f"[bold red]✖ Error exporting report: {filepath}[/bold red]")

    pause_for_user()


def main_menu():
    """Main application loop."""
    # Load working memory from local JSON
    inventory = load_inventory()

    while True:
        try:
            clear_screen()
            display_header(inventory)

            menu_text = (
                "[bold cyan][1][/bold cyan] View Product Inventory\n"
                "[bold cyan][2][/bold cyan] Search Product\n"
                "[bold cyan][3][/bold cyan] Add New Product\n"
                "[bold cyan][4][/bold cyan] Update Stock\n"
                "[bold cyan][5][/bold cyan] [bold green]Run Expert Analysis[/bold green]\n"
                "[bold cyan][6][/bold cyan] Product Recommendations\n"
                "[bold cyan][7][/bold cyan] [bold yellow]Test a Rule (AI Explanation Facility)[/bold yellow]\n"
                "[bold cyan][8][/bold cyan] View Retail Summary\n"
                "[bold cyan][9][/bold cyan] Export Analysis Report\n"
                "[bold red][0][/bold red] Exit Application"
            )

            console.print(Panel(
                menu_text,
                title="[bold yellow]MAIN MENU[/bold yellow]",
                border_style="cyan",
                box=box.ROUNDED
            ))

            choice = Prompt.ask(
                "[bold]Select an option[/bold]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                default="5"
            )

            if choice == "1":
                view_inventory_view(inventory)
            elif choice == "2":
                search_product_view(inventory)
            elif choice == "3":
                add_product_view(inventory)
            elif choice == "4":
                update_stock_view(inventory)
            elif choice == "5":
                run_expert_analysis_view(inventory)
            elif choice == "6":
                product_recommendations_view(inventory)
            elif choice == "7":
                test_rule_view(inventory)
            elif choice == "8":
                retail_summary_view(inventory)
            elif choice == "9":
                export_report_view(inventory)
            elif choice == "0":
                clear_screen()
                console.print(Panel(
                    "[bold green]Thank you for using Retail Expert System.[/bold green]\n"
                    "[dim]Session ended safely. All data persisted to local storage.[/dim]",
                    title="[bold cyan]Goodbye![/bold cyan]",
                    border_style="cyan"
                ))
                sys.exit(0)

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Program interrupted by user. Exiting gracefully...[/yellow]")
            sys.exit(0)


if __name__ == "__main__":
    main_menu()
