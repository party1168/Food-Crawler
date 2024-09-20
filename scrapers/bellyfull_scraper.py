from scrapers.base_scraper import BaseScraper
from utils.data_utils import parse_html,clean_and_validate_ingredient
from utils.http_utils import make_request

class BellyFullScraper(BaseScraper):
    def __init__(self,base_url):
        self.base_url = base_url
        self.ingredient_keywords = ['cheese', 'sauce', 'dough', 'meat', 'vegetable', 'fruit', 'spice', 'herb', 'oil', 'flour', 'sugar', 'salt']
        self.non_ingredient_keywords = ['Add', 'Time-saving', 'oven', 'box', 'bag', 'machine', 'air fryer', 'basket', 'recipe', 'brush', 'assemble', 'remove', 'change', 'use']
    def get_recipe_categories(self):
        response_text = make_request(self.base_url)
        if not response_text:
            return []
        soup = parse_html(response_text)
        categories = []
        categorie_containers = soup.find_all('div',class_="section-posts")
        if not categorie_containers:
            return []
        for categorie_container in categorie_containers:
            category_items = categorie_container.find_all('a',class_="box-image")
            if not category_items:
                category_items = categorie_container.find_all('a',class_="circle-image")
            for category_item in category_items:
                category_url = category_item.get('href')
                categories.append({
                    'url':category_url
                })
        if not categories:
            print("categories Not Found")
        return categories
    def get_recipe_names(self, category_url):
        page = 1
        while True:
            current_url = f"{category_url}page/{page}/" if page > 1 else category_url
            response_text = make_request(current_url)
            if not response_text:
                return []
            recipes = {}
            soup = parse_html(response_text)
            article_content = soup.find('div',class_="archive-content")
            recipe_items = article_content.find_all('article')
            for recipe_item in recipe_items:
                recipe_a = recipe_item.find('a')
                recipe_url = recipe_a.get('href')
                recipe_name = recipe_a.find('h2').text.strip()
                if recipe_url and recipe_url not in recipes:
                    recipes[recipe_url] = {
                        'name':recipe_name,
                        'url':recipe_url
                    }
            next_page = soup.find('a',class_="next")
            if not next_page:
                break
            page+=1
        return list(recipes.values())
    def get_recipe_detail(self, recipe_url):
        response_text = make_request(recipe_url)
        if not response_text:
            return None
        soup = parse_html(response_text)
        ingredients = []
        units = set()
        recipe_title = soup.find('h1',class_="entry-title").text.strip().strip("\"")
        try:
            ingredients_container = soup.find('div',class_="wprm-recipe-ingredients-container")
            if not ingredients_container:
                return None
            ingredients_groups = ingredients_container.find_all('div',class_="wprm-recipe-ingredient-group")
            for ingredients_group in ingredients_groups:
                lis = ingredients_group.find_all('li',class_="wprm-recipe-ingredient")
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
        except Exception as e:
            print(recipe_url)
        if ingredients:
            return {
                'recipe_name':recipe_title,
                'ingredients':ingredients,
                'url':recipe_url,
                'unit':list(units)
            }
    def scrape_all_recipes(self):
        return super().scrape_all_recipes()