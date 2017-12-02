from sys import argv

import requests

#API URLs and payload info
get_routes_url = 'http://svc.metrotransit.org/NexTrip/Routes'
get_directions_url = 'http://svc.metrotransit.org/NexTrip/Directions/{route}'
get_stops_url = 'http://svc.metrotransit.org/NexTrip/Stops/{route}/{direction}'
get_departures_url = 'http://svc.metrotransit.org/NexTrip/{route}/{direction}/{stop}'
payload = {'format':'json'}

#Check for exactly 3 arguments after script name on the command line
if len(argv) != 4:
    print('Expecting 3 arguments in order "BUS ROUTE" "BUS STOP NAME" "DIRECTION"')
    quit()
else:
    script, req_route, req_stop, req_direction = argv

#Use a generator to list conversion to find a match for the requested route
routes_json = requests.get(get_routes_url, params=payload).json()
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

#If we reach this point, one route has been found for the input
route = routes[0]['Route']

#Now we validate that the route goes in the entered direction
directions_json = requests.get(get_directions_url.format(route=route), params=payload).json()
try:
    direction = (direction['Value'] for direction in directions_json if req_direction.lower() == direction['Text'][:-5].lower()).__next__()
except StopIteration as stopiter:
    print('The direction you entered is not valid for the given route.')
    print('For this route, enter either {x} or {y}.'.format(x=directions_json[0]['Text'][:-5].lower(), y=directions_json[1]['Text'][:-5].lower()))
    quit()

#Now we validate that the entered bus stop exists on the route, again using a generator
stops_json = requests.get(get_stops_url.format(route=route, direction=direction), params=payload).json()
try:
    stop = (stop['Value'] for stop in stops_json if req_stop.lower() == stop['Text'].lower()).__next__()
except StopIteration as stopiter:
    print('No bus stop named \'{stop}\' found on your entered route.'.format(stop=req_stop))
    print('The bus stops on your entered route are as follows:')
    print('\n'.join(stop['Text'] for stop in stops_json))
    quit()

#If we reach this point, we have a valid route, stop, and direction
print(route, stop, direction)
departures_json = requests.get(get_departures_url.format(route=route, direction=direction, stop=stop), params=payload).json()

