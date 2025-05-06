from pathlib import Path
import json
import logging
import re

def procesar_archivos(directorio):
    servidores = 0
    total_cpu = 0
    total_memoria = 0
    sistemas_operativos = None
    
    for archivo in directorio.glob("*.json"):
        try:
            with archivo.open('r', encoding='utf-8') as f:
                datos = json.load(f)
            
            es_valido, mensaje = validador(datos)
            if not es_valido:
                logging.warning(f"Error en {archivo.name}: {mensaje}")
                continue
            
            servidores += 1
            total_cpu += datos["cpu"]
            total_memoria += datos["memory_gb"]  
            sistemas_operativos = datos["os"] 
            
        except json.JSONDecodeError:
            logging.error(f"Error del formato {archivo.name}.")
    
    if servidores > 0:
        resultado = {
            "Configuraciones válidas": servidores,
            "Total CPUs": total_cpu,
            "Promedio CPUs": total_cpu / servidores,
            "Total Memoria": total_memoria,
            "Promedio Memoria": total_memoria / servidores,
            "Sistema Operativo": sistemas_operativos
        }
        with Path('summary.json').open('w', encoding='utf-8') as archivo_json:
            json.dump(resultado, archivo_json, indent=4)
        logging.info("Resumen generado correctamente.")
        print(json.dumps(resultado, indent=4))
    else:
        logging.warning("Configuración no válida.")
        print("Configuración no válida.")

def validador(datos):
    claves = {
        "hostname", 
        "ip_address", 
        "cpu", 
        "memory_gb",  
        "os"
    }
    
    if any(clave not in datos for clave in claves):
        return False, "Faltan claves requeridas."
    if not re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', datos["ip_address"]):
        return False, "Dirección IP no válida."
    if datos["cpu"] <= 0:
        return False, "El número de CPU's no puede ser negativo"
    if datos["memory_gb"] <= 0:  
        return False, "La memoria no puede ser negativa"
    return True, "Válido"

def directorio():
    ruta = Path(input("Introduce la ruta."))
    if not ruta.is_dir():
        logging.error(f"La ruta {ruta} no existe.")
        print("Error en la ruta")
        exit()
    return ruta

def registro():
    logging.basicConfig(
        filename='aggregator.log',  
        level=logging.INFO,  
    )

def main():
    registro()
    directorio_ruta = directorio()
    procesar_archivos(directorio_ruta)

if __name__ == "__main__":
    main()
