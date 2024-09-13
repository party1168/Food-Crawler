from scrapers.base_scraper import BaseScraper
from tqdm import tqdm
from utils.data_utils import parse_html,clean_and_validate_ingredient
from utils.http_utils import make_request

class FeelGoodFoodieScraper(BaseScraper):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.ingredient_keywords = ['cheese', 'sauce', 'dough', 'meat', 'vegetable', 'fruit', 'spice', 'herb', 'oil', 'flour', 'sugar', 'salt']
        self.non_ingredient_keywords = ['Add', 'Time-saving', 'oven', 'box', 'bag', 'machine', 'air fryer', 'basket', 'recipe', 'brush', 'assemble', 'remove', 'change', 'use']
    #This Scraper don't need this function
    #This Website don't need to search by category
    def get_recipe_categories(self):
        return super().get_recipe_categories()
    def get_recipe_names(self):
        page = 1
        recipes = {}
        while page<111:
            current_url = f"{self.base_url}?_paged={page}" if page>1 else self.base_url
            response_text = make_request(current_url)
            if not response_text:
                return []
            soup = parse_html(response_text)
            recipes_container = soup.find('div',class_="archive-post-listing")
            recipe_items = recipes_container.find_all("article",class_="post-summary")
            new_recipes = 0
            for recipe_item in recipe_items:
                recipe_title = recipe_item.find('h2',class_="post-summary__title")
                recipe_href = recipe_title.find('a')
                recipe_url = recipe_href.get('href')
                recipe_name = recipe_href.text.strip()
                if recipe_url and recipe_name and recipe_url not in recipes:
                    recipes[recipe_url] = {
                        'name': recipe_name,
                        'url':recipe_url
                    }
                    new_recipes+=1
            if new_recipes == 0:
                break
            page+=1
        return list(recipes.values())

    def get_recipe_detail(self, recipe_url):
        response_text = make_request(recipe_url)
        if not response_text:
            return None
        soup = parse_html(response_text)
        recipe_title = soup.find('h1',class_="entry-title").text.strip()
        ingredients = []
        ingredients_container = soup.find('div',class_="wprm-recipe-ingredients-container")
        ingredients_items_containers = ingredients_container.find_all('ul',class_="wprm-recipe-ingredients")
        for ingredients_items_container in ingredients_items_containers:
            ingredient_items = ingredients_items_container.find_all('li',class_="wprm-recipe-ingredient")
            for ingredient_item in ingredient_items:
                ingredient_amount_item = ingredient_item.find('span',class_="wprm-recipe-ingredient-amount")
                ingredient_amount = ingredient_amount_item.text.strip() if ingredient_amount_item else ""
                ingredient_unit_item = ingredient_item.find('span',class_="wprm-recipe-ingredient-unit")
                ingredient_unit = ingredient_unit_item.text.strip() if ingredient_unit_item else ""
                ingredient_name_item = ingredient_item.find('span',class_="wprm-recipe-ingredient-name")
                ingredient_name_href = ingredient_name_item.find('a')
                ingredient_name = ingredient_name_href.text.strip() if ingredient_name_href else ingredient_item.text.strip()
                ingredient_text = ingredient_amount + ingredient_unit + ingredient_name
                pass_ingredient = clean_and_validate_ingredient(ingredient_text,self.ingredient_keywords,self.non_ingredient_keywords)
                if pass_ingredient:
                    ingredients.append(pass_ingredient)
        if ingredients:
            return {
                'recipe_name': recipe_title,
                'ingredients':ingredients,
                'url':recipe_url
            }
    def scrape_all_recipes(self):
        all_recipes = []
        recipes = self.get_recipe_names()
        for recipe in tqdm(recipes,desc="爬取食譜進度",unit="recipes"):
            details = self.get_recipe_detail(recipe['url'])
            if details and details['ingredients']:
                all_recipes.append(details)
        return all_recipes