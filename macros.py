#!/usr/bin/env python3
"""
Macro Calculator CLI

Calculate nutritional macros for recipes using Woolworths product data.

Usage:
    python macros.py <recipe.md>
    python macros.py <recipe.md> --refresh  # Force refresh cached data
"""

import sys
from pathlib import Path

from parser import parse_recipe
from scraper import get_nutrition, manual_entry, NutritionInfo
from calculator import calculate_recipe_macros, format_macros_table


def main():
    if len(sys.argv) < 2:
        print("Usage: python macros.py <recipe.md> [--refresh]")
        print("\nCalculate nutritional macros for a recipe.")
        print("\nOptions:")
        print("  --refresh    Force refresh cached nutrition data")
        sys.exit(1)

    recipe_path = sys.argv[1]
    force_refresh = "--refresh" in sys.argv

    if not Path(recipe_path).exists():
        print(f"Error: File not found: {recipe_path}")
        sys.exit(1)

    # Parse the recipe
    try:
        recipe = parse_recipe(recipe_path)
    except ValueError as e:
        print(f"Error parsing recipe: {e}")
        sys.exit(1)

    print(f"Recipe: {recipe.name}")
    print(f"Servings: {recipe.servings}")
    print(f"Ingredients: {len(recipe.ingredients)}")
    print()

    # Fetch nutrition data for each ingredient
    nutrition_data: dict[str, NutritionInfo] = {}

    for ingredient in recipe.ingredients:
        print(f"  {ingredient.quantity_grams}g {ingredient.name}")

        nutrition = get_nutrition(ingredient.url, force_refresh=force_refresh)

        if nutrition is None:
            # Scraping failed, ask for manual entry
            nutrition = manual_entry(ingredient.url, ingredient.name)

        nutrition_data[ingredient.url] = nutrition

    print()

    # Calculate macros
    totals, per_serving = calculate_recipe_macros(recipe, nutrition_data)

    # Output the markdown table
    output = format_macros_table(per_serving, totals, recipe.servings)

    print("=" * 50)
    print("Copy the following into your recipe:")
    print("=" * 50)
    print()
    print(output)
    print()


if __name__ == "__main__":
    main()
