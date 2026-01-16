import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth


@dataclass
class NutritionInfo:
    calories: float  # kcal per 100g
    protein: float   # g per 100g
    carbs: float     # g per 100g
    fat: float       # g per 100g
    fibre: float     # g per 100g
    source_url: str
    product_name: str


CACHE_FILE = Path(__file__).parent / "nutrition_cache.json"


def load_cache() -> dict:
    """Load the nutrition cache from disk."""
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    return {}


def save_cache(cache: dict) -> None:
    """Save the nutrition cache to disk."""
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding='utf-8')


def parse_nutrition_value(value: str) -> float:
    """Parse a nutrition value string to float."""
    if not value or value == "-":
        return 0.0
    # Remove units and extract number
    match = re.search(r'([\d.]+)', str(value))
    return float(match.group(1)) if match else 0.0


def scrape_nutrition_playwright(url: str) -> Optional[NutritionInfo]:
    """
    Scrape nutrition info from Woolworths using Playwright with stealth mode.
    """
    print("  Opening browser...")

    stealth = Stealth()

    with stealth.use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Sydney',
        )
        page = context.new_page()

        try:
            # Navigate to the product page
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for JS to render
            page.wait_for_timeout(3000)

            # Get page content
            content = page.content()

            # Get product name
            h1 = page.query_selector('h1')
            product_name = h1.inner_text() if h1 else "Unknown Product"

            # Extract nutrition data from embedded JSON
            nutrition_data = extract_nutrition_json(content)

            if nutrition_data:
                return NutritionInfo(
                    calories=nutrition_data.get('energy', 0),
                    protein=nutrition_data.get('protein', 0),
                    carbs=nutrition_data.get('carbs', 0),
                    fat=nutrition_data.get('fat', 0),
                    fibre=nutrition_data.get('fibre', 0),
                    source_url=url,
                    product_name=product_name.strip()
                )

            return None

        except Exception as e:
            print(f"  Error: {e}")
            return None
        finally:
            browser.close()


def extract_nutrition_json(content: str) -> Optional[dict]:
    """
    Extract nutrition values from embedded JSON in the page.
    Woolworths embeds nutrition data as a NutritionalInformation array.
    """
    # Look for the NutritionalInformation JSON array
    match = re.search(r'"NutritionalInformation"\s*:\s*(\[.*?\])', content)
    if not match:
        return None

    try:
        nutrition_array = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    nutrition = {}

    for item in nutrition_array:
        name = item.get("Name", "").lower()
        values = item.get("Values", {})
        # Get the per 100g value
        value_str = values.get("Quantity Per 100g / 100mL", "-")

        if "energy" in name:
            # Convert kJ to kcal (1 kcal = 4.184 kJ)
            kj = parse_nutrition_value(value_str)
            nutrition['energy'] = round(kj / 4.184, 1)
        elif "protein" in name:
            nutrition['protein'] = parse_nutrition_value(value_str)
        elif "carbohydrate" in name and "sugars" not in name:
            nutrition['carbs'] = parse_nutrition_value(value_str)
        elif "fat" in name and "total" in name:
            nutrition['fat'] = parse_nutrition_value(value_str)
        elif "fat" in name and "saturated" not in name and "trans" not in name:
            # Fallback for fat if "Fat, Total" not found
            if 'fat' not in nutrition:
                nutrition['fat'] = parse_nutrition_value(value_str)
        elif "fibre" in name or "fiber" in name:
            nutrition['fibre'] = parse_nutrition_value(value_str)

    # Fill in missing values with 0
    nutrition.setdefault('energy', 0)
    nutrition.setdefault('protein', 0)
    nutrition.setdefault('carbs', 0)
    nutrition.setdefault('fat', 0)
    nutrition.setdefault('fibre', 0)

    return nutrition


def get_nutrition(url: str, force_refresh: bool = False) -> Optional[NutritionInfo]:
    """
    Get nutrition info for a Woolworths product URL.
    Uses cache if available, otherwise scrapes with Playwright.
    """
    cache = load_cache()

    if not force_refresh and url in cache:
        data = cache[url]
        return NutritionInfo(**data)

    print(f"Fetching nutrition data for: {url}")
    nutrition = scrape_nutrition_playwright(url)

    if nutrition:
        cache[url] = asdict(nutrition)
        save_cache(cache)
        print(f"  Found: {nutrition.product_name}")
        print(f"  Calories: {nutrition.calories} kcal, Protein: {nutrition.protein}g, Carbs: {nutrition.carbs}g, Fat: {nutrition.fat}g, Fibre: {nutrition.fibre}g")
        return nutrition

    return None


def manual_entry(url: str, name: str) -> NutritionInfo:
    """Prompt user to manually enter nutrition info."""
    print(f"\nCould not automatically fetch nutrition for: {name}")
    print(f"URL: {url}")
    print("\nPlease enter nutrition values per 100g:")

    calories = float(input("  Calories (kcal): ") or 0)
    protein = float(input("  Protein (g): ") or 0)
    carbs = float(input("  Carbs (g): ") or 0)
    fat = float(input("  Fat (g): ") or 0)
    fibre = float(input("  Fibre (g): ") or 0)

    nutrition = NutritionInfo(
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        fibre=fibre,
        source_url=url,
        product_name=name
    )

    # Cache the manually entered data
    cache = load_cache()
    cache[url] = asdict(nutrition)
    save_cache(cache)

    return nutrition
