import tkinter as tk
import random

#Creacion de la ventana "raiz" y su geometria
root = tk.Tk()
root.geometry("500x500")

# Creacion de un canvas para colocar los objetos dentro de el:
canvJuego = tk.Canvas(root,bg="#555555",width=500,height=500) # Se asignan los valores para las propiedades
canvJuego.pack() # Se coloca el canvas


p1 = canvJuego.create_rectangle(0,500,30,470,fill="red") # Se crea un rectangulo con las coordenadas dadas y de color rojo
# Coordenadas con .coords son 
# [0] = x0, 
# [1] = y0, 
# [2] = x1, 
# [3] = y1

bucle = None # Guarda el ID del after() para luego poder cancelar el bucle
saltando = False # Guarda el estado de salto
vely = 0 # velocidad en el eje y
velx = 5 # velocidad en el eje x (no se cambia mucho)

def movimiento(evento,tecla):
    global bucle
    if tecla == "d" and bucle == None: # Se asegura de que no haya ningun bucle antes de llamar la funcion y que no se presione la otra tecla
        mvderecha()
    elif tecla == "a" and bucle == None:
        mvizquierda()
    else:
        root.after_cancel(bucle)
        bucle = None # Si no se presiona ninguna tecla, permite que se de el bucle otra vez

def mvderecha():
    global bucle # se usa global para poder guardar el bucle del movimiento
    canvJuego.move(p1,velx,0)
    bucle = root.after(16,mvderecha)

def mvizquierda():
    global bucle # Se usa el mismo bucle porque no se puede mover en ambas direcciones a la vez, y por simplicidad
    canvJuego.move(p1,-velx,0)
    bucle = root.after(16,mvizquierda)


""" Funciones un poco complicadas, lo que hacen es que detectan cada ingreso de la tecla y .bind() les asigna un evento,
para poder llamar otras funciones con otras variables, se hace un lambda con parametro evento para que pueda guardar lo que asigna
.bind() y ademas poder mandar ese evento mas las variables para el resto. Bueno asi creo que sirve pero puedo estar incorrecto""" 

# Teclas para el movimiento
root.bind('<KeyPress-d>', lambda evento: movimiento(evento, "d")) # d = derecha
root.bind('<KeyPress-a>', lambda evento: movimiento(evento, "a")) # a = izq

# Deteccion si se solto una tecla (hace el movimiento mas fluido)
root.bind('<KeyRelease-d>', lambda evento: movimiento(evento, "!d")) # !d = no derecha
root.bind('<KeyRelease-a>', lambda evento: movimiento(evento, "!a")) # !a = no izq


# Bucle de la ventana principal
root.mainloop()