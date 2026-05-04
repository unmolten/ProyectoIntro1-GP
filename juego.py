import tkinter as tk
import random
import time
import pygame

# Ventana principal
root = tk.Tk()
root.geometry("500x400+400+200")
root.resizable(0,0)
root.title("Ghost Escape")
root.protocol("WM_DELETE_WINDOW", root.destroy) # Esto se usa para asegurarse de que la ventana al cerrarse con la x no se quede en el fondo.




""" Variables para el juego y ventanas
Se usaron con listas ya que son mutables y sirven para multiples funciones distintas """
# Tamaño del canvas
canvx = 900
canvy = 750


# Variables para el juego

canvJuego = [None] # Canvas del juego
ventana_juego = [None] # Info de la ventana de juego
ventana_resultado = [None] # Info de la ventana de resultados
labeltiempo = [None] # Tiempo que se ve en la ventana de juego
labelvidas = [None] # Vidas que se ven en el juego
editado = [False] # Guarda si es que se jugo en un mapa editado para que se guarde en los puntajes
bucles = [None,None,None,None,None] # Guarda los ID de los bucles para poder cancelarlos acordemente
# 0 = movimiento horizontal, 1 = gravedad, 2 = escalera, 3 = tiempo, 4 = animaciones

ganarnivel = [False] # Estado de victoria
perdio = [False] # Estado de fallo
muerto = [False] # Para reiniciar el nivel
vidas = [3] # Vidas. al contar a 0 se pierde
saltando = [False] # Estado de salto para detectar si esta en el aire
ultimo_frame= [time.time()] # Tiempo desde la ultima llamada para el delta time (ver documentación)
tiempospuntos = [[],[]] # Se guardan los tiempos / 0 va cambiando / 1 es el tiempo final.
mapaactual = [None]
cajasmapa = [[],[]] # Se guardan los id de las cajas del mapa y sus sprites
sierrasmapa = [[]]  # Sprites de las sierras para la animacion de ellas

# Datos Jugador, Jugador / Su sprite / velocidad vertical / Horizontal
p1 = [None]
p1sprite = [None]
vely = [0] 
velx = 9 
# Indicadores si la tecla esta siendo presionada. 
d_held = [False] # der
a_held = [False] # izq
up_held = [False] # arriba (escaleras)

# Modo editor
cursor = [0, 0] # Pos cursor
modo_editor = [False] # Estado de modo editor
pos_jugador_editor = [0, canvy - 60] # Posicion del jugador editable

# Fondos
fondomapa = tk.PhotoImage(file="fondo-juego.png")
fondomenu = tk.PhotoImage(file="menu.png")
fondoresultados = tk.PhotoImage(file="fondoresultados.png")

# Sprites estaticos para el juego
spritecaja = tk.PhotoImage(file="caja.png")
spriteescalera = tk.PhotoImage(file="escalera.png")
spritelava = tk.PhotoImage(file="lava.png") # Picos


""" Logica de sprites animados. (Documentación) """

spritesaw_frames = [] # Fotogramas de la animacion de la sierra
framesaw = 0 # Frame actual

spritepersonaje_frames = [] # Fotogramas animacion personaje
framepersonaje = 0 

# Al inicio, revisa cada uno de los fotogramas dentro del .gif del personaje y la sierra y los va añadiendo a la lista para ir cambiando
while True:
    try:
        spritesaw_frames.append(tk.PhotoImage(file="saw.gif", format=f"gif -index {framesaw}")) # Guarda los frames de la sierra
        spritepersonaje_frames.append(tk.PhotoImage(file="personaje.gif", format=f"gif -index {framepersonaje}")) # Frames Jugador
        # Cambia de frame actual
        framesaw += 1
        framepersonaje += 1 
    except:
        break  # No hay mas frames


# Aqui sucede la animacion de las sierras

sierra_frame_actual = [0]

def animar_sierras():
    # Pasa al siguiente frame, vuelve a 0 cuando llega al final
    sierra_frame_actual[0] += 1
    if sierra_frame_actual[0] >= len(spritesaw_frames):
        sierra_frame_actual[0] = 0

    # Actualiza el sprite de cada sierra en el mapa
    for sierra in sierrasmapa[0]:
        canvJuego[0].itemconfig(sierra, image=spritesaw_frames[sierra_frame_actual[0]])

    bucles[4] = root.after(50, animar_sierras)  # Bucle para la animacion.



# Aqui sucede la animacion del personaje

personaje_frame_actual = [0]

def animar_personaje():
    personaje_frame_actual[0] += 1
    if personaje_frame_actual[0] >= len(spritepersonaje_frames):
        personaje_frame_actual[0] = 0
    canvJuego[0].itemconfig(p1sprite[0], image=spritepersonaje_frames[personaje_frame_actual[0]])
    bucles[4] = root.after(100, animar_personaje)  # velocidad de animacion

# Se guardan los id de los bucles para luego cancelarlos con un None



""" Logica de las teclas y de movimiento horizontal. (Documentación) """
# Presionado de teclas
def presionar(evento, tecla):
    # Revisa las teclas dadas por el commando de .bind()
    if tecla == "d": # der
        d_held[0] = True 
    elif tecla == "a": # izq
        a_held[0] = True
    elif tecla == "up": # arriba
        up_held[0] = True
        escalera() # Llama a escaleras para el movimiento de las escaleras

    if bucles[0] == None: # Ademas revisa si no hay bucles previos para llamar la funcion de movimiento
        mover()

# "Suelta" la tecla presionada
def soltar(evento, tecla):
    if tecla == "d": # der
        d_held[0] = False 
    elif tecla == "a": # izq
        a_held[0] = False
    elif tecla == "up": # arriba
        up_held[0] = False
        bucles[2] = None # Al soltar la tecla de la escalera, se cancela el bucle
        


# Funcion de movimiento horizontal.
def mover():

    # Coordenadas del jugador
    x0 = canvJuego[0].coords(p1[0])[0] 
    x1 = canvJuego[0].coords(p1[0])[2]
    
    # Calculos para el delta time
    ahora = time.time() # Tiempo actual
    dt = min(ahora - ultimo_frame[0], 0.016) # dt (diferencia tiempo), se usa un min en el caso de si dt es muy grande
    ultimo_frame[0] = ahora # Se guarda por separado.

    # Indicadores con que lado se dio una colision para no poder moverse a ese lado
    colx_der = False
    colx_izq = False

    # Revisar colisiones por cada caja que hay en el mapa
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i]) # Valores de la colision.
        tag = canvJuego[0].gettags(cajasmapa[0][i]) # Revisa los tags de la caja para ver si es una escalera

        # Si colisiona horizontalmente(indice 0), y en un margen vertical mas pequeño (indice 2) y si no es una escalera
        if col[0] and col[2] and tag[0] != "Escalera": 

            # Consigue las cordenadas de la caja
            x0caja = canvJuego[0].coords(cajasmapa[0][i])[0] # Lado izq de la caja
            x1caja = canvJuego[0].coords(cajasmapa[0][i])[2] # Lado derecho de la caja

            # Si chocha el lado derecho
            if x0 <= x0caja:
                colx_der = True
                # Se mueve al borde derecho para que no este dentro
                canvJuego[0].move(p1[0], x0caja - x1, 0) 
                canvJuego[0].move(p1sprite[0], x0caja - x1, 0) 
            # Si choca con el lado izq
            else:
                colx_izq = True
                # Igual al borde izquierdo
                canvJuego[0].move(p1[0], x1caja - x0, 0) 
                canvJuego[0].move(p1sprite[0], x1caja - x0, 0)

    # Si se mantiene la tecla, esta en los margenes de la ventana, y no hay colision, se puede mover
    if d_held[0] and x1 <= canvx and not colx_der:
        # El movimiento se multiplica por el deltatime, y por 60, para un movimiento fluido
        canvJuego[0].move(p1[0], velx * dt * 60, 0)
        canvJuego[0].move(p1sprite[0], velx * dt * 60, 0)
    elif a_held[0] and x0 >= 0 and not colx_izq:
        canvJuego[0].move(p1[0], -velx * dt  * 60, 0)
        canvJuego[0].move(p1sprite[0], -velx * dt  * 60, 0)

    # Se llama la gravedad desde aca para asegurarse de que tenga gravedad cuando camina fuera de una caja
    if not saltando[0] and not en_piso() and bucles[1] is None:
        saltando[0] = True # Ahora esta en el aire
        gravedad()
    
    # Bucle del movimiento.
    if d_held[0] or a_held[0]:
        bucles[0] = root.after(1,mover)
    else:
        bucles[0] = None # Si no se presiona ninguna tecla, se cancela el bucle


""" Funciones de movimiento vertical y escaleras. (Documentación) """
# Funcion de Salto
def saltar(evento):
    if not saltando[0]: # Si no esta en el aire
            saltando[0] = True # Ahora si
            vely[0] = -17 # Acelera verticalmente
            gravedad()

# Logica de gravedad, funcion un poco compleja y rara pero sirve. 
def gravedad():
    vely_anterior = vely[0]  # Guarda la velocidad antes de modificar para saber de donde venia el jugador

    # Va moviendo el jugador en la direccion de vely
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

        # Revisa si tiene colisiones en ambos ejes y si no esta en una escalera
        if col[0] and col[1] and tag[0] != "Escalera":
            y0caja = canvJuego[0].coords(cajasmapa[0][i])[1]  # lado arriba de la caja
            y1caja = canvJuego[0].coords(cajasmapa[0][i])[3]  # abajo de la caja

            # Se revisa si anteriormente se dirigia para abajo, si esta encima de la caja,
            # y si ademas no esta más de 5 pixeles abajo del borde de la caja (significaria que no vino desde arriba, si no desde el lado.)
            if vely_anterior >= 0 and y1 >= y0caja and y1 <= y0caja + vely_anterior + 5:
                # corrige posicion al borde
                canvJuego[0].move(p1[0], 0, y0caja - y1) 
                canvJuego[0].move(p1sprite[0], 0, y0caja - y1)

                saltando[0] = False # Habilita saltar otra vez
                vely[0] = 0 # Para al jugador
                bucles[1] = None # Elimina el bucle de la lista para poder correrlo otra vez cuando se vueva a llamar
                return 0  # sale de la funcion para no seguir con el bucle

            # Si sube y la cabeza esta en el rango del fondo de la caja, y que si haya venido de abajo el personaje
            elif vely_anterior < 0 and y0 <= y1caja and y0 >= y1caja + vely_anterior - 5:
                canvJuego[0].move(p1[0], 0, y1caja - y0)  # empuja hacia abajo de la caja
                canvJuego[0].move(p1sprite[0], 0, y1caja - y0)
                saltando[0] = True  # sigue en el aire
                vely[0] = 1  # empieza a caer


    # Colision con el piso de la ventana
    if y1 >= canvy - 10:
        # corrige al borde del piso
        canvJuego[0].move(p1[0], 0, canvy - y1)  
        canvJuego[0].move(p1sprite[0], 0, canvy - y1)

        saltando[0] = False 
        vely[0] = 0
        bucles[1] = None # Elimina el bucle
    else:
        bucles[1] = root.after(17, gravedad)  # Sigue el bucle si no esta en el piso

# Logica de la escalera
def escalera():
    en_escalera = False # Indica si ya esta en una escalera para no hacer bucles infinitos

    # Revisa cada caja del mapa para ver si es una escalera
    for i in range(len(cajasmapa[0])):
        col = colision(cajasmapa[0][i])
        tag = canvJuego[0].gettags(cajasmapa[0][i])
        # Igual que en la colision de gravedad, solo que si aqui esta en la escalera
        if col[0] and col[1] and tag[0] == "Escalera":
            en_escalera = True
            vely[0] = 0 # Cancela la velocidad
            # Va moviendo el jugador para arriba
            canvJuego[0].move(p1[0],0,-10) 
            canvJuego[0].move(p1sprite[0],0,-10)
    # Si se mantiene arriba, esta en una escalera, y no se mueve horizontalmente 
    if up_held[0] and en_escalera and not d_held[0] and not a_held[0]:
        bucles[2] = root.after(16,escalera)


""" Funciones para la logica de las colisiones (Documentación) """

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
        # [1] (vertical) y [3] (x pero mas pequeño) y  no escalera
        if col[1] and col[3] and  tag[0] != "Escalera": 
            return True 
        
    # Si no hay nada, returna false
    return False


# Sistema de colision con las cajas
def colision(caja): 

    # Colisiones enteras
    colx = False 
    coly = False 
    # Colisiones con margenes mas pequeños
    adentroy = False 
    adentrox = False

    # Tag para ver si son Picos o una Sierra
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

    # Si tiene ambas colisiones
    if colx and coly:
        # Revisa si son los picos o la sierra
        if tag[0] == "Lava" or tag[0] == "Saw":
            muerto[0] = True # Muerto
            reiniciar() # Llama la funcion para reiniciar casi todo

    # Si llega a la meta (El cielo)
    if y1 <= 0 and not ganarnivel[0]:
        ganarnivel[0] = True # Gana el nivel
        mostrar_resultado() # Va a mostrar resultados

    return [colx,coly,adentroy,adentrox] # Retorna todo para revisar colisiones individualmente

""" Funciones Extra """
# Funcion para reiniciar el personaje e ir restando la cantidad de vidas
def reiniciar():
    # Actualiza el label de las vidas para tener el valor actual
    labelvidas[0].config(text="Vidas: " + str(vidas[0]))
    # Si aun tiene vidas y se murio
    if vidas[0] > 1 and muerto[0]:
        time.sleep(0.3) # Para un momento todo para mostrar donde se murio
        muerto[0] = False # Reinicia el estado de muerto
        vidas[0] -= 1 # Resta 1 vida
        labelvidas[0].config(text="Vidas: " + str(vidas[0])) # Actualiza otra vez

        # Mueve el Jugador a la posicion inicial
        canvJuego[0].moveto(p1[0], pos_jugador_editor[0], pos_jugador_editor[1])
        canvJuego[0].moveto(p1sprite[0], pos_jugador_editor[0], pos_jugador_editor[1])
    
    # Si solo tiene una vida al momento de muerte
    elif vidas[0] == 1:
        vidas[0] -= 1
        labelvidas[0].config(text="Vidas: " + str(vidas[0]))
        perdio[0] = True # Pierde
        mostrar_resultado() # Llama la pantalla de resultados

# Va contando el tiempo si no ha ganado
def contartiempo(tiempoactual): 
    tiempospuntos[0] = time.time() # Pone el tiempo de inicio
    if not ganarnivel[0]:
        tiempospuntos[1] = round(tiempospuntos[0] - tiempoactual, 2) # Hace la resta del tiempo actual y la del inicio
        labeltiempo[0].config(text=tiempospuntos[1]) #Se actualiza el tiempo
        bucles[3] = root.after(30,contartiempo, tiempoactual) # Bucle
    else:
        bucles[3] = None



""" Funciones de Generacion del mapa (Documentación) """
# Mapa Principal
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

# Mapa para editar
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
# Mapa secreto (Buscar en el editor un boton muy pequeño)
mapasecreto = [
    [0,0,0,0,4,4,4,4,4,0,0,2], 
    [0,0,0,0,4,0,0,0,0,0,0,2], 
    [4,4,0,0,0,0,1,0,0,0,3,2],
    [4,0,0,0,0,0,4,0,1,0,1,1], 
    [0,0,3,3,3,1,0,0,0,0,4,4], 
    [2,1,1,1,1,4,0,0,0,0,0,4], 
    [2,0,0,0,4,0,0,0,0,3,0,0], 
    [2,2,2,2,2,0,0,0,0,1,1,2], 
    [2,2,2,2,1,1,0,0,0,4,1,0], 
    [3,3,3,3,3,1,3,3,3,3,1,0]
    ]

# Creacion de los obstaculos del mapa dado
def crear_cajas(mapa):
    # Cancela el bucle del tiempo si estaba corriendo antes de cargar un mapa nuevo
    if bucles[3] is not None:
        root.after_cancel(bucles[3])
        bucles[3] = None
    # Reinicia los estados del juego para empezar desde cero
    ganarnivel[0] = False
    muerto[0] = False
    vidas[0] = 3
    reiniciar() # Reinicia el personaje
    contartiempo(time.time()) # Empieza a contar el tiempo

    # Limpia las listas de cajas y sierras para no acumular los del mapa anterior
    cajasmapa[0] = []
    cajasmapa[1] = []
    sierrasmapa[0] = []
    # Borra todos los objetos del canvas por tag para limpiar el mapa anterior
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
        # Por cada caja en la fila
        for caja in range(len(mapa[filai])):
            # Si es un 1 crea una caja normal
            if fila[caja] == 1: 
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0,y0,x0 + 75, y0 + 75,tags="Caja",outline="")]
                cajasmapa[1] += [canvJuego[0].create_image(x0 + 37.5, y0 + 37.5,image=spritecaja,tags="Caja")]

            # Escaleras
            elif fila[caja] == 2: 
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0,y0,x0 + 75, y0 + 75,tags="Escalera",outline="")]
                cajasmapa[1] += [canvJuego[0].create_image(x0 + 37.5, y0 + 37.5,image=spriteescalera,tags="Escalera")]

            # Picos / lava, la hitbox es mas pequeña que la caja (y0+50 en vez de y0)
            elif fila[caja] == 3: 
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0,y0+75,x0 + 75, y0+50,tags="Lava",outline="")]
                cajasmapa[1] += [canvJuego[0].create_image(x0 + 37.5, y0+62.5 ,image=spritelava,tags="Lava")]

            # Sierra, la hitbox es mas pequeña que la celda para dar margen al jugador
            elif fila[caja] == 4: 
                cajasmapa[0] += [canvJuego[0].create_rectangle(x0+ 15,y0+ 15,x0 + 60, y0 +60,tags="Saw",outline="")]
                sierrasmapa[0] += [canvJuego[0].create_image(x0 + 38, y0+38 ,image=spritesaw_frames[0],tags="Saw")]

            # Pasa al proximo lugar horizontalmente
            x0 += 75
        # Pasa al proximo lugar verticalmente
        y0 += 75
        # Reinicia la posicion horizontal
        x0 = 0
    canvJuego[0].tag_raise(p1[0]) # Pone al jugador encima de todo
    canvJuego[0].tag_raise(p1sprite[0])

def mostrar_resultado():    
    # Detiene la musica al llegar al resultado
    if pygame.mixer_music.get_busy():
        pygame.mixer.quit()
    # Para todos los bucles los cancela
    for i in range(len(bucles)):
        if bucles[i] is not None:
            root.after_cancel(bucles[i])
            bucles[i] = None

    # Quita la ventana del juego
    ventana_juego[0].withdraw()

    # Crea la ventana de resultado
    ventana_resultado[0] = tk.Toplevel(root)
    ventana_resultado[0].geometry("500x400+400+200")
    ventana_resultado[0].resizable(0, 0)
    ventana_resultado[0].title("Resultado")
    ventana_resultado[0].protocol("WM_DELETE_WINDOW", root.destroy)  # Para asegurarse de que no quede la ventana del menu en el fondo
    tk.Label(ventana_resultado[0],image=fondoresultados).place(x=0,y=0)
    # Muestra pantalla de derrota o victoria segun corresponda
    if perdio[0]:
        tk.Label(ventana_resultado[0], text="Perdiste.", font=("Arial", 40)).pack(pady=30)
    else:
        tk.Label(ventana_resultado[0], text="Ganaste!", font=("Arial", 40)).pack(pady=30)
        tk.Label(ventana_resultado[0], text="Tiempo: " + str(tiempospuntos[1]), font=("Arial", 25)).pack()
        # Solo permite guardar puntaje si gano
        tk.Label(ventana_resultado[0], text="Ingresa tu nombre: ", font=("Arial",12)).pack(pady=10)
        entrynombre = tk.Entry(ventana_resultado[0])
        entrynombre.pack(pady=5)
        tk.Button(ventana_resultado[0], text="Guardar Resultado",command=lambda:guardar_resultados(entrynombre) ,font=("Arial", 18)).pack(pady=10)
    
    tk.Button(ventana_resultado[0], text="Volver al menu", font=("Arial", 18),
            command=lambda: [ventana_resultado[0].destroy(), ventana_juego[0].destroy(), root.deiconify()]).pack(pady=10)

def guardar_resultados(entry):
    # Intenta crear el archivo si no existe aun
    try:
        f = open("puntajes.txt", "x")
    except:
        pass # Si ya existe, no hace nada
    # Lee el contenido actual para evitar duplicados
    with open("puntajes.txt", "r") as f:
        puntajes = f.read()

    with open("puntajes.txt", "a") as f:
        # Agrega una marca si se jugo en un mapa editado
        if editado[0]:
            if (entry.get() + ": " + str(tiempospuntos[1]) + "s. " + "Vidas: " + str(vidas[0]) + " [Mapa Editado]\n") not in puntajes:
                f.write(entry.get() + ": " + str(tiempospuntos[1]) + "s. " + "Vidas: " + str(vidas[0]) + " [Mapa Editado]\n")
        else:
            # Solo escribe si el puntaje no esta ya guardado (evita duplicados al hacer click varias veces)
            if (entry.get() + ": " + str(tiempospuntos[1]) + "s. " + "Vidas: " + str(vidas[0]) + "\n") not in puntajes:
                f.write(entry.get() + ": " + str(tiempospuntos[1]) + "s. " + "Vidas: " + str(vidas[0]) + "\n")

def ver_puntajes():
    # Abre una ventana nueva para mostrar los puntajes guardados
    ventana_puntajes = tk.Toplevel(root)
    ventana_puntajes.geometry("300x300+400+200")
    try:
        with open("puntajes.txt", "r") as f:
            puntajes = f.read()
            tk.Label(ventana_puntajes, text=puntajes).pack()
    except:
        # Si el archivo no existe todavia, avisa al usuario
        tk.Label(ventana_puntajes, text="No hay puntajes al momento.").pack()


def iniciar_juego(mapa):
    # Reinicia todos los estados antes de empezar
    mapaactual[0] = mapa
    perdio[0] = False
    muerto[0] = False
    ganarnivel[0] = False
    d_held[0] = False
    a_held[0] = False
    saltando[0] = False
    # Cancela cualquier bucle activo que haya quedado de una partida anterior
    for i in range(len(bucles)):
        if bucles[i] is not None:
            root.after_cancel(bucles[i])
            bucles[i] = None

    # Inicia la musica del juego
    pygame.mixer.init()
    pygame.mixer_music.set_volume(0.5)
    pygame.mixer_music.load("musicajuego.mp3")
    pygame.mixer_music.play(10)

    root.withdraw()  # esconde el menu

    # Crea la ventana del juego
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
    p1sprite[0] = canvJuego[0].create_image(20, canvy - 30, image=spritepersonaje_frames[0])
    
    # Si es mapa editado, usa la posicion del editor. Si es el mapa1, reinicia la posicion al inicio
    if mapa != mapa1:
        editado[0] = True
        canvJuego[0].moveto(p1[0], pos_jugador_editor[0], pos_jugador_editor[1])
        canvJuego[0].moveto(p1sprite[0], pos_jugador_editor[0], pos_jugador_editor[1])
    else:
        editado[0] = False
        pos_jugador_editor[0] = 0
        pos_jugador_editor[1] = 750 
        canvJuego[0].moveto(p1[0], pos_jugador_editor[0], pos_jugador_editor[1] - 60)
        canvJuego[0].moveto(p1sprite[0], pos_jugador_editor[0], pos_jugador_editor[1] - 60)
    
    # Labels y botones
    labeltiempo[0] = tk.Label(ventana_juego[0], text="0", font="Helvetica")
    labeltiempo[0].pack(side="right", padx=100)
    labelvidas[0] = tk.Label(ventana_juego[0], text="Vidas: " + str(vidas[0]), font="Helvetica")
    labelvidas[0].pack(side="left", padx=100)
    tk.Button(ventana_juego[0], text="Menu", font=("Arial", 12),command=lambda: [ventana_juego[0].destroy(), root.deiconify(), pygame.mixer.quit()]).pack(side="left", padx=30)

    # Animaciones
    animar_sierras()
    animar_personaje()

    # Controles. Se bindean tanto minusculas, mayusculas y flechas para mayor comodidad
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


""" Funciones del Editor """
# Cambia la herramienta activa del editor al valor dado
def cambiar_herramienta(herramienta, valor):
    herramienta[0] = valor

# Mueve el cursor en la grilla del editor, limitado a los bordes del mapa
def mover_cursor(movercol, moverfila, canvEditor):
    cursor[0] += movercol
    cursor[1] += moverfila

    # Limita el cursor dentro de los bordes del mapa (12 columnas, 10 filas)
    if cursor[0] < 0:
        cursor[0] = 0
    if cursor[0] > 11:
        cursor[0] = 11
    if cursor[1] < 0:
        cursor[1] = 0
    if cursor[1] > 9:
        cursor[1] = 9

    dibujar_editor(canvEditor) # Actualiza la vista del editor

# Coloca la herramienta seleccionada en la posicion actual del cursor
def colocar(canvEditor, herramienta):
    col, fila = cursor[0], cursor[1]
    # Si la herramienta es el jugador (5), actualiza su posicion en vez de editar el mapa
    if herramienta[0] == 5:
        pos_jugador_editor[0] = col * 75
        pos_jugador_editor[1] = fila * 75
    else:
        mapacustom[fila][col] = herramienta[0] # Escribe el valor en el mapa
    dibujar_editor(canvEditor)

# Dibuja la vista previa del mapa en el canvas del editor
def dibujar_editor(canvEditor):
    canvEditor.delete("prev") # Borra el dibujo anterior para redibujar
    colores = ["", "green", "blue", "orange", "gray"] # Color por tipo: 1=caja, 2=escalera, 3=picos, 4=sierra
    
    y0 = 0
    x0 = 0
    for filai in range(len(mapacustom)):
        fila = mapacustom[filai]
        for caja in range(len(mapacustom[filai])):
            if fila[caja] > 0: # Solo dibuja si hay algo en la celda
                canvEditor.create_rectangle(x0, y0, x0+75, y0+75, fill=colores[fila[caja]], tags="prev")
            x0 += 75
        y0 += 75
        x0 = 0

    # Jugador (representado como un rectangulo rojo)
    canvEditor.create_rectangle(pos_jugador_editor[0]+10, pos_jugador_editor[1],pos_jugador_editor[0]+50, pos_jugador_editor[1]+60, fill="red", tags="prev")

    # Cursor (borde blanco sobre la celda actual)
    canvEditor.create_rectangle(cursor[0]*75, cursor[1]*75, cursor[0]*75+75, cursor[1]*75+75,outline="white", width=3, tags="prev")

def iniciar_editor():
    modo_editor[0] = True
    root.withdraw() # Esconde el menu principal
    herramienta = [1] # Herramienta activa por defecto (caja)

    ventanaeditor = tk.Toplevel(root)
    ventanaeditor.resizable(0, 0)
    ventanaeditor.title("Editor")
    ventanaeditor.protocol("WM_DELETE_WINDOW", root.destroy)

    # Canvas del editor con el mismo fondo del juego
    canvEditor = tk.Canvas(ventanaeditor , width=canvx, height=canvy)
    canvEditor.create_image(0, 0, image=fondomapa, anchor="nw")
    canvEditor.pack(side="top")

    # Botones para seleccionar herramientas y mover el cursor
    tk.Button(ventanaeditor, text="Caja", bg="green", command=lambda: cambiar_herramienta(herramienta, 1)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Escalera", bg="blue", command=lambda: cambiar_herramienta(herramienta, 2)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Picos", bg="orange", command=lambda: cambiar_herramienta(herramienta, 3)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Sierra", bg="gray",   command=lambda: cambiar_herramienta(herramienta, 4)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Jugador", bg="red",    command=lambda: cambiar_herramienta(herramienta, 5)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Aire", bg="white", command=lambda: cambiar_herramienta(herramienta, 0)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="Colocar", bg="yellow", command=lambda: colocar(canvEditor, herramienta)).pack(side="left", padx=3)
    # Controles de movimiento del cursor
    tk.Button(ventanaeditor, text="▲", command=lambda: mover_cursor( 0,-1, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="▼", command=lambda: mover_cursor( 0, 1, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="<-", command=lambda: mover_cursor(-1, 0, canvEditor)).pack(side="left", padx=3)
    tk.Button(ventanaeditor, text="->", command=lambda: mover_cursor( 1, 0, canvEditor)).pack(side="left", padx=3)
    # Boton secreto (sin texto) que lanza el mapa secreto
    tk.Button(ventanaeditor, text="",command=lambda: [ventanaeditor.destroy(), iniciar_juego(mapasecreto), print(mapacustom)]).pack(side="right")
    # Boton para confirmar el mapa editado e iniciar el juego con el
    tk.Button(ventanaeditor, text="Confirmar", bg="yellow",command=lambda: [ventanaeditor.destroy(), iniciar_juego(mapacustom), print(mapacustom)]).pack(side="right", padx=10)
    
    dibujar_editor(canvEditor) # Dibuja el estado inicial del editor


# Resto de las cosas del menu principal
tk.Label(image=fondomenu).place(x=0,y=0)
tk.Button(root, text="Puntajes",font=("Arial", 20),command=ver_puntajes).pack(anchor="w",side="bottom",padx=20,pady=10)
tk.Button(root, text="Editar y Jugar", font=("Arial", 20),command=lambda: iniciar_editor()).pack(anchor="w", side="bottom", padx=20, pady=10)
tk.Button(root, text="Jugar", font=("Arial", 20), command=lambda: iniciar_juego(mapa1)).pack(anchor="w",side="bottom",padx=20,pady=10)

# Bucle de tkinter
root.mainloop()