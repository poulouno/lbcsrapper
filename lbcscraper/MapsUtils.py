import googlemaps

gmaps = googlemaps.Client(key)


def getDistance(origin, dest):
    res = gmaps.distance_matrix(origins=origin, destinations=dest,
                     mode='driving')
    elem = res.get('rows')[0].get('elements')[0]
    #print elem
    duration =  elem.get('duration').get('value')/60
    distance =  elem.get('distance').get('value')/1000
    

    return distance, duration

if __name__ == "__main__":
    print getDistance('meylan', 'saint egreve 38120')