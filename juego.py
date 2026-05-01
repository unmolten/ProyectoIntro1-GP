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
fondomapa = tk.PhotoImage(file="fondo-juego.png")
canvJuego = tk.Canvas(root,width=canvx,height=canvy)
canvJuego.create_image(0, 0, image=fondomapa, anchor="nw")
canvJuego.pack(side="top")

# Jugador
spritejugador = tk.PhotoImage(file="personaje.png") # Para inicializar el jugador
p1 = canvJuego.create_rectangle(0,canvy,40,canvy-60,outline="")
p1sprite = canvJuego.create_image(20,canvy-30,image=spritejugador)



# Sprites para los obstaculos
spritecaja = tk.PhotoImage(file="caja.png")
spriteescalera = tk.PhotoImage(file="escalera.png")
spritelava = tk.PhotoImage(file="lava.png")

# Logica para las animaciones
spritesaw_frames = []
framesaw = 0

spritepersonaje_frames = []
framepersonaje = 0

while True:
    try:
        spritesaw_frames.append(tk.PhotoImage(file="saw.gif", format=f"gif -index {framesaw}"))
        spritepersonaje_frames.append(tk.PhotoImage(file="personaje.gif", format=f"gif -index {framepersonaje}"))
        framesaw += 1
        framepersonaje += 1
    except:
        break  # no hay mas frames

# Frame actual de la animacion
sierra_frame_actual = [0]
sierrasmapa = [[]]  # sprites de las sierras en el canvas

def animar_sierras():
    # Pasa al siguiente frame, vuelve a 0 cuando llega al final
    sierra_frame_actual[0] += 1
    if sierra_frame_actual[0] >= len(spritesaw_frames):
        sierra_frame_actual[0] = 0
    # Actualiza el sprite de cada sierra en el mapa
    for sprite in sierrasmapa[0]:
        canvJuego.itemconfig(sprite, image=spritesaw_frames[sierra_frame_actual[0]])
    root.after(50, animar_sierras)  # velocidad de animacion

animar_sierras()

personaje_frame_actual = [0]

def animar_personaje():
    personaje_frame_actual[0] += 1
    if personaje_frame_actual[0] >= len(spritesaw_frames):
        personaje_frame_actual[0] = 0
    canvJuego.itemconfig(p1sprite, image=spritepersonaje_frames[personaje_frame_actual[0]])
    root.after(100, animar_personaje)  # velocidad de animacion

animar_personaje()

# Variables
# Se guardan los id de los bucles para luego cancelarlos con un None
# 0 = movimiento horizontal, 1 = gravedad, 2 = escalera, 3 = tiempo
bucles = [None,None,None,None] 
ganarnivel = [False]
ganar =[False]
perdio = [False]
muerto = [False]
vidas = [3]
saltando = [False] # Estado de salto
ultimo_frame= [time.time()] # Tiempo desde la ultima llamada para el delta time (ver documentación)
tiempospuntos = [[]]
cajasmapa = [[],[]] # Se guardan los id de las cajas del mapa y sus sprites
vely = [0] # Velocidad vertical
velx = 9 # Velocidad horizontal (no cambia)



# Indicadores si la tecla esta siendo presionada. 
d_held = [False]
a_held = [False]
up_held = [False]
# --- INPUT ---
def presionar(evento, tecla):
    if tecla == "d":
        d_held[0] = True # Si recive la tecla d indica que esta siendo mantenida
    elif tecla == "a": 
        a_held[0] = True # Igual aca
    elif tecla == "up":
        up_held[0] = True
        escalera()

    if bucles[0] == None: # Ademas revisa si no hay bucles previos para llamar la funcion de movimiento
        mover()

# "Suelta" la tecla presionada
def soltar(evento, tecla):
    if tecla == "d":
        d_held[0] = False 
    elif tecla == "a":
        a_held[0] = False
    elif tecla == "up":
        up_held[0] = False

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
                canvJuego.move(p1sprite, x0caja - x1, 0)
            # Si choca con el lado izq
            else:
                colx_izq = True
                canvJuego.move(p1, x1caja - x0, 0) # Igual al borde
                canvJuego.move(p1sprite, x1caja - x0, 0)

    # Si se mantiene la tecla, esta en los margenes de la ventana, y no hay colision, se puede mover
    if d_held[0] and x1 <= canvx and not colx_der:
        canvJuego.move(p1, velx * dt * 60, 0)
        canvJuego.move(p1sprite, velx * dt * 60, 0)
    elif a_held[0] and x0 >= 0 and not colx_izq:
        canvJuego.move(p1, -velx * dt  * 60, 0)
        canvJuego.move(p1sprite, -velx * dt  * 60, 0)
    # Se llama la gravedad desde aca para asegurarse de que tenga gravedad cuando camina fuera de una caja
    if not saltando[0] and not en_piso() and bucles[1] is None:
        saltando[0] = True
        gravedad()
    
    # Bucle del movimiento.
    if d_held[0] or a_held[0]:
        bucles[0] = root.after(1,mover)
    else:
        bucles[0] = None # Si no se presiona ninguna tecla, se cancela el bucle

