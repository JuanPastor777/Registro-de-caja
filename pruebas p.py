# Clase Cliente
class Cliente:
    def __init__(self, nombre, apellido, telefono=""):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__telefono = telefono

    # Getters
    def get_nombre(self):
        return self.__nombre

    def get_apellido(self):
        return self.__apellido

    def get_telefono(self):
        return self.__telefono

    # Setters
    def set_nombre(self, nombre):
        self.__nombre = nombre

    def set_apellido(self, apellido):
        self.__apellido = apellido

    def set_telefono(self, telefono):
        self.__telefono = telefono

    # Mostrar datos
    def mostrar_cliente(self):
        print("\n--- DATOS DEL CLIENTE ---")
        print("Nombre:", self.__nombre)
        print("Apellido:", self.__apellido)
        print("Teléfono:", self.__telefono)


# Clase Producto
class Producto:
    def __init__(self, nombre, marca, modelo, descripcion):
        self.__nombre = nombre
        self.__marca = marca
        self.__modelo = modelo
        self.__descripcion = descripcion

    # Getters
    def get_nombre(self):
        return self.__nombre

    def get_marca(self):
        return self.__marca

    def get_modelo(self):
        return self.__modelo

    def get_descripcion(self):
        return self.__descripcion

    # Setters
    def set_nombre(self, nombre):
        self.__nombre = nombre

    def set_marca(self, marca):
        self.__marca = marca

    def set_modelo(self, modelo):
        self.__modelo = modelo

    def set_descripcion(self, descripcion):
        self.__descripcion = descripcion

    # Mostrar datos
    def mostrar_producto(self):
        print("\n--- DATOS DEL PRODUCTO ---")
        print("Nombre:", self.__nombre)
        print("Marca:", self.__marca)
        print("Modelo:", self.__modelo)
        print("Descripción:", self.__descripcion)


# Registro Cliente
print("REGISTRO DE CLIENTE ")
nombre = input("Ingrese nombre: ")
apellido = input("Ingrese apellido: ")
telefono = input("Ingrese teléfono (opcional): ")

cliente1 = Cliente(nombre, apellido, telefono)

# Registro Producto
print("\nREGISTRO DE PRODUCTO ")
nombre_producto = input("Ingrese nombre del producto: ")
marca = input("Ingrese marca: ")
modelo = input("Ingrese modelo: ")
descripcion = input("Ingrese descripción: ")

producto1 = Producto(nombre_producto, marca, modelo, descripcion)

# Mostrar nuevamente al finalizar
print("\n      DATOS INGRESADOS")

cliente1.mostrar_cliente()
producto1.mostrar_producto()