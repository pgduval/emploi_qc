import time
import bs4
import pandas as pd
import datetime
import os
import random

from selenium import webdriver

CHROME_PATH = '/home/elmaster/chromedriver folder/2.28/chromedriver'
PATH = '/home/elmaster/project/emploi_qc'


def list_to_csv(data, columns, name, dropvar=False):
    data = pd.DataFrame(data)
    data.columns = columns
    if dropvar:
        data = data.drop(dropvar, 1)
    data.to_csv(os.path.join(PATH, 'output', name), index=False)


def extract_city_specific(driver, city):
    source = bs4.BeautifulSoup(driver.page_source, 'lxml')
    donnees = source.find('table', {'class': 'donnees'})
    all_data = []
    for row in donnees.find_all('tr')[1:]:
        # Extract columns
        col = row.find_all('td')
        n_offre = col[0].text
        appelation = col[1].text
        employeur = col[2].text
        n_poste = col[3].text
        scolarite = col[4].text
        annee_exp = col[5].text
        lieu_travail = col[6].text
        all_data.append([city, n_offre, appelation, employeur,
                         n_poste, scolarite, annee_exp, lieu_travail])
    time.sleep(random.uniform(2, 5))
    return all_data


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-notifications')
driver = webdriver.Chrome(CHROME_PATH, chrome_options=chrome_options)

driver.get('http://placement.emploiquebec.gouv.qc.ca/mbe/ut/rechroffr/erechroffr.asp?CL=french')

# Click offre depuis 1 semaine
driver.find_element_by_id("MB_TYPE_RECH_GEN5").click()
time.sleep(random.uniform(1, 3))
# Click Tout le quebec
driver.find_element_by_id("MB_ST_MOBL2").click()
time.sleep(random.uniform(1, 3))
# Click Recherche
driver.find_element_by_name("BTNRECHR").click()
time.sleep(random.uniform(5, 10))

# Extract Job Summary for all City
source = bs4.BeautifulSoup(driver.page_source, 'lxml')
contenu = source.find('div', {'class': 'contenu'})
donnees = contenu.find_all('table', {'class': 'donnees'})
all_data = []
for donnee in donnees:
    for row in donnee.find_all('tr')[1:]:
        city = row.find_all('td')[0].text
        offre = row.find('a')
        link = offre['href']
        number = [int(s) for s in offre.text.split() if s.isdigit()][0]
        all_data.append([city, number, link])

date = datetime.datetime.now().strftime("%Y-%m-%d")
list_to_csv(data=all_data,
            columns=['ville', 'nombre_offre', 'lien'],
            dropvar='lien',
            name='tout_emplois_{}.csv'.format(date))


# Extract city specific details
all_city = []
for data in all_data:

    city_name = data[0]
    city_link = data[2]

    print("Starting extraction for city {}".format(city_name))

    # Get city specific url
    driver.get(city_link)

    # Extract pages links to follow to next page
    source = bs4.BeautifulSoup(driver.page_source, 'lxml')
    all_pages = source.find('p', {'class': 'boutonsnav'}).findNext('p').find_all('a')

    # Extract information on current city
    city_output = []
    city_output = city_output + extract_city_specific(driver, city_name)
    for page in all_pages[1:]:
        print("Extracting page {}".format(page.text))
        driver.get(page['href'])
        city_output = city_output + extract_city_specific(driver, city_name)
    all_city = all_city + city_output

# Store data after main city loop
date = datetime.datetime.now().strftime("%Y-%m-%d")
list_to_csv(data=all_city,
            columns=['city_name', 'n_offre',
                     'appelation', 'employeur', 'n_poste',
                     'scolarite', 'annee_exp', 'lieu_travail'],
            dropvar=False,
            name='villes_{}.csv'.format(date))

# End
