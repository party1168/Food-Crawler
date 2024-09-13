from bs4 import BeautifulSoup
import csv
import json
import re

def parse_html(html_content, parser='html.parser'):
    return BeautifulSoup(html_content, parser)

def extract_data_from_soup(soup, selector, attribute=None):
    elements = soup.select(selector)
    if attribute:
        return [elem.get(attribute) for elem in elements if elem.has_attr(attribute)]
    return [elem.text.strip() for elem in elements]

def save_to_csv(data, filename, fieldnames,mode ='a'):
    with open(filename,mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()
        for item in data:
            writer.writerow(item)
    print(f"數據已保存到 {filename}")

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)
    print(f"數據已保存到 {filename}")

def get_pagination_urls(base_url, max_pages):
    return [f"{base_url}page/{page}/" if page > 1 else base_url for page in range(1, max_pages + 1)]

def clean_and_validate_ingredient(ingredient_text,
                                  ingredient_keywords,
                                  non_ingredient_keywords,
                                  max_length=50,
                                  excluded_words=['privacy', 'contact', 'sign up', 'policy'],
                                  time_pattern=r'\d+\s*(minutes|hours|mins|hrs)',
                                  exclusion_pattern=r'(just|always|for|instead of|such as|like)'):
        # 清理文本
    ingredient_text = re.sub(r'http\S+', '', ingredient_text)
    ingredient_text = re.sub(r'\(.*?\)', '', ingredient_text)
    ingredient_text = re.sub(r'\s+', ' ', ingredient_text).strip()
    
    # 驗證條件
    if (len(ingredient_text) < max_length and
        not any(word in ingredient_text.lower() for word in excluded_words) and
        not re.search(time_pattern, ingredient_text, re.I) and
        not re.search(exclusion_pattern, ingredient_text, re.I)):
        
        if is_likely_ingredient(ingredient_text, ingredient_keywords, non_ingredient_keywords):
            return ingredient_text
    
    return None

def is_likely_ingredient(text, ingredient_keywords, non_ingredient_keywords):
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ingredient_keywords):
        return True
    if any(keyword in text_lower for keyword in non_ingredient_keywords):
        return False
    if re.match(r'^([\w\s]+\s)?(cheese|sauce|meat|vegetable|fruit|spice|herb)', text_lower):
        return True
    if len(text.split()) < 3:
        return True
    return False