#!/usr/bin/env python

import json
import requests
import datetime

# https://danepubliczne.imgw.pl/api/data/synop/id/12375
# {"id_stacji":"12375",
# "stacja":"Warszawa",
# "data_pomiaru":"2022-08-24",
# "godzina_pomiaru":"15",
# "temperatura":"29.6",
# "predkosc_wiatru":"4",
# "kierunek_wiatru":"360",
# "wilgotnosc_wzgledna":"49.9",
# "suma_opadu":"0",
# "cisnienie":"1017.9"}

DEBUG = False
#DEBUG = True

CZUJNIKI = {
    # IMGW ID : [ temp+bar+wilg idx, wiatr idx, opad idx ]
    "12375": [23,22,24], # Warszawa; ## opad robiony przez imgw-opad.sh -- ma wartości godzinowe
    "12650": [35,36,37], # Kasprowy Wierch
    "12135": [38,40,0], # Hel
}

for czuj in CZUJNIKI:
    try:
        czUrl = "https://danepubliczne.imgw.pl/api/data/synop/id/" + czuj
        if DEBUG: print(czUrl)
        r = requests.get(czUrl)

        if DEBUG: print("rc=%i" % r.status_code)

        if r.status_code != 200:
            raise Exception("JSON request failed, status code=%i url=%s" % (r.status_code, czUrl))

        j = json.loads(r.text)

        if DEBUG: print(j)

        cisn = 0
        temp = float(j['temperatura'])
        wiatr = float(j['predkosc_wiatru']) # m/s
        wkier = int(j['kierunek_wiatru'])
        wilgp = float(j['wilgotnosc_wzgledna'])
        opad = float(j['suma_opadu'])
        if 'cisnienie' in j:
            if type(j['cisnienie']) is str:
                cisn = float(j['cisnienie'])

        da = datetime.datetime.now()

        if DEBUG: print("[%s] temp=%.2f wiatr=%.2f wkier=%i wilgp=%.2f opad=%.2f cisn=%.2f" % (da,temp,wiatr,wkier,wilgp,opad,cisn))

        idxTemp = CZUJNIKI[czuj][0]
        if idxTemp > 0:
            u = 'http://127.0.0.1:8080/json.htm?type=command&param=udevice&idx=' + str(idxTemp) + '&svalue=' + str("%.2f;%.2f;0;%.2f;0" % (temp,wilgp,cisn))
            if DEBUG: print(u)
            d = requests.post(u)

    # https://www.domoticz.com/wiki/Domoticz_API/JSON_URL's#Wind
        idxWiatr = CZUJNIKI[czuj][1]
        if idxWiatr > 0:
            dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            ix = int((wkier + 11.25)/22.5)
            wdir = dirs[ix % 16]
            u = 'http://127.0.0.1:8080/json.htm?type=command&param=udevice&idx=' + str(idxWiatr) + '&svalue=' + str("%i;%s;%s;%.2f;%.2f;%.2f" % (wkier,wdir,10*wiatr,10*wiatr,temp,temp))
            if DEBUG: print(u)
            d = requests.post(u)

        idxOpad = CZUJNIKI[czuj][2]
        if idxOpad > 0:
            u = 'http://127.0.0.1:8080/json.htm?type=command&param=udevice&idx=' + str(idxOpad) + '&svalue=' + str("%.2f" % (opad))
            if DEBUG: print(u)
            d = requests.post(u)

    except Exception as e:
        raise
