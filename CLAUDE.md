# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python CLI tool that calculates nutritional macros (Calories, Protein, Carbs, Fat, Fibre) for recipes stored in Obsidian markdown format. Uses Woolworths.com.au product URLs for nutrition data.

## Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Chromium browser for Playwright (one-time)
playwright install chromium
```

## Commands

```bash
# Calculate macros for a recipe
python macros.py <recipe.md>

# Force refresh cached nutrition data
python macros.py <recipe.md> --refresh
```

## Architecture

- `macros.py` - CLI entry point
- `parser.py` - Extracts frontmatter (servings) and ingredient lines from markdown
- `scraper.py` - Fetches nutrition data from Woolworths using Playwright with stealth mode
- `calculator.py` - Computes per-serving macros from ingredient quantities
- `nutrition_cache.json` - Cached nutrition data keyed by Woolworths URL

## Recipe Format

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

- Scraper uses Playwright with stealth mode to avoid Woolworths bot detection
- Falls back to manual entry if scraping fails
- Nutrition values are per 100g in the cache
- All quantities must be in grams
- Energy is converted from kJ to kcal automatically
