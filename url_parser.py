import csv, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():

    driver = webdriver.Chrome()
    driver.get('https://www.tripadvisor.com.sg/Hotels-g294262-Singapore-Hotels.html')

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_numbers = soup.find_all('span', {'class':['pageNum', 'last']})
    page_count = int(list(filter(lambda link: set(link.get('class')) == set(['pageNum', 'last', 'taLnk', '']), page_numbers))[0].text)

    hotels = []
    hotel_id = 0

    for page in range(1, page_count + 1):

        print('Scraping Page', page)

        # navigate to next page
        if page > 1:            
            while True:
                try:
                    page_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="taplc_main_pagination_bar_hotels_pagination_links_optimization_0"]/div/div/div/span[2]')))
                    page_button.click()
                    break
                except:
                    driver.implicitly_wait(1)
            driver.implicitly_wait(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

        # extract data from hotel blocks
        hotel_tags = soup.find_all('div', {'class': 'prw_rup prw_meta_hsx_responsive_listing ui_section listItem'})
        for hotel_tag in hotel_tags:
            hotel_id += 1
            hotel_name = hotel_tag.find('div', {'class': 'listing_title'}).text
            url = 'https://www.tripadvisor.com.sg' + hotel_tag.find('div', {"class": 'listing_title'}).find('a').get('href')
            n_comment = hotel_tag.find('a', {"class": "review_count"}).text
            n_comment = re.sub('[^0-9,]', "", n_comment).replace(',','')
            rank_in_country = hotel_tag.find('div', {"class": "popindex"}).text
            hotel = {
                'id': hotel_id,
                'hotel_name': hotel_name.encode('utf-8'),
                'n_comment': n_comment,
                'rank_in_country': rank_in_country.encode('utf-8'),
                'url': url
            }
            hotels.append(hotel)

    # write extracted hotel data to csv
    if hotels:
        with open('data/hotels.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'hotel_name', 'n_comment', 'rank_in_country', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for hotel in hotels:
                writer.writerow(hotel)


if __name__ == '__main__':
    main()