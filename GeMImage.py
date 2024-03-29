import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

session = requests.Session()

def scrape_image_url(url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    image_span = soup.find('span', attrs={'data-src': True})
    if image_span:
        image_url = image_span['data-src']
        return image_url
    return None

def get_first_three_links(product_name):
    search_url = "https://mkp.gem.gov.in/search?q=" + product_name
    response = session.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    bn_group_elements = soup.find_all('li', {'class': 'bn-group'}, limit=3)
    links = ["https://mkp.gem.gov.in" + group.find('li', {'class': 'bn-link'}).find('a')['href'] for group in bn_group_elements]
    return links

def get_variant_title_link(url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    variant_title_element = soup.find('span', {'class': 'variant-title'})
    link = "https://mkp.gem.gov.in" + variant_title_element.find('a')['href']
    return link

def get_product_name(url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_name_selector = 'h1.like-h3'
    product_name = soup.select_one(product_name_selector).text.strip()
    return product_name

def get_product_price(url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_price_selector = 'span.m-w'
    product_price = soup.select_one(product_price_selector).text.strip()
    return product_price

def get_product_info(link):
    variant_title_link = get_variant_title_link(link)
    product_info = {
        'product_name': get_product_name(variant_title_link),
        'product_price': get_product_price(variant_title_link),
        'product_image': scrape_image_url(variant_title_link),
    }
    return product_info

if __name__ == '__main__':
    product_name = input("Enter the product name: ")
    first_three_links = get_first_three_links(product_name)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_product_info, link) for link in first_three_links]
        for future in futures:
            product_info = future.result()
            print(product_info)
