import requests
import json
from sys import argv
from difflib import SequenceMatcher

DIRECTIONS = {
    "south" : 1,
    "east"  : 2,
    "west"  : 3,
    "north" : 4
}
payload = {'format':'json'}
get_routes_url = 'http://svc.metrotransit.org/NexTrip/Routes'
get_stops_url = 'http://svc.metrotransit.org/NexTrip/Stops/{ROUTE}/{DIRECTION}'

#Check for exactly 3 arguments after script name on the command line
if len(argv) != 4:
    print('Expecting 3 arguments in order "BUS ROUTE" "BUS STOP NAME" "DIRECTION"')
    quit()
else:
    script, req_route, req_stop, req_direction = argv

#Check if valid direction
if req_direction.lower() not in DIRECTIONS:
    print('\'{asdf}\' is not a valid direction. Please enter as "north", "south", "east", or "west".'.format(asdf=direction))
    quit()

#Needs to be an existing route
routes = requests.get(get_routes_url, params=payload).json()

#for route in routes:
#    if SequenceMatcher(None, req_route, route['Description']).ratio() > .75:
#        print(route)

routeID = (route['Route'] for route in routes if req_route in route['Description']).__next__()
print(routeID)