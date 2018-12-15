import json
import requests
import bs4
import vch

urls = [
    "http://maps.gov.bc.ca//arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13498059.020913355%2C%22ymin%22%3A6206972.077885551%2C%22xmax%22%3A-13790653.122172846%2C%22ymax%22%3A6414377.976626059%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=10210",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13712870.818394372%2C%22ymin%22%3A6321783.875366569%2C%22xmax%22%3A-13709167.869024117%2C%22ymax%22%3A6325486.824736822%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13709167.869024117%2C%22ymin%22%3A6321783.875366569%2C%22xmax%22%3A-13705464.919653863%2C%22ymax%22%3A6325486.824736822%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13705464.919653863%2C%22ymin%22%3A6321783.875366569%2C%22xmax%22%3A-13701761.970283609%2C%22ymax%22%3A6325486.824736822%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13712870.818394372%2C%22ymin%22%3A6318080.925996315%2C%22xmax%22%3A-13709167.869024117%2C%22ymax%22%3A6321783.875366569%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13709167.869024117%2C%22ymin%22%3A6318080.925996315%2C%22xmax%22%3A-13705464.919653863%2C%22ymax%22%3A6321783.875366569%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100",
    "http://maps.gov.bc.ca/arcgis/rest/services/mcf/ccf/MapServer/1/query?f=json&returnGeometry=true&spatialRel=esriSpatialRelIntersects&geometry=%7B%22xmin%22%3A-13705464.919653863%2C%22ymin%22%3A6318080.925996315%2C%22xmax%22%3A-13701761.970283609%2C%22ymax%22%3A6321783.875366569%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&geometryType=esriGeometryEnvelope&inSR=102100&outFields=*&outSR=102100"
]


def list_daycares(url):
    response = requests.get(url)
    data = json.loads(response.content)
    #print(data)
    daycares = list()
    for daycare in data['features']:
        if daycare['attributes']['VACANCY_SRVC_UNDER36_IND'] == "Y":
            daycare_dict = {}
            daycare_dict['address'] = daycare['attributes']['DESC_FULL_ADDRESS']
            daycare_dict['name'] = daycare['attributes']['OCCUPANT_NAME']
            daycare_dict['last_update'] = daycare['attributes']['VACANCY_LAST_UPDATE_DATE']
            daycare_dict['email'] = daycare['attributes']['CONTACT_EMAIL']
            daycare_dict['phone'] = daycare['attributes']['CONTACT_PHONE']
            daycare_dict['website'] = daycare['attributes']['WEBSITE_URL']
            daycare_dict['latitude'] = daycare['attributes']['LATITUDE']
            daycare_dict['longitude'] = daycare['attributes']['LONGITUDE']
            daycares.append(daycare_dict)
    return daycares


def filter_daycares(daycares, minx, maxx, miny, maxy):
    temp = list()
    for daycare in daycares:
        if minx < daycare['longitude'] and daycare['longitude'] < maxx:
            if miny < daycare['latitude'] and daycare['latitude'] < maxy:
                temp.append(daycare)
    return temp    


def print_daycares(daycares):
    for daycare in daycares:
        #print(daycare)
        #print("\"https://www.google.com/maps/place/{}%2C{}\"".format(daycare['latitude'], daycare['longitude']))
        vch_data = vch.get_data(daycare['name'])
        print("{}, {} {} {} {} {} {}".format(daycare['name'], daycare['address'], daycare['email'], daycare['last_update'], vch_data['infractions'], vch_data['critical-infractions'], vch_data['capacity']))


all_daycares = list()
count = 0
for url in urls:
    all_daycares = all_daycares + list_daycares(url)
    
unique_daycares = {v['address']:v for v in all_daycares}.values()

print_daycares(filter_daycares(unique_daycares, -123.193, -123.10, 49.257, 49.289))
