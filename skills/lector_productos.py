import csv
import os
from datetime import datetime

def registrar_actualizacion(mensaje):
    """Registra eventos en el archivo actualizaciones.log"""
    ruta_log = "actualizaciones.log"
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ruta_log, "a", encoding="utf-8") as log:
            log.write(f"[{ahora}] - {mensaje}\n")
    except Exception as e:
        print(f"Error al escribir en el log: {e}")

def cargar_productos_desde_csv(ruta_archivo):
    """
    Skill: Lector de Productos
    Objetivo: Leer el inventario desde el CSV y organizar los datos.
    """
    productos = []
    if not os.path.exists(ruta_archivo):
        return []

    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                val_talle = row.get("Talle")
                val_precio = row.get("PRECIO")
                val_cantidad = row.get("Cantidad")

                try:
                    producto = {
                        "nombre": row.get("Producto"),
                        "talle": int(val_talle) if val_talle and str(val_talle).strip().isdigit() else 0,
                        "precio": float(val_precio) if val_precio else 0.0,
                        "stock": int(val_cantidad) if val_cantidad and str(val_cantidad).strip().isdigit() else 0,
                        "multimedia": row.get("Multimedia") or ""
                    }
                    if producto["nombre"]:
                        productos.append(producto)
                except (ValueError, TypeError):
                    continue
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
    
    return productos

def obtener_catalogo_unico(productos):
    """Retorna una lista de nombres de productos únicos."""
    return sorted(list(set(p["nombre"] for p in productos)))

def obtener_talles_disponibles(productos, nombre_producto):
    """Retorna los talles disponibles para un modelo específico."""
    talles = [p["talle"] for p in productos if p["nombre"] == nombre_producto and p["stock"] > 0]
    return sorted(talles)

def obtener_precio_producto(productos, nombre_producto):
    """Retorna el precio de un modelo."""
    for p in productos:
        if p["nombre"] == nombre_producto:
            return p["precio"]
    return 0.0

def obtener_multimedia_producto(productos, nombre_producto):
    """Retorna el enlace multimedia de un modelo."""
    for p in productos:
        if p["nombre"] == nombre_producto:
            return p["multimedia"]
    return ""

def obtener_proximo_id_venta():
    """Retorna el próximo número de venta basado en el CSV histórico."""
    ruta_ventas = "ventas.csv"
    if not os.path.exists(ruta_ventas):
        return 1
    try:
        with open(ruta_ventas, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            if len(lineas) <= 1:
                return 1
            ultima_linea = lineas[-1].split(",")
            return int(ultima_linea[0]) + 1
    except:
        return 1

def registrar_venta(pedido):
    """Registra la venta finalizada en ventas.csv con auditoría."""
    ruta_ventas = "ventas.csv"
    id_venta = obtener_proximo_id_venta()
    existe = os.path.exists(ruta_ventas)
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Determinar estado de comprobante
    estado_pago = pedido.get("estado_pago", "PENDIENTE")
    envio_comprobante = "SI" if estado_pago == "PAGADO" else "NO"
    
    try:
        with open(ruta_ventas, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not existe:
                writer.writerow(["ID", "Fecha", "Producto", "Talle", "Zona", "Metodo", "Total", "Estado Pago", "Comprobante"])
            
            writer.writerow([
                id_venta,
                ahora,
                pedido.get("modelo"),
                pedido.get("talle"),
                pedido.get("zona"),
                pedido.get("metodo_pago"),
                pedido.get("precio_final"),
                estado_pago,
                envio_comprobante
            ])
        registrar_actualizacion(f"Venta #{id_venta} registrada como {estado_pago}.")
        return id_venta
    except Exception as e:
        print(f"Error al registrar venta: {e}")
        return None
def buscar_modelos_por_talle(productos, talle_buscado):
    """Retorna una lista de modelos que tienen stock en el talle especificado."""
    modelos = [p["nombre"] for p in productos if p["talle"] == talle_buscado and p["stock"] > 0]
    return sorted(list(set(modelos)))
