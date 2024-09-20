from scrapers.base_scraper import BaseScraper
from utils.data_utils import parse_html,clean_and_validate_ingredient
from utils.http_utils import make_request
from urllib.parse import urlparse,urlunparse

class WellPlatedScraper(BaseScraper):
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

        categorie_container = soup.find('div',class_="block-category-listing__inner")
        category_items = categorie_container.find_all('a',class_="cat")
        for category_item in category_items:
            category_url = category_item.get('href')
            category_name_item = category_item.find('span')
            category_name = category_name_item.text.strip()
            if category_url:
                categories.append({
                    'name':category_name,
                    'url':category_url
                })
        if not categories:
            print("Cateogries Not Found")
        return categories
    
    def get_recipe_names(self, category_url):
        page = 1
        recipes = {}
        def construct_url(base_url, page_num, format_type):
            parsed_url = urlparse(base_url)
            if format_type == 'path':
                path = f"{parsed_url.path.rstrip('/')}/page/{page_num}"
                return urlunparse(parsed_url._replace(path=path))
            elif format_type == 'query':
                query = f"_paged={page_num}"
                return urlunparse(parsed_url._replace(query=query))
        while True:
            url_formats = [
                construct_url(category_url, page, 'path'),
                construct_url(category_url, page, 'query')
            ]

            response_text = None
            for url in url_formats:
                response_text = make_request(url)
                if response_text:
                    break
            if not response_text:
                print("Page Not Found")
                break
                
            
            soup = parse_html(response_text)

            articles = soup.select('header.archive-recent-header ~ article.post-summary')
            for article in articles:
                recipe_item = article.find('h2',class_="post-summary__title")
                if not recipe_item:
                    return []
                recipe_a = recipe_item.find('a')
                recipe_name = recipe_a.text.strip().strip("\"")
                recipe_url = recipe_a.get('href')
                if recipe_url and recipe_url not in recipes:
                    recipes[recipe_url] = {
                        'name':recipe_name,
                        'url':recipe_url
                    }
            next_page = soup.find('li',class_="pagination-next")
            if not next_page:
                break
            page+=1
        return list(recipes.values())
    
    def get_recipe_detail(self, recipe_url):
        return super().get_recipe_detail(recipe_url)
    
    def scrape_all_recipes(self):
        return super().scrape_all_recipes()