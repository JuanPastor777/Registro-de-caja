def aperturaCaja():
    print("=== APERTURA DE CAJA ===")
    print("Ingrese la cantidad de billetes por denominación\n")

    total = 0

    billetes = {
        1: 0,
        5: 0,
        10: 0,
        20: 0,
        50: 0,
        100: 0,
        200: 0
    }

    for denominacion in billetes:
        cantidad = int(input(f"Billetes de Q{denominacion}: "))
        billetes[denominacion] = cantidad
        total += denominacion * cantidad

    print("\n--- RESUMEN ---")
    for d, c in billetes.items():
        print(f"Q{d} x {c} = Q{d*c}")

    print("----------------------")
    print(f"TOTAL EN CAJA: Q{total}")


# Ejecutar
aperturaCaja()