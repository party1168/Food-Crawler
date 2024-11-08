from abc import ABC,abstractmethod
from tqdm import tqdm
class BaseScraper(ABC):
    def __init__(self,base_url):
        self.base_url = base_url

    #用來獲取食譜類別的抽象方法
    @abstractmethod
    def get_recipe_categories(self):
        pass

    #用來獲取食譜名稱的抽象方法
    @abstractmethod
    def get_recipe_names(self,category_url):
        pass


    #用來獲取食譜內容的抽象方法
    @abstractmethod
    def get_recipe_detail(self,recipe_url):
        pass
    
    #用來獲取所有食譜的抽象方法
    @abstractmethod
    def scrape_all_recipes(self):
        all_recipes = []
        categories = self.get_recipe_categories()
        for category in tqdm(categories,desc="食譜種類進度",unit="category"):
            recipes = self.get_recipe_names(category['url'])
            for recipe in tqdm(recipes,desc="爬取食譜進度",unit="recipes"):
                details = self.get_recipe_detail(recipe['url'])
                if details and details['ingredients']:
                    all_recipes.append(details)
        return all_recipes