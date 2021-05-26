#!/usr/bin/env python3

from gtts import gTTS
import os
from flask import Flask, request
from flask_restful import Api, Resource, abort
import requests
import time
import pygame

app = Flask(__name__)
api = Api(app)

user = 'some-user'
passwd = 'some-pass'

http_endpoint = 'https://translate.google.com'
endpoint_timeout = 5
audio_file = os.path.dirname(os.path.realpath(__file__)) + '/tmp/audio.mp3'
static_audio_file = os.path.dirname(os.path.realpath(__file__)) + '/tts-pt-br-static.mp3'
pygame.init()

def talk(audio):
    #playsound(audio)
    #os.system("/usr/bin/mpg123 %s" % audio)
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(1)

    clock = pygame.time.Clock()
    clock.tick(10)

    while pygame.mixer.music.get_busy():
        pygame.event.poll()
        clock.tick(10)
    pygame.mixer.music.unload()
    return {'message': 'ok'}

def checkUser(req):
    try:
        username = req.authorization.username
        password = req.authorization.password
    except Exception as e:
        abort(401, message="Username and Password for Basic Auth is missing! " + str(e))

    if user == username and passwd == password:
        pass
    else:
        abort(401, message="Authentication failed!")

def checkHttpEndpoint(url, timeout=5):
    r = requests.head(url, timeout=timeout)
    if r.status_code != 200:
        raise Exception('Bad HTTP status code: %s' % r.status_code)
    return r.status_code == 200


class TTS(Resource):
    def get(self, lang, alert, zabbixtext):
        checkUser(request)

        try:
            checkHttpEndpoint(http_endpoint, endpoint_timeout)
            AudioDoTexto = gTTS(text=zabbixtext, lang=lang)
            os.remove(audio_file)
            AudioDoTexto.save(audio_file)
            if alert != "null":
                talk(os.path.dirname(os.path.realpath(__file__)) + "/custom-alerts/" + alert)
                
            return talk(audio_file)

        except Exception as e:
            print("Method failed: ", str(e))
            talk(static_audio_file)
            return {'message': 'Method failed: ' + str(e)}


api.add_resource(TTS, '/<string:lang>/<string:alert>/<string:zabbixtext>')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
