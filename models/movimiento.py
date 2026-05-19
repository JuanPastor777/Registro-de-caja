from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.tiempo import ahora_local


class MovimientoCaja:
    TIPO_INGRESO = 'INGRESO'
    TIPO_EGRESO = 'EGRESO'

    def __init__(self, id_movimiento=None, id_caja_fk=None, tipo_movimiento=None,
                 descripcion=None, monto=0, fecha_hora=None, id_usuario_fk=None):
        self.id_movimiento = id_movimiento
        self.id_caja_fk = id_caja_fk
        self.tipo_movimiento = tipo_movimiento
        self.descripcion = descripcion
        self.monto = monto
        # Usar ahora_local() en lugar de datetime.now()
        self.fecha_hora = fecha_hora or ahora_local()
        self.id_usuario_fk = id_usuario_fk

    def to_dict(self):
        return {
            'id_movimiento': self.id_movimiento,
            'id_caja_fk': self.id_caja_fk,
            'tipo_movimiento': self.tipo_movimiento,
            'descripcion': self.descripcion,
            'monto': self.monto,
            'fecha_hora': self.fecha_hora,
            'id_usuario_fk': self.id_usuario_fk
        }

    @staticmethod
    def from_dict(data):
        return MovimientoCaja(
            id_movimiento=data.get('id_movimiento'),
            id_caja_fk=data.get('id_caja_fk'),
            tipo_movimiento=data.get('tipo_movimiento'),
            descripcion=data.get('descripcion'),
            monto=data.get('monto', 0),
            fecha_hora=data.get('fecha_hora'),
            id_usuario_fk=data.get('id_usuario_fk')
        )

    def es_ingreso(self):
        return self.tipo_movimiento == self.TIPO_INGRESO

    def es_egreso(self):
        return self.tipo_movimiento == self.TIPO_EGRESO

    def __str__(self):
        return f"Movimiento {self.id_movimiento} - {self.tipo_movimiento}: Q{self.monto}"