import requests
from bs4 import BeautifulSoup
import re
import csv
import json

def make_request(url):
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"請求錯誤: {e}")

def get_recipe_categories(url):
    try:
        response_text = make_request(url)
        soup = BeautifulSoup(response_text, 'html.parser')
        
        categories = []
        categories_containers = soup.find_all('ul', class_="feast-category-index-list")
        
        if categories_containers:
            for categories_container in categories_containers:
                category_items = categories_container.find_all('li')
                for item in category_items:
                    link = item.find('a')
                    if link:
                        title_div = link.find('div', class_=["fsci-title"])  # 檢查兩種可能的類名
                        if title_div:
                            category_name = title_div.text.strip()
                            category_url = link['href']

                            if not category_url.startswith('http'):
                                category_url = url + category_url
                            categories.append({
                                'name': category_name,
                                'url': category_url
                            })
        else:
            print("無法找到類別列表容器")
        
        return categories  # 添加返回值
    
    except requests.RequestException as e:
        print(f"請求錯誤: {e}")
        return []
    except Exception as e:
        print(f"發生錯誤: {e}")
        return []
def get_recipe_names(category_name,category_url):

    recipes = {}  # 使用字典而不是列表
    page = 1

    while True:
        if page == 1:
            current_url = category_url
        else:
            current_url = f"{category_url}page/{page}/"
        
        try:
            print(f"正在處理第 {page} 頁")
            response_text = make_request(category_url)
            soup = BeautifulSoup(response_text, 'html.parser')

            recipe_items = soup.find_all('li', class_="listing-item")
            if not recipe_items:
                print("沒有找到更多食譜，結束爬取")
                break
            
            new_recipes = 0
            for recipe_item in recipe_items:
                recipe = recipe_item.find('a')
                if recipe:
                    recipe_url = recipe.get('href')
                    if recipe_url and recipe_url not in recipes:
                        recipe_name = recipe.find('div', class_="fsri-title").text.strip()
                        recipes[recipe_url] = {
                            'name': recipe_name,
                            'url': recipe_url
                        }
                        new_recipes += 1

            print(f"在第 {page} 頁找到 {new_recipes} 個新食譜")
            
            if new_recipes == 0:
                print("沒有新的食譜，結束爬取")
                break

            next_page = soup.find('a', class_="next page-numbers")
            if not next_page:
                print("沒有下一頁，結束爬取")
                break

            page += 1
        except requests.RequestException as e:
            print(f"請求錯誤: {e}")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")
            break

    print(f"總共找到 {len(recipes)} 個不重複的食譜")
    return list(recipes.values())  # 返回字典值的列表
def is_likely_ingredient(text):
    # 定義可能的食材關鍵詞
    ingredient_keywords = ['cheese', 'sauce', 'dough', 'meat', 'vegetable', 'fruit', 'spice', 'herb', 'oil', 'flour', 'sugar', 'salt']
    
    # 定義不太可能是食材的關鍵詞
    non_ingredient_keywords = ['add','Time-saving','oven','box','bag','machine','air fryer', 'basket', 'recipe', 'brush', 'assemble', 'remove', 'change', 'use']
    
    # 檢查文本是否包含食材關鍵詞
    if any(keyword in text.lower() for keyword in ingredient_keywords):
        return True
    
    # 檢查文本是否包含非食材關鍵詞
    if any(keyword in text.lower() for keyword in non_ingredient_keywords):
        return False
    
    # 檢查文本是否以常見的食材開頭（如蔬菜、肉類等）
    if re.match(r'^([\w\s]+\s)?(cheese|sauce|meat|vegetable|fruit|spice|herb)', text.lower()):
        return True
    
    # 如果文本很短（例如少於3個詞），可能是簡單的食材名稱
    if len(text.split()) < 3:
        return True
    
    return False
def get_recipe_detail(recipe_url):
    try:
        response_text = make_request(recipe_url)
        soup = BeautifulSoup(response_text,'html.parser')

        title = soup.find('h1', class_='entry-title')
        title = title.text.strip() if title else "標題未找到"

        ingredients = []

        ingredient_sections = soup.find_all('ul', class_="wp-block-list")
        for ingredient_section in ingredient_sections:
            lis = ingredient_section.find_all('li')
            for li in lis:
                # 先嘗試查找 <strong> 標籤
                ingredient = li.find('strong')
                if ingredient:
                    ingredient_text = ingredient.text.strip()
                else:
                    # 如果沒有 <strong>，則獲取整個 <li> 的文本
                    ingredient_text = li.get_text(strip=True)

                # 分割並只取第一部分（通常是食材名稱）
                ingredient_text = ingredient_text.split(',')[0].split(':')[0].strip()
                
                # 清理文本
                ingredient_text = re.sub(r'http\S+', '', ingredient_text)
                ingredient_text = re.sub(r'\(.*?\)', '', ingredient_text)
                ingredient_text = re.sub(r'\s+', ' ', ingredient_text).strip()
                
                # 過濾條件
                if (len(ingredient_text) < 50 and  # 長度限制
                    not any(word in ingredient_text.lower() for word in ['privacy', 'contact', 'sign up', 'policy']) and  # 關鍵詞過濾
                    not re.search(r'\d+\s*(minutes|hours|mins|hrs)', ingredient_text, re.I) and  # 排除時間相關描述
                    not re.search(r'(always|for|instead of|such as|like)', ingredient_text, re.I)):  # 排除非食材描述
                    if is_likely_ingredient(ingredient_text):
                        ingredients.append(ingredient_text)
    except requests.RequestException as e:
        print(f"請求錯誤: {e}")
    except Exception as e:
        print(f"發生錯誤: {e}")
    return{
        'recipe_name':title,
        'ingredients':ingredients,
        'url':recipe_url
    }
def save_to_csv(data,filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['recipe_name', 'ingredients', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for recipe in data:
            writer.writerow({
                'recipe_name': recipe['recipe_name'],
                'ingredients': ', '.join(recipe['ingredients']),
                'url': recipe['url']
            })
    print(f"已保存到 {filename}")
def save_to_json(data,filename):
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)
    print(f"已保存到 {filename}")
def main():
    base_url = "https://tastyoven.com/quick-and-tasty-recipes-for-busy-families-2/"

    categories = get_recipe_categories(base_url)
    all_recipes = []
    for category in categories:
        print(category['url'])
        recipes = get_recipe_names(category['name'],category['url'])
        for recipe in recipes:
            details = get_recipe_detail(recipe['url'])
            all_recipes.append(details)
        pass
    pass
    for index, recipe in enumerate(all_recipes, 1):
        print(f"\n--- Recipe {index} ---")
        print(f"Name: {recipe['recipe_name']}")
        print(f"URL: {recipe['url']}")
        print("Ingredients:")
        for ingredient in recipe['ingredients']:
            print(f"  - {ingredient}")
        print("-" * 30)

    print(f"\nTotal {len(all_recipes)} recipes")

    save_to_csv(all_recipes,'recipes.csv')
pass

if __name__ == "__main__":
    main()