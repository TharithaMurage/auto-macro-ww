# Auto Macro Calculator

A Python CLI tool that calculates nutritional macros (Calories, Protein, Carbs, Fat, Fibre) for recipes stored in Obsidian markdown format. It scrapes nutrition data from [Woolworths.com.au](https://www.woolworths.com.au) product pages and caches results locally so each product only needs to be fetched once.

## Prerequisites

- Python 3.10+
- A Chromium browser (installed automatically by Playwright)

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Macro Calculator

Calculate per-serving and total macros for a recipe file:

```bash
python macros.py "recipes/Chicken Curry.md"
```

The tool will:
1. Parse the recipe markdown for servings and ingredient lines
2. Scrape nutrition data from each ingredient's Woolworths URL (or use cached data)
3. Scale each ingredient's per-100g nutrition values to the actual quantity used
4. Sum totals and divide by the number of servings
5. Print a markdown table you can paste into your recipe's `## Nutrition` section

If scraping fails for a product (e.g. bot detection), the tool falls back to interactive manual entry — you'll be prompted to type in the per-100g values. These are also cached.

To force re-fetch all nutrition data (ignoring the cache):

```bash
python macros.py "recipes/Chicken Curry.md" --refresh
```

### Example output

```
Recipe: Chicken Curry
Servings: 4
Ingredients: 6

==================================================
Copy the following into your recipe:
==================================================

| Macro    | Per Serve | Total |
| -------- | --------: | ----: |
| Calories |    385    | 1540  |
| Protein  |     32g   |  128g |
| Carbs    |     28g   |  112g |
| Fat      |     15g   |   60g |
| Fibre    |      5g   |   20g |
```

## Shopping List Generator

Interactively select recipes and generate an aggregated shopping list:

```bash
python shopping.py
```

By default it looks for recipes in the Obsidian vault (`C:\Users\thari\Tharitha_OW\70 Reciepes`). To use a different directory:

```bash
python shopping.py --recipes-dir "recipes"
```

The tool will:
1. List all available recipes (excluding files starting with `_`)
2. Prompt you to select recipes by number (e.g. `1,3,5` or `1-4` or `all`)
3. Aggregate ingredients across all selected recipes, combining duplicates by URL
4. Convert weight-based quantities to purchase units where configured (e.g. onions → count) using `unit_weights.json`
5. Write a markdown shopping list to `YYYY-MM-DD_Shopping_List.md` in the current directory

## Recipe Format

Recipes are markdown files with YAML frontmatter. See `recipes/_template.md` for a starting point.

```markdown
---
servings: 4
---

# Recipe Name

## Ingredients
- 500g Chicken Breast https://www.woolworths.com.au/shop/productdetails/123456/product-name
- 200g Basmati Rice https://www.woolworths.com.au/shop/productdetails/789012/product-name

## Method
1. Step one
2. Step two

## Nutrition
<!-- paste macro calculator output here -->
```

Key rules:
- Every ingredient line must follow the format: `- {grams}g {name} {woolworths_url}`
- All quantities **must be in grams** — the calculator does not handle cups, tablespoons, etc.
- The Woolworths URL must be the last thing on the line (the parser regex requires this)
- The `servings` field in frontmatter controls the per-serving division

## Finding Woolworths URLs

1. Go to [woolworths.com.au](https://www.woolworths.com.au)
2. Search for the product
3. Click through to the product page
4. Copy the URL from the address bar — it will look like `https://www.woolworths.com.au/shop/productdetails/123456/product-name`

## Caching

Nutrition data is cached in `nutrition_cache.json`, keyed by Woolworths URL. Each entry stores per-100g values for energy (kJ), protein, carbs, fat, and fibre. Energy is automatically converted from kJ to kcal (÷ 4.184) during calculation.

Delete a specific entry from the JSON file to re-fetch just that product, or use `--refresh` to re-fetch everything.

## Unit Weights

`unit_weights.json` maps Woolworths URLs to purchase-unit conversions for the shopping list. For example, if onions are sold individually and each weighs ~150g:

```json
{
  "https://www.woolworths.com.au/shop/productdetails/...": {
    "unit_weight_g": 150,
    "unit_name": "Brown Onion"
  }
}
```

The shopping list generator uses this to show `3x Brown Onion` instead of `450g Brown Onion`.
