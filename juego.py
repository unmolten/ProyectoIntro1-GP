import tkinter as tk
import random
import time
import pygame

# Ventana principal
root = tk.Tk()
root.geometry("500x400+400+200")
root.resizable(0,0)
root.title("Ghost Escape")
root.protocol("WM_DELETE_WINDOW", root.destroy)

# Tamaño del canvas
canvx = 900
canvy = 750

# Fondos
fondomapa = tk.PhotoImage(file="fondo-juego.png")
fondomenu = tk.PhotoImage(file="menu.png")
fondoresultados = tk.PhotoImage(file="fondoresultados.png")



# Variables para el juego y la ventana de juego
canvJuego = [None]
p1 = [None]
p1sprite = [None]
ventana_juego = [None]
ventana_resultado = [None]
labeltiempo = [None]
labelvidas = [None]

# Modo editor
cursor = [0, 0]
modo_editor = [False]
pos_jugador_editor = [0, canvy - 60]

# Sprites para el juego
spritejugador = tk.PhotoImage(file="personaje.png") 
spritecaja = tk.PhotoImage(file="caja.png")
spriteescalera = tk.PhotoImage(file="escalera.png")
spritelava = tk.PhotoImage(file="lava.png")

# Sprites animados y su logica
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
        canvJuego[0].itemconfig(sprite, image=spritesaw_frames[sierra_frame_actual[0]])
    root.after(50, animar_sierras)  # velocidad de animacion

personaje_frame_actual = [0]

def animar_personaje():
    personaje_frame_actual[0] += 1
    if personaje_frame_actual[0] >= len(spritesaw_frames):
        personaje_frame_actual[0] = 0
    canvJuego[0].itemconfig(p1sprite[0], image=spritepersonaje_frames[personaje_frame_actual[0]])
    root.after(100, animar_personaje)  # velocidad de animacion

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
tiempospuntos = [[],[]]
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
    x0 = canvJuego[0].coords(p1[0])[0] 
    x1 = canvJuego[0].coords(p1[0])[2]
    
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
        tag = canvJuego[0].gettags(cajasmapa[0][i]) # Revisa los tags de la caja para ver si es una escalera
        # Revisa si esta chocando horizontalmente [0] y si choca en un y un poco mas alto para que no se quede pegado
        if col[0] and col[2] and tag[0] != "Escalera": 
            # Consigue las cordenadas si hay una colison
            x0caja = canvJuego[0].coords(cajasmapa[0][i])[0]
            x1caja = canvJuego[0].coords(cajasmapa[0][i])[2]

            # Si chocha el lado derecho
            if x0 <= x0caja:
                colx_der = True
                canvJuego[0].move(p1[0], x0caja - x1, 0) # Se mueve al borde para que no este dentro
                canvJuego[0].move(p1sprite[0], x0caja - x1, 0)
            # Si choca con el lado izq
            else:
                colx_izq = True
                canvJuego[0].move(p1[0], x1caja - x0, 0) # Igual al borde
                canvJuego[0].move(p1sprite[0], x1caja - x0, 0)

    # Si se mantiene la tecla, esta en los margenes de la ventana, y no hay colision, se puede mover
    if d_held[0] and x1 <= canvx and not colx_der:
        canvJuego[0].move(p1[0], velx * dt * 60, 0)
        canvJuego[0].move(p1sprite[0], velx * dt * 60, 0)
    elif a_held[0] and x0 >= 0 and not colx_izq:
        canvJuego[0].move(p1[0], -velx * dt  * 60, 0)
        canvJuego[0].move(p1sprite[0], -velx * dt  * 60, 0)
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
    canvJuego[0].move(p1[0], 0, vely[0])
    canvJuego[0].move(p1sprite[0], 0, vely[0])
    vely[0] += 1  # Aumenta la velocidad para abajo (gravedad)

    # Coordenadas verticales del jugador
    y0 = canvJuego[0].coords(p1[0])[1]
    y1 = canvJuego[0].coords(p1[0])[3]

    # Revision de colisiones con las cajas
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i])
        tag = canvJuego[0].gettags(cajasmapa[0][i])
        if col[0] and col[1] and tag[0] != "Escalera":
            y0caja = canvJuego[0].coords(cajasmapa[0][i])[1]  # lado arriba de la caja
            y1caja = canvJuego[0].coords(cajasmapa[0][i])[3]  # abajo de la caja

            # Si cae y el jugador esta en la parte de arriba de la caja
            if vely_anterior >= 0 and y1 >= y0caja and y1 <= y0caja + vely_anterior + 5:
                canvJuego[0].move(p1[0], 0, y0caja - y1)  # corrige posicion al borde
                canvJuego[0].move(p1sprite[0], 0, y0caja - y1)
                saltando[0] = False
                vely[0] = 0
                bucles[1] = None
                return 0  # sale de la funcion para no seguir con el bucle

            # Si sube y la cabeza esta en el rango del fondo de la caja
            elif vely_anterior < 0 and y0 <= y1caja and y0 >= y1caja + vely_anterior - 5:
                canvJuego[0].move(p1[0], 0, y1caja - y0)  # empuja hacia abajo de la caja
                canvJuego[0].move(p1sprite[0], 0, y1caja - y0)
                saltando[0] = True  # sigue en el aire
                vely[0] = 1  # empieza a caer

    # Colision con el piso de la ventana
    if y1 >= canvy - 10:
        canvJuego[0].move(p1[0], 0, canvy - y1)  # corrige al borde del piso
        canvJuego[0].move(p1sprite[0], 0, canvy - y1)
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
        tag = canvJuego[0].gettags(cajasmapa[0][i])
        if col[0] and col[1] and tag[0] == "Escalera":
            vely[0] = 0
            canvJuego[0].move(p1[0],0,-10)
            canvJuego[0].move(p1sprite[0],0,-10)
    
    if up_held[0] and not d_held[0] and not a_held[0]:
        bucles[2] = root.after(16,escalera)
    else:
        bucles[2] = None # Si no se presiona ninguna tecla, se cancela el bucle


