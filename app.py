#!/usr/bin/env python

import logging
import urllib
import urllib2
import json
import operator
from flask import Flask
from flask import jsonify
from flask import request

from spyne import Application, srpc, ServiceBase, Iterable, UnsignedInteger, Unicode, Float
from spyne.protocol.json import JsonDocument
from spyne.protocol.http import HttpRpc
from spyne.server.wsgi import WsgiApplication

class checkcrime(ServiceBase):
    @srpc(Float, Float, Float, _returns=Unicode)
    def checkcrime(lat, lon, radius):
      
        url = "https://api.spotcrime.com/crimes.json?lat={0}&lon={1}&radius={2}&key=.".format(lat, lon, radius)
        response = urllib.urlopen(url)
        datas = json.loads(response.read())
        count = 0
        count_a = 0
        count_b = 0
        count_c = 0
        count_d = 0
        count_e = 0
        count_f = 0
        count_g = 0
        count_h = 0
        sets = datas["crimes"]
        d = {}
        street = {}
        top = {}
        for total_crimes in sets:
            count += 1
            
            if (d.get(total_crimes ["type"]) == None):
                d[total_crimes["type"]] = 1
            else:
                d[total_crimes["type"]] +=1
            
            x = total_crimes ["date"]
            am_pm = x[-2:]
            split = x[-8:]
            shorten = split[:5]
            clock = shorten.replace(":","")
            int_clock = int(clock)

            if split == "12:00 AM":
                count_h += 1
            elif split == "12:00 PM":
                count_d += 1
            elif am_pm == "AM":
                if ((int_clock >= 1201 and int_clock <= 1259) or (int_clock >= 100 and int_clock <= 300)):
                    count_a += 1
                elif (int_clock >= 301 and int_clock <= 600):
                    count_b += 1
                elif (int_clock >= 601 and int_clock <= 901):
                    count_c += 1
                else:
                    count_d += 1
            elif am_pm == "PM":
                if ((int_clock >= 1201 and int_clock <= 1259) or (int_clock >= 100 and int_clock <= 300)):
                    count_e += 1
                elif (int_clock >= 301 and int_clock <= 600):
                    count_f += 1
                elif (int_clock >= 601 and int_clock <= 901):
                    count_g += 1
                else:
                    count_h += 1
            
            y = total_crimes ["address"]
            
            if '&' in y:
                split_address = y.split(" & ")
                if (street.get(split_address[0]) == None) :
                    street[split_address[0]] = 1
                else:
                    street[split_address[0]] += 1
                
                if (street.get(split_address[1]) == None) :
                    street[split_address[1]] = 1
                else:
                    street[split_address[1]] += 1

            elif 'BLOCK BLOCK' in y:
                split_address = y.split(" BLOCK BLOCK ")
                if (street.get(split_address[1]) == None) :
                    street[split_address[1]] = 1
                else:
                    street[split_address[1]] += 1 
            
            elif 'OF' in y:
                split_address = y.split(" OF ")
                if (street.get(split_address[1]) == None) :
                    street[split_address[1]] = 1
                else:
                    street[split_address[1]] += 1
        sorted_streets = sorted(street.items(), key=operator.itemgetter(1))
        
        third = sorted_streets[-3]
        three, extra = third
        second = sorted_streets[-2]
        two, extra = second
        first = sorted_streets[-1]
        one, extra = first

        top = (one, two, three)

        return ({"total_crimes" : count, "the_most_dangerous_streets" : top, "crime_type_count" : json.loads(json.dumps(d)), "event_time_count" : {"12:01am-3am" : count_a, "3:01am-6am" : count_b, "6:01am-9am" : count_c, "9:01am-12noon" : count_d, "12:01pm-3pm" : count_e, "3:01pm-6pm" : count_f, "6:01pm-9pm" : count_g, "9:01pm-12midnight" : count_h}})

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    logging.basicConfig(level=logging.DEBUG)

    application = Application([checkcrime], tns ='spyne.checkcrime',
        in_protocol=HttpRpc(validator='soft'),
        out_protocol=JsonDocument(ignore_wrappers=True)
    )

    wsgi_application = WsgiApplication(application)

    server = make_server('127.0.0.1', 8000, wsgi_application)

    server.serve_forever()