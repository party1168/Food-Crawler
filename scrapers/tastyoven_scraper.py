# scrapers/tasty_oven_scraper.py
import re
from scrapers.base_scraper import BaseScraper
from tqdm import tqdm
from utils.http_utils import make_request
from utils.data_utils import parse_html, extract_data_from_soup, is_likely_ingredient

class TastyOvenScraper(BaseScraper):
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
        ingredient_sections = soup.find_all('ul', class_="wp-block-list")
        for ingredient_section in ingredient_sections:
            lis = ingredient_section.find_all('li')
            for li in lis:
                ingredient = li.find('strong')
                ingredient_text = ingredient.text.strip() if ingredient else li.get_text(strip=True)
                ingredient_text = ingredient_text.split(',')[0].split(':')[0].strip()
                ingredient_text = re.sub(r'http\S+', '', ingredient_text)
                ingredient_text = re.sub(r'\(.*?\)', '', ingredient_text)
                ingredient_text = re.sub(r'\s+', ' ', ingredient_text).strip()
                
                if (len(ingredient_text) < 50 and
                    not any(word in ingredient_text.lower() for word in ['privacy', 'contact', 'sign up', 'policy']) and
                    not re.search(r'\d+\s*(minutes|hours|mins|hrs)', ingredient_text, re.I) and
                    not re.search(r'(just|always|for|instead of|such as|like)', ingredient_text, re.I)):
                    if is_likely_ingredient(ingredient_text, self.ingredient_keywords, self.non_ingredient_keywords):
                        ingredients.append(ingredient_text)

        return {
            'recipe_name': title,
            'ingredients': ingredients,
            'url': recipe_url
        }

    def scrape_all_recipes(self):
        return super().scrape_all_recipes()