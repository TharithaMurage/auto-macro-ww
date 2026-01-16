import re
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Ingredient:
    quantity_grams: float
    name: str
    url: str


@dataclass
class Recipe:
    name: str
    servings: int
    ingredients: list[Ingredient]


def parse_recipe(filepath: str) -> Recipe:
    """Parse a recipe markdown file and extract servings and ingredients."""
    content = Path(filepath).read_text(encoding='utf-8')

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError("Recipe must have YAML frontmatter with servings")

    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    servings = frontmatter.get('servings', 1)

    # Extract recipe name from first heading
    name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    recipe_name = name_match.group(1) if name_match else "Untitled Recipe"

    # Extract ingredients
    # Format: - 200g Ingredient Name https://www.woolworths.com.au/...
    ingredient_pattern = re.compile(
        r'^-\s*(\d+(?:\.\d+)?)\s*g\s+(.+?)\s+(https?://(?:www\.)?woolworths\.com\.au/\S+)',
        re.MULTILINE
    )

    ingredients = []
    for match in ingredient_pattern.finditer(content):
        quantity = float(match.group(1))
        name = match.group(2).strip()
        url = match.group(3).strip()
        ingredients.append(Ingredient(quantity_grams=quantity, name=name, url=url))

    if not ingredients:
        raise ValueError("No ingredients found. Format: - 200g Ingredient Name https://woolworths.com.au/...")

    return Recipe(name=recipe_name, servings=servings, ingredients=ingredients)
