# main.py
import concurrent.futures
from tqdm import tqdm
from scrapers.africanbites_scraper import AfricanBitesScraper
from scrapers.tastyoven_scraper import TastyOvenScraper
from scrapers.thecookingcollective_scraper import TheCookingCollectiveScraper
from scrapers.feelgoodfoodie_scraper import FeelGoodFoodieScraper
from scrapers.bellyfull_scraper import BellyFullScraper
from scrapers.feastingathome_scraper import FeastingAtHomeScraper
from utils.data_utils import save_to_csv, save_to_json
import time

def scrape_website(scraper):
    print(f"正在爬取 {scraper.__class__.__name__}")
    recipes = scraper.scrape_all_recipes()
    return recipes
def main():
    scrapers = [
        TastyOvenScraper("https://tastyoven.com/quick-and-tasty-recipes-for-busy-families-2/"),
        # 在這裡添加其他網站的爬蟲實例
        AfricanBitesScraper('https://www.africanbites.com/category/collections/'),
        TheCookingCollectiveScraper('https://www.thecookingcollective.com.au/recipes/'),
        FeelGoodFoodieScraper('https://feelgoodfoodie.net/recipe/'),
        BellyFullScraper('https://bellyfull.net/recipe-index/'),
        FeastingAtHomeScraper("https://www.feastingathome.com/recipes/"),

    ]
    fieldname = ['recipe_name','ingredients','url','unit']
    filename = 'recipes.csv'
    all_recipes = []
    s_time = time.time()
    # for scraper in scrapers:
    #     try:
    #         recipes = scrape_website(scraper)
    #         all_recipes.extend(recipes)
    #     except Exception as e:
    #         print(f"{scraper.__class__.__name__} 產生了一個異常: {e}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
            future_to_scraper = {executor.submit(scrape_website, scraper): scraper for scraper in scrapers}
            
            for future in tqdm(concurrent.futures.as_completed(future_to_scraper), total=len(scrapers), desc="總體爬取進度",unit="website"):
                scraper = future_to_scraper[future]
                try:
                    recipes = future.result()
                    all_recipes.extend(recipes)
                    print(f"{scraper.__class__.__name__} 完成, 獲取到 {len(recipes)} 個食譜")
                except Exception as e:
                    print(f"{scraper.__class__.__name__} 產生了一個異常: {e}")
        # 保存結果
    e_time = time.time()
    print(f"\n共爬取到 {len(all_recipes)} 個食譜,耗時:{e_time-s_time}")
    save_to_csv(all_recipes, filename=filename,fieldnames=fieldname,mode="w")

if __name__ == "__main__":
    main()