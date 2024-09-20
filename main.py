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

def scrape_website(scraper,pbar):
    print(f"正在爬取 {scraper.__class__.__name__}")
    recipes = scraper.scrape_all_recipes()
    pbar.update(1)
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
    with tqdm(total=len(scrapers), desc="總體爬取進度", unit="網站") as pbar:
        # 使用 ThreadPoolExecutor 進行並發爬取
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
            # 提交所有爬取任務
            future_to_scraper = {executor.submit(scrape_website, scraper, pbar): scraper for scraper in scrapers}
            
            # 等待所有任務完成並處理結果
            for future in concurrent.futures.as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                try:
                    recipes = future.result()
                    all_recipes.extend(recipes)
                except Exception as e:
                    print(f"{scraper.__class__.__name__} 產生了一個異常: {e}")
        # 保存結果
        print(f"\n共爬取到 {len(all_recipes)} 個食譜")
    save_to_csv(all_recipes, filename=filename,fieldnames=fieldname,mode="w")

if __name__ == "__main__":
    main()