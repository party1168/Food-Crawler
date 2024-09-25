from scrapers.base_scraper import BaseScraper
import re
from utils.http_utils import make_request
from utils.data_utils import parse_html, extract_data_from_soup, clean_and_validate_ingredient

class AfricanBitesScraper(BaseScraper):

    def __init__(self, base_url):
        super().__init__(base_url)
        self.ingredient_keywords = ['cheese', 'sauce', 'dough', 'meat', 'vegetable', 'fruit', 'spice', 'herb', 'oil', 'flour', 'sugar', 'salt']
        self.non_ingredient_keywords = ['Add', 'Time-saving', 'oven', 'box', 'bag', 'machine', 'air fryer', 'basket', 'recipe', 'brush', 'assemble', 'remove', 'change', 'use']

    def get_recipe_categories(self):
        response_text = make_request(self.base_url)

        if not response_text:
            return []
        
        soup = parse_html(response_text)
        categories = []
        categories_container = soup.find('div',class_="archive-internal")
        category_items = categories_container.find_all('div',class_="entry")
        for category_item in category_items:
            link = category_item.find('a')
            if link:
                category_name = link.find('h2',class_="entry-title").text.strip()
                category_url = link.get("href")
                if not category_url.startswith('http'):
                    category_url = self.base_url + category_url
                categories.append({
                    'name':category_name,
                    'url':category_url
                })
        if not categories:
            print("Categories not found")
        return categories
    def get_recipe_names(self, category_url):
        page = 1
        recipes = {}
        while True:
            current_url = f"{category_url}page/{page}/" if page > 1 else category_url
            response_text = make_request(current_url)
            if not response_text:
                break
            soup = parse_html(response_text)
            recipes_container = soup.find('main',class_="content")
            recipe_items = recipes_container.find_all('article',class_="post")
            new_recipes = 0
            for recipe_item in recipe_items:
                recipe_header = recipe_item.find('header',class_="entry-header")
                recipe_a = recipe_header.find('a',class_="entry-image-link")
                recipe_url = recipe_a.get('href')
                recipe_title = recipe_header.find('h2',class_="entry-title")
                recipe_title_a = recipe_title.find('a',class_="entry-title-link")
                recipe_name = recipe_title_a.text.strip()
                if recipe_url and recipe_url not in recipes:
                    recipes[recipe_url] = {
                        'name': recipe_name,
                        'url':recipe_url
                    }
                    new_recipes+=1
            if new_recipes == 0:
                break
            next_page = soup.find('li',class_="pagination-next")
            if not next_page:
                break
            page+=1
        return list(recipes.values())

    def get_recipe_detail(self, recipe_url):
        response_text = make_request(recipe_url)
        if not response_text:
            return None
        soup = parse_html(response_text)
        recipe_title = soup.find('h1',class_="entry-title").text.strip().strip("\"")
        ingredients = []
        units = set()
        ingredient_container = soup.find('div',class_='wprm-recipe-ingredient-group')
        if not ingredient_container:
            return None
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
                units.add(ingredient_unit)
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
                'recipe_name':recipe_title,
                'ingredients':ingredients,
                'url':recipe_url,
                'unit':[]
            }

    def scrape_all_recipes(self):
        return super().scrape_all_recipes()