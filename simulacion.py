from math import cos, radians, sin
from pathlib import Path
import argparse
import webbrowser
from lector import leer_angulos


def orientacion(roll, pitch, yaw):

    r, p, y = map(radians, (roll, pitch, yaw))
    cr, sr = cos(r), sin(r)
    cp, sp = cos(p), sin(p)
    cy, sy = cos(y), sin(y)
    eje_x = (cy * cp, sy * cp, -sp)
    eje_y = (cy * sp * sr - sy * cr, sy * sp * sr + cy * cr, cp * sr)
    return eje_x, eje_y


def main():
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument(
        "--sin-navegador", action="store_true",
        help="Muestra la dirección para abrirla manualmente en un navegador",
    )
    opciones = argumentos.parse_args()
    navegador = None if opciones.sin_navegador else webbrowser.get()

    class Lanzador:
        def open(self, url, new=0, autoraise=True):
            print(f"\nAbre esta dirección y deja la terminal funcionando:\n{url}\n", flush=True)
            if navegador is not None:
                return navegador.open(url, new=new, autoraise=autoraise)
            return True

    webbrowser.register("simulacion", None, Lanzador(), preferred=True)


    muestras = list(leer_angulos(Path(__file__).with_name("inercial.bin")))
    if not muestras:
        raise ValueError("El archivo no contiene muestras")
    print(f"hay: {len(muestras)} muestras.", flush=True)

    from vpython import box, button, canvas, color, compound, rate, slider, vector, wtext

    escena = canvas(
        title="Sensor BWT901CL — reproducción 3D\n",
        width=1000, height=650, background=vector(0.07, 0.09, 0.13),
        up=vector(0, 0, 1), forward=vector(-1.5, 1, -0.8),
        center=vector(0, 0, -0.3), range=3.5,
    )
    print("Escena creada. Preparando el cubo…", flush=True)
    box(pos=vector(0, 0, -1.5), size=vector(6, 6, 0.06), color=color.blue)
    sensor = compound([
        box(size=vector(1.4, 1, 0.8), color=color.red),
        box(size=vector(2.6, 0.035, 0.035), color=color.cyan),
        box(size=vector(0.035, 2.6, 0.035), color=color.green),
        box(size=vector(0.035, 0.035, 2.6), color=color.yellow),
    ], origin=vector(0, 0, 0))

    indice = 0
    reproduciendo = True
    frecuencia = 30

    def mostrar():
        roll, pitch, yaw = muestras[indice]
        eje_x, eje_y = orientacion(roll, pitch, yaw)
        sensor.axis = vector(*eje_x)
        sensor.up = vector(*eje_y)
        lectura.text = (
            f"Muestra {indice + 1}/{len(muestras)} | "
            f"Roll: {roll:.2f}° | Pitch: {pitch:.2f}° | Yaw: {yaw:.2f}°"
        )

    def alternar(boton):
        nonlocal reproduciendo, indice
        if not reproduciendo and indice == len(muestras) - 1:
            indice = 0
            mostrar()
        reproduciendo = not reproduciendo
        boton.text = "Pausar" if reproduciendo else "Continuar"

    def reiniciar(_):
        nonlocal indice, reproduciendo
        indice = 0
        reproduciendo = True
        pausa.text = "Pausar"
        mostrar()

    def cambiar_velocidad(control):
        nonlocal frecuencia
        frecuencia = int(control.value)
        velocidad.text = f" {frecuencia} muestras/s"

    escena.append_to_caption("\nEjes del sensor: X cian · Y verde · Z amarillo\n\n")
    pausa = button(text="Pausar", bind=alternar)
    button(text="Reiniciar", bind=reiniciar)
    escena.append_to_caption("\n\nVelocidad de reproducción: ")
    slider(min=1, max=60, step=1, value=frecuencia, bind=cambiar_velocidad)
    velocidad = wtext(text=f" {frecuencia} muestras/s")
    escena.append_to_caption("\nLa frecuencia original no está indicada en el archivo.\n\n")
    lectura = wtext(text="")
    mostrar()
    print("Cubo preparado. Reproducción iniciada.", flush=True)

    while True:
        rate(frecuencia)
        if reproduciendo:
            if indice < len(muestras) - 1:
                indice += 1
                mostrar()
            else:
                reproduciendo = False
                pausa.text = "Reproducir de nuevo"


if __name__ == "__main__":
    main()
