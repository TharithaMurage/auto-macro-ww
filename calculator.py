from dataclasses import dataclass
from parser import Recipe, Ingredient
from scraper import NutritionInfo


@dataclass
class MacroTotals:
    calories: float
    protein: float
    carbs: float
    fat: float
    fibre: float


def calculate_ingredient_macros(ingredient: Ingredient, nutrition: NutritionInfo) -> MacroTotals:
    """Calculate macros for an ingredient based on its quantity."""
    # Nutrition is per 100g, so scale by quantity
    scale = ingredient.quantity_grams / 100.0

    return MacroTotals(
        calories=round(nutrition.calories * scale, 1),
        protein=round(nutrition.protein * scale, 1),
        carbs=round(nutrition.carbs * scale, 1),
        fat=round(nutrition.fat * scale, 1),
        fibre=round(nutrition.fibre * scale, 1)
    )


def calculate_recipe_macros(
    recipe: Recipe,
    nutrition_data: dict[str, NutritionInfo]
) -> tuple[MacroTotals, MacroTotals]:
    """
    Calculate total and per-serving macros for a recipe.

    Args:
        recipe: The parsed recipe
        nutrition_data: Dict mapping URLs to NutritionInfo

    Returns:
        Tuple of (total_macros, per_serving_macros)
    """
    totals = MacroTotals(calories=0, protein=0, carbs=0, fat=0, fibre=0)

    for ingredient in recipe.ingredients:
        nutrition = nutrition_data.get(ingredient.url)
        if not nutrition:
            print(f"Warning: No nutrition data for {ingredient.name}")
            continue

        macros = calculate_ingredient_macros(ingredient, nutrition)
        totals.calories += macros.calories
        totals.protein += macros.protein
        totals.carbs += macros.carbs
        totals.fat += macros.fat
        totals.fibre += macros.fibre

    # Round totals to avoid floating point errors
    totals.calories = round(totals.calories, 1)
    totals.protein = round(totals.protein, 1)
    totals.carbs = round(totals.carbs, 1)
    totals.fat = round(totals.fat, 1)
    totals.fibre = round(totals.fibre, 1)

    # Calculate per serving
    per_serving = MacroTotals(
        calories=round(totals.calories / recipe.servings, 1),
        protein=round(totals.protein / recipe.servings, 1),
        carbs=round(totals.carbs / recipe.servings, 1),
        fat=round(totals.fat / recipe.servings, 1),
        fibre=round(totals.fibre / recipe.servings, 1)
    )

    return totals, per_serving


def format_macros_table(per_serving: MacroTotals, totals: MacroTotals, servings: int) -> str:
    """Format macros as a markdown table."""
    lines = [
        "## Nutrition",
        "",
        f"*{servings} servings*",
        "",
        "| Nutrient | Per Serving | Total |",
        "|----------|-------------|-------|",
        f"| Calories | {per_serving.calories} kcal | {totals.calories} kcal |",
        f"| Protein  | {per_serving.protein}g | {totals.protein}g |",
        f"| Carbs    | {per_serving.carbs}g | {totals.carbs}g |",
        f"| Fat      | {per_serving.fat}g | {totals.fat}g |",
        f"| Fibre    | {per_serving.fibre}g | {totals.fibre}g |",
    ]
    return "\n".join(lines)
