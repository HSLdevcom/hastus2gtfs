from string import digits
import os

#TODO: Check 'UP'

TRANSLATION = {'00': 'MA-PE', '25': 'MA-TO', '13': 'MA', '14': 'TI', '11': 'KE', '03': 'TO', '04': 'PE', '05': 'LA', '06': 'SU', 'UP': 'UP'}
WEEKDAY_TRANSLATION = {'00': [1,1,1,1,1,0,0], '25': [1,1,1,1,0,0,0], '13': [1,0,0,0,0,0,0], '14': [0,1,0,0,0,0,0], '11': [0,0,1,0,0,0,0], '03': [0,0,0,1,0,0,0], '04': [0,0,0,0,1,0,0], '05': [0,0,0,0,0,1,0], '06': [0,0,0,0,0,0,1], 'UP': [0,0,0,0,0,0,0]}

digit_trans = str.maketrans('a','a',digits)

current_route = ''
calendar = ''
route = ''
trip_id = ''
valid = False
sidx = 1

calendars = []
calendar_objs = {}
routes = []
trips = []
trip_objs = {}
stoptimes = []
any_stops = False

stops = set([])
missing_stops = set([])

for stop in open('gtfs/stops.txt'):
    stops.add(stop.split(',')[0])

headsigns = {}
for route in open('./routes.csv'):
    headsigns[route.split(',')[0]] = route.split(',')[1].strip()

def getCalendar(sched_type, start, end):
    calendar = TRANSLATION[sched_type] + '_' + start + '_' + end
    weekdays = WEEKDAY_TRANSLATION[sched_type]
    if end == '':
        end = '20160619'
    if start == '':
        start = '20150810'
    return {'service_id': calendar, 'monday': weekdays[0], 'tuesday': weekdays[1], 'wednesday': weekdays[2], 'thursday': weekdays[3], 'friday': weekdays[4], 'saturday': weekdays[5], 'sunday': weekdays[6], 'start_date': start, 'end_date': end}

def getTime(time):
    return time[:2] + ':' + time[2:4] + ':' + time[4:]

for f in os.listdir('.'):
    if not f.endswith('.exp'):
        continue
    print(f)
    for line in open(f, encoding='ISO_8859-15'):
        elements = line.strip().split(';')
        if elements[0] == '1':
            pass
        elif elements[0] == '2':
            pass
        elif elements[0] == '3':
            calendar = getCalendar(elements[2], elements[5], elements[6])
            if not calendar['service_id'] in calendars:
                calendars.append(calendar['service_id'])
                calendar_objs[calendar['service_id']] = calendar
            calendar = calendar['service_id']

        elif elements[0] == '4':
            pass
        elif elements[0] == '5':
            if any_stops == False:
                #print ('No stops for ' + trip_id + ' on route ' + route)
                pass
            any_stops = False
            valid = elements[5] == '0'
            if not valid:
                #print('Siirtoajo')
                #print(elements)
                continue
            route = elements[6] + elements[8].translate(digit_trans)
            if route == '':
                print('Empty route' + str(elements))
            if not route in routes:
                routes.append(route)
            trip_id = elements[3]
            if not trip_id in trips:
                trips.append(trip_id)
                direction = str(int(elements[18])-1)
                shape_id = route + "_" + elements[18]
                headsign = headsigns[shape_id] if shape_id in headsigns else "missing!"


                trip_objs[trip_id] = {'route_id': route, 'service_id': calendar, 'trip_id': trip_id, 'direction_id': direction, 'shape_id': shape_id, 'trip_headsign': headsign}
                sidx = 1
            else:
                print('Duplicate trip' + trip_id)
        elif elements[0] == '6':
            if valid:
                if elements[3] == '':
                    #print(elements)
                    continue
                if elements[3] not in stops:
                    missing_stops.add(elements[3])
                any_stops = True
                stop_id = elements[3]
                time = getTime(elements[8])
                timepoint = elements[11] == 'a' and '1' or '0'
                stoptimes.append({'trip_id': trip_id, 'arrival_time': time, 'departure_time': time, 'stop_id': stop_id, 'stop_sequence': sidx,'timepoint': timepoint})
                sidx += 1

import csv

with open('gtfs/calendar.txt', 'w') as csvfile:
    fieldnames = ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date', 'end_date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for calendar in calendar_objs.values():
        writer.writerow(calendar)

with open('gtfs/routes.txt', 'w') as csvfile:
    fieldnames = ['route_id', 'route_short_name', 'route_type', 'agency_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for route in routes:
        route_short_name = ''
        route_type = ''
        if route[0] == '3':
            route_short_name = route[4]
            route_type = '2'
        elif route[0:4] == '1300':
            route_short_name = 'Metro'
            route_type = '1'
        elif route[0:4] == '1019':
            route_short_name = 'Lautta'
            route_type = '4'
        else:
            route_short_name = route[1:].lstrip('0')
            route_type = '3'
        writer.writerow({'route_id': route, 'route_short_name': route_short_name, 'route_type': route_type,'agency_id': 'HSL'})


with open('gtfs/trips.txt', 'w') as csvfile:
    fieldnames = ['route_id', 'service_id', 'trip_id', 'direction_id', 'trip_headsign', 'shape_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for trip in trip_objs.values():
        writer.writerow(trip)

with open('gtfs/stop_times.txt', 'w') as csvfile:
    fieldnames = ['trip_id', 'stop_id', 'arrival_time', 'departure_time', 'stop_sequence', 'timepoint']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for stoptime in stoptimes:
        writer.writerow(stoptime)

with open('gtfs/missing_stops.txt', 'w') as csvfile:
    fieldnames = ['stop_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for stop in missing_stops:
        writer.writerow({'stop_id': stop})