# --- COLISIONES ---

# Revisa si esta apoyado en una plataforma o en el piso
def en_piso():
    # "pies" del personaje
    y1 = canvJuego[0].coords(p1[0])[3]

    # Piso de la ventana
    if y1 >= canvy - 10:
        return True
    
    # Revisa para las cajas
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i])
        tag = canvJuego[0].gettags(cajasmapa[0][i])
        if col[1] and col[3] and  tag[0] != "Escalera": # [1] (vertical) y [3] (x pero mas pequeño) y escalera
            return True 
        
    # Si no hay nada, returna false
    return False

def reiniciar():
    labelvidas[0].config(text="Vidas: " + str(vidas[0]))
    if vidas[0] > 1 and muerto[0]:
        time.sleep(0.3)
        muerto[0] = False
        vidas[0] -= 1
        labelvidas[0].config(text="Vidas: " + str(vidas[0]))
        canvJuego[0].moveto(p1[0],       pos_jugador_editor[0], pos_jugador_editor[1])
        canvJuego[0].moveto(p1sprite[0], pos_jugador_editor[0], pos_jugador_editor[1])
        if bucles[3] is not None:
            root.after_cancel(bucles[3])
            bucles[3] = None
        contartiempo(time.time())
    elif vidas[0] == 1:
        vidas[0] -= 1
        labelvidas[0].config(text="Vidas: " + str(vidas[0]))
        perdio[0] = True
        mostrar_resultado()

# Sistema de colision con las cajas (originalmente se trato de usar canvas.find_overlapping() pero entre mas elementos habian
# retornaba una tupla muy confusa.)
def colision(caja): 

    # Variables para las colisiones
    colx = False
    coly = False
    adentroy = False
    adentrox = False
    tag = tag = canvJuego[0].gettags(caja)

    # Coordenadas jugador
    x0 = canvJuego[0].coords(p1[0])[0] 
    y0 = canvJuego[0].coords(p1[0])[1] 
    x1 = canvJuego[0].coords(p1[0])[2]
    y1 = canvJuego[0].coords(p1[0])[3]

    # Coordenadas caja
    x0caja = canvJuego[0].coords(caja)[0]
    y0caja =canvJuego[0].coords(caja)[1]
    x1caja =canvJuego[0].coords(caja)[2]
    y1caja = canvJuego[0].coords(caja)[3]

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
    if y1 <= 0 and not ganarnivel[0]:
        ganarnivel[0] = True
        mostrar_resultado()

    return [colx,coly,adentroy,adentrox] # Retorna todo para revisar colisiones individualmente

