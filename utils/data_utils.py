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

def save_to_csv(data, filename, fieldnames):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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