from flask import Flask, Blueprint, jsonify

import json
import requests
import xmltodict

app = Blueprint('bus_info', __name__)

route = "N"
destination = "5205"

def get_bus_data(route, destination):

    route_dict_url = "http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni"
    route_dict_response = requests.get(route_dict_url)
    route_dict_data = json.loads(json.dumps(xmltodict.parse(route_dict_response.content)))
    route_dict = {}

    for entry in route_dict_data["body"]["route"]:
        route_dict[entry["@tag"]] = entry["@title"]

    route_url = "http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r={}".format(route)
    route_response = requests.get(route_url)
    route_data = json.loads(json.dumps(xmltodict.parse(route_response.content)))

    try:
        stops_dict = {}
        for entry in route_data["body"]["route"]["stop"]:
            stops_dict[entry["@tag"]] = {"stopId": int(entry["@stopId"]), "lat": float(entry["@lat"]), "lon": float(entry["@lon"]), "title": entry["@title"]}
    except:
        return "You must enter a valid route"

    stop_url = "http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=sf-muni&r={}&s={}&useShortTitles=true".format(route, destination)
    stop_response = requests.get(stop_url)
    stop_data = json.loads(json.dumps(xmltodict.parse(stop_response.content))) 
    try:
        # for some reason, the XML sometimes switches the location of the list in the structure
        next_bus = stop_data["body"]["predictions"]["direction"]["prediction"][0]
    except:
        next_bus = stop_data["body"]["predictions"]["direction"][0]["prediction"]
    route_estimate = 0

    if int(next_bus["@seconds"]) > 60:
        route_estimate = "{} minutes".format(next_bus["@minutes"])
    else:
        route_estimate = "{} seconds".format(next_bus["@seconds"])

    muni_data = {"sf-muni": {"routes": route_dict, "stops": stops_dict, "eta": route_estimate}, "route": route, "destination": stops_dict[destination]["title"]}

    return muni_data

@app.route('/')
def get_bus_info():
    
    muni = get_bus_data(route, destination)
    public_transit_data = {"muni": muni}
    try:
        return jsonify(**public_transit_data)
#        return get_bart_data()
    except Exception as error:
        return error
