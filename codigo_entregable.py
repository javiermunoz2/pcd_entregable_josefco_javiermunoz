from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
import random
import time
import asyncio

# Generador de datos simulados
async def generador_sensor_datos():
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        temperatura = random.uniform(0, 50)
        yield timestamp, temperatura
        await asyncio.sleep(5)  

class Sujeto(ABC):
    @abstractmethod
    def adjuntar(self, observador: Observador) -> None:
        pass

    @abstractmethod
    def desadjuntar(self, observador: Observador) -> None:
        pass

    @abstractmethod
    def notificar(self, estado) -> None:
        pass

class Observador(ABC):
    @abstractmethod
    def actualizar(self, estado) -> None:
        pass

class GestionDatos(Observador):
    _instancia_unica = None

    def obtener_instancia(cls):
        if cls._instancia_unica is None:
            cls._instancia_unica = cls()
        return cls._instancia_unica

    def __init__(self):
        self.nombre = "Gestor 1"
        self._datos = []
        self._datos_30 = []
        self._estrategia = None
        self._inicio = None

    def actualizar(self, estado) -> None:
        control_ejecucion = False  # Inicializamos control_ejecucion aquí
        if len(self._datos_30) == 0:
            self._inicio = time.time()
            self._datos_30.append(estado[1])
        else:
            self._datos_30.append(estado[1])
            if time.time() - self._inicio >= 30:
                control_ejecucion = True
            
        print(f"{self.nombre}: He recibido la notificación del estado actual del invernadero: {estado}")
        self._datos.append(estado[1])
        print(f"{self.nombre}: Ordenando pasos encadenados")
        print(f"datos totales: {self._datos}")
        print(f"datos últimos 30 segundos: {self._datos_30}")
        self._manejador.manejar(self._datos, self._datos_30, control_ejecucion)
        if control_ejecucion:
            self._datos_30 = []


class Invernadero(Sujeto):
    def __init__(self):
        self._observadores: List[Observador] = []

    def adjuntar(self, observador: Observador) -> None:
        print("Invernadero: Se adjuntó un observador.")
        self._observadores.append(observador)

    def desadjuntar(self, observador: Observador) -> None:
        self._observadores.remove(observador)

    def notificar(self, estado) -> None:
        print("Invernadero: Notificando a los observadores...")
        for observador in self._observadores:
            observador.actualizar(estado)

    async def iniciar_sensor(self):
        print("Invernadero: Comienzo a tomar datos del sensor")
        async for dato in generador_sensor_datos():
            self.modificar_estado(dato)

    def modificar_estado(self, estado):
        print("\nInvernadero: Acabo de cambiar de estado.")
        self.notificar(estado)

class Manejador(ABC):
    @abstractmethod
    def establecer_siguiente(self, manejador: Manejador) -> Manejador:
        pass

    @abstractmethod
    def manejar(self, datos: List, datos_30: List, control: bool) -> Optional[str]:
        pass

class Estadisticos(Manejador):
    def __init__(self, estrategia: Estrategia) -> None:
        self._estrategia = estrategia

    def establecer_siguiente(self, manejador: Manejador) -> Manejador:
        self._siguiente_manejador = manejador
        return manejador

    def manejar(self, datos: List, datos_30: List, control: bool) -> str:
        print("Estadistico de la temperatura según la estrategia establecida:")
        resultado = self._estrategia.realizar_algoritmo(datos)
        if isinstance(self._estrategia, Media):
            print(f"Cálculo de la media: {resultado}")
        elif isinstance(self._estrategia, Mediana):
            print(f"Cálculo de la mediana: {resultado}")
        else:
            print(f"Cálculo de la desviación típica: {resultado}")
        return self._siguiente_manejador.manejar(datos, datos_30, control)




class ManejadorAbstracto(Manejador):
    _siguiente_manejador: Manejador = None

    def establecer_siguiente(self, manejador: Manejador) -> Manejador:
        self._siguiente_manejador = manejador
        return manejador

    def manejar(self, datos: List, datos_30: List, control: bool) -> Optional[str]:
        if self._siguiente_manejador:
            return self._siguiente_manejador.manejar(datos, datos_30, control)
        return None

class Estrategia(ABC):
    @abstractmethod
    def realizar_algoritmo(self, datos: List) :
        pass

class Media(Estrategia):
    def realizar_algoritmo(self, datos: List) -> float:
        return sum(datos) / len(datos)

class Mediana(Estrategia):
    def realizar_algoritmo(self, datos: List) -> float:
        datos_ordenados = sorted(datos)
        n = len(datos_ordenados)
        if n % 2 == 0:
            return (datos_ordenados[n // 2 - 1] + datos_ordenados[n // 2]) / 2
        else:
            return datos_ordenados[n // 2]

class DesviacionTipica(Estrategia):
    def realizar_algoritmo(self, datos: List) -> float:
        media = Media().realizar_algoritmo(datos)
        varianza = sum((x - media) ** 2 for x in datos) / len(datos)
        return varianza ** 0.5

class Umbral(ManejadorAbstracto):
    def manejar(self, datos: List, datos_30: List, control: bool) -> str:
        umbral = 10
        print(f"La temperatura {datos[-1]} excede del umbral {umbral}: {datos[-1] > umbral}")
        return super().manejar(datos, datos_30, control)

class CambioDrastico(ManejadorAbstracto):
    def manejar(self, datos: List, datos_30: List, control: bool) -> str:
        if control:
            resultados = self.comprobar_cambio_drastico(datos_30, 10)
            print("Comprobamos si durante los últimos 30 segs la temperatura ha aumentado en más de 10º")
            print(f"{resultados}")
        return super().manejar(datos, datos_30, control)

    def comprobar_cambio_drastico(self, datos_30: List, umbral: int) -> List[tuple]:
        return [(datos_30[i], datos_30[i+1] - datos_30[i] > umbral) for i in range(len(datos_30) - 1)]

async def main():
    invernadero = Invernadero()
    gestor = GestionDatos()
    invernadero.adjuntar(gestor)

    estrategia_media = Media()
    estrategia_mediana = Mediana()
    estrategia_desviacion_tipica = DesviacionTipica()

    estadisticos = Estadisticos(estrategia_media)
    umbral = Umbral()
    cambio_drastico = CambioDrastico()
    estadisticos.establecer_siguiente(umbral).establecer_siguiente(cambio_drastico)

    gestor._manejador = estadisticos

    async def cambiar_estrategia(estadisticos):
        while True:
            estrategia = random.choice([estrategia_media, estrategia_mediana, estrategia_desviacion_tipica])
            print(f"\n**Cambio de estrategia**: {type(estrategia).__name__}\n")
            estadisticos.estrategia = estrategia
            estadisticos._estrategia = estrategia  # Aquí se actualiza la estrategia utilizada en manejar
            await asyncio.sleep(30)


    asyncio.create_task(cambiar_estrategia(estadisticos))
    await invernadero.iniciar_sensor()

asyncio.run(main())
