import pygame
import sys
import random
from cryptography.fernet import Fernet
import tempfile
import os

# Pygame alustaminen
pygame.init()

# Pelin asetukset
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Syntymäpäiväpeli")
clock = pygame.time.Clock()

# Värit
TURQUOISE = (171, 219, 227)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (165, 42, 42)
LILAC = (200, 162, 200)

# Tikku-ukon asetukset
stickman_size = 40
stickman = pygame.Rect(100, HEIGHT - stickman_size - 10, stickman_size, stickman_size)
stickman_speed = 5
gravity = 1
jump_speed = -15
velocity_y = 0

# Tasojen asetukset
platforms = [
    pygame.Rect(50, 500, 200, 10),
    pygame.Rect(300, 400, 200, 10),
    pygame.Rect(550, 300, 200, 10),
]

# Kakkupalat
cake_pieces = [
    pygame.Rect(100, 460, 20, 20),
    pygame.Rect(350, 360, 20, 20),
    pygame.Rect(600, 260, 20, 20),
    pygame.Rect(750, 550, 20, 20),  # Viimeinen pala
]
cakes_collected = 0

# Kortin animaatioasetukset
def pura_ja_lataa_kuva():
    """Puraa salattu kuvatiedosto ja lataa se Pygameen."""
    with open("salausavain.key", "rb") as avaintiedosto:
        avain = avaintiedosto.read()
    cipher = Fernet(avain)

    with open("Kuva.png.jpg.enc", "rb") as salattu_tiedosto:
        salattu_data = salattu_tiedosto.read()
    kuva_data = cipher.decrypt(salattu_data)

    # Luo väliaikainen tiedosto
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(kuva_data)
    temp_file.close()

    # Lataa kuva Pygamessa
    kuva = pygame.image.load(temp_file.name)

    # Poista väliaikainen tiedosto pelin sulkeuduttua
    os.unlink(temp_file.name)

    return kuva


card_image = pura_ja_lataa_kuva()
card_original_width, card_original_height = card_image.get_size()

# Skaalataan kortti siten, että se mahtuu näytölle ja säilyttää kuvasuhteen
if card_original_width / card_original_height > WIDTH / HEIGHT:
    # Kortti on leveämpi suhteessa näytön kokoon
    final_width = WIDTH
    final_height = int(card_original_height * (WIDTH / card_original_width))
else:
    # Kortti on korkeampi suhteessa näyttöön
    final_height = HEIGHT
    final_width = int(card_original_width * (HEIGHT / card_original_height))

card_revealed = False
animation_progress = 0  # Arvo välillä 0-1, joka määrittää animaation etenemisen

# Sydämet taustalle
hearts = []  # Lista sydämistä
for _ in range(30):  # Lisää 30 sydäntä alussa
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.uniform(1, 3)  # Satunnainen nopeus
    hearts.append({"x": x, "y": y, "speed": speed})  # Sydämen tiedot


def draw_heart(surface, x, y, size, color):
    """Piirrä sydän (yhdistelmä kaaria ja kolmiota)."""
    half_size = size // 2
    quarter_size = size // 4

    # Piirrä kaksi kaarta sydämen "yläosiksi"
    pygame.draw.circle(surface, color, (x - quarter_size, y), quarter_size)
    pygame.draw.circle(surface, color, (x + quarter_size, y), quarter_size)

    # Piirrä kolmio sydämen "alaosaksi"
    points = [
        (x - half_size, y),  # Vasen yläkulma
        (x + half_size, y),  # Oikea yläkulma
        (x, y + size),       # Sydämen kärki
    ]
    pygame.draw.polygon(surface, color, points)


def draw_hearts():
    """Piirrä siniset sydämet taustalle."""
    for heart in hearts:
        heart["y"] += heart["speed"]  # Liikuta sydäntä alaspäin
        if heart["y"] > HEIGHT:  # Jos sydän menee ruudun ulkopuolelle, siirrä se takaisin ylös
            heart["y"] = -10
            heart["x"] = random.randint(0, WIDTH)
        draw_heart(screen, heart["x"], heart["y"], 20, LILAC)


