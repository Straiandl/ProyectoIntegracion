import hashlib
import json
import time
import datetime
import shutil

ARCHIVO_CRITICO = "config.json"
ARCHIVO_RESPALDO = "config_backup.json"
LOG_SEGURIDAD = "security_events.json"

def calcular_hash(ruta):
    """Calcula la huella digital SHA-256 de un archivo."""
    hasher = hashlib.sha256()
    with open(ruta, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def registrar_restauracion(hash_antiguo, hash_nuevo):
    evento = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tipo": "Restauracion Automatica de Archivo Critico",
        "archivo_afectado": ARCHIVO_CRITICO,
        "hash_alterado": hash_nuevo,
        "accion": "Archivo restaurado desde el respaldo JSON de forma exitosa."
    }
    
    try:
        with open(LOG_SEGURIDAD, "r+") as f:
            logs = json.load(f)
            logs.append(evento)
            f.seek(0)
            json.dump(logs, f, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(LOG_SEGURIDAD, "w") as f:
            json.dump([evento], f, indent=4)

def monitorear_y_restaurar():
    print(" Monitor de Integridad de Archivos (FIM) iniciado...")
    hash_base = calcular_hash(ARCHIVO_RESPALDO)

    while True:
        try:
            hash_actual = calcular_hash(ARCHIVO_CRITICO)
            
            # Si el hash cambió, significa que hubo una modificación no autorizada
            if hash_actual != hash_base:
                print(f"\n [ALERTA FIM] Modificación no autorizada detectada en '{ARCHIVO_CRITICO}'!")
                
                # Restauración automática usando el archivo backup JSON
                shutil.copyfile(ARCHIVO_RESPALDO, ARCHIVO_CRITICO)
                print(" [RESTAURACIÓN] El archivo 'config.json' ha sido restaurado exitosamente a su estado seguro.")
                
                # Registramos el evento
                registrar_restauracion(hash_base, hash_actual)

        except Exception as e:
            print(f"Error en el monitoreo: {e}")

        time.sleep(2)  #Verifica la integridad cada 2 segundos

if __name__ == "__main__":
    monitorear_y_restaurar()