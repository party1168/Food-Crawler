from scrapers.base_scraper import BaseScraper
from utils.http_utils import make_request
from utils.data_utils import parse_html,clean_and_validate_ingredient
class TheCookingCollectiveScraper(BaseScraper):
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
        categories_containers = soup.find_all('ul',class_="feast-category-index-list")
        if not categories_containers:
            return []
        for categories_container in categories_containers:
            lis = categories_container.find_all('li')
            if not lis:
                return []
            for li in lis:
                category_url = li.find('a').get('href')
                if not category_url.startswith('http'):
                    category_url = self.base_url + category_url
                category_title = li.find('div',class_="fsci-title")
                category_name = category_title.text.strip()
                categories.append({
                    'name':category_name,
                    'url':category_url
                })
        if not categories:
            print('Categories Not found')
        return categories             
    def get_recipe_names(self, category_url):
        page = 1
        recipes = {}
        while True:
            current_url = f"{category_url}page/{page}/" if page > 1 else category_url
            response_text = make_request(current_url)
            if not response_text:
                return []
            soup = parse_html(response_text)
            new_recipes = 0
            recipe_items = soup.find_all('article',class_="post")
            for recipe_item in recipe_items:
                recipe_title = recipe_item.find('h2',class_="entry-title")
                recipe_href = recipe_title.find('a')
                recipe_url = recipe_href.get('href')
                recipe_name = recipe_href.text.strip()
                if recipe_url and recipe_url not in recipes:
                    recipes[recipe_url] = {
                        'name':recipe_name,
                        'url': recipe_url
                    }
                    new_recipes+=1
            if new_recipes == 0:
                break
            next_page = soup.find('div',class_="pagination-next")
            if not next_page:
                break
            page+=1
        return list(recipes.values())
    def get_recipe_detail(self, recipe_url):
        response_text = make_request(recipe_url)
        if not response_text:
            return None
        soup = parse_html(response_text)
        recipe_title = soup.find("h1",class_="entry-title").text.strip().strip("\"")
        ingredients = []
        units =set()
        ingredients_containers = soup.find('div',class_="wprm-recipe-ingredient-group")
        for ingredients_container in ingredients_containers:
            lis = ingredients_container.find_all('li',class_="wprm-recipe-ingredient")
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
            return{
                'recipe_name':recipe_title,
                'ingredients':ingredients,
                'url':recipe_url,
                'unit':list(units)
            }
        
    def scrape_all_recipes(self):
        return super().scrape_all_recipes()