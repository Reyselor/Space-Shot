import pygame
import random
import os

pygame.init()

ANCHO = 1200
ALTO = 800
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
SPRITES_DIR = os.path.join(os.path.dirname(__file__), "sprites")
BALA_ANIM_MS = 90

cadencia_de_disparo = 1000
cadencia_nivel = 0
cadencia_max = 10
cadencia_costo = 100
INCREMENTO_COSTO_CADENCIA = 50

cañones_extra = 0
cañon_costo = 500
cañon_max = 2
INCREMENTO_COSTO_CAÑON = 500

velocidad = 5
velocidad_enemigos = 3
velocidad_balas = 7

puntos = 1000

clock = pygame.time.Clock()

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Space shot!")
fuente = pygame.font.SysFont(None, 60)

#Funciones
def cargar_imagen(nombre, escala=None, subdir=""):
    ruta = os.path.join(SPRITES_DIR, subdir, nombre)
    img = pygame.image.load(ruta).convert_alpha()
    if escala:
        img = pygame.transform.scale(img, escala)
    return img

disparo_sonido = pygame.mixer.Sound(os.path.join(SPRITES_DIR, "sounds", "laser.wav"))
disparo_sonido.set_volume(0.6)

balas_sprites = [
    cargar_imagen("shot_1.png", (45, 45), "shot"),
    cargar_imagen("shot_2.png", (45, 45), "shot"),
    cargar_imagen("shot_3.png", (45, 45), "shot"),
    cargar_imagen("shot_4.png", (45, 45), "shot"),
    cargar_imagen("shot_asset.png", (45, 45), "shot")
]

bala_explosion_sprites = [
    cargar_imagen("shot_exp0.png", (45, 45), "shot"),
    cargar_imagen("shot_exp1.png", (45, 45), "shot"),
    cargar_imagen("shot_exp2.png", (45, 45), "shot"),
    cargar_imagen("shot_exp3.png", (45, 45), "shot"),
    cargar_imagen("shot_exp4.png", (45, 45), "shot"),
]

#Sprites enemigos
enemigo1 = cargar_imagen("enemigo1.png", (40, 40))
enemigo2 = cargar_imagen("enemigo2.png", (50, 50))
enemigo3 = cargar_imagen("enemigo3.png", (60, 60))
enemigo4 = cargar_imagen("enemigo4.png", (120, 90))

ENEMIGOS_CONFIG = [
    {"sprite": enemigo1, "vida": 1},
    {"sprite": enemigo2, "vida": 2},
    {"sprite": enemigo3, "vida": 4},
    {"sprite": enemigo4, "vida": 10}
]

nave = cargar_imagen("Spaceship.png", (100, 80))
nave_mask = pygame.mask.from_surface(nave)