# --- GRAVEDAD ---d 

# Logica de gravedad, funcion un poco compleja y rara pero sirve. 
def gravedad():
    vely_anterior = vely[0]  # Guarda la velocidad antes de modificar para saber de donde venia el jugador
    canvJuego.move(p1, 0, vely[0])
    canvJuego.move(p1sprite, 0, vely[0])
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
                canvJuego.move(p1sprite, 0, y0caja - y1)
                saltando[0] = False
                vely[0] = 0
                bucles[1] = None
                return 0  # sale de la funcion para no seguir con el bucle

            # Si sube y la cabeza esta en el rango del fondo de la caja
            elif vely_anterior < 0 and y0 <= y1caja and y0 >= y1caja + vely_anterior - 5:
                canvJuego.move(p1, 0, y1caja - y0)  # empuja hacia abajo de la caja
                canvJuego.move(p1sprite, 0, y1caja - y0)
                saltando[0] = True  # sigue en el aire
                vely[0] = 1  # empieza a caer

    # Colision con el piso de la ventana
    if y1 >= canvy - 10:
        canvJuego.move(p1, 0, canvy - y1)  # corrige al borde del piso
        canvJuego.move(p1sprite, 0, canvy - y1)
        saltando[0] = False
        vely[0] = 0
        bucles[1] = None
    else:
        bucles[1] = root.after(17, gravedad)  # sigue el bucle si no esta en el piso


def saltar(evento):
    if not saltando[0]:
            saltando[0] = True 
            vely[0] = -17 # Asocia la altura del salto basicamente
            gravedad()

def escalera():
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i])
        tag = canvJuego.gettags(cajasmapa[0][i])
        if col[0] and col[1] and tag[0] == "Escalera":
            vely[0] = 0
            canvJuego.move(p1,0,-10)
            canvJuego.move(p1sprite,0,-10)
    
    if up_held[0] and not d_held[0] and not a_held[0]:
        bucles[2] = root.after(16,escalera)
    else:
        bucles[2] = None # Si no se presiona ninguna tecla, se cancela el bucle


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

def reiniciar():
    labelvidas.config(text="Vidas: " + str(vidas[0]))
    if vidas[0] > 1 and muerto[0]:
        time.sleep(0.3)
        muerto[0] = False
        vidas[0] -= 1
        labelvidas.config(text="Vidas: " + str(vidas[0]))
        canvJuego.moveto(p1, 0, canvy - 60)
        canvJuego.moveto(p1sprite, 0, canvy - 60)
        if bucles[3] is not None:
            root.after_cancel(bucles[3])
            bucles[3] = None
        contartiempo(time.time())
    elif vidas[0] == 1:
        vidas[0] -= 1
        labelvidas.config(text="Vidas: " + str(vidas[0]))
        perdio[0] = False
        root.quit()
        print("perdio")

# Sistema de colision con las cajas (originalmente se trato de usar canvas.find_overlapping() pero entre mas elementos habian
# retornaba una tupla muy confusa.)
def colision(caja): 

    # Variables para las colisiones
    colx = False
    coly = False
    adentroy = False
    adentrox = False
    tag = tag = canvJuego.gettags(caja)

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

    if colx and coly:
        if tag[0] == "Lava" or tag[0] == "Saw":
            muerto[0] = True
            reiniciar()
    if y1 <= 0:
        ganarnivel[0] = True
        print("gana")

    return [colx,coly,adentroy,adentrox] # Retorna todo para revisar colisiones individualmente

# --- CREAR MAPA ---

# Mapa 12x10 (1 = bloque)
mapa = [
    [0,1,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,1,0,0,1,1,1,1],
    [0,1,3,0,0,0,0,0,1,0,0,0],
    [0,1,1,1,0,0,0,0,1,0,0,0],
    [0,1,0,0,0,1,1,0,0,0,0,0],
    [0,1,0,0,4,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,2,0,0,0],
    [0,0,0,0,0,0,0,0,2,0,0,0],
    [0,0,0,0,0,0,0,0,2,0,0,0],
]

