#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined. 
      To access global parameters use conf['global']['parameterName']. For end-user parameters use conf['secret']['parameterName'] 
     
    Refer to the documentation for further details. 
    """ 
    
    import googlemaps
    from datetime import datetime
    
    apiKey = conf['secret']['key']
    proxy = conf['secret']['proxy']
    
    gmaps = None
    if len (proxy) > 0:
        gmaps = googlemaps.Client(key=apiKey, requests_kwargs={'proxies':{"http":proxy,"https":proxy}})
    else:
        gmaps = googlemaps.Client(key=apiKey)
    
    #get the slots from intent
    tmp_origin = ""
    tmp_destination = ""
    for (slot_value, slot) in intentMessage.slots.items():
        if slot_value == "from":
            tmp_origin = slot.first().value.encode("utf8")
        elif slot_value == "to":
            tmp_destination = slot.first().value.encode("utf8")
    
    starttime = datetime.now()
    origin = tmp_origin
    destination = tmp_destination
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
            hermes.publish_end_session(intentMessage.session_id, str)
    except:
        hermes.publish_end_session(intentMessage.session_id, "Keine Ergebnisse")
    


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("burkhardzeiner:checkDistance", subscribe_intent_callback) \
         .start()
