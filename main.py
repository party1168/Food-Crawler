# main.py
import concurrent.futures
from tqdm import tqdm
from scrapers.africanbites_scraper import AfricanBitesScraper
from scrapers.tastyoven_scraper import TastyOvenScraper
from scrapers.thecookingcollective_scraper import TheCookingCollectiveScraper
from scrapers.feelgoodfoodie_scraper import FeelGoodFoodieScraper
from utils.data_utils import save_to_csv, save_to_json

def scrap_website(scraper):
    print(f"正在爬取 {scraper.__class__.__name__}")
    recipes = scraper.scrape_all_recipes()
    return recipes
def main():
    scrapers = [
        TastyOvenScraper("https://tastyoven.com/quick-and-tasty-recipes-for-busy-families-2/"),
        # 在這裡添加其他網站的爬蟲實例
        AfricanBitesScraper('https://www.africanbites.com/category/collections/'),
        TheCookingCollectiveScraper('https://www.thecookingcollective.com.au/recipes/'),
        FeelGoodFoodieScraper('https://feelgoodfoodie.net/recipe/')
    ]
    fieldname = ['recipe_name','ingredients','url']
    filename = 'recipes.csv'
    all_recipes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        future_to_scraper = {executor.submit(scrap_website,scraper): scraper for scraper in scrapers}
        for future in tqdm(concurrent.futures.as_completed(future_to_scraper),total=len(scrapers),desc="Scrape Website Progress",unit="website"):
            scraper = future_to_scraper[future]
            try:
                recipes = future.result()
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
                print(f"\nTotal {len(recipes)} recipes for {scraper.__class__.__name__}")
            except Exception as e:
                print(f"{scraper.__class__.__name__} generated an exception: {e}")
        # 保存結果
    save_to_csv(all_recipes, filename=filename,fieldnames=fieldname,mode="w")

if __name__ == "__main__":
    main()