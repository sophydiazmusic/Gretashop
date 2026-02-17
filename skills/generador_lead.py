def generar_resumen_pedido(datos_pedido):
    """
    Skill: Generador de Lead
    Objetivo: Formatear el pedido para el administrador.
    
    Estructura de datos_pedido esperada:
    {
        "marca": str,
        "modelo": str,
        "talle": int/str,
        "zona": str,
        "metodo_pago": str,
        "contacto": str
    }
    """
    total_formateado = f"${float(datos_pedido.get('precio_final', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    contacto = datos_pedido.get('contacto', 'N/A')
    if "whatsapp:" in contacto:
        contacto = contacto.replace("whatsapp:+", "wa.me/")
    
    resumen = (
        f"📝 **RESUMEN DEL PEDIDO #{datos_pedido.get('id_venta', '000')}**\n"
        "--------------------------\n"
        f"👟 **Modelo:** {datos_pedido.get('modelo', 'N/A')}\n"
        f"📏 **Talle:** {datos_pedido.get('talle', 'N/A')}\n"
        f"📍 **Entrega:** {datos_pedido.get('zona', 'N/A')}\n"
        f"💳 **Método de Pago:** {datos_pedido.get('metodo_pago', 'N/A')}\n"
        f"💰 **Total a Pagar:** {total_formateado}\n"
        "--------------------------\n"
        f"👤 **Contacto:** {contacto}\n\n"
        "✅ *Por favor, enviá este mensaje por WhatsApp para confirmar tu pedido.*"
    )
    return resumen
