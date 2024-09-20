from scrapers.base_scraper import BaseScraper
from tqdm import tqdm
from utils.data_utils import parse_html,clean_and_validate_ingredient
from utils.http_utils import make_request

class FeastingAtHomeScraper(BaseScraper):

    def __init__(self, base_url):
        super().__init__(base_url)
        self.ingredient_keywords = ['cheese', 'sauce', 'dough', 'meat', 'vegetable', 'fruit', 'spice', 'herb', 'oil', 'flour', 'sugar', 'salt']
        self.non_ingredient_keywords = ['Add', 'Time-saving', 'oven', 'box', 'bag', 'machine', 'air fryer', 'basket', 'recipe', 'brush', 'assemble', 'remove', 'change', 'use']

    def get_recipe_categories(self):
        return super().get_recipe_categories()
    
    def get_recipe_names(self):
        page = 1
        recipes = {}
        while True:
            current_url = f"{self.base_url}page/{page}" if page>1 else self.base_url
            response_text = make_request(current_url)
            if not response_text:
                return []
            
            soup = parse_html(response_text)
            new_recipe = 0
            recipes_container = soup.find('div',class_="archive-post-listing")
            recipe_items = recipes_container.find_all('article',class_="post-summary")
            for recipe_item in recipe_items:
                recipe_title = recipe_item.find('h2',class_="post-summary__title")
                recipe_a = recipe_title.find('a')
                recipe_name = recipe_a.text.strip().strip("")
                recipe_url = recipe_a.get('href')
                if recipe_url and recipe_url not in recipes:
                    recipes[recipe_url] = {
                        'name':recipe_name,
                        'url':recipe_url
                    }
                    new_recipe+=1
            if new_recipe == 0:
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
        units = set()
        ingredients = []
        # 提取食譜標題
        recipe_title = soup.find('h1', class_='page-header__title').text.strip().strip("\"") if soup.find('h1', class_='page-header__title') else "未知食譜"
        
        try:
            ingredient_list = soup.find('div',class_="tasty-recipes-ingredients-body")
            if not ingredient_list:
                return None
            for item in ingredient_list.find_all('li', attrs={'data-tr-ingredient-checkbox': True}):         
                amount_span = item.find('span', attrs={'data-amount': True})
                ingredient_amount = amount_span.get('data-amount',"") if amount_span else ""
                # 提取單位
                unit_span = item.find('span', attrs={'data-unit': True})
                ingredient_unit = unit_span.get('data-unit',"") if unit_span else ""
                if ingredient_unit:
                    units.add(ingredient_unit)  # 添加到單位集合
                # 提取食材名稱
                ingredient_name = item.get_text(strip=True)
                ingredient_text = ingredient_amount + ingredient_unit + ingredient_name
                pass_ingredient = clean_and_validate_ingredient(ingredient_text,self.ingredient_keywords,self.non_ingredient_keywords)
                if pass_ingredient:
                    ingredients.append(pass_ingredient)
        except Exception as e:
            print(recipe_url)
        if ingredients:
            return {
                'recipe_name': recipe_title,
                'ingredients': ingredients,
                'url': recipe_url,
                'unit': list(units)  # 將集合轉換為列表
            }
        else:
            return None  # 如果沒有找到食材，返回None
    
    def scrape_all_recipes(self):
        all_recipes = []
        recipes = self.get_recipe_names()
        for recipe in tqdm(recipes,desc=f"{self.__class__.__name__}食譜種類進度",unit="recipes"):
            details = self.get_recipe_detail(recipe['url'])
            if details and details['ingredients']:
                all_recipes.append(details)
        return all_recipes