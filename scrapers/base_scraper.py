from abc import ABC,abstractmethod

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
        pass