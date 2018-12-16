import json
import requests
import bs4
import hashlib
import vch
import pickle
import datetime
from slackclient import SlackClient


slack_token = ''

urls = [
    "http://maps.gov.bc.ca//arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13498059.020913355%2C%22ymin%22%3A6206972.077885551%2C%22xmax%22%3A-13790653.122172846%2C%22ymax%22%3A6414377.976626059%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=10210",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13712870.818394372%2C%22ymin%22%3A6321783.875366569%2C%22xmax%22%3A-13709167.869024117%2C%22ymax%22%3A6325486.824736822%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13709167.869024117%2C%22ymin%22%3A6321783.875366569%2C%22xmax%22%3A-13705464.919653863%2C%22ymax%22%3A6325486.824736822%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13705464.919653863%2C%22ymin%22%3A6321783.875366569%2C%22xmax%22%3A-13701761.970283609%2C%22ymax%22%3A6325486.824736822%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13712870.818394372%2C%22ymin%22%3A6318080.925996315%2C%22xmax%22%3A-13709167.869024117%2C%22ymax%22%3A6321783.875366569%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13709167.869024117%2C%22ymin%22%3A6318080.925996315%2C%22xmax%22%3A-13705464.919653863%2C%22ymax%22%3A6321783.875366569%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13705464.919653863%2C%22ymin%22%3A6318080.925996315%2C%22xmax%22%3A-13701761.970283609%2C%22ymax%22%3A6321783.875366569%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100"
]

def send_slack(content):
    sc = SlackClient(slack_token)
    sc.api_call(
        "chat.postMessage",
        channel="#general",
        text=content,
        as_user=True,
        mrkdwn=True,
        username="DaycareBot"
        )

def create_pickle_file(data):
    pickle_out = open("dict.pickle", "wb")
    pickle.dump(data, pickle_out)
    pickle_out.close()


def check_new_listing(data):
    try:
        pickle_in = open("dict.pickle", "rb")
        old_listings = pickle.load(pickle_in)
        # comparing dics
        if data == old_listings:
            print("No changes")
            return False
        else:
            for key, val in data.items():
                if not old_listings.get(key, False):
                    send_slack(val)
                    print("New daycare found")

            pickle_out = open("dict.pickle", "wb")
            pickle.dump(data, pickle_out)
            pickle_out.close()
            print("{} - New daycares found".format(datetime.datetime.now()))
            return True
    except Exception:
    #except FileNotFoundError as e:
        print("File not found, creating it")
        create_pickle_file(data)
        return True


def list_daycares(url):
    response = requests.get(url)
    data = json.loads(response.content)
    #print(data)
    daycares = {}
    for daycare in data['features']:
        if daycare['attributes']['VACANCY_SRVC_UNDER36_IND'] == "Y":
            m = hashlib.md5()
            m.update(daycare['attributes']['DESC_FULL_ADDRESS'].join(daycare['attributes']['OCCUPANT_NAME']).encode('utf-8'))
            dict_id = str(int(m.hexdigest(), 16))[0:12]
            daycares[dict_id] = {
                'address': daycare['attributes']['DESC_FULL_ADDRESS'],
                'name': daycare['attributes']['OCCUPANT_NAME'],
                'last_update': daycare['attributes']['VACANCY_LAST_UPDATE_DATE'],
                'email': daycare['attributes']['CONTACT_EMAIL'],
                'phone': daycare['attributes']['CONTACT_PHONE'],
                'website': daycare['attributes']['WEBSITE_URL'],
                'latitude': daycare['attributes']['LATITUDE'],
                'longitude': daycare['attributes']['LONGITUDE']
            } 
    return daycares


def filter_daycares(daycares, minx, maxx, miny, maxy):
    temp = {} 
    for key, val in daycares.items():
        if minx < val['longitude'] and val['longitude'] < maxx:
            if miny < val['latitude'] and val['latitude'] < maxy:
                temp[key] = val
    return temp 


def print_daycares(daycare):
        #print(daycare)
        #print("\"https://www.google.com/maps/place/{}%2C{}\"".format(daycare['latitude'], daycare['longitude']))
        vch_data = vch.get_data(daycare['name'])
        send_slack("{}, {} {} {} {} {} {}".format(daycare['name'], daycare['address'], daycare['email'], daycare['last_update'], vch_data['infractions'], vch_data['critical-infractions'], vch_data['capacity']))


all_daycares = {}
count = 0
for url in urls:
    all_daycares.update(list_daycares(url)) 
    
#unique_daycares = {v['address']:v for v in all_daycares}.values()

filtered_daycares = filter_daycares(all_daycares, -123.193, -123.10, 49.257, 49.289)
check_new_listing(filtered_daycares)
