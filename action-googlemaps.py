#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
import io
import googlemaps
from datetime import datetime
import json

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

NO_RESULT_TXT = "Kein Ergebnis gefunden"

class GoogleMapsAPI:
    def __init__(self, key, home, work, proxy):
        self.apiKey = key
        self.home = home
        self.work = work
        self.proxy = proxy

    def getTimeToWork (self, starttime = datetime.now()):
        if len (proxy) > 0:
            gmaps = googlemaps.Client(key=self.apiKey, requests_kwargs={'proxies':{"http":proxy,"https":proxy}})
        else:
            gmaps = googlemaps.Client(key=self.apiKey)

        origin = self.home
        destination = self.work
        travel_mode = "driving"

        try:
            directions_result = gmaps.directions(origin,
                                                destination,
                                                mode=travel_mode,
                                                traffic_model='best_guess',
                                                alternatives='false',
                                                language="DE",
                                                departure_time=starttime)

            if len (directions_result) > 0:
                str = "%s über %s. " % (directions_result[0]["legs"][0]["duration_in_traffic"]["text"],
                        directions_result[0]["summary"])
                if len (directions_result[0]["warnings"]) > 0:
                    str += directions_result[0]["warnings"]
                else:
                    str += "Es liegen keine Warnungen vor."
                return str
        except:
            return NO_RESULT_TXT
        return NO_RESULT_TXT

    def getDistance (self, origin, destination):
        if len (proxy) > 0:
            gmaps = googlemaps.Client(key=self.apiKey, requests_kwargs={'proxies':{"http":proxy,"https":proxy}})
        else:
            gmaps = googlemaps.Client(key=self.apiKey)

        starttime = datetime.now()
        travel_mode = "driving"

        try:
            directions_result = gmaps.directions(origin,
                                                destination,
                                                mode=travel_mode,
                                                traffic_model='best_guess',
                                                alternatives='false',
                                                language="DE",
                                                departure_time=starttime)

            if len (directions_result) > 0:
                str = "%s über %s. " % (directions_result[0]["legs"][0]["distance"]["text"],
                    directions_result[0]["summary"])
                str = str + "Die Fahrt dauert %s." % directions_result[0]["legs"][0]["duration_in_traffic"]["text"]
                return str
        except:
            return NO_RESULT_TXT
        return NO_RESULT_TXT

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {
            section: {option_name: option for option_name, option in self.items(section)} for section in self.sections()
        }


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.read_file(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error):
        return dict()


def timetowork_callback(hermes, intent_message):
    text_to_speech = googleMapsAccess.getTimeToWork()
    hermes.publish_end_session(intent_message.session_id, text_to_speech)

def distance_callback(hermes, intent_message):
    #get the slots from intent
    for (slot_value, slot) in intent_message.slots.items():
        if slot_value == "from":
            tmp_origin = slot.first().value.encode("utf8")
        elif slot_value == "to":
            tmp_destination = slot.first().value.encode("utf8")

    text_to_speech = googleMapsAccess.getDistance(tmp_origin, tmp_destination)
    hermes.publish_end_session(intent_message.session_id, text_to_speech)

if __name__ == "__main__":
    conf = read_configuration_file(CONFIG_INI)
    googleMapsAccess = GoogleMapsAPI(conf['secret']['key'], conf['secret']['home'], conf['secret']['work'], conf['secret']['proxy'])
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("burkhardzeiner:checkToWorkTraffic", timetowork_callback)
        h.subscribe_intent("burkhardzeiner:checkDistance", distance_callback)
        h.start()
