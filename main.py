import os
import csv
import json
import re
import time
from selenium import webdriver
from bs4 import BeautifulSoup

FILENAME = './data/whoscored.csv'

def get_html(url):
    browser = webdriver.Chrome()
    browser.get(url)

    time.sleep(5)

    html = browser.page_source.encode('utf-8')
    browser.close()
    return html


def get_data(html):
    soup = BeautifulSoup(html, 'lxml')
    scripts = soup.find('script', type='text/javascript', text=re.compile('matchCentreData'))
    data = scripts.text.split('var')[1].split('=')[1].strip().rstrip(';')
    return data


def get_localData(filename):
    with open('whoscored2.html', 'r') as file:
        soup = BeautifulSoup(file, 'lxml')
    scripts = soup.find('script', type='text/javascript', text=re.compile('matchCentreData'))
    data = scripts.text.split('var')[1].split('=')[1].strip().rstrip(';')
    return data


def write_csv(data):
    """Write data in csv file"""
    if not os.path.exists(os.path.dirname(FILENAME)):
        os.makedirs(os.path.dirname(FILENAME))
    with open(FILENAME, 'a', encoding='utf-8') as file:
        order = ['eventId',
                'minute_event',
                'second_event',
                'teamId',
                'playerId',
                'firstName',
                'lastName',
                'x_event',
                'y_event',
                'type_event',
                'outcomeType',
                'isTouch',
                'endX_pass',
                'endY_pass',
                'length_pass',
                'angle_pass',
                'zone_pass',
                'isShot',
                'goalMouthY',
                'goalMouthZ', ]
        writer = csv.DictWriter(file, fieldnames=order)
        writer.writerow(data)


def run_once(f):
    def wrapper(*args, **kwargs):
        wrapper.has_run = os.path.isfile(FILENAME)
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


@run_once
def print_headline():
    """Insert table header"""
    data_headline = {'eventId': 'eventId',
                     'minute_event': 'Min',
                     'second_event': 'Sec',
                     'teamId': 'teamId',
                     'playerId': 'playerId',
                     'firstName': 'firstName',
                     'lastName': 'lastName',
                     'x_event': 'x_event',
                     'y_event': 'y_event',
                     'type_event': 'type_event',
                     'outcomeType': 'outcomeType',
                     'isTouch': 'isTouch',
                     'endX_pass': 'endX_pass',
                     'endY_pass': 'endY_pass',
                     'length_pass': 'length_pass',
                     'angle_pass': 'angle_pass',
                     'zone_pass': 'zone_pass',
                     'isShot': 'isShot',
                     'goalMouthY': 'goalMouthY',
                     'goalMouthZ': 'goalMouthZ', }
    write_csv(data_headline)


def get_dictionary(data):
    with open('temp.txt', 'w') as file:
        print(data, file=file)
    with open('temp.txt', 'r') as file:
        matchCentreData = json.load(file)
    os.remove('temp.txt')
    return matchCentreData


def get_qualifiers(qualifiers):
    length_pass, angle_pass, zone_pass = [None, None, None]
    for item in qualifiers:
        if item.get('type').get('displayName') == 'Length':
            length_pass = item.get('value')
            continue
        if item.get('type').get('displayName') == 'Angle':
            angle_pass = item.get('value')
            continue
        if item.get('type').get('displayName') == 'Zone':
            zone_pass = item.get('value')
            continue
    return length_pass, angle_pass, zone_pass


def get_playerName(nameDictionary, playerId):
    firstName, lastName = [None, None]
    for keys in nameDictionary:
        if int(playerId) == int(keys):
            playerName = nameDictionary[keys].split(' ')
            if len(playerName) == 1:
                firstName = None
                lastName = playerName[0]
            elif len(playerName) >= 3:
                firstName = playerName[0]
                lastName = ' '.join(playerName[1:])
            else:
                firstName = playerName[0]
                lastName = playerName[1]
            break
    return firstName, lastName


def get_events(matchCentreData):
    print_headline()
    for event in matchCentreData['events']:
        eventId = event.get('eventId')
        minute_event = event.get('minute')
        second_event = event.get('second')
        teamId = event.get('teamId')
        playerId = event.get('playerId')
        x_event = event.get('x')
        y_event = event.get('y')
        type_event = event.get('type').get('displayName')
        outcomeType = event.get('outcomeType').get('displayName')
        isTouch = event.get('isTouch')

        endX_pass = event.get('endX')
        endY_pass = event.get('endY')

        length_pass, angle_pass, zone_pass = get_qualifiers(event['qualifiers'])

        isShot = event.get('isShot')
        goalMouthY = event.get('goalMouthY')
        goalMouthZ = event.get('goalMouthZ')

        try:
            firstName, lastName = get_playerName(
                matchCentreData['playerIdNameDictionary'], playerId)
        except TypeError:
            firstName, lastName = [None, None]

        data = {'eventId': eventId,
                'minute_event': minute_event,
                'second_event': second_event,
                'teamId': teamId,
                'playerId': playerId,
                'firstName': firstName,
                'lastName': lastName,
                'x_event': x_event,
                'y_event': y_event,
                'type_event': type_event,
                'outcomeType': outcomeType,
                'isTouch': isTouch,
                'endX_pass': endX_pass,
                'endY_pass': endY_pass,
                'length_pass': length_pass,
                'angle_pass': angle_pass,
                'zone_pass': zone_pass,
                'isShot': isShot,
                'goalMouthY': goalMouthY,
                'goalMouthZ': goalMouthZ, }
        write_csv(data)


def get_playersDoing(data, playerId):
    i = 0
    for item in data['events']:
        if item.get('playerId') == playerId:
            if item.get('type').get('displayName') == 'Goal':
                i += 1
                print(f'---{i}---')
                print(item.get('type').get('displayName'))
                print(item.get('outcomeType').get('displayName'))
                print(item)


def main():
    matchId = '1376045' 
    url = 'https://1xbet.whoscored.com/Matches/{matchId}/Live/'

    # matchCentreData_text = get_data(get_html(url))
    matchCentreData_text = get_localData('whoscored2.html')
    matchCentreData = get_dictionary(matchCentreData_text)

    get_events(matchCentreData)

    # playerId = 73084
    # get_playersDoing(matchCentreData, playerId)


if __name__ == "__main__":
    main()