#!/usr/bin/env python

from flask import Flask

server = Flask(__name__)

@server.route('/')
def home():
    return "Welcome. The purpose of this server is to parse hard-to-use XML into JSON that you can use more easily. Head to /bus_info to check out the results."

def init(name, prefix):
    server.register_blueprint(__import__(name).app, url_prefix = prefix)

init("bus_info", "/apps/bus_info")

if __name__ == '__main__':
    server.run(host='0.0.0.0',debug=True)

