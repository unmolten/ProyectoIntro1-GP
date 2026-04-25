import tkinter as tk
import random


#Creacion de la ventana "raiz" y su geometria
root = tk.Tk()
root.geometry("1000x750")
root.resizable(0,0)

# Variables para tener tamaños constantes
canvx = 990 # grosor
canvy = 740 # altura

# Creacion de un canvas para colocar los objetos dentro de el:
canvJuego = tk.Canvas(root,bg="#555555",width=canvx,height=canvy) # Se asignan los valores para las propiedades
canvJuego.pack() # Se coloca el canvas

p1 = canvJuego.create_rectangle(0,canvy,30,canvy-30,fill="red") # Se crea un rectangulo con las coordenadas dadas y de color rojo
# Coordenadas con .coords son 
# [0] = x0, 
# [1] = y0, 
# [2] = x1, 
# [3] = y1

bucle = None # Guarda el ID del after() para luego poder cancelar el bucle
saltando = False # Guarda el estado de salto
vely = 0 # velocidad en el eje y (no cambia la altura del salto desde acá)
velx = 10 # velocidad en el eje x (no se cambia mucho)


# Variables para ver si la tecla esta actualmente presionada
d_held = False # der
a_held = False # izq

# Al entrar una tecla, cambia la variable asociada a True, lo cual activa los bucles de movimiento.
# Esta manera de hacerlo evita errores y se puede trabajar más adelante

def presionar(evento, tecla):
    global d_held, a_held, bucle # se hacen globales las variables para poder modificarlas facilmente y porque se usan en varias funciones
    if tecla == "d": 
        d_held = True # Tecla d presionda
    elif tecla == "a": 
        a_held = True # Tecla a presionada

    if bucle == None: # Revisa si no hay bucles para no hacer un bucle infinito con after()
        mover()

# Si entra una tecla, cambia la variable a false, es decir suelta la tecla
def soltar(evento, tecla):
    global d_held, a_held
    if tecla == "d":
        d_held = False # suelta d
    elif tecla == "a":
        a_held = False # suelta a

def mover():
    global bucle
    # Coordenadas del jugador para revisar si se sale o no de la pantalla
    x0 = canvJuego.coords(p1)[0] 
    x1 = canvJuego.coords(p1)[2]

    if d_held and x1 <= canvx:
        canvJuego.move(p1, velx, 0) # Al personaje (p1) se mueve a la derecha y 0 hacia arriba
        bucle = root.after(16, mover) # hace el bucle cada 16ms
    elif a_held and x0 >= 0:
        canvJuego.move(p1, -velx, 0) # Al personaje (p1) se mueve a la izq y 0 hacia arriba
        bucle = root.after(16, mover)# bucle cada 16ms
    else:
        bucle = None  # los bucles se detienen para que el personaje se detenga

# La logica del salto es: si no esta en medio salto, añade velocidad vertical (para luego en gravedad mover el objeto)
def saltar(evento):
    global saltando, vel_y
    # Revisa si no esta en el aire
    if not saltando:
        saltando = True 
        vel_y = -20 # esta variable modifica la altura del salto
        gravedad()

# Cuando esta en el aire, su velocidad hacia arriba va bajando por 1 hasta llegar al piso
def gravedad():
    global saltando, vel_y
    canvJuego.move(p1, 0, vel_y)  # Va moviendo el jugador verticalmente, empieza llendo para arriba, y va desacelerando 
    vel_y += 1 # Aumenta la velocidad para abajo

    y2 = canvJuego.coords(p1)[3] # Coordenada de parte de abajo del personaje
    # revisa si choca con el piso, y para de mover hacia abajo
    if y2 >= canvy:
        canvJuego.move(p1, 0, canvy - y2) # mueve el personaje al nivel piso para evitar que se quede pegado el jugador
        saltando = False
        vel_y = 0 # quita la velocidad
    else:
        root.after(16, gravedad) # bucle para el movimiento

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