#!/usr/bin/env python3
"""
Shopping List Generator

Interactively select recipes and generate an aggregated shopping list.

Usage:
    python shopping.py
    python shopping.py --recipes-dir "path/to/recipes"
"""

import json
import math
import sys
from datetime import date
from pathlib import Path

from parser import parse_recipe

# Default recipes directory
DEFAULT_RECIPES_DIR = Path(r"C:\Users\thari\Tharitha_OW\70 Reciepes")
UNIT_WEIGHTS_FILE = Path(__file__).parent / "unit_weights.json"


def load_unit_weights() -> dict:
    """Load unit weight conversions from config file."""
    if UNIT_WEIGHTS_FILE.exists():
        return json.loads(UNIT_WEIGHTS_FILE.read_text(encoding='utf-8'))
    return {}


def get_recipe_files(recipes_dir: Path) -> list[Path]:
    """Get all recipe markdown files, excluding template."""
    recipes = []
    for f in recipes_dir.glob("*.md"):
        if f.name.startswith("_"):
            continue
        recipes.append(f)
    return sorted(recipes, key=lambda p: p.stem)


def display_recipes(recipes: list[Path]) -> None:
    """Display numbered list of available recipes."""
    print("\nAvailable Recipes:")
    print("-" * 40)
    for i, recipe in enumerate(recipes, 1):
        print(f"  {i}. {recipe.stem}")
    print()


def parse_selection(selection: str, max_num: int) -> list[int]:
    """
    Parse user selection string into list of indices.
    Supports: "1,3,5" or "1-4" or "1,3-5,7" or "all"
    """
    if selection.strip().lower() == "all":
        return list(range(max_num))

    indices = []
    parts = selection.replace(" ", "").split(",")

    for part in parts:
        if "-" in part:
            start, end = part.split("-", 1)
            start_idx = int(start) - 1
            end_idx = int(end) - 1
            indices.extend(range(start_idx, end_idx + 1))
        else:
            indices.append(int(part) - 1)

    # Filter valid indices
    return [i for i in indices if 0 <= i < max_num]


def aggregate_ingredients(recipes: list[Path]) -> dict[str, dict]:
    """
    Parse recipes and aggregate ingredients by URL.
    Returns dict: url -> {name, total_grams}
    """
    aggregated = {}

    for recipe_path in recipes:
        try:
            recipe = parse_recipe(str(recipe_path))
        except ValueError as e:
            print(f"  Warning: Skipping {recipe_path.stem}: {e}")
            continue

        for ingredient in recipe.ingredients:
            url = ingredient.url
            if url in aggregated:
                aggregated[url]["total_grams"] += ingredient.quantity_grams
            else:
                aggregated[url] = {
                    "name": ingredient.name,
                    "total_grams": ingredient.quantity_grams
                }

    return aggregated


def format_shopping_list(aggregated: dict[str, dict], unit_weights: dict, selected_recipes: list[Path]) -> str:
    """Format aggregated ingredients as a markdown shopping list."""
    lines = [
        "# Shopping List",
        "",
        "## Recipes",
        ""
    ]

    for recipe in selected_recipes:
        lines.append(f"- {recipe.stem}")

    lines.extend(["", "## Ingredients", ""])

    # Sort by ingredient name
    sorted_items = sorted(aggregated.items(), key=lambda x: x[1]["name"].lower())

    for url, data in sorted_items:
        name = data["name"]
        total_grams = data["total_grams"]

        if url in unit_weights:
            # Convert to quantity
            unit_info = unit_weights[url]
            unit_weight = unit_info["unit_weight_g"]
            unit_name = unit_info["unit_name"]
            quantity = math.ceil(total_grams / unit_weight)
            lines.append(f"- [ ] {quantity}x {unit_name}")
        else:
            # Keep as weight
            if total_grams == int(total_grams):
                lines.append(f"- [ ] {int(total_grams)}g {name}")
            else:
                lines.append(f"- [ ] {total_grams}g {name}")

    return "\n".join(lines)


def main():
    # Parse command line args
    recipes_dir = DEFAULT_RECIPES_DIR
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--recipes-dir" and i < len(sys.argv) - 1:
            recipes_dir = Path(sys.argv[i + 1])

    if not recipes_dir.exists():
        print(f"Error: Recipes directory not found: {recipes_dir}")
        sys.exit(1)

    # Load unit weights config
    unit_weights = load_unit_weights()

    # Get available recipes
    recipe_files = get_recipe_files(recipes_dir)
    if not recipe_files:
        print(f"No recipes found in {recipes_dir}")
        sys.exit(1)

    # Display recipes
    display_recipes(recipe_files)

    # Get user selection
    print("Enter recipe numbers (e.g., 1,3,5 or 1-4 or all):")
    selection = input("> ").strip()

    if not selection:
        print("No selection made.")
        sys.exit(0)

    selected_indices = parse_selection(selection, len(recipe_files))
    if not selected_indices:
        print("No valid recipes selected.")
        sys.exit(0)

    selected_recipes = [recipe_files[i] for i in selected_indices]

    print(f"\nSelected {len(selected_recipes)} recipe(s):")
    for recipe in selected_recipes:
        print(f"  - {recipe.stem}")

    # Aggregate ingredients
    print("\nAggregating ingredients...")
    aggregated = aggregate_ingredients(selected_recipes)

    if not aggregated:
        print("No ingredients with URLs found.")
        sys.exit(0)

    # Format shopping list
    shopping_list = format_shopping_list(aggregated, unit_weights, selected_recipes)

    # Write to markdown file
    filename = f"{date.today().isoformat()}_Shopping_List.md"
    output_path = Path.cwd() / filename
    output_path.write_text(shopping_list, encoding='utf-8')
    print(f"\nShopping list saved to: {output_path}")


if __name__ == "__main__":
    main()
