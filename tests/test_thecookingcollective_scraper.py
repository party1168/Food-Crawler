import test_setup
from scrapers.thecookingcollective_scraper import TheCookingCollectiveScraper

def test_get_categories(scraper):
    recipes_categories= scraper.get_recipe_categories()
    for index,recipe in enumerate(recipes_categories,1):
        print(f"name:{recipe['name']}")
        print(f"url:{recipe['url']}")
        print("---")
def test_get_names(scraper):
    recipes_categories = scraper.get_recipe_categories()
    for recieps_category in recipes_categories:
        recipes = scraper.get_recipe_names(recieps_category['url'])
        for recipe in recipes:
            print(f"Recipe Title:{recipe['name']}")
            print(f"Recipe URL:{recipe['url']}")
            print("---")
def test_scraper_all_recipes(scraper):
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
    scraper = TheCookingCollectiveScraper('https://www.thecookingcollective.com.au/recipes/')
    #test_get_categories(scraper)
    #test_get_names(scraper)
    test_scraper_all_recipes(scraper)
if __name__ == "__main__":
    main()