def contartiempo(tiempoactual): 
    tiempospuntos[0] = time.time()
    if not ganarnivel[0]:
        labeltiempo.config(text=round(tiempospuntos[0] - tiempoactual, 2))
        bucles[3] = root.after(30,contartiempo, tiempoactual)
    else:
        bucles[3] = None

def crear_cajas():
    if bucles[3] is not None:
        root.after_cancel(bucles[3])
        bucles[3] = None
    ganarnivel[0] = False
    muerto[0] = False
    vidas[0] = 3
    reiniciar()
    contartiempo(time.time())
    cajasmapa[0] = []
    cajasmapa[1] = []
    sierrasmapa[0] = []
    canvJuego.delete("Caja")
    canvJuego.delete("Escalera")
    canvJuego.delete("Lava")
    canvJuego.delete("Saw")
    # Posicion actual de la caja
    y0 = 0
    x0 = 0
    # Por cada fila en el mapa
    for filai in range(len(mapa)):
        fila = mapa[filai] # La fila actual
        # Por cada caja en la filaa 
        for caja in range(len(mapa[filai])):
            if fila[caja] == 1: # Si es un 1 crea una caja normal
                cajasmapa[0] += [canvJuego.create_rectangle(x0,y0,x0 + 75, y0 + 75,tags="Caja",outline="")]
                cajasmapa[1] += [canvJuego.create_image(x0 + 37.5, y0 + 37.5,image=spritecaja,tags="Caja")]
            elif fila[caja] == 2:
                cajasmapa[0] += [canvJuego.create_rectangle(x0,y0,x0 + 75, y0 + 75,tags="Escalera",outline="")]
                cajasmapa[1] += [canvJuego.create_image(x0 + 37.5, y0 + 37.5,image=spriteescalera,tags="Escalera")]
            elif fila[caja] == 3:
                cajasmapa[0] += [canvJuego.create_rectangle(x0,y0+75,x0 + 75, y0+50,tags="Lava",outline="")]
                cajasmapa[1] += [canvJuego.create_image(x0 + 37.5, y0+62.5 ,image=spritelava,tags="Lava")]
            elif fila[caja] == 4:
                cajasmapa[0] += [canvJuego.create_rectangle(x0+ 15,y0+ 15,x0 + 60, y0 +60,tags="Saw",outline="")]
                sierrasmapa[0] += [canvJuego.create_image(x0 + 38, y0+38 ,image=spritelava,tags="Saw")]
            # Pasa al proximo lugar horizontalmente
            x0 += 75
        # Pasa al proximo lugar verticalmente
        y0 += 75
        # Reinicia la posicion horizontal
        x0 = 0
    canvJuego.tag_raise(p1) # Pone al jugador encima de todo
    canvJuego.tag_raise(p1sprite)


def crear_mapa_aleatorio():
    cajasmapa[0] = []
    for filai in range(len(mapa)):
        fila = mapa[filai] # La fila actual
        # Por cada caja en la fila
        for caja in range(len(mapa[filai])):
            fila[caja] = random.choice([0,0,0,0,0,0,0,1,2,3,4])
    
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

root.bind('<KeyPress-W>',   lambda e: presionar(e, "up")) 
root.bind('<KeyPress-w>',   lambda e: presionar(e, "up")) 
root.bind('<KeyPress-Up>',   lambda e: presionar(e, "up")) 
root.bind('<KeyPress-space>', saltar) 

root.bind('<KeyRelease-W>', lambda e: soltar(e, "up")) 
root.bind('<KeyRelease-w>', lambda e: soltar(e, "up")) 
root.bind('<KeyRelease-Up>',   lambda e: soltar(e, "up")) 
root.bind('<KeyRelease-space>', saltar) 

boton_mapa_aleatorio = tk.Button(text="Generar Mapa", command=lambda: crear_mapa_aleatorio())
boton_mapa_aleatorio.pack(side="left",padx= 10)

labeltiempo = tk.Label(text=tiempospuntos[0],font="Helvetica")
labeltiempo.pack(side="right", padx= 10)
labelvidas = tk.Label(text="Vidas: " + str(vidas[0]), font="Helvetica")
labelvidas.pack(side="left", padx= 10)

crear_cajas()
root.mainloop()