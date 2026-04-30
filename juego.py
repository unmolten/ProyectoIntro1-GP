import tkinter as tk
import random
import time

# Ventana principal
root = tk.Tk()
root.geometry("1000x800+100+100")
root.resizable(0,0)

# Tamaño del canvas
canvx = 900
canvy = 750

# Canvas
canvJuego = tk.Canvas(root,bg="#555555",width=canvx,height=canvy)
canvJuego.pack(side="top")

# Jugador
p1 = canvJuego.create_rectangle(0,canvy,30,canvy-50,fill="red")


# Variables
bucles = [None,None] # Se guardan los id de los bucles para luego cancelarlos con un None
saltando = [False] # Estado de salto
ultimo_frame= [time.time()] # Tiempo desde la ultima llamada para el delta time (ver documentación)
cajasmapa = [[]] # Se guardan los id de las cajas del mapa
vely = [0] # Velocidad vertical
velx = 12 # Velocidad horizontal (no cambia)



# Indicadores si la tecla esta siendo presionada. 
d_held = [False]
a_held = [False]

# --- INPUT ---
def presionar(evento, tecla):
    if tecla == "d":
        d_held[0] = True # Si recive la tecla d indica que esta siendo mantenida
    elif tecla == "a": 
        a_held[0] = True # Igual aca

    if bucles[0] == None: # Ademas revisa si no hay bucles previos para llamar la funcion de movimiento
        mover()

# "Suelta" la tecla presionada
def soltar(evento, tecla):
    if tecla == "d":
        d_held[0] = False 
    elif tecla == "a":
        a_held[0] = False

# --- MOVIMIENTO ---

# Funcion de movimiento horizontal.
def mover():
    # Coordenadas del jugador
    x0 = canvJuego.coords(p1)[0] 
    x1 = canvJuego.coords(p1)[2]
    
    # Calculos para el delta time
    ahora = time.time()
    dt = min(ahora - ultimo_frame[0], 0.016)
    ultimo_frame[0] = ahora

    # Indicadores con que lado se dio una colision para no poder moverse a ese lado
    colx_der = False
    colx_izq = False

    # Revisar colisiones por cada caja que hay en el mapa
    for i in range(len(cajasmapa[0])):
        # Originalmente se llamaba colision(cajasmapa[0][i]) y se le daba el indice pero esto lo hace mas limpio
        col = colision(cajasmapa[0][i])
        tag = canvJuego.gettags(cajasmapa[0][i]) # Revisa los tags de la caja para ver si es una escalera
        # Revisa si esta chocando horizontalmente [0] y si choca en un y un poco mas alto para que no se quede pegado
        if col[0] and col[2] and tag[0] != "Escalera": 
            # Consigue las cordenadas si hay una colison
            x0caja = canvJuego.coords(cajasmapa[0][i])[0]
            x1caja = canvJuego.coords(cajasmapa[0][i])[2]

            # Si chocha el lado derecho
            if x0 <= x0caja:
                colx_der = True
                canvJuego.move(p1, x0caja - x1, 0) # Se mueve al borde para que no este dentro
            # Si choca con el lado izq
            else:
                colx_izq = True
                canvJuego.move(p1, x1caja - x0, 0) # Igual al borde

    # Si se mantiene la tecla, esta en los margenes de la ventana, y no hay colision, se puede mover
    if d_held[0] and x1 <= canvx and not colx_der:
        canvJuego.move(p1, velx * dt * 60, 0)
    elif a_held[0] and x0 >= 0 and not colx_izq:
        canvJuego.move(p1, -velx * dt  * 60, 0)

    # Se llama la gravedad desde aca para asegurarse de que tenga gravedad cuando camina fuera de una caja
    if not saltando[0] and not en_piso() and bucles[1] is None:
        saltando[0] = True
        gravedad()
    
    # Bucle del movimiento.
    if d_held[0] or a_held[0]:
        bucles[0] = root.after(1,mover)
    else:
        bucles[0] = None # Si no se presiona ninguna tecla, se cancela el bucle

# --- SALTO ---

def saltar(evento):
    if not saltando[0]:
        saltando[0] = True 
        vely[0] = -17 # Asocia la altura del salto basicamente
        gravedad()

# --- GRAVEDAD ---d 

# Logica de gravedad, funcion un poco compleja y rara pero sirve. 
def gravedad():
    vely_anterior = vely[0]  # Guarda la velocidad antes de modificar para saber de donde venia el jugador
    canvJuego.move(p1, 0, vely[0])
    vely[0] += 1  # Aumenta la velocidad para abajo (gravedad)

    # Coordenadas verticales del jugador
    y0 = canvJuego.coords(p1)[1]
    y1 = canvJuego.coords(p1)[3]

    # Revision de colisiones con las cajas
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i])
        tag = canvJuego.gettags(cajasmapa[0][i])
        if col[0] and col[1] and tag[0] != "Escalera":
            y0caja = canvJuego.coords(cajasmapa[0][i])[1]  # lado arriba de la caja
            y1caja = canvJuego.coords(cajasmapa[0][i])[3]  # abajo de la caja

            # Si cae y el jugador esta en la parte de arriba de la caja
            if vely_anterior >= 0 and y1 >= y0caja and y1 <= y0caja + vely_anterior + 5:
                canvJuego.move(p1, 0, y0caja - y1)  # corrige posicion al borde
                saltando[0] = False
                vely[0] = 0
                bucles[1] = None
                return 0  # sale de la funcion para no seguir con el bucle

            # Si sube y la cabeza esta en el rango del fondo de la caja
            elif vely_anterior < 0 and y0 <= y1caja and y0 >= y1caja + vely_anterior - 5:
                canvJuego.move(p1, 0, y1caja - y0)  # empuja hacia abajo de la caja
                saltando[0] = True  # sigue en el aire
                vely[0] = 1  # empieza a caer

    # Colision con el piso de la ventana
    if y1 >= canvy - 10:
        canvJuego.move(p1, 0, canvy - y1)  # corrige al borde del piso
        saltando[0] = False
        vely[0] = 0
        bucles[1] = None
    else:
        bucles[1] = root.after(17, gravedad)  # sigue el bucle si no esta en el piso