# --- CREAR MAPA ---

# Mapa 12x10 (1 = bloque)
mapa1 = [
    [0,1,1,1,1,1,1,1,1,0,0,0],
    [0,1,0,4,0,0,0,0,0,0,3,0],
    [0,1,0,0,0,1,0,0,1,1,1,1],
    [0,1,3,0,0,0,1,0,0,0,0,0],
    [0,1,1,1,0,0,0,0,3,0,0,0],
    [0,1,0,0,0,1,1,0,1,2,0,0],
    [0,1,3,3,3,0,0,0,0,2,0,0],
    [1,1,1,1,1,1,1,1,1,2,0,0],
    [0,0,0,1,0,0,0,0,0,2,0,0],
    [0,1,0,0,0,1,0,0,0,2,0,0],
]

mapacustom = [
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
]

def contartiempo(tiempoactual): 
    tiempospuntos[0] = time.time()
    if not ganarnivel[0]:
        tiempospuntos[1] = round(tiempospuntos[0] - tiempoactual, 2)
        labeltiempo[0].config(text=tiempospuntos[1])
        bucles[3] = root.after(30,contartiempo, tiempoactual)
    else:
        bucles[3] = None

def crear_cajas(mapa):
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
    canvJuego[0].delete("Caja")
    canvJuego[0].delete("Escalera")
    canvJuego[0].delete("Lava")
    canvJuego[0].delete("Saw")
    # Posicion actual de la caja
    y0 = 0
    x0 = 0
    # Por cada fila en el mapa
    for filai in range(len(mapa)):
        fila = mapa[filai] # La fila actual
        # Por cada caja en la filaa 
        for caja in range(len(mapa[filai])):
            if fila[caja] == 1: # Si es un 1 crea una caja normal
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0,y0,x0 + 75, y0 + 75,tags="Caja",outline="")]
                cajasmapa[1] += [canvJuego[0].create_image(x0 + 37.5, y0 + 37.5,image=spritecaja,tags="Caja")]
            elif fila[caja] == 2:
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0,y0,x0 + 75, y0 + 75,tags="Escalera",outline="")]
                cajasmapa[1] += [canvJuego[0].create_image(x0 + 37.5, y0 + 37.5,image=spriteescalera,tags="Escalera")]
            elif fila[caja] == 3:
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0,y0+75,x0 + 75, y0+50,tags="Lava",outline="")]
                cajasmapa[1] += [canvJuego[0].create_image(x0 + 37.5, y0+62.5 ,image=spritelava,tags="Lava")]
            elif fila[caja] == 4:
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0+ 15,y0+ 15,x0 + 60, y0 +60,tags="Saw",outline="")]
                sierrasmapa[0] += [canvJuego[0].create_image(x0 + 38, y0+38 ,image=spritelava,tags="Saw")]
            # Pasa al proximo lugar horizontalmente
            x0 += 75
        # Pasa al proximo lugar verticalmente
        y0 += 75
        # Reinicia la posicion horizontal
        x0 = 0
    canvJuego[0].tag_raise(p1[0]) # Pone al jugador encima de todo
    canvJuego[0].tag_raise(p1sprite[0])

def mostrar_resultado():
    if pygame.mixer_music.get_busy():
        pygame.mixer.quit()
    # Para todos los bucles los cancela
    for i in range(len(bucles)):
        if bucles[i] is not None:
            root.after_cancel(bucles[i])
            bucles[i] = None

    # Quita la ventana del juego
    ventana_juego[0].withdraw()

    # Crea la ventana de juego
    ventana_resultado[0] = tk.Toplevel(root)
    ventana_resultado[0].geometry("500x400+400+200")
    ventana_resultado[0].resizable(0, 0)
    ventana_resultado[0].title("Resultado")
    ventana_resultado[0].protocol("WM_DELETE_WINDOW", root.destroy)  # Para asegurarse de que no quede la ventana del menu en el fondo
    tk.Label(ventana_resultado[0],image=fondoresultados).place(x=0,y=0)
    if perdio[0]:
        tk.Label(ventana_resultado[0], text="Perdiste.", font=("Arial", 40)).pack(pady=30)
    else:
        tk.Label(ventana_resultado[0], text="Ganaste!", font=("Arial", 40)).pack(pady=30)
        tk.Label(ventana_resultado[0], text="Tiempo: " + str(tiempospuntos[1]), font=("Arial", 25)).pack()
        tk.Button(ventana_resultado[0], text="Guardar Resultado", font=("Arial", 18)).pack(pady=30)
    
    tk.Button(ventana_resultado[0], text="Volver al menu", font=("Arial", 18),
            command=lambda: [ventana_resultado[0].destroy(), ventana_juego[0].destroy(), root.deiconify()]).pack(pady=30)



