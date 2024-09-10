# main.py

from scrapers.tastyoven_scraper import TastyOvenScraper
from utils.data_utils import save_to_csv, save_to_json

def main():
    scrapers = [
        TastyOvenScraper("https://tastyoven.com/quick-and-tasty-recipes-for-busy-families-2/"),
        # 在這裡添加其他網站的爬蟲實例
    ]

    for scraper in scrapers:
        print(f"正在爬取 {scraper.__class__.__name__}")
        recipes = scraper.scrape_all_recipes()
        
        # 打印結果
        for index, recipe in enumerate(recipes, 1):
            print(f"\n--- Recipe {index} ---")
            print(f"Name: {recipe['recipe_name']}")
            print(f"URL: {recipe['url']}")
            print("Ingredients:")
            for ingredient in recipe['ingredients']:
                print(f"  - {ingredient}")
            print("-" * 30)

        print(f"\nTotal {len(recipes)} recipes")

        # 保存結果
        save_to_csv(recipes, f'{scraper.__class__.__name__}_recipes.csv', ['recipe_name', 'ingredients', 'url'])
        save_to_json(recipes, f'{scraper.__class__.__name__}_recipes.json')

if __name__ == "__main__":
    main()