# --- COLISIONES ---

# Revisa si esta apoyado en una plataforma o en el piso
def en_piso():
    # "pies" del personaje
    y1 = canvJuego.coords(p1)[3]

    # Piso de la ventana
    if y1 >= canvy - 10:
        return True
    
    # Revisa para las cajas
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i])
        tag = canvJuego.gettags(cajasmapa[0][i])
        if col[1] and col[3] and  tag[0] != "Escalera": # [1] (vertical) y [3] (x pero mas pequeño) y escalera
        
            return True
        
    # Si no hay nada, returna false
    return False

# Sistema de colision con las cajas (originalmente se trato de usar canvas.find_overlapping() pero entre mas elementos habian
# retornaba una tupla muy confusa.)
def colision(caja): 
    
    # Variables para las colisiones
    colx = False
    coly = False
    adentroy = False
    adentrox = False

    # Coordenadas jugador
    x0 = canvJuego.coords(p1)[0] 
    y0 = canvJuego.coords(p1)[1] 
    x1 = canvJuego.coords(p1)[2]
    y1 = canvJuego.coords(p1)[3]

    # Coordenadas caja
    x0caja = canvJuego.coords(caja)[0]
    y0caja =canvJuego.coords(caja)[1]
    x1caja =canvJuego.coords(caja)[2]
    y1caja = canvJuego.coords(caja)[3]

    # Revisar colisiones
    if x1 > x0caja and x0 < x1caja: # colision en x
        colx = True
    if y1  >= y0caja and y0 <= y1caja: # colision en y
        coly = True
    if y1 - 10 >= y0caja and y0 + 10 <= y1caja: # y mas pequeño
        adentroy = True
    if x1 -10 >= x0caja and x0 + 10 <= x1caja: # x mas pequeño
        adentrox = True

    return [colx,coly,adentroy,adentrox] # Retorna todo para revisar colisiones individualmente

# --- CREAR MAPA ---

# Mapa 12x10 (1 = bloque)
mapa = [
    [0,1,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,1,0,0,1,1,1,1],
    [0,1,3,3,0,0,0,0,1,0,0,0],
    [0,1,1,1,0,0,0,0,1,0,0,0],
    [0,1,0,0,0,1,1,0,0,0,0,0],
    [0,1,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,2,0,0,0],
    [0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
]


def crear_cajas():
    cajasmapa[0].clear()
    canvJuego.delete("Caja")
    canvJuego.delete("Escalera")
    canvJuego.delete("Lava")
    # Posicion actual de la caja
    y0 = 0
    x0 = 0
    # Por cada fila en el mapa
    for filai in range(len(mapa)):
        fila = mapa[filai] # La fila actual
        # Por cada caja en la fila
        for caja in range(len(mapa[filai])):
            if fila[caja] == 1: # Si es un 1 crea una caja normal
                cajasmapa[0] += [canvJuego.create_rectangle(x0,y0,x0 + 75, y0 + 75,fill="green",tags="Caja")]
            elif fila[caja] == 2:
                cajasmapa[0] += [canvJuego.create_rectangle(x0,y0,x0 + 75, y0 + 75,fill="blue",tags="Escalera")]
            elif fila[caja] == 3:
                cajasmapa[0] += [canvJuego.create_rectangle(x0,y0+75,x0 + 75, y0+50,fill="orange",tags="Lava")]
            # Pasa al proximo lugar horizontalmente
            x0 += 75
        # Pasa al proximo lugar verticalmente
        y0 += 75
        # Reinicia la posicion horizontal
        x0 = 0
    canvJuego.tag_raise(p1) # Pone al jugador encima de todo

crear_cajas()

def crear_mapa_aleatorio():
    cajasmapa[0] = []
    for filai in range(len(mapa)):
        fila = mapa[filai] # La fila actual
        # Por cada caja en la fila
        for caja in range(len(mapa[filai])):
            fila[caja] = random.choice([0,0,0,0,0,0,0,1,2,3])
    
    crear_cajas()

# --- CONTROLES ---
root.bind('<KeyPress-d>',   lambda e: presionar(e, "d")) 
root.bind('<KeyPress-Right>',   lambda e: presionar(e, "d")) 
root.bind('<KeyPress-D>',   lambda e: presionar(e, "d")) 

root.bind('<KeyRelease-d>', lambda e: soltar(e, "d")) 
root.bind('<KeyRelease-Right>',   lambda e: soltar(e, "d")) 
root.bind('<KeyRelease-D>',   lambda e: soltar(e, "d")) 


root.bind('<KeyPress-Left>',   lambda e: presionar(e, "a")) 
root.bind('<KeyPress-a>',   lambda e: presionar(e, "a")) 
root.bind('<KeyPress-A>',   lambda e: presionar(e, "a")) 

root.bind('<KeyRelease-a>', lambda e: soltar(e, "a")) 
root.bind('<KeyRelease-Left>', lambda e: soltar(e, "a")) 
root.bind('<KeyRelease-A>',   lambda e: soltar(e, "a")) 

root.bind('<KeyPress-w>', saltar)
root.bind('<KeyPress-Up>',saltar)
root.bind('<KeyPress-space>',saltar)

boton_mapa_aleatorio = tk.Button(text="Generar Mapa", command=lambda: crear_mapa_aleatorio())
boton_mapa_aleatorio.pack()
root.mainloop()