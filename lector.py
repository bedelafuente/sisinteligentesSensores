"""Lee los ángulos grabados del sensor BWT901CL."""

import ctypes as ct
from pathlib import Path


class Trama(ct.Structure):
    """Los once bytes de un paquete del sensor."""

    _fields_ = [(f"B{i}", ct.c_ubyte) for i in range(11)]


def convertir_angulo(bajo, alto):
    """Une los bytes, interpreta el signo y convierte a grados."""
    valor = ct.c_int16((alto << 8) | bajo).value
    return valor / 32768 * 180


def leer_angulos(ruta):
    """Entrega una tupla (roll, pitch, yaw) por paquete válido."""
    with open(ruta, "rb") as archivo:
        numero = 0
        while True:
            datos = archivo.read(ct.sizeof(Trama))
            if not datos:
                break

            numero += 1
            if len(datos) != 11:
                raise ValueError(f"Paquete {numero}: incompleto")
            if datos[:2] != b"\x55\x53":
                raise ValueError(f"Paquete {numero}: cabecera inesperada")
            if (sum(datos[:10]) & 0xFF) != datos[10]:
                raise ValueError(f"Paquete {numero}: checksum incorrecto")

            trama = Trama.from_buffer_copy(datos)
            yield (
                convertir_angulo(trama.B2, trama.B3),
                convertir_angulo(trama.B4, trama.B5),
                convertir_angulo(trama.B6, trama.B7),
            )


if __name__ == "__main__":
    ruta = Path(__file__).with_name("inercial.bin")
    total = 0
    for total, (roll, pitch, yaw) in enumerate(leer_angulos(ruta), start=1):
        print(
            f"{total:03d} | Roll: {roll:8.2f}° | "
            f"Pitch: {pitch:8.2f}° | Yaw: {yaw:8.2f}°"
        )
    print(f"\nPaquetes válidos: {total}")
