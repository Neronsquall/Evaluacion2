import requests
from typing import Dict, Optional

# ============================================================================
# CONFIGURA TU API KEY AQUÍ
# Obtén una gratis en: https://www.graphhopper.com/
# ============================================================================
API_KEY = "c8bd4c3c-d194-40b9-9a35-305ecaa4c0ce"


class GraphHopperDirecciones:
    """Cliente para la API de GraphHopper para obtener direcciones y rutas"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://graphhopper.com/api/1"
    
    def geocodificar(self, direccion: str) -> Optional[tuple]:
        """
        Convierte una dirección en coordenadas
        
        Args:
            direccion: Dirección a buscar
        
        Returns:
            Tupla (latitud, longitud) o None si no se encuentra
        """
        endpoint = f"{self.base_url}/geocode"
        
        params = {
            "key": self.api_key,
            "q": direccion,
            "limit": 1,
            "locale": "es"
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            resultado = response.json()
            
            if "hits" in resultado and len(resultado["hits"]) > 0:
                lugar = resultado["hits"][0]
                lat = lugar["point"]["lat"]
                lon = lugar["point"]["lng"]
                nombre = lugar.get("name", direccion)
                return (lat, lon, nombre)
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al geocodificar: {e}")
            return None
    
    def obtener_direcciones(self, origen: tuple, destino: tuple, vehiculo: str = "car") -> Dict:
        """
        Obtiene direcciones entre dos puntos
        
        Args:
            origen: Tupla (latitud, longitud) del punto de origen
            destino: Tupla (latitud, longitud) del punto de destino
            vehiculo: Tipo de vehículo (car, bike, foot, motorcycle)
        
        Returns:
            Diccionario con la respuesta de la API
        """
        endpoint = f"{self.base_url}/route"
        
        # Construir URL con múltiples parámetros 'point'
        url_params = []
        url_params.append(f"point={origen[0]},{origen[1]}")
        url_params.append(f"point={destino[0]},{destino[1]}")
        url_params.append(f"key={self.api_key}")
        url_params.append(f"vehicle={vehiculo}")
        url_params.append("locale=es")
        url_params.append("instructions=true")
        url_params.append("calc_points=true")
        url_params.append("points_encoded=false")
        
        url_completa = f"{endpoint}?{'&'.join(url_params)}"
        
        try:
            response = requests.get(url_completa)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def traducir_instruccion(self, texto: str) -> str:
        """
        Traduce palabras en inglés que puedan aparecer en las instrucciones
        
        Args:
            texto: Texto de la instrucción
        
        Returns:
            Texto traducido
        """
        # Diccionario de traducciones (orden importa para frases compuestas)
        traducciones = {
            # Frases compuestas primero
            "keep left": "mantente a la izquierda",
            "keep right": "mantente a la derecha",
            "turn left": "gira a la izquierda",
            "turn right": "gira a la derecha",
            "slight left": "levemente a la izquierda",
            "slight right": "levemente a la derecha",
            "sharp left": "cerrado a la izquierda",
            "sharp right": "cerrado a la derecha",
            "u-turn": "da vuelta en U",
            "and take": "y toma",
            "take the": "toma la",
            # Palabras individuales
            "towards": "hacia",
            "toward": "hacia",
            "onto": "hacia",
            "continue": "continúa",
            "arrive": "llega",
            "destination": "destino",
            "roundabout": "rotonda",
            "exit": "salida",
            "enter": "entra",
            "ferry": "ferry",
            "merge": "incorpórate",
            "ramp": "rampa",
            "fork": "bifurcación",
            "straight": "recto",
            "uturn": "da vuelta en U",
            "left": "izquierda",
            "right": "derecha",
            "keep": "mantente",
            "turn": "gira",
            "take": "toma",
            "and": "y",
            "the": "la",
            "at": "en",
            "to": "a",
            "for": "por"
        }
        
        texto_traducido = texto
        
        # Traducir frases y palabras (respetando mayúsculas/minúsculas)
        for ingles, espanol in traducciones.items():
            # Reemplazar con la primera letra en mayúscula si está al inicio
            if texto_traducido.startswith(ingles.capitalize()):
                texto_traducido = texto_traducido.replace(
                    ingles.capitalize(), 
                    espanol.capitalize(), 
                    1
                )
            # Reemplazar en minúsculas en el resto del texto
            texto_traducido = texto_traducido.replace(ingles, espanol)
        
        return texto_traducido
    
    def mostrar_direcciones(self, resultado: Dict, dir_origen: str, dir_destino: str):
        """
        Muestra las direcciones en formato legible
        
        Args:
            resultado: Diccionario con la respuesta de la API
            dir_origen: Dirección de origen (texto)
            dir_destino: Dirección de destino (texto)
        """
        if "error" in resultado:
            print(f"\n❌ Error: {resultado['error']}")
            return
        
        if "paths" not in resultado or len(resultado["paths"]) == 0:
            print("\n❌ No se encontraron rutas disponibles.")
            return
        
        path = resultado["paths"][0]
        
        # Información general
        distancia_km = path["distance"] / 1000
        tiempo_min = path["time"] / 60000
        tiempo_horas = tiempo_min / 60
        
        print("\n" + "=" * 70)
        print(f"{'RUTA CALCULADA':^70}")
        print("=" * 70)
        print(f"\n📍 Origen:  {dir_origen}")
        print(f"📍 Destino: {dir_destino}")
        print(f"\n📏 Distancia total: {distancia_km:.2f} km")
        
        if tiempo_min >= 60:
            print(f"⏱️  Tiempo estimado: {tiempo_horas:.2f} horas ({tiempo_min:.2f} minutos)")
        else:
            print(f"⏱️  Tiempo estimado: {tiempo_min:.2f} minutos")
        
        print("\n" + "=" * 70)
        print("INSTRUCCIONES PASO A PASO:")
        print("=" * 70 + "\n")
        
        # Instrucciones paso a paso
        if "instructions" in path:
            for i, instruccion in enumerate(path["instructions"], 1):
                texto = instruccion.get("text", "")
                texto_traducido = self.traducir_instruccion(texto)
                distancia_metros = instruccion.get("distance", 0)
                tiempo_ms = instruccion.get("time", 0)
                tiempo_seg = tiempo_ms / 1000
                
                print(f"Paso {i}: {texto_traducido}")
                
                if distancia_metros > 0:
                    if distancia_metros >= 1000:
                        distancia_km_paso = distancia_metros / 1000
                        print(f"   → Distancia: {distancia_km_paso:.2f} km")
                    else:
                        print(f"   → Distancia: {distancia_metros:.2f} metros")
                    
                    if tiempo_seg >= 60:
                        tiempo_min_paso = tiempo_seg / 60
                        print(f"   → Tiempo: {tiempo_min_paso:.2f} minutos")
                    else:
                        print(f"   → Tiempo: {tiempo_seg:.2f} segundos")
                
                print()
        
        print("=" * 70)
        print("¡Buen viaje!")
        print("=" * 70)


def obtener_ruta():
    """Función principal que solicita dos direcciones y muestra la ruta"""
    
    print("=" * 70)
    print(f"{'SISTEMA DE DIRECCIONES':^70}")
    print("=" * 70)
    
    cliente = GraphHopperDirecciones(API_KEY)
    
    # Solicitar dirección de origen
    print("\n📍 Ingrese la dirección de ORIGEN:")
    dir_origen = input("   → ").strip()
    
    if not dir_origen:
        print("❌ Debe ingresar una dirección de origen.")
        return
    
    print("\n⏳ Buscando dirección de origen...")
    coords_origen = cliente.geocodificar(dir_origen)
    
    if not coords_origen:
        print(f"❌ No se pudo encontrar la dirección: {dir_origen}")
        return
    
    print(f"✅ Origen encontrado: {coords_origen[2]}")
    print(f"   Coordenadas: {coords_origen[0]:.6f}, {coords_origen[1]:.6f}")
    
    # Solicitar dirección de destino
    print("\n📍 Ingrese la dirección de DESTINO:")
    dir_destino = input("   → ").strip()
    
    if not dir_destino:
        print("❌ Debe ingresar una dirección de destino.")
        return
    
    print("\n⏳ Buscando dirección de destino...")
    coords_destino = cliente.geocodificar(dir_destino)
    
    if not coords_destino:
        print(f"❌ No se pudo encontrar la dirección: {dir_destino}")
        return
    
    print(f"✅ Destino encontrado: {coords_destino[2]}")
    print(f"   Coordenadas: {coords_destino[0]:.6f}, {coords_destino[1]:.6f}")
    
    # Solicitar tipo de vehículo
    print("\n🚗 Seleccione el tipo de vehículo:")
    print("   1. Automóvil")
    print("   2. Bicicleta")
    print("   3. A pie")
    print("   4. Motocicleta")
    
    vehiculo_map = {"1": "car", "2": "bike", "3": "foot", "4": "motorcycle"}
    vehiculo_opcion = input("\nOpción (presione Enter para automóvil): ").strip()
    vehiculo = vehiculo_map.get(vehiculo_opcion, "car")
    
    # Obtener y mostrar direcciones
    print("\n⏳ Calculando ruta...")
    
    resultado = cliente.obtener_direcciones(
        (coords_origen[0], coords_origen[1]),
        (coords_destino[0], coords_destino[1]),
        vehiculo
    )
    
    cliente.mostrar_direcciones(resultado, coords_origen[2], coords_destino[2])


if __name__ == "__main__":
    try:
        while True:
            obtener_ruta()
            
            print("\n" + "=" * 70)
            continuar = input("¿Desea calcular otra ruta? (s/n): ").strip().lower()
            
            if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
                print("\n" + "=" * 70)
                print("👋 ¡Gracias por usar el sistema de direcciones!")
                print("=" * 70)
                break
            
            print("\n" * 2)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("👋 Programa interrumpido. ¡Hasta luego!")
        print("=" * 70)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")