def validar_talle(entrada_usuario):
    """
    Skill: Validador de Stock
    Objetivo: Validar que el talle esté entre 37 y 45.
    """
    try:
        # Intentamos extraer el número de la entrada (por si el usuario pone "talle 40")
        talle = int(''.join(filter(str.isdigit, str(entrada_usuario))))
        
        if 35 <= talle <= 45:
            return {
                "valido": True,
                "mensaje": f"¡Excelente elección! El talle {talle} está disponible. ¿Te gustaría confirmar el modelo?",
                "talle": talle
            }
        else:
            return {
                "valido": False,
                "mensaje": "Lo lamento, por el momento solo trabajamos talles (del 35 al 45). No contamos con talles chicos ni especiales.",
                "talle": talle
            }
    except ValueError:
        return {
            "valido": False,
            "mensaje": "No pude entender el talle. Por favor, ingresá un número entre el 35 y el 45.",
            "talle": None
        }
