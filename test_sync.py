import sys
import time
import os
from skills.lector_productos import registrar_actualizacion

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def test_sincronizacion():
    ruta_csv = "zapatillas_greta.csv"
    ruta_log = "actualizaciones.log"
    
    print("🚀 Probando Sistema de Sincronización...")
    
    # 1. Verificar si el log existe
    if os.path.exists(ruta_log):
        print(f"✅ Archivo de log encontrado: {ruta_log}")
    else:
        print("⚠️ El log se creará en la primera actualización.")

    # 2. Simular una actualización "tocando" el archivo
    print("📝 Simulando actualización del archivo CSV...")
    original_mtime = os.path.getmtime(ruta_csv)
    
    # Esperar un segundo para asegurar que el mtime cambie
    time.sleep(1.1)
    
    # "Touch" el archivo modificando su tiempo de acceso/modificación
    os.utime(ruta_csv, None)
    
    nuevo_mtime = os.path.getmtime(ruta_csv)
    
    if nuevo_mtime > original_mtime:
        print("✅ El tiempo de modificación del CSV ha cambiado.")
        registrar_actualizacion("Prueba de sincronización detectada (Simulada).")
    else:
        print("❌ Error: No se pudo simular el cambio de tiempo.")

    # 3. Leer el log
    print("\n📄 Últimas entradas del log:")
    try:
        with open(ruta_log, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            for linea in lineas[-3:]:
                print(f"  > {linea.strip()}")
    except Exception as e:
        print(f"Error al leer el log: {e}")

if __name__ == "__main__":
    test_sincronizacion()
