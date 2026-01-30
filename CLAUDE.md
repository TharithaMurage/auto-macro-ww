# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool that calculates nutritional macros (Calories, Protein, Carbs, Fat, Fibre) for recipes stored in Obsidian markdown format. Uses Woolworths.com.au product URLs for nutrition data.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Commands

```bash
# Calculate macros for a recipe
python macros.py <recipe.md>

# Force refresh cached nutrition data
python macros.py <recipe.md> --refresh

# Generate shopping list (interactive)
python shopping.py
```

## Architecture

**Data flow:** Recipe markdown → `parser.py` → `scraper.py` (fetch/cache) → `calculator.py` → Markdown table output

- `macros.py` - CLI entry point, orchestrates the pipeline
- `parser.py` - Extracts YAML frontmatter (servings) and ingredient lines using regex; defines `Recipe` and `Ingredient` dataclasses
- `scraper.py` - Fetches nutrition from Woolworths using Playwright stealth mode; extracts data from embedded `NutritionalInformation` JSON array in page source (not HTML parsing)
- `calculator.py` - Scales nutrition values from per-100g to actual quantities, sums totals, divides by servings
- `nutrition_cache.json` - Persistent cache keyed by Woolworths URL; stores per-100g values
- `shopping.py` - Interactive shopping list generator; select recipes and aggregate ingredients by URL
- `unit_weights.json` - Config for weight-to-quantity conversions (e.g., onions sold by count not weight)

## Recipe Format

Recipes are stored in `C:\Users\thari\Tharitha_OW\70 Reciepes`. See `_template.md` in that folder.

```markdown
---
servings: 4
---

# Recipe Name

## Ingredients
- 500g Ingredient Name https://www.woolworths.com.au/shop/productdetails/123456/product-slug

## Nutrition
<!-- paste output here -->
```

Ingredient format: `- {grams}g {name} {woolworths_url}`

## Key Constraints

- All quantities must be in grams
- Nutrition values are stored per 100g in the cache
- Energy is auto-converted from kJ to kcal (÷ 4.184)
- Scraper uses Playwright stealth mode to avoid bot detection
- Falls back to interactive manual entry if scraping fails (also cached)
- The regex for ingredients requires the URL to be at the end of the line
