# models/apartado.py
from datetime import date
from typing import Optional


class Apartado:
    """Modelo de apartado con todos los campos de la BD"""
    
    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_COMPLETADO = 'COMPLETADO'
    ESTADO_CANCELADO = 'CANCELADO'
    
    def __init__(
        self,
        id_apartado: Optional[int] = None,
        id_cliente_fk: Optional[int] = None,
        id_producto_fk: Optional[int] = None,
        total_producto: float = 0,
        fecha_inicio: Optional[date] = None,
        estado: str = ESTADO_ACTIVO,
        monto_original: float = 0,
        descuento_pactado: float = 0,
        monto_final: float = 0,
        es_envio: bool = False,
        id_empresa_fk: Optional[int] = None,
        numero_guia: Optional[str] = None,
        forma_pago_acordada: Optional[str] = None,
        incremento_pactado: float = 0
    ):
        self.id_apartado = id_apartado
        self.id_cliente_fk = id_cliente_fk
        self.id_producto_fk = id_producto_fk
        self.total_producto = total_producto
        self.fecha_inicio = fecha_inicio or date.today()
        self.estado = estado
        self.monto_original = monto_original
        self.descuento_pactado = descuento_pactado
        self.monto_final = monto_final
        self.es_envio = es_envio
        self.id_empresa_fk = id_empresa_fk
        self.numero_guia = numero_guia
        self.forma_pago_acordada = forma_pago_acordada
        self.incremento_pactado = incremento_pactado
    
    def calcular_monto_final(self) -> float:
        """Calcula: monto_original - descuento_pactado + incremento_pactado"""
        self.monto_final = self.monto_original - self.descuento_pactado + self.incremento_pactado
        if self.total_producto == 0:
            self.total_producto = self.monto_final
        return max(self.monto_final, 0)
    
    def to_dict(self) -> dict:
        return {
            'id_apartado': self.id_apartado,
            'id_cliente_fk': self.id_cliente_fk,
            'id_producto_fk': self.id_producto_fk,
            'total_producto': self.total_producto,
            'fecha_inicio': self.fecha_inicio,
            'estado': self.estado,
            'monto_original': self.monto_original,
            'descuento_pactado': self.descuento_pactado,
            'monto_final': self.monto_final,
            'es_envio': self.es_envio,
            'id_empresa_fk': self.id_empresa_fk,
            'numero_guia': self.numero_guia,
            'forma_pago_acordada': self.forma_pago_acordada,
            'incremento_pactado': self.incremento_pactado
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Apartado':
        return Apartado(
            id_apartado=data.get('id_apartado'),
            id_cliente_fk=data.get('id_cliente_fk'),
            id_producto_fk=data.get('id_producto_fk'),
            total_producto=data.get('total_producto', 0),
            fecha_inicio=data.get('fecha_inicio'),
            estado=data.get('estado', Apartado.ESTADO_ACTIVO),
            monto_original=data.get('monto_original', 0),
            descuento_pactado=data.get('descuento_pactado', 0),
            monto_final=data.get('monto_final', 0),
            es_envio=data.get('es_envio', False),
            id_empresa_fk=data.get('id_empresa_fk'),
            numero_guia=data.get('numero_guia'),
            forma_pago_acordada=data.get('forma_pago_acordada'),
            incremento_pactado=data.get('incremento_pactado', 0)
        )