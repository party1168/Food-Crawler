import requests
from bs4 import BeautifulSoup

url = "https://tastyoven.com/air-fryer/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
print(soup.title)