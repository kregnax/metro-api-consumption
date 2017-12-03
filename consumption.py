'''
This script takes 3 arguments (Bus Route, Bus Stop Name, and Direction) and returns
the time in minutes until the next departure.
'''

from sys import argv
from time import time

import requests

#API URLs and payload info
get_routes_url = 'http://svc.metrotransit.org/NexTrip/Routes'
get_directions_url = 'http://svc.metrotransit.org/NexTrip/Directions/{route}'
get_stops_url = 'http://svc.metrotransit.org/NexTrip/Stops/{route}/{direction}'
get_departures_url = 'http://svc.metrotransit.org/NexTrip/{route}/{direction}/{stop}'
payload = {'format':'json'}


def handle_status_code(status_code):
    '''Check for successfull request from API, quit if anything other than 200'''
    if status_code != 200:
        print('Expected 200, got {code}'.format(status_code))
        quit()

#Check for exactly 3 arguments after script name on the command line
if len(argv) != 4:
    print('Expecting 3 arguments in order "BUS ROUTE" "BUS STOP NAME" "DIRECTION"')
    quit()
else:
    script, req_route, req_stop, req_direction = argv

routes_response = requests.get(get_routes_url, params=payload)
handle_status_code(routes_response.status_code)
routes_json = routes_response.json()

#Use a generator converted to a list to find a match for the requested route
routes = list((route for route in routes_json if req_route.lower() in route['Description'].lower()))

#If more than 1 potential route matches, display routes so user can rerun script with desired route
if len(routes) > 1:
    print('More than one possible route found, please rerun script using the desired route:')
    print('\n'.join(route['Description'] for route in routes))
    quit()

#No valid routes found
elif len(routes) <= 0:
    print('Route \'{}\' not found or not in service today.'.format(req_route))
    quit()

#If we reach this point, one route has been identified
route = routes[0]['Route']


directions_response = requests.get(get_directions_url.format(route=route), params=payload)
handle_status_code(directions_response.status_code)
directions_json = directions_response.json()

#Now we validate that the route goes in the requested direction
try:
    direction = (direction['Value'] for direction in directions_json if req_direction.lower() == direction['Text'][:-5].lower()).__next__()
except StopIteration as stopiter:
    print('The direction you entered is not valid for the given route.')
    print('For this route, enter either {x} or {y}.'.format(x=directions_json[0]['Text'][:-5].lower(), y=directions_json[1]['Text'][:-5].lower()))
    quit()


stops_response = requests.get(get_stops_url.format(route=route, direction=direction), params=payload)
handle_status_code(stops_response.status_code)
stops_json = stops_response.json()

#Now we validate that the requested bus stop exists on the route, again using a generator
try:
    stop = (stop['Value'] for stop in stops_json if req_stop.lower() == stop['Text'].lower()).__next__()
except StopIteration as stopiter:
    print('No bus stop named \'{stop}\' found on your entered route.'.format(stop=req_stop))
    print('The bus stops on your entered route are as follows:')
    print('\n'.join(stop['Text'] for stop in stops_json))
    quit()


departures_response = requests.get(get_departures_url.format(route=route, direction=direction, stop=stop), params=payload)
handle_status_code(departures_response.status_code)

#If we reach this point, we have a valid route, stop, and direction
departures_json = departures_response.json()

#In case there are no more departures today
if len(departures_json) < 1:
    print('No more departures from {stop} scheduled for today.'.format(stop=req_stop))
    quit()

#Finally, calculate the difference between now and the given departure time
departure = int(departures_json[0]['DepartureTime'][6:16])
now = int(time())
minutes_to_departure = (departure-now)//60
print('{minutes} minutes'.format(minutes=minutes_to_departure))