def draw_game():
    """Piirretään pelin elementit."""
    screen.fill(TURQUOISE)

    # Piirrä siniset sydämet
    draw_hearts()

    # Piirrä tasot
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform)

    # Piirrä tikku-ukko
    # Pää (ympyrä)
    pygame.draw.circle(screen, BLUE, (stickman.x + stickman_size // 2, stickman.y + 10), 10)
    # Vartalo (viiva)
    pygame.draw.line(screen, BLUE, (stickman.x + stickman_size // 2, stickman.y + 20), 
                     (stickman.x + stickman_size // 2, stickman.y + 35), 2)
    # Kädet (viivat)
    pygame.draw.line(screen, BLUE, (stickman.x + stickman_size // 2, stickman.y + 25), 
                     (stickman.x + stickman_size // 2 - 10, stickman.y + 30), 2)
    pygame.draw.line(screen, BLUE, (stickman.x + stickman_size // 2, stickman.y + 25), 
                     (stickman.x + stickman_size // 2 + 10, stickman.y + 30), 2)
    # Jalat (viivat)
    pygame.draw.line(screen, BLUE, (stickman.x + stickman_size // 2, stickman.y + 35), 
                     (stickman.x + stickman_size // 2 - 10, stickman.y + 45), 2)
    pygame.draw.line(screen, BLUE, (stickman.x + stickman_size // 2, stickman.y + 35), 
                     (stickman.x + stickman_size // 2 + 10, stickman.y + 45), 2)

    # Piirrä kakkupalat
    for cake in cake_pieces:
        pygame.draw.rect(screen, BROWN, cake)  # Kakun pohja
        pygame.draw.polygon(screen, RED, [(cake.x, cake.y), (cake.x + 20, cake.y), (cake.x + 10, cake.y - 10)])  # Kakun "kuorrutus"

    # Näytä kerätyt kakut
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Kakut: {cakes_collected}/4", True, BLACK)
    screen.blit(text, (10, 10))


def animate_card():
    """Näytetään animaatio, jossa kortti avautuu."""
    global animation_progress
    animation_progress += 0.02  # Kasvata animaation etenemistä
    if animation_progress > 1:
        animation_progress = 1  # Animaatio valmis

    # Laske kortin koko animaation etenemisen perusteella
    current_width = int(final_width * animation_progress)
    current_height = int(final_height * animation_progress)

    # Keskitetään kortti näytölle
    card_x = (WIDTH - current_width) // 2
    card_y = (HEIGHT - current_height) // 2

    # Skaalaa kortti smoothscale-funktiolla ja piirrä se
    scaled_card = pygame.transform.smoothscale(card_image, (current_width, current_height))
    screen.blit(scaled_card, (card_x, card_y))


# Pääsilmukka
running = True
while running:
    screen.fill(TURQUOISE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ohjaus
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        stickman.x -= stickman_speed
    if keys[pygame.K_RIGHT]:
        stickman.x += stickman_speed
    if keys[pygame.K_SPACE] and velocity_y == 0:  # Hypätään vain, jos tikku-ukko on maassa
        velocity_y = jump_speed

    # Painovoima ja liike
    velocity_y += gravity
    stickman.y += velocity_y

    # Tarkista, onko tikku-ukko tasojen päällä
    on_platform = False
    for platform in platforms:
        if stickman.colliderect(platform) and velocity_y > 0:
            stickman.y = platform.y - stickman_size
            velocity_y = 0
            on_platform = True

    # Pidä tikku-ukko ruudun sisällä
    if stickman.x < 0:
        stickman.x = 0
    if stickman.x > WIDTH - stickman_size:
        stickman.x = WIDTH - stickman_size
    if stickman.y > HEIGHT - stickman_size:
        stickman.y = HEIGHT - stickman_size
        velocity_y = 0

    # Kakkupalojen kerääminen
    for cake in cake_pieces[:]:
        if stickman.colliderect(cake):
            cake_pieces.remove(cake)
            cakes_collected += 1

    # Tarkista, onko kaikki kakut kerätty
    if cakes_collected == 4:
        card_revealed = True

    # Piirrä peli
    if card_revealed:
        animate_card()
    else:
        draw_game()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()