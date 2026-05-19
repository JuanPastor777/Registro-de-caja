from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils.tiempo import ahora_local


class AperturaCierre:
    def __init__(self, id_apertura=None, id_caja_fk=None, id_usuario_fk=None,
                 fecha_hora_apertura=None, monto_inicial=0,
                 fecha_hora_cierre=None, monto_final=None):
        self.id_apertura = id_apertura
        self.id_caja_fk = id_caja_fk
        self.id_usuario_fk = id_usuario_fk
        # Usar ahora_local() en lugar de datetime.now()
        self.fecha_hora_apertura = fecha_hora_apertura or ahora_local()
        self.monto_inicial = monto_inicial
        self.fecha_hora_cierre = fecha_hora_cierre
        self.monto_final = monto_final

    def to_dict(self):
        return {
            'id_apertura': self.id_apertura,
            'id_caja_fk': self.id_caja_fk,
            'id_usuario_fk': self.id_usuario_fk,
            'fecha_hora_apertura': self.fecha_hora_apertura,
            'monto_inicial': self.monto_inicial,
            'fecha_hora_cierre': self.fecha_hora_cierre,
            'monto_final': self.monto_final
        }

    @staticmethod
    def from_dict(data):
        return AperturaCierre(
            id_apertura=data.get('id_apertura'),
            id_caja_fk=data.get('id_caja_fk'),
            id_usuario_fk=data.get('id_usuario_fk'),
            fecha_hora_apertura=data.get('fecha_hora_apertura'),
            monto_inicial=data.get('monto_inicial', 0),
            fecha_hora_cierre=data.get('fecha_hora_cierre'),
            monto_final=data.get('monto_final')
        )

    def cerrar(self, monto_final):
        self.fecha_hora_cierre = ahora_local()
        self.monto_final = monto_final

    def esta_abierta(self):
        return self.fecha_hora_cierre is None

    def __str__(self):
        estado = "Abierta" if self.esta_abierta() else "Cerrada"
        return f"Apertura {self.id_apertura} - {estado}"