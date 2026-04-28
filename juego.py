import tkinter as tk
import random
import time


# Creacion de la ventana "raiz"
root = tk.Tk()
root.geometry("1000x750+100+100") # Dimensiones de ventana, el +100+100 coloca la ventana 100 pixeles a la derecha y 100 pixeles abajo
root.resizable(0,0) # Evita cambiar la ventana de tamaño

# Variables para tener tamaños constantes
canvx = 900 # grosor
canvy = 750 # altura
# Creacion de un canvas para colocar los objetos dentro de el:
canvJuego = tk.Canvas(root,bg="#555555",width=canvx,height=canvy) # Se asignan los valores para las propiedades
canvJuego.pack() # Se coloca el canvas

p1 = canvJuego.create_rectangle(0,canvy,30,canvy-50,fill="red") # Se crea un rectangulo con las coordenadas dadas y de color rojo
# Coordenadas con .coords son 
# [0] = x0, 
# [1] = y0, 
# [2] = x1, 
# [3] = y1

bucle = [None] # Guarda el ID del after() para luego poder cancelar el bucle
saltando = [False] # Guarda el estado de salto
vely = [0] # velocidad en el eje y (no cambia la altura del salto desde acá)
velx = 10 # velocidad en el eje x (no se cambia mucho)

""" Debido a un bug con after() que causa que con tiempos muy pequeños, se actualiza correctamente solo cuando se mueve el mouse.
esto hace que se vea muy cortado y 'lageado'. entonces se toma el tiempo y se resta con la ultima vez que se tomo el tiempo y se
revisa si es mayor o igual a 16ms. A esto se le llama Delta time, y se usa de manera muy comun en videojuegos más avanzados y
en este caso arregla el problema de la funcion after()"""
ultimo_frame=[time.time()]

# Variables para ver si la tecla esta actualmente presionada
d_held = [False] # der
a_held = [False] # izq

# Al entrar una tecla, cambia la variable asociada a True, lo cual activa los bucles de movimiento.
# Esta manera de hacerlo evita errores y se puede trabajar más adelante

def presionar(evento, tecla):
    if tecla == "d":
        d_held[0] = True # Tecla d presionda
    elif tecla == "a": 
        a_held[0] = True # Tecla a presionada

    if bucle[0] == None: # Revisa si no hay bucles para no hacer un bucle infinito con after()
        mover()

# Si entra una tecla, cambia la variable a false, es decir suelta la tecla
def soltar(evento, tecla):
    if tecla == "d":
        d_held[0] = False # suelta d
    elif tecla == "a":
        a_held[0] = False # suelta a

def mover():

    # Coordenadas del jugador para revisar si se sale o no de la pantalla
    x0 = canvJuego.coords(p1)[0] 
    x1 = canvJuego.coords(p1)[2]
    ahora = time.time()
    dt = min(ahora - ultimo_frame[0], 0.016) #se limita el dt a 16ms o menos para no causar errores

    # Empieza a contar el tiempo para luego hacer la comparacion
    # Revisa si se mantiene el boton, y se esta dentro del marco del canvas
    if d_held[0] and x1 <= canvx:
        canvJuego.move(p1, velx * dt * 60, 0) # Al personaje (p1) se mueve a la derecha y 0 hacia arriba
    elif a_held[0] and x0 >= 0:
        canvJuego.move(p1, -velx * dt  * 60, 0) # Al personaje (p1) se mueve a la izq y 0 hacia arriba

    ultimo_frame[0] = ahora

    # Se hace el bucle para que sea consistente
    if d_held[0] or a_held[0]:
        bucle[0] = root.after(1,mover)
    else:
        bucle[0] = None  # los bucles se detienen para que el personaje se detenga


# La logica del salto es: si no esta en medio salto, añade velocidad vertical (para luego en gravedad mover el objeto)
# no se le añade deltatime porque no cambia mucho, ademas ya que el jugador saltaria moviendose usualmente y eso arregla el bug
def saltar(evento):
    # Revisa si no esta en el aire
    if not saltando[0]:
        saltando[0] = True 
        vely[0] = -20 # esta variable modifica la altura del salto
        gravedad()

# Cuando esta en el aire, su velocidad hacia arriba va bajando por 1 hasta llegar al piso
def gravedad():
    canvJuego.move(p1, 0, vely[0])  # Va moviendo el jugador verticalmente, empieza llendo para arriba, y va desacelerando 
    vely[0] += 1 # Aumenta la velocidad para abajo

    y2 = canvJuego.coords(p1)[3] # Coordenada de parte de abajo del personaje

    # revisa si choca con el piso, y para de mover hacia abajo
    if y2 >= canvy - 10:
        canvJuego.move(p1, 0, canvy - y2) # mueve el personaje al nivel piso para evitar que se quede pegado el jugador
        saltando[0] = False
        vely[0] = 0 # quita la velocidad
    else:
        root.after(18, gravedad) # bucle para el movimiento
    
""" Funciones un poco complicadas, lo que hacen es que detectan cada ingreso de la tecla y .bind() les asigna un evento.
para poder llamar otras funciones con otras variables, se hace un lambda con parametro evento para que pueda guardar lo que asigna
.bind() y ademas poder mandar ese evento mas las variables para el resto. Bueno asi creo que sirve pero puedo estar incorrecto""" 

# Teclas para movimiento

# presionar der
root.bind('<KeyPress-d>',   lambda e: presionar(e, "d")) 
root.bind('<KeyPress-Right>',   lambda e: presionar(e, "d")) 
# soltar der
root.bind('<KeyRelease-d>', lambda e: soltar(e, "d")) 
root.bind('<KeyRelease-Right>',   lambda e: soltar(e, "d")) 

# presionar izq
root.bind('<KeyPress-Left>',   lambda e: presionar(e, "a")) 
root.bind('<KeyPress-a>',   lambda e: presionar(e, "a")) 
# soltar izq
root.bind('<KeyRelease-a>', lambda e: soltar(e, "a")) 
root.bind('<KeyRelease-Left>', lambda e: soltar(e, "a")) 

# Teclas para salto
root.bind('<KeyPress-w>', saltar) # Prueba Se va a cabiar por el movimiento de escaleras
root.bind('<KeyPress-Up>',saltar) # Prueba
root.bind('<KeyPress-space>',saltar)


# Bucle de la ventana principal
root.mainloop()