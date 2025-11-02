import requests
import urllib.parse

# Clave válida
key = "c8bd4c3c-d194-40b9-9a35-305ecaa4c0ce"

def buscar_coordenadas(lugar, key):
    if not lugar:
        lugar = input("¿Dónde cresta es eso? No caché: ")
    
    url_busqueda = "https://graphhopper.com/api/1/geocode?"
    parametros = urllib.parse.urlencode({
        "q": lugar, 
        "limit": "1", 
        "key": key
    })
    
    try:
        respuesta = requests.get(url_busqueda + parametros, timeout=10)
        datos = respuesta.json()
        
        if respuesta.status_code == 200 and datos.get("hits"):
            punto = datos["hits"][0]["point"]
            lat = punto["lat"]
            lng = punto["lng"]
            nombre = datos["hits"][0].get("name", "Sin nombre")
            
            region = datos["hits"][0].get("state", "")
            pais = datos["hits"][0].get("country", "")
            
            if region:
                ubicacion_completa = f"{nombre}, {region}, {pais}"
            else:
                ubicacion_completa = f"{nombre}, {pais}"
                
            return respuesta.status_code, lat, lng, ubicacion_completa
        else:
            print(f"No se encontró '{lugar}' en el mapa.")
            return respuesta.status_code, None, None, lugar
            
    except Exception as error:
        print(f"Ocurrió un problema: {error}")
        return 500, None, None, lugar


print("*** CALCULADORA DE RUTAS ***")
print("(escribe 'salir' para terminar)")

while True:
    print("\n" + "="*50)
    vehiculo = input("¿Cómo vas a viajar? (auto/bicicleta/pie): ").lower().strip()
    
    if vehiculo in ['salir', 's', 'exit', 'q']:
        print("Hasta luego. Buen viaje.")
        break
        
    if vehiculo not in ['auto', 'bicicleta', 'pie']:
        print("No reconocí ese medio de transporte, asumiré que vas en auto.")
        vehiculo_api = "car"
    else:
        vehiculo_api = {"auto": "car", "bicicleta": "bike", "pie": "foot"}[vehiculo]
    
    desde = input("¿Desde dónde sales? ").strip()
    if desde in ['salir', 's']:
        break
        
    hasta = input("¿Hacia dónde vas? ").strip() 
    if hasta in ['salir', 's']:
        break
    
    print("Buscando coordenadas, por favor espera...")
    origen = buscar_coordenadas(desde, key)
    destino = buscar_coordenadas(hasta, key)
    
    if origen[0] != 200 or destino[0] != 200:
        print("No se pudo encontrar alguna de las ubicaciones.")
        continue
        
    if not origen[1] or not destino[1]:
        print("Hubo un problema con las coordenadas.")
        continue

    # Se agrega locale=es para obtener resultados en español
    params_base = urllib.parse.urlencode({
        "key": key,
        "vehicle": vehiculo_api,
        "locale": "es"
    })

    punto_origen = f"&point={origen[1]},{origen[2]}"
    punto_destino = f"&point={destino[1]},{destino[2]}"
    
    url_ruta = f"https://graphhopper.com/api/1/route?{params_base}{punto_origen}{punto_destino}"
    
    try:
        respuesta = requests.get(url_ruta, timeout=15)
        datos_ruta = respuesta.json()
        
        print("\n" + "="*50)
        print(f"Desde: {origen[3]}")
        print(f"Hasta: {destino[3]}")
        print(f"Medio de transporte: {vehiculo}")
        print("="*50)
        
        if respuesta.status_code == 200 and datos_ruta.get("paths"):
            ruta = datos_ruta["paths"][0]
            
            metros = ruta["distance"]
            km = metros / 1000
            millas = km / 1.61
            
            segundos_totales = ruta["time"] / 1000
            horas = int(segundos_totales // 3600)
            minutos = int((segundos_totales % 3600) // 60)
            segundos = int(segundos_totales % 60)
            
            print(f"Distancia total: {km:.1f} km ({millas:.1f} millas)")
            print(f"Tiempo estimado: {horas:02d}:{minutos:02d}:{segundos:02d}")
            print("="*50)
            
            if "instructions" in ruta:
                print("Indicaciones paso a paso:")
                for i, paso in enumerate(ruta["instructions"], 1):
                    texto = paso["text"]
                    dist_paso_km = paso["distance"] / 1000
                    print(f"{i}. {texto} ({dist_paso_km:.1f} km)")
            else:
                print("No hay instrucciones detalladas para esta ruta.")
                
        else:
            mensaje_error = datos_ruta.get("message", "Error desconocido.")
            print(f"No se pudo calcular la ruta: {mensaje_error}")
            
    except requests.exceptions.Timeout:
        print("El servidor tardó demasiado en responder.")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    print("="*50)
    print("\n¿Quieres calcular otra ruta? (presiona Enter para continuar o escribe 'salir' para terminar)")
    if input().lower() in ['salir', 's', 'no', 'n']:
        print("Hasta pronto.")
        break