def iniciar_juego(mapa):
    saltando[0] = False
    d_held = False
    a_held = False
    up_held = False
    pygame.mixer.init()
    pygame.mixer_music.set_volume(0.5)
    pygame.mixer_music.load("musicajuego.mp3")
    pygame.mixer_music.play(10)

    root.withdraw()  # esconde el menu

    ventana_juego[0] = tk.Toplevel(root)
    ventana_juego[0].geometry("1000x800+200+50")
    ventana_juego[0].resizable(0, 0)
    ventana_juego[0].title("Juego")
    ventana_juego[0].protocol("WM_DELETE_WINDOW", root.destroy)


    # Canvas
    canvJuego[0] = tk.Canvas(ventana_juego[0], width=canvx, height=canvy)
    canvJuego[0].create_image(0, 0, image=fondomapa, anchor="nw")
    canvJuego[0].pack(side="top")

    # Jugador
    p1[0] = canvJuego[0].create_rectangle(0, canvy, 40, canvy - 60, outline="")
    p1sprite[0] = canvJuego[0].create_image(20, canvy - 30, image=spritejugador)
    canvJuego[0].moveto(p1[0],       pos_jugador_editor[0], pos_jugador_editor[1])
    canvJuego[0].moveto(p1sprite[0], pos_jugador_editor[0], pos_jugador_editor[1])

    # Labels y botones
    labeltiempo[0] = tk.Label(ventana_juego[0], text="0", font="Helvetica")
    labeltiempo[0].pack(side="right", padx=100)
    labelvidas[0] = tk.Label(ventana_juego[0], text="Vidas: " + str(vidas[0]), font="Helvetica")
    labelvidas[0].pack(side="left", padx=100)
    tk.Button(ventana_juego[0], text="Menu", font=("Arial", 12),command=lambda: [ventana_juego[0].destroy(), root.deiconify()]).pack(side="right", padx=10)

    # Animaciones
    animar_sierras()
    animar_personaje()

    # Controles
    
    ventana_juego[0].bind('<KeyPress-d>',       lambda e: presionar(e, "d"))
    ventana_juego[0].bind('<KeyPress-Right>',    lambda e: presionar(e, "d"))
    ventana_juego[0].bind('<KeyPress-D>',        lambda e: presionar(e, "d"))
    ventana_juego[0].bind('<KeyRelease-d>',      lambda e: soltar(e, "d"))
    ventana_juego[0].bind('<KeyRelease-Right>',  lambda e: soltar(e, "d"))
    ventana_juego[0].bind('<KeyRelease-D>',      lambda e: soltar(e, "d"))


    ventana_juego[0].bind('<KeyPress-Left>',     lambda e: presionar(e, "a"))
    ventana_juego[0].bind('<KeyPress-a>',        lambda e: presionar(e, "a"))
    ventana_juego[0].bind('<KeyPress-A>',        lambda e: presionar(e, "a"))
    ventana_juego[0].bind('<KeyRelease-a>',      lambda e: soltar(e, "a"))
    ventana_juego[0].bind('<KeyRelease-Left>',   lambda e: soltar(e, "a"))
    ventana_juego[0].bind('<KeyRelease-A>',      lambda e: soltar(e, "a"))

    ventana_juego[0].bind('<KeyPress-W>',        lambda e: presionar(e, "up"))
    ventana_juego[0].bind('<KeyPress-w>',        lambda e: presionar(e, "up"))
    ventana_juego[0].bind('<KeyPress-Up>',       lambda e: presionar(e, "up"))
    ventana_juego[0].bind('<KeyRelease-W>',      lambda e: soltar(e, "up"))
    ventana_juego[0].bind('<KeyRelease-w>',      lambda e: soltar(e, "up"))
    ventana_juego[0].bind('<KeyRelease-Up>',     lambda e: soltar(e, "up"))

    ventana_juego[0].bind('<KeyPress-space>',    saltar)
    ventana_juego[0].bind('<KeyRelease-space>',  saltar)

    crear_cajas(mapa)

def cambiar_herramienta(herramienta, valor):
    herramienta[0] = valor

def mover_cursor(movercol, moverfila, canvEditor):
    cursor[0] += movercol
    cursor[1] += moverfila

    if cursor[0] < 0:
        cursor[0] = 0
    if cursor[0] > 11:
        cursor[0] = 11
    if cursor[1] < 0:
        cursor[1] = 0
    if cursor[1] > 9:
        cursor[1] = 9

    dibujar_editor(canvEditor)

def colocar(canvEditor, herramienta):
    col, fila = cursor[0], cursor[1]
    if herramienta[0] == 5:
        pos_jugador_editor[0] = col * 75
        pos_jugador_editor[1] = fila * 75
    else:
        mapacustom[fila][col] = herramienta[0]
    dibujar_editor(canvEditor)

def dibujar_editor(canvEditor):
    canvEditor.delete("prev")
    colores = ["", "green", "blue", "orange", "gray"]
    
    y0 = 0
    x0 = 0
    for filai in range(len(mapacustom)):
        fila = mapacustom[filai]
        for caja in range(len(mapacustom[filai])):
            if fila[caja] > 0:
                canvEditor.create_rectangle(x0, y0, x0+75, y0+75,
                    fill=colores[fila[caja]], tags="prev")
            x0 += 75
        y0 += 75
        x0 = 0

    # Jugador
    canvEditor.create_rectangle(
        pos_jugador_editor[0], pos_jugador_editor[1],
        pos_jugador_editor[0]+40, pos_jugador_editor[1]+60,
        fill="red", tags="prev")

    # Cursor
    canvEditor.create_rectangle(
        cursor[0]*75, cursor[1]*75,
        cursor[0]*75+75, cursor[1]*75+75,
        outline="white", width=3, tags="prev")

def iniciar_editor():
    modo_editor[0] = True
    root.withdraw()
    herramienta = [1]

    ventanaeditor = tk.Toplevel(root)
    ventanaeditor.resizable(0, 0)
    ventanaeditor.title("Editor")
    ventanaeditor.protocol("WM_DELETE_WINDOW", root.destroy)

    canvEditor = tk.Canvas(ventanaeditor , width=canvx, height=canvy)
    canvEditor.create_image(0, 0, image=fondomapa, anchor="nw")
    canvEditor.pack(side="top")

    tk.Button(ventanaeditor, text="Caja", bg="green", command=lambda: herramienta.__setitem__(0, 1)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Escalera", bg="blue", command=lambda: herramienta.__setitem__(0, 2)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Picos", bg="orange", command=lambda: herramienta.__setitem__(0, 3)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Sierra", bg="gray",   command=lambda: herramienta.__setitem__(0, 4)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Jugador", bg="red",    command=lambda: herramienta.__setitem__(0, 5)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Aire", bg="white",  command=lambda: herramienta.__setitem__(0, 0)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Colocar", bg="yellow", command=lambda: colocar(canvEditor, herramienta)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="▲", command=lambda: mover_cursor( 0,-1, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="▼", command=lambda: mover_cursor( 0, 1, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="<-", command=lambda: mover_cursor(-1, 0, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="->", command=lambda: mover_cursor( 1, 0, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Confirmar", bg="yellow",command=lambda: [ventanaeditor.destroy(), iniciar_juego(mapacustom)]).pack(side="right", padx=10)

    dibujar_editor(canvEditor)

tk.Label(image=fondomenu).place(x=0,y=0)
tk.Button(root, text="Puntajes",font=("Arial", 20)).pack(anchor="w",side="bottom",padx=20,pady=10)
tk.Button(root, text="Editar y Jugar", font=("Arial", 20),command=lambda: iniciar_editor()).pack(anchor="w", side="bottom", padx=20, pady=10)
tk.Button(root, text="Jugar", font=("Arial", 20), command=lambda: iniciar_juego(mapa1)).pack(anchor="w",side="bottom",padx=20,pady=10)

root.mainloop()