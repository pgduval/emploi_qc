import requests
import bs4
import pandas as pd
import time
import os

PATH = '/home/elmaster/project/emploi_qc'
BASE_URL = 'https://fr.wikipedia.org'


def extract_region(region, page):

    soup = bs4.BeautifulSoup(page.content, 'lxml')
    table = soup.find('table', {'class': 'wikitable'})

    all_data = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')

        nom = cols[0].text
        designation = cols[1].text
        superficie = cols[2].text.replace(",", "").strip()
        population = cols[3].text.replace(u'\xa0', '').strip()
        mrc = cols[4].text
        code_geo = cols[5].text

        all_data.append([region, nom, designation, superficie, population, mrc, code_geo])

    return all_data


headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'}
page = requests.get('https://fr.wikipedia.org/wiki/Liste_des_municipalit%C3%A9s_locales_du_Qu%C3%A9bec', headers=headers)

soup = bs4.BeautifulSoup(page.content, 'lxml')
contenu = soup.find('ol')

all_data = []
for li in contenu.find_all('li')[13:]:
    region_name = li.text.split(" ")[-1].replace("l'", "")
    region_link = li.find('a')['href']

    print('extracting region {}'.format(region_name))

    region_page = requests.get('{}{}'.format(BASE_URL, region_link), headers=headers)

    all_data = all_data + extract_region(region_name, region_page)
    time.sleep(5)

print(all_data)

out_data = pd.DataFrame(all_data)
out_data.columns = ['region', 'nom', 'designation',
                    'superficie', 'population', 'mrc',
                    'code_geo']
out_data.to_csv(os.path.join(PATH, 'output', 'liste_municipalites.csv'), index=False)

# End #
