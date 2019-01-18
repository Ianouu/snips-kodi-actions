#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io

import simplejson
import requests
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """
    unmute
    """

    addr_ = conf['global']['ip']
    port_ =conf['global']['port']
    
    def isMute():
        request = "{\"jsonrpc\": \"2.0\", \"method\": \"Application.GetProperties\", \"params\": {\"properties\": [\"muted\"]}, \"id\": 1}"
        url = "http://" + addr_ + ":" + port_ + "/jsonrpc?request=" + request
        response = requests.get(url)
        json_data = simplejson.loads(response.text)
        muted = json_data['result']['muted']
        return muted

    def unmute():   
        request = "{\"jsonrpc\": \"2.0\", \"method\": \"Application.SetMute\", \"params\": {\"mute\":false}, \"id\": 1}"
        url = "http://" + addr_ + ":" + port_ + "/jsonrpc?request=" + request
        r = requests.get(url)
        json_data = simplejson.loads(r.text)
        if 'error' in json_data:
            print(json_data['error'])
                

    try:           
        if isMute():
            unmute()
        hermes.publish_end_session(intentMessage.session_id, "")
    except requests.exceptions.RequestException:
        hermes.publish_end_session(intentMessage.session_id, "Erreur de connection.")
    except Exception:
        hermes.publish_end_session(intentMessage.session_id, "Erreur de l'application.")



    




if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("Ianou:Unmute", subscribe_intent_callback) \
         .start()