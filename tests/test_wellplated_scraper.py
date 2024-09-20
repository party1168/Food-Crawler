import test_setup
from scrapers.wellplated_scraper import WellPlatedScraper

def test_get_categories(scraper):
    recipes_categories= scraper.get_recipe_categories()
    print(recipes_categories)
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

def test_scrape_all_recipes(scraper):
    pass

def main():
    scraper = WellPlatedScraper('https://www.wellplated.com/recipe-index/')
    #test_get_categories(scraper)
    test_get_names(scraper)
if __name__ == "__main__":
    main()