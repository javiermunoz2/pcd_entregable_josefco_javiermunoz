# test_invernadero.py

import pytest
from unittest.mock import MagicMock
from codigo_entregable import (
    Invernadero, GestionDatos, Media, Mediana, DesviacionTipica,
    Estadisticos, Umbral, CambioDrastico, Estrategia
)

@pytest.fixture
def setup_invernadero():
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

    return invernadero, gestor, estadisticos

def test_adjuntar_observador(setup_invernadero):
    invernadero, gestor, _ = setup_invernadero
    assert len(invernadero._observadores) == 1

def test_notificar_observador(setup_invernadero):
    invernadero, gestor, _ = setup_invernadero
    gestor.actualizar = MagicMock()
    estado = ('2023-01-01 12:00:00', 25.0)
    invernadero.notificar(estado)
    gestor.actualizar.assert_called_once_with(estado)

def test_media_estrategia():
    estrategia = Media()
    datos = [1, 2, 3, 4, 5]
    resultado = estrategia.realizar_algoritmo(datos)
    assert resultado == 3

def test_mediana_estrategia():
    estrategia = Mediana()
    datos = [1, 2, 3, 4, 5]
    resultado = estrategia.realizar_algoritmo(datos)
    assert resultado == 3

def test_desviacion_tipica_estrategia():
    estrategia = DesviacionTipica()
    datos = [1, 2, 3, 4, 5]
    resultado = estrategia.realizar_algoritmo(datos)
    assert round(resultado, 2) == 1.41

def test_manejador_umbral(setup_invernadero):
    _, gestor, estadisticos = setup_invernadero
    datos = [1, 2, 3, 15]
    datos_30 = []
    umbral = Umbral()
    resultado = umbral.manejar(datos, datos_30, False)
    assert resultado is None  # Ya que no hay manejador siguiente en el test

def test_manejador_cambio_drastico(setup_invernadero):
    _, gestor, estadisticos = setup_invernadero
    datos = [1, 2, 3, 15]
    datos_30 = [1, 12, 5, 15]
    cambio_drastico = CambioDrastico()
    resultado = cambio_drastico.manejar(datos, datos_30, True)
    assert resultado is None  # Ya que no hay manejador siguiente en el test

def test_gestion_datos_actualizar(setup_invernadero):
    _, gestor, estadisticos = setup_invernadero
    estado = ('2023-01-01 12:00:00', 25.0)
    gestor.actualizar(estado)
    assert len(gestor._datos) == 1
    assert gestor._datos[0] == 25.0

def test_estadisticos_manejar(setup_invernadero):
    _, gestor, estadisticos = setup_invernadero
    datos = [1, 2, 3, 4, 5]
    datos_30 = [1, 2, 3]
    resultado = estadisticos.manejar(datos, datos_30, False)
    assert resultado is None  # Ya que el siguiente manejador no está definido en el test
