# Auto Macro Calculator

Calculate nutritional macros for recipes using Woolworths product data.

## Setup (one-time)

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

1. Create a recipe using the template in `recipes/_template.md`
2. Add Woolworths product URLs for each ingredient
3. Run the calculator:

```bash
python macros.py "recipes/Your Recipe.md"
```

4. Copy the output table into your recipe

## Recipe Format

```markdown
---
servings: 4
---

# Recipe Name

## Ingredients
- 500g Ingredient Name https://www.woolworths.com.au/shop/productdetails/123456/product-name

## Method
1. Step one
2. Step two

## Nutrition
<!-- paste output here -->
```

**Important:** All quantities must be in grams.

## Finding Woolworths URLs

1. Go to [woolworths.com.au](https://www.woolworths.com.au)
2. Search for the product
3. Copy the URL from the product page

## Caching

Nutrition data is cached in `nutrition_cache.json`. Once an ingredient is fetched, it won't need to be scraped again.

To force refresh cached data:
```bash
python macros.py "recipes/Your Recipe.md" --refresh
```
