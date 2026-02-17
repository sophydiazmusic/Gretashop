import os
import time
from datetime import datetime
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
    buscar_modelos_por_talle
)

class BotWhatsApp:
    def __init__(self):
        self.ruta_csv = "zapatillas_greta.csv"
        self.inventario = cargar_productos_desde_csv(self.ruta_csv)
        self.catalogo = obtener_catalogo_unico(self.inventario)
        # Diccionario para guardar el estado de cada usuario: {telefono: {datos_pedido}}
        self.sesiones = {}

    def obtener_estado_usuario(self, telefono):
        if telefono not in self.sesiones:
            self.sesiones[telefono] = self._crear_nueva_sesion(telefono)
        # Actualizar siempre la última interacción al recibir mensaje
        self.sesiones[telefono]["ultima_interaccion"] = time.time()
        self.sesiones[telefono]["recordatorio_enviado"] = False
        return self.sesiones[telefono]

    def _crear_nueva_sesion(self, telefono="N/A"):
        return {
            "contacto": telefono,
            "modelo": None,
            "talle": None,
            "metodo_pago": None,
            "envio_o_retiro": None,  # Nuevo campo
            "zona": None,
            "estado_pago": None,
            "pedido_completado": False,
            "ultima_interaccion": time.time(),
            "recordatorio_enviado": False
        }

    def procesar_mensaje(self, telefono, mensaje):
        mensaje = mensaje.strip().lower()
        pedido = self.obtener_estado_usuario(telefono)
        
        # 1. Comandos de Navegación
        if "menu" in mensaje or "menú" in mensaje or "reiniciar" in mensaje or "hola" in mensaje or "nuevo" in mensaje:
            self.sesiones[telefono] = self._crear_nueva_sesion(telefono)
            pedido = self.sesiones[telefono]
            return self.manejar_etapa_modelo(pedido, "lista")

        if "atras" in mensaje or "atrás" in mensaje or "volver" in mensaje:
            return self.retroceder_estado(pedido)

        # Si el pedido ya estaba completado, invitar a uno nuevo
        if pedido.get("pedido_completado"):
            return "Tu pedido anterior ya fue registrado. ✨\n\nSi querés hacer uno nuevo, escribí **'MENÚ'** o **'REINICIAR'**."

        # 2. Manejo de Objeciones (IA)
        objecion = manejar_objecion(mensaje)
        if objecion:
            return f"{objecion['respuesta']}\n\n💡 *Para avanzar*, seguimos con el pedido de su {pedido.get('modelo', 'calzado')}."

        # 3. Determinar en qué etapa estamos
        if not pedido["modelo"]:
            return self.manejar_etapa_modelo(pedido, mensaje)
        if not pedido["talle"]:
            return self.manejar_etapa_talle(pedido, mensaje)
        if not pedido["metodo_pago"]:
            return self.manejar_etapa_pago(pedido, mensaje)
        if not pedido["zona"]:
            return self.manejar_etapa_zona(pedido, mensaje)
        if pedido["metodo_pago"] == "Transferencia" and not pedido["estado_pago"]:
            return self.manejar_etapa_comprobante(pedido, mensaje)
        
        return "Para volver a empezar escribe **'MENÚ'**."

    def verificar_timeouts(self):
        """
        Revisa todas las sesiones activas y genera mensajes de recordatorio o cierre.
        Retorna: [(telefono, mensaje)]
        """
        ahora = time.time()
        mensajes_proactivos = []
        telefonos_a_borrar = []

        for telefono, pedido in self.sesiones.items():
            if pedido.get("pedido_completado"):
                continue

            transcurrido = ahora - pedido["ultima_interaccion"]

            # 5 Minutos (300 segundos): Cierre amigable
            if transcurrido > 300:
                msg = "¡Hola! Notamos que no hubo respuesta, así que cerramos la conversación por ahora para no interrumpirte. 😊\n\nCualquier duda que tengas, ¡escribinos cuando quieras! Greta Shop te espera. ✨"
                mensajes_proactivos.append((telefono, msg))
                telefonos_a_borrar.append(telefono)
            
            # 2 Minutos (120 segundos): Recordatorio
            elif transcurrido > 120 and not pedido.get("recordatorio_enviado"):
                msg = "¡Che! Seguimos por acá por si todavía querés tus zapas. ¡No te cuelgues que vuelan! 😊👟"
                mensajes_proactivos.append((telefono, msg))
                pedido["recordatorio_enviado"] = True

        for t in telefonos_a_borrar:
            del self.sesiones[t]

        return mensajes_proactivos

    def retroceder_estado(self, pedido):
        pedido["pedido_completado"] = False
        if pedido["zona"]: pedido["zona"] = None; return "Volvemos a la zona. ¿En qué zona estás?"
        if pedido["metodo_pago"]: pedido["metodo_pago"] = None; return "Volvemos al pago. ¿Transferencia o Efectivo?"
        if pedido["talle"]: pedido["talle"] = None; return "Volvemos al talle. ¿Qué talle buscás?"
        if pedido["modelo"]: 
            pedido["modelo"] = None
            prefijo = "Volvemos al inicio. Elegí un modelo de la lista.\n\n"
            return prefijo + self.manejar_etapa_modelo(pedido, "lista")
        return "Ya estamos en el inicio."

    def manejar_etapa_modelo(self, pedido, mensaje):
        modelo_seleccionado = None
        # Buscar por nombre o número
        if mensaje.isdigit() and 1 <= int(mensaje) <= len(self.catalogo):
            modelo_seleccionado = self.catalogo[int(mensaje)-1]
        else:
            for m in self.catalogo:
                if m.lower() in mensaje.lower():
                    modelo_seleccionado = m
                    break
        
        if modelo_seleccionado:
            pedido["modelo"] = modelo_seleccionado
            pedido["precio_lista"] = obtener_precio_producto(self.inventario, modelo_seleccionado)
            link_visual = obtener_multimedia_producto(self.inventario, modelo_seleccionado)
            talles = obtener_talles_disponibles(self.inventario, modelo_seleccionado)
            
            resp = f"¡Buenísimo! Elegiste **{modelo_seleccionado}**. Es re fachero. 🔥\n"
            if link_visual:
                resp += f"📸 Mirá las fotos/videos acá: {link_visual}\n"
            resp += f"📏 Talles disponibles en este modelo: {talles}\n\n"
            resp += "¿Qué talle buscás? ¡Avisanos que vuelan!\n*(Escribí **ATRAS** para volver o **MENU** para el inicio)*"
            return resp
        else:
            lista = "\n".join([f"{i+1}. {m}" for i, m in enumerate(self.catalogo)])
            return f"👟 ¡Hola! Bienvenida a **Greta Shop**. ¿Cómo va todo? \n\nElegite un modelo de la lista y lo reservamos. Hacemos entregas en mano en **Moreno, San Miguel y Grand Bourg**. 📍\n\n{lista}\n\n*(Escribí **MENU** en cualquier momento para volver aquí)*"

    def manejar_etapa_talle(self, pedido, mensaje):
        resultado = validar_talle(mensaje)
        if resultado['valido']:
            talle_num = int(resultado['talle'])
            
            # Regla de talles: Explicar si es muy chico
            if talle_num < 37:
                return f"¡Che! Te cuento que por ahora estamos laburando fuerte del **37 en adelante**. Te recomiendo estar atenta que siempre entran cosas nuevas. 😊\n\n¿Querés probar con otro talle o ver otros modelos? (Escribí **ATRAS**)"

            talles_reales = obtener_talles_disponibles(self.inventario, pedido["modelo"])
            
            if talle_num in talles_reales:
                pedido["talle"] = resultado['talle']
                precio_f = f"${pedido['precio_lista']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"¡De diez! Talle {resultado['talle']} reservado. ✅\n\n💰 Precio: **{precio_f}**\n\n💳 **¿Cómo preferís abonar?**\n1. Transferencia (10% OFF)\n2. Efectivo (al retirar)\n\n*(Escribí **ATRAS** para cambiar de talle o **MENU** para el inicio)*"
            
            # Si no hay talle, buscar otros modelos
            alternativos = buscar_modelos_por_talle(self.inventario, talle_num)
            resp = f"Ese talle no me quedó en **{pedido['modelo']}**. Tenemos: {talles_reales}\n\n"
            if alternativos:
                modelos_str = ", ".join(alternativos)
                resp += f"💡 *Dato:* En talle **{talle_num}** sí tengo stock de: {modelos_str}. (Escribí **ATRAS** si querés cambiar de modelo)"
            else:
                resp += f"Lo siento, por el momento no tengo ningún modelo en talle **{talle_num}**."
            return resp
            
        return f"No entendí el talle. ¿Podrías decirme solo el número? (ej: 38)"

    def manejar_etapa_pago(self, pedido, mensaje):
        if "transferencia" in mensaje.lower() or "1" in mensaje:
            pedido["metodo_pago"] = "Transferencia"
            pedido["precio_final"] = calcular_descuento_transferencia(pedido["precio_lista"])["precio_final"]
            precio_d = f"${pedido['precio_final']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"💸 ¡Genial! Con transferencia te queda en **{precio_d}**. Una ganga. 🙌\n\n¿Cómo preferís recibir tus zapas?\n1. Retiro en punto de encuentro (**¡ES GRATIS!**)\n2. Envío por Correo Argentino"
        elif "efectivo" in mensaje.lower() or "2" in mensaje:
            pedido["metodo_pago"] = "Efectivo"
            pedido["envio_o_retiro"] = "Retiro"
            pedido["precio_final"] = pedido["precio_lista"]
            pedido["estado_pago"] = "PAGADO_EN_MANO"
            return "💵 Dale, pagás al retirar. ¡Te esperamos!\n\n📍 ¿En qué punto retirás? (**¡ES GRATIS!**)\n1. Moreno\n2. San Miguel\n3. Grand Bourg\n4. Morón\n5. Caballito\n6. OTRO (Envío por Correo)"
        return "Por favor, elegí: 1. Transferencia o 2. Efectivo."

    def manejar_etapa_zona(self, pedido, mensaje):
        # Si eligió transferencia y aún no definió si es retiro o envío
        if pedido["metodo_pago"] == "Transferencia" and not pedido["envio_o_retiro"]:
            if "1" in mensaje or "retiro" in mensaje.lower():
                pedido["envio_o_retiro"] = "Retiro"
                return "📍 ¿En qué punto retirás? (**¡ES GRATIS!**)\n1. Grand Bourg\n2. Morón\n3. San Miguel\n4. El Triángulo\n5. Caballito\n6. OTRO (Envío por Correo)"
            elif "2" in mensaje or "envio" in mensaje.lower():
                pedido["envio_o_retiro"] = "Envío"
                pedido["zona"] = "Correo Argentino"
                # Pasamos directo a datos bancarios
                return self.finalizar_etapa_zona_transferencia(pedido)
            else:
                return "Por favor, elegí: 1. Retiro o 2. Envío por Correo."

        # Mapeo de números a zonas si el usuario elige por número
        ZONAS_RETIRQ = {
            "1": "Grand Bourg",
            "2": "Morón",
            "3": "San Miguel",
            "4": "El Triángulo",
            "5": "Caballito",
            "6": "OTRO"
        }
        if mensaje in ZONAS_RETIRQ:
            mensaje = ZONAS_RETIRQ[mensaje]

        resultado = clasificar_zona_entrega(mensaje)
        pedido["zona"] = resultado.get("zona_detectada", mensaje)
        
        if pedido["metodo_pago"] == "Transferencia":
            return self.finalizar_etapa_zona_transferencia(pedido, resultado['mensaje'])
        
        return self.finalizar_pedido(pedido, "¡Excelente!")

    def finalizar_etapa_zona_transferencia(self, pedido, prefijo_zona=""):
        precio_f = f"${pedido['precio_final']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        resp = ""
        if prefijo_zona:
            resp += f"{prefijo_zona}\n\n"
        
        resp += (
            f"💳 **Datos para transferir:**\n"
            f"💰 Monto: **{precio_f}**\n"
            f"🔗 Alias: paramore.com\n"
            f"🏦 CVU: 0000003100008908041561\n"
            f"👤 Titular: Sofia Marina Diaz\n\n"
            "¿Pudiste enviar el comprobante?"
        )
        return resp

    def manejar_etapa_comprobante(self, pedido, mensaje):
        if "si" in mensaje.lower() or "listo" in mensaje.lower() or "ya" in mensaje.lower() or "enviado" in mensaje.lower():
            pedido["estado_pago"] = "PAGADO"
            return self.finalizar_pedido(pedido, "¡Excelente! Comprobante recibido. ✅")
        
        if "no" in mensaje.lower() or "todavia" in mensaje.lower() or "despues" in mensaje.lower():
            pedido["estado_pago"] = "PENDIENTE"
            return self.finalizar_pedido(pedido, "Tu pedido queda como **PENDIENTE** hasta que envíes el comprobante. 🙏")
        
        if "efectivo" in mensaje.lower() or "cambiar" in mensaje.lower():
            pedido["metodo_pago"] = None
            pedido["estado_pago"] = None
            return "¡Okey! ¿Cómo preferís abonar entonces? (Efectivo o Transferencia)"

        return "Para confirmar tu pedido, por favor enviame el comprobante. 🙏\n\n*(Escribí 'SÍ' si ya lo mandaste, o 'DESPUES' si lo mandás más tarde)*"

    def finalizar_pedido(self, pedido, prefijo=""):
        pedido["pedido_completado"] = True
        id_v = registrar_venta(pedido)
        pedido["id_venta"] = id_v
        resumen = generar_resumen_pedido(pedido)
        mensaje_final = (
            f"{prefijo}\n\n{resumen}\n\n"
            "--------------------------\n"
            "📞 *En instantes un asesor se comunicará con vos para coordinar la entrega.*\n\n"
            "✨ Escribí **'NUEVO'** para otro pedido."
        )
        return mensaje_final
