import sys
import os
from skills.validador_talles import validar_talle
from skills.calculadora_descuento import calcular_descuento_transferencia
from skills.detector_zona import clasificar_zona_entrega
from skills.generador_lead import generar_resumen_pedido
from skills.ventas_consultiva import manejar_objecion
from skills.lector_productos import (
    cargar_productos_desde_csv, 
    obtener_catalogo_unico, 
    obtener_talles_disponibles, 
    obtener_precio_producto,
    obtener_multimedia_producto,
    registrar_venta,
    registrar_actualizacion
)

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def simulador_bot():
    print("🚀 --- ZAPAS SHOW: BOT DE VENTAS PROFESIONAL --- 🚀")
    
    ruta_csv = "zapatillas_greta.csv"
    
    # --- CARGA INICIAL ---
    inventario = cargar_productos_desde_csv(ruta_csv)
    if not inventario:
        print("❌ Error: No se pudo cargar el inventario. Verificá el archivo CSV.")
        return
    
    catalogo = obtener_catalogo_unico(inventario)
    ultimo_mtime = os.path.getmtime(ruta_csv)
    
    registrar_actualizacion(f"Bot iniciado. {len(inventario)} registros cargados: {len(catalogo)} modelos.")

    def verificar_actualizacion_inventario(inv, cat, mtime):
        nonlocal inventario, catalogo, ultimo_mtime
        try:
            current_mtime = os.path.getmtime(ruta_csv)
            if current_mtime > mtime:
                print("\n[SISTEMA] 🔄 Detectada actualización en la lista. Recargando...")
                nuevos_datos = cargar_productos_desde_csv(ruta_csv)
                if nuevos_datos:
                    inventario = nuevos_datos
                    catalogo = obtener_catalogo_unico(inventario)
                    ultimo_mtime = current_mtime
                    registrar_actualizacion(f"Base de datos actualizada automáticamente: {len(catalogo)} modelos cargados.")
                    print("[SISTEMA] ✅ Datos actualizados con éxito.")
                else:
                    print("[SISTEMA] ❌ Error al recargar. Se mantienen datos anteriores.")
        except Exception as e:
            print(f"[SISTEMA] Error al verificar cambios: {e}")

    # --- MEMORIA DEL BOT (MÁQUINA DE ESTADOS) ---
    pedido = {
        "marca": "Zapas Show",
        "modelo": None,
        "precio_lista": 0,
        "contacto": "wa.me/5491173739122",
        "talle": None,
        "zona": None,
        "metodo_pago": None,
        "precio_final": None
    }
    
    def flujo_esperado():
        if not pedido.get("modelo"): return "MODELO"
        if not pedido.get("talle"): return "TALLE"
        if not pedido.get("metodo_pago"): return "PAGO"
        if not pedido.get("zona"): return "ZONA"
        if pedido.get("metodo_pago") == "Transferencia" and not pedido.get("estado_pago"): return "COMPROBANTE"
        return "FINALIZADO"

    while True:
        # Verificar si Greta subió un nuevo Excel/CSV
        verificar_actualizacion_inventario(inventario, catalogo, ultimo_mtime)
        
        estado = flujo_esperado()
        
        if estado == "FINALIZADO":
            # Registrar en el histórico de ventas y obtener ID
            id_v = registrar_venta(pedido)
            pedido["id_venta"] = id_v
            resumen = generar_resumen_pedido(pedido)
            if id_v:
                print(f"\n[SISTEMA] ✅ Venta #{id_v} registrada con éxito.")
            print(f"\n📢 {resumen}")
            break

        print(f"\n[SISTEMA] Esperando: {estado}")
        
        if estado == "MODELO":
            print("Bot: 👟 ¡Bienvenido! Elegí uno de nuestros modelos disponibles:")
            for i, modelo in enumerate(catalogo, 1):
                print(f"{i}. {modelo}")
            entrada = input("Tu elección (número o nombre): ").strip()
        else:
            entrada = input("Cliente: ").strip()
        
        if entrada.lower() in ['salir', 'exit', 'quit']: break

        # 1. Manejo de Objeciones (Filtro prioritario)
        objecion = manejar_objecion(entrada)
        if objecion:
            print(f"\nBot: {objecion['respuesta']}")
            print(f"Bot: 💡 *Para avanzar*, sigamos con la selección de {estado.lower()}.")
            continue

        # 2. Lógica de Flujo
        if estado == "MODELO":
            # Validar selección de modelo
            modelo_seleccionado = None
            if entrada.isdigit() and 1 <= int(entrada) <= len(catalogo):
                modelo_seleccionado = catalogo[int(entrada)-1]
            else:
                for m in catalogo:
                    if m.lower() in entrada.lower():
                        modelo_seleccionado = m
                        break
            
            if modelo_seleccionado:
                pedido["modelo"] = modelo_seleccionado
                pedido["precio_lista"] = obtener_precio_producto(inventario, modelo_seleccionado)
                
                # --- NUEVA LÓGICA MULTIMEDIA ---
                link_visual = obtener_multimedia_producto(inventario, modelo_seleccionado)
                print(f"\nBot: ¡Genial! Elegiste **{modelo_seleccionado}**.")
                
                if link_visual:
                    print(f"Bot: 📸 Podés ver las fotos y videos reales acá: {link_visual}")
                
                talles_disponibles = obtener_talles_disponibles(inventario, modelo_seleccionado)
                print(f"Bot: 📏 Para este modelo tenemos disponibles: {talles_disponibles}")
                print("Bot: ¿Qué talle buscás?")
            else:
                print("\nBot: ❌ No pude encontrar ese modelo. Por favor, elegí uno de la lista.")

        elif estado == "TALLE":
            resultado = validar_talle(entrada)
            if resultado['valido']:
                # Validar contra stock real del CSV
                talles_reales = obtener_talles_disponibles(inventario, pedido["modelo"])
                if int(resultado['talle']) in talles_reales:
                    print(f"\nBot: {resultado['mensaje']}")
                    pedido["talle"] = resultado['talle']
                    print(f"Bot: El precio de lista es **${pedido['precio_lista']:,.2f}**.".replace(",", "X").replace(".", ",").replace("X", "."))
                    
                    print("\nBot: 💳 **¿Cómo preferís abonar?**")
                    print("1. **Transferencia (10% OFF)**")
                    print("2. **Efectivo (al retirar)**")
                else:
                    print(f"\nBot: Lo lamento, el talle {resultado['talle']} no lo tenemos en stock para este modelo. Probá con: {talles_reales}")
            else:
                print(f"\nBot: {resultado['mensaje']}")

        elif estado == "PAGO":
            metodo = entrada.lower()
            
            if "transferencia" in metodo or "1" in metodo:
                pedido["metodo_pago"] = "Transferencia"
                factura = calcular_descuento_transferencia(pedido["precio_lista"])
                pedido["precio_final"] = factura["precio_final"]
                print(f"\nBot: � ¡Genial! Con transferencia te queda en solo **${pedido['precio_final']:,.2f}**.".replace(",", "X").replace(".", ",").replace("X", "."))
                print("Bot: 📍 ¿En qué zona estás para ver el envío?")
            elif "efectivo" in metodo or "2" in metodo:
                pedido["metodo_pago"] = "Efectivo"
                pedido["precio_final"] = pedido["precio_lista"]
                pedido["estado_pago"] = "PAGADO_EN_MANO"
                print("\nBot: 💵 ¡Perfecto! Pagás en efectivo al momento de retirar.")
                print("Bot: 📍 ¿En qué punto de entrega preferís retirar? (Caballito / El Triángulo)")
            else:
                manejar_objecion(entrada)

        elif estado == "ZONA":
            resultado = clasificar_zona_entrega(entrada)
            print(f"\nBot: {resultado['mensaje']}")
            pedido["zona"] = resultado.get("zona_detectada", entrada)
            
            if pedido["metodo_pago"] == "Transferencia":
                print(f"\nBot: 💳 **Datos para la Transferencia:**")
                print(f"💰 **Monto: ${pedido['precio_final']:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
                print(f"🔗 **Alias:** paramore.com")
                print(f"🏦 **CVU:** 0000003100008908041561")
                print(f"👤 **Titular:** Sofia Marina Diaz")
                print(f"\nBot: ¿Pudiste realizar el envío del comprobante? (Si/No)")
            else:
                print("\nBot: ¡Perfecto! Estoy procesando tu pedido...")
        
        elif estado == "COMPROBANTE":
            if "si" in entrada.lower():
                pedido["estado_pago"] = "PAGADO"
                print("\nBot: ¡Excelente! Comprobante recibido. ✅")
            else:
                pedido["estado_pago"] = "PENDIENTE"
                print("\nBot: Dale, no hay problema. Tu pedido queda registrado como **PENDIENTE** hasta que envíes el comprobante. 🙏")

if __name__ == "__main__":
    simulador_bot()
