import requests
import bs4
import re

session = requests.Session()
base_url = "https://inspections.vcha.ca" 

def find_daycare(search_text):
    try:
        session.get("https://inspections.vcha.ca/ChildCare/Table?searchText={}".format(search_text))
        session.post("https://inspections.vcha.ca/{}".format("?returnUrl=%2FChildCare%2FTable"))
        url3 = session.get("https://inspections.vcha.ca/ChildCare/Table?searchText={}".format(search_text))
    except: 
        print("Error initiating daycare finder")
    return url3.content


def extract_link(html_content):
    html = bs4.BeautifulSoup(html_content, 'html.parser')
    try:
        href = html.find('tr', {'class': 'hovereffect'})['onclick']
        link = ("{}{}".format(base_url, href.split('\'')[1]))
        return link
    except: 
        print("Error accessing object")


def daycare_details(url):
    response = session.get(url)
    html = bs4.BeautifulSoup(response.content, 'html.parser')
    data = {}
    data['title'] = html.find('h1', {'class':'article-title'}).text
    tr_rows = html.find_all('tr', {'class': 'nozebrastripes'})
    for row in tr_rows:
        if "Outstanding Infractions" in row.find('td', {'class': 'detail-label'}).text:
            data['infractions'] = row.find('td', {'class':'detail-field'}).find('span', {'class': 'display-field'}).text
        if "Outstanding Critical Infractions" in row.find('td', {'class': 'detail-label'}).text:
            data['critical-infractions'] = row.find('td', {'class':'detail-field'}).find('span', {'class': 'display-field'}).text
        if "Capacity" in row.find('td', {'class': 'detail-label'}).text:
            data['capacity'] = row.find('td', {'class':'detail-field'}).find('span', {'class': 'display-field'}).text
    return data


def get_data(daycare_name):
    return(daycare_details(extract_link(find_daycare(daycare_name))))
