import requests
import urllib.parse
from googletrans import Translator

route_url = "https://graphhopper.com/api/1/route?"
key = "b53b75ff-ee94-43ab-9dfe-fe3581786865"  ### Reemplaza con tu clave de API

translator = Translator()

def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    print("Geocoding API URL for " + location + ":\n" + url)
    if json_status == 200 and len(json_data["hits"]) != 0:
        json_data = requests.get(url).json()
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country = ""

        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state = ""

        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name

        print("Geocoding API URL for " + new_loc + " (Location Type: " + value + ")\n" + url)
        return json_status, lat, lng, new_loc
    else:
        print("Error en la solicitud. Estado:", json_status)
        return json_status, None, None, location

def calcular_distancia_y_duracion(origen, destino, key):
    orig = geocoding(origen, key)
    dest = geocoding(destino, key)
    
    if orig[0] != 200 or dest[0] != 200:
        print("No se pudieron obtener las coordenadas para calcular la ruta.")
        return
    
    op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
    dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
    paths_url = route_url + urllib.parse.urlencode({"key": key}) + op + dp
    paths_data = requests.get(paths_url).json()
    
    if "paths" not in paths_data or len(paths_data["paths"]) == 0:
        print("No se encontraron rutas disponibles entre", orig[3], "y", dest[3])
        return
    
    distancia_km = paths_data["paths"][0]["distance"] / 1000
    duracion_segundos = paths_data["paths"][0]["time"] / 1000
    
    duracion_horas = int(duracion_segundos / 3600)
    duracion_segundos %= 3600
    duracion_minutos = int(duracion_segundos / 60)
    duracion_segundos %= 60
    
    return distancia_km, duracion_horas, duracion_minutos, duracion_segundos, paths_data

while True:
    loc1 = input("Ciudad de origen (o 'salir' para terminar): ")
    if loc1.lower() == "salir":
        print("¡Hasta luego!")
        break
    
    loc2 = input("Ciudad de destino (o 'salir' para terminar): ")
    if loc2.lower() == "salir":
        print("¡Hasta luego!")
        break
    
    resultado = calcular_distancia_y_duracion(loc1, loc2, key)
    
    if resultado:
        distancia, horas, minutos, segundos, paths_data = resultado
        print("=================================================")
        print("Distancia entre", loc1, "y", loc2, ":", "{:.2f}".format(distancia), "km")
        print("Duración del viaje:", "{:02.0f}:{:02.0f}:{:02.0f}".format(float(horas), float(minutos), float(segundos)))
        print("=================================================")
        print("Narrativa del viaje:")
        print(f"¡Viaje desde {loc1} hasta {loc2}!")
        print(f"La distancia es de {distancia:.2f} km y tomará aproximadamente {horas} horas, {minutos} minutos y {segundos} segundos.")
        print("Instrucciones de viaje:")
        print("=============================================")
        for each in range(len(paths_data["paths"][0]["instructions"])):
            path = paths_data["paths"][0]["instructions"][each]["text"]
            distance = paths_data["paths"][0]["instructions"][each]["distance"]
            
            # Traduce el texto al español
            translated_text = translator.translate(path, src='en', dest='es')
            
            print("{0} ( {1:.1f} km )".format(translated_text.text, distance/1000))
        print("=============================================")