#JUEGO PRINCIPAL
def jugar():
    global puntos, cadencia_de_disparo
    enemigos = []
    balas = []

    x = (ANCHO // 2) - 50
    y = ALTO - 100
    running = True

    def crear_enemigos():
        if random.randint(1, 40) == 1:
            enemigo_x = random.randint(0, ANCHO - 60)
            config = random.choice(ENEMIGOS_CONFIG)
            enemigos.append({
                "x": enemigo_x,
                "y": 0,
                "sprite": config["sprite"],
                "mask": pygame.mask.from_surface(config["sprite"]),
                "vida": config["vida"],
                "vida_max": config["vida"],
                "ultimo_daño": -9999
            })

    def mover_animar_balas():
        for bala in balas[:]:
            if bala["estado"] == "volando":
                bala["rect"].y -= velocidad_balas

            if pygame.time.get_ticks() - bala["ultimo_frame"] > BALA_ANIM_MS:
                bala["ultimo_frame"] = pygame.time.get_ticks()
                if bala["estado"] == "volando":
                    if bala["frame_index"] < len(bala["frames"]) - 1:
                        bala["frame_index"] += 1
                        bala["mask"] = pygame.mask.from_surface(bala["frames"][bala["frame_index"]])
                elif bala["estado"] == "explosion":
                    bala["frame_index"] += 1
                    if bala["frame_index"] >= len(bala["frames"]):
                        balas.remove(bala)

    def dibujar_enemigos_y_colisiones():
        nonlocal x, y
        global puntos
        colision = False
        nave_rect = nave.get_rect(topleft=(x, y))

        for enemigo in enemigos[:]:
            pantalla.blit(enemigo["sprite"], (enemigo["x"], enemigo["y"]))
            enemigo_rect = enemigo["sprite"].get_rect(topleft=(enemigo["x"], enemigo["y"]))

            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - enemigo["ultimo_daño"] < 1500:
                barra_ancho = enemigo_rect.width
                barra_alto = 5
                barra_x = enemigo["x"]
                barra_y = enemigo["y"] - barra_alto - 2
                pygame.draw.rect(pantalla, (60, 60, 60), (barra_x, barra_y, barra_ancho, barra_alto))
                vida_ratio = enemigo["vida"] / enemigo["vida_max"]
                if vida_ratio > 0.6:
                    color = (0, 255, 0)
                elif vida_ratio > 0.3:
                    color = (255, 215, 0)
                else:
                    color = (255, 0, 0)
                pygame.draw.rect(pantalla, color, (barra_x, barra_y, int(barra_ancho * vida_ratio), barra_alto))

            #Colisión de la nave
            offset = (enemigo_rect.x - nave_rect.x, enemigo_rect.y - nave_rect.y)
            if nave_mask.overlap(enemigo["mask"], offset):
                colision = True

            #Colisión de las balas
            for bala in balas[:]:
                offset_bala = (enemigo_rect.x - bala["rect"].x, enemigo_rect.y - bala["rect"].y)
                if bala["mask"] and bala["mask"].overlap(enemigo["mask"], offset_bala):
                    enemigo["vida"] -= 1
                    enemigo["ultimo_daño"] = pygame.time.get_ticks()
                    bala["frames"] = bala_explosion_sprites
                    bala["frame_index"] = 0
                    bala["estado"] = "explosion"
                    bala["ultimo_frame"] = pygame.time.get_ticks()
                    bala["mask"] = None

                    if enemigo["vida"] <= 0:
                        enemigos.remove(enemigo)
                        puntos += 10 * enemigo["vida_max"]
                    break
        return colision

    #Bucle principal del juego
    while running:
        pantalla.fill(NEGRO)
        fuente_puntos = pygame.font.SysFont(None, 36)
        texto_puntos = fuente_puntos.render(f"Puntos: {puntos}", True, BLANCO)
        pantalla.blit(texto_puntos, (10, 10))

        pantalla.blit(nave, (x, y))

        crear_enemigos()
        for enemigo in enemigos:
            enemigo["y"] += velocidad_enemigos
        enemigos[:] = [enemigo for enemigo in enemigos if enemigo["y"] < ALTO]

        mover_animar_balas()

        balas[:] = [bala for bala in balas if bala["rect"].y > 0]

        colision = dibujar_enemigos_y_colisiones()

        for bala in balas:
            sprite_actual = bala["frames"][bala["frame_index"]]
            pantalla.blit(sprite_actual, bala["rect"])

        if colision:
            texto = fuente.render("¡Game Over!", True, BLANCO)
            pantalla.blit(texto, (ANCHO // 2 - 150, ALTO // 2 - 30))
            pygame.display.flip()
            pygame.time.delay(2000)
            return

        #Movimiento de la nave
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            x -= velocidad
            if x < 0:
                x = 0
        if teclas[pygame.K_RIGHT]:
            x += velocidad
            if x > ANCHO - nave.get_width():
                x = ANCHO - nave.get_width()

        #Disparamos una bala con la spacebar
        if teclas[pygame.K_SPACE]:
            if len(balas) == 0 or pygame.time.get_ticks() - balas[-1]["tiempo"] > cadencia_de_disparo:
                rect_bala = balas_sprites[0].get_rect(center=(x + nave.get_width() // 2, y))
                balas.append({
                    "rect": rect_bala,
                    "frames": balas_sprites,
                    "frame_index": 0,
                    "ultimo_frame": pygame.time.get_ticks(),
                    "tiempo": pygame.time.get_ticks(),
                    "mask": pygame.mask.from_surface(balas_sprites[0]),
                    "estado": "volando"
                })
                #Balas extra por cañones
                for i in range(cañones_extra):
                    desplazamiento = 20 * (i + 1)  #Distancia desde el centro
                    #izquierda
                    rect_bala_izq = balas_sprites[0].get_rect(center=(x + nave.get_width() // 2 - desplazamiento, y))
                    balas.append({
                        "rect": rect_bala_izq,
                        "frames": balas_sprites,
                        "frame_index": 0,
                        "ultimo_frame": pygame.time.get_ticks(),
                        "tiempo": pygame.time.get_ticks(),
                        "mask": pygame.mask.from_surface(balas_sprites[0]),
                        "estado": "volando"
                    })
                    #Derecha
                    rect_bala_der = balas_sprites[0].get_rect(center=(x + nave.get_width() // 2 + desplazamiento, y))
                    balas.append({
                        "rect": rect_bala_der,
                        "frames": balas_sprites,
                        "frame_index": 0,
                        "ultimo_frame": pygame.time.get_ticks(),
                        "tiempo": pygame.time.get_ticks(),
                        "mask": pygame.mask.from_surface(balas_sprites[0]),
                        "estado": "volando"
                    })
                disparo_sonido.play()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.flip()
        clock.tick(60)

def tienda():
    global puntos, cadencia_nivel, cadencia_costo, cadencia_de_disparo, cañon_costo, cañones_extra, cañon_max
    while True:
        pantalla.fill((40, 20, 20))
        titulo = fuente.render("TIENDA", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - 100, 100))

        fuente_puntos = pygame.font.SysFont(None, 40)
        texto_puntos = fuente_puntos.render(f"Puntos: {puntos}", True, BLANCO)
        pantalla.blit(texto_puntos, (50, 50))

        if cadencia_nivel < cadencia_max:
            txt_mejora = f"1. Mejorar cadencia ({cadencia_nivel}/{cadencia_max}) - Costo: {cadencia_costo}"
        else:
            txt_mejora = f"1. Mejorar cadencia ({cadencia_nivel}/{cadencia_max}) - MAX"

        texto_mejora = fuente_puntos.render(txt_mejora, True, BLANCO)
        pantalla.blit(texto_mejora, (200, 300))

        if cañones_extra < cañon_max:
            txt_cañon = f"2. Agregar cañón ({cañones_extra}/{cañon_max}) - Costo: {cañon_costo}"
        else:
            txt_cañon = f"2. Agregar cañón ({cañones_extra}/{cañon_max}) - MAX"

        texto_cañon = fuente_puntos.render(txt_cañon, True, BLANCO)
        pantalla.blit(texto_cañon, (200, 350))

        texto_volver = fuente_puntos.render("3. Volver al menú", True, BLANCO)
        pantalla.blit(texto_volver, (200, 400))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and cadencia_nivel < cadencia_max:
                    if puntos >= cadencia_costo:
                        puntos -= cadencia_costo
                        cadencia_nivel += 1
                        cadencia_costo += INCREMENTO_COSTO_CADENCIA
                        cadencia_de_disparo = cadencia_de_disparo - 70
                elif event.key == pygame.K_2 and cañones_extra < cañon_max:
                    if puntos >= cañon_costo:
                        puntos -= cañon_costo
                        cañones_extra += 1
                        cañon_costo += INCREMENTO_COSTO_CAÑON
                elif event.key == pygame.K_3:
                    return

        pygame.display.flip()
        clock.tick(60)


# Menu principal
def menu():
    while True:
        pantalla.fill((20, 20, 40))
        titulo = fuente.render("SPACE SHOT!", True, BLANCO)
        jugar_txt = fuente.render("1. Jugar", True, BLANCO)
        tienda_txt = fuente.render("2. Tienda", True, (180, 180, 180))
        salir_txt = fuente.render("3. Salir", True, (180, 180, 180))

        pantalla.blit(titulo, (ANCHO // 2 - 150, 200))
        pantalla.blit(jugar_txt, (ANCHO // 2 - 150, 350))
        pantalla.blit(tienda_txt, (ANCHO // 2 - 150, 450))
        pantalla.blit(salir_txt, (ANCHO // 2 - 150, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    jugar() 
                elif event.key == pygame.K_2:
                    tienda()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    exit()

        pygame.display.flip()
        clock.tick(60)

#Inicio
menu()