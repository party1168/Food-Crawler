# main.py
from tqdm import tqdm
from scrapers.africanbites_scraper import AfricanBitesScraper
from scrapers.tastyoven_scraper import TastyOvenScraper
from scrapers.thecookingcollective_scraper import TheCookingCollectiveScraper
from utils.data_utils import save_to_csv, save_to_json

def main():
    scrapers = [
        TastyOvenScraper("https://tastyoven.com/quick-and-tasty-recipes-for-busy-families-2/"),
        # 在這裡添加其他網站的爬蟲實例
        AfricanBitesScraper('https://www.africanbites.com/category/collections/'),
        TheCookingCollectiveScraper('https://www.thecookingcollective.com.au/recipes/')
    ]
    fieldname = ['recipe_name','ingredients','url']
    filename = 'recipes.csv'
    all_recipes = []
    for scraper in tqdm(scrapers,desc="爬取網站進度",unit="scraper"):
        print(f"正在爬取 {scraper.__class__.__name__}")
        recipes = scraper.scrape_all_recipes()
        all_recipes.extend(recipes)
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
    save_to_csv(all_recipes, filename=filename,fieldnames=fieldname,mode="w")

if __name__ == "__main__":
    main()