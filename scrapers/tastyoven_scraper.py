# scrapers/tasty_oven_scraper.py
import re
from scrapers.base_scraper import BaseScraper
from tqdm import tqdm
from utils.http_utils import make_request
from utils.data_utils import parse_html, clean_and_validate_ingredient

class TastyOvenScraper(BaseScraper):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.ingredient_keywords = ['cheese', 'sauce', 'dough', 'meat', 'vegetable', 'fruit', 'spice', 'herb', 'oil', 'flour', 'sugar', 'salt']
        self.non_ingredient_keywords = ['Time-saving', 'oven', 'box', 'bag', 'machine', 'air fryer', 'basket', 'recipe', 'brush', 'assemble', 'remove', 'change', 'use']

    def get_recipe_categories(self):
        response_text = make_request(self.base_url)
        if not response_text:
            return []
        
        soup = parse_html(response_text)
        categories = []
        categories_containers = soup.find_all('ul', class_="feast-category-index-list")
        
        for categories_container in categories_containers:
            category_items = categories_container.find_all('li')
            for item in category_items:
                link = item.find('a')
                if link:
                    title_div = link.find('div', class_=["fsci-title"])
                    if title_div:
                        category_name = title_div.text.strip()
                        category_url = link['href']
                        if not category_url.startswith('http'):
                            category_url = self.base_url + category_url
                        categories.append({
                            'name': category_name,
                            'url': category_url
                        })
        
        return categories

    def get_recipe_names(self, category_url):
        recipes = {}
        page = 1

        while True:
            current_url = f"{category_url}page/{page}/" if page > 1 else category_url
            response_text = make_request(current_url)
            if not response_text:
                break

            soup = parse_html(response_text)
            recipe_items = soup.find_all('li', class_="listing-item")
            if not recipe_items:
                break

            new_recipes = 0
            for recipe_item in recipe_items:
                recipe = recipe_item.find('a')
                if recipe:
                    recipe_url = recipe.get('href')
                    if recipe_url and recipe_url not in recipes:
                        recipe_name = recipe.find('div', class_="fsri-title").text.strip()
                        recipes[recipe_url] = {
                            'name': recipe_name,
                            'url': recipe_url
                        }
                        new_recipes += 1

            if new_recipes == 0:
                break

            next_page = soup.find('a', class_="next page-numbers")
            if not next_page:
                break

            page += 1

        return list(recipes.values())

    def get_recipe_detail(self, recipe_url):
        response_text = make_request(recipe_url)
        if not response_text:
            return None

        soup = parse_html(response_text)
        title = soup.find('h1', class_='entry-title')
        title = title.text.strip() if title else "標題未找到"

        ingredients = []
        ingredient_sections = soup.find_all('div',class_='wprm-recipe-ingredient-group') 
        if not ingredient_sections:
            return None 
        for ingredient_section in ingredient_sections:
            ingredient_container = ingredient_section.find('ul',class_="wprm-recipe-ingredients")
            lis = ingredient_container.find_all('li',class_="wprm-recipe-ingredient")
            for li in lis:
                ingredient_amount_item = li.find('span',class_="wprm-recipe-ingredient-amount")
                if ingredient_amount_item:
                    ingredient_amount = ingredient_amount_item.text.strip()
                else:
                    ingredient_amount =""
                ingredient_unit_item = li.find('span',class_="wprm-reicpe-ingredient-unit")
                if ingredient_unit_item:
                    ingredient_unit = ingredient_unit_item.text.strip()
                else:
                    ingredient_unit = ""
                ingredient_name = li.find('span',class_="wprm-recipe-ingredient-name").text.strip()
                ingredient_text = ingredient_amount + ingredient_unit + ingredient_name
                ingredient_text = ingredient_text.strip()
                pass_ingredient = clean_and_validate_ingredient(ingredient_text,self.ingredient_keywords,self.non_ingredient_keywords)
                if pass_ingredient:
                    ingredients.append(pass_ingredient)
        if ingredients:
            return {
            'recipe_name': title,
            'ingredients': ingredients,
            'url': recipe_url
            }

    def scrape_all_recipes(self):
        return super().scrape_all_recipes()