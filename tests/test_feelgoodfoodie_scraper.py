import test_setup
from scrapers.feelgoodfoodie_scraper import FeelGoodFoodieScraper

def test_get_names(scraper):
    recipes = scraper.get_recipe_names()
    for recipe in recipes:
        print(f"Recipe Title:{recipe['name']}")
        print(f"Recipe URL:{recipe['url']}")
        print("---")
def test_scrape_all_recipes(scraper):
    recipes = scraper.scrape_all_recipes()
    for index, recipe in enumerate(recipes, 1):
        print(f"\n--- Recipe {index} ---")
        print(f"Name: {recipe['recipe_name']}")
        print(f"URL: {recipe['url']}")
        print("Ingredients:")
        for ingredient in recipe['ingredients']:
            print(f"  - {ingredient}")
        print("-" * 30)    
def main():
    scraper = FeelGoodFoodieScraper("https://feelgoodfoodie.net/recipe/")
    test_scrape_all_recipes(scraper)
if __name__ == "__main__":
    main()