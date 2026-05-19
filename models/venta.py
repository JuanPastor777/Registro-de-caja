class Venta:
    FORMA_EFECTIVO = 'EF'
    FORMA_TARJETA = 'TC/TD'
    FORMA_TRANSFERENCIA = 'TF'
    FORMA_DEPOSITO = 'DP'
    FORMA_ENVIO = 'COD'

    def __init__(self, id_venta=None, id_movimiento_fk=None, id_cliente_fk=None,
                 numero_documento=None, forma_pago=None, total=0,
                 es_envio=False, id_empresa_fk=None, numero_guia=None):
        self.id_venta = id_venta
        self.id_movimiento_fk = id_movimiento_fk
        self.id_cliente_fk = id_cliente_fk
        self.numero_documento = numero_documento
        self.forma_pago = forma_pago
        self.total = total
        self.es_envio = es_envio
        self.id_empresa_fk = id_empresa_fk
        self.numero_guia = numero_guia

    def to_dict(self):
        return {
            'id_venta': self.id_venta,
            'id_movimiento_fk': self.id_movimiento_fk,
            'id_cliente_fk': self.id_cliente_fk,
            'numero_documento': self.numero_documento,
            'forma_pago': self.forma_pago,
            'total': self.total,
            'es_envio': self.es_envio,
            'id_empresa_fk': self.id_empresa_fk,
            'numero_guia': self.numero_guia
        }

    @staticmethod
    def from_dict(data):
        return Venta(
            id_venta=data.get('id_venta'),
            id_movimiento_fk=data.get('id_movimiento_fk'),
            id_cliente_fk=data.get('id_cliente_fk'),
            numero_documento=data.get('numero_documento'),
            forma_pago=data.get('forma_pago'),
            total=data.get('total', 0),
            es_envio=data.get('es_envio', False),
            id_empresa_fk=data.get('id_empresa_fk'),
            numero_guia=data.get('numero_guia')
        )

    def __str__(self):
        return f"Venta {self.numero_documento} - Q{self.total}"