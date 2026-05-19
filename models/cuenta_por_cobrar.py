class CuentaPorCobrar:
    def __init__(self, id_cuenta=None, id_movimiento_fk=None, numero_documento=None,
                 monto=0, id_venta_fk=None, pagado=False):
        self.id_cuenta = id_cuenta
        self.id_movimiento_fk = id_movimiento_fk
        self.numero_documento = numero_documento
        self.monto = monto
        self.id_venta_fk = id_venta_fk
        self.pagado = pagado

    def to_dict(self):
        return {
            'id_cuenta': self.id_cuenta,
            'id_movimiento_fk': self.id_movimiento_fk,
            'numero_documento': self.numero_documento,
            'monto': self.monto,
            'id_venta_fk': self.id_venta_fk,
            'pagado': self.pagado
        }

    @staticmethod
    def from_dict(data):
        return CuentaPorCobrar(
            id_cuenta=data.get('id_cuenta'),
            id_movimiento_fk=data.get('id_movimiento_fk'),
            numero_documento=data.get('numero_documento'),
            monto=data.get('monto', 0),
            id_venta_fk=data.get('id_venta_fk'),
            pagado=data.get('pagado', False)
        )

    def marcar_pagado(self):
        self.pagado = True

    def __str__(self):
        estado = "Pagado" if self.pagado else "Pendiente"
        return f"Cuenta {self.id_cuenta}: Q{self.monto} - {estado}"