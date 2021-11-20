"""
Created by Ivan Danylenko
Date 09.11.21
"""

#  Zarządzanie symulacją:
#       Zarządzanie położeniem kamery w przestrzeni XZ:     Press W|A|S|D
#       Zarządzanie kątem nachylenia kamery:                Hold RMB and drag
#       ZOOM:                                               Scroll
#       Pokazać kolejne położenie łodzi podwodnej:          Press Q (delay 0.15s)
#       Tworzenie nowej łodzi podwodnej:                    Hold N for 0.5s (delay 0.5s) then press Q 1 time
#  Uwaga: nowa łódź podwodna generuje się na losowych współrzędnych

from ursina import *
from classes import Pool
from functions_for_visualisation import *


def update():
    # definiowanie łodzi podwodnej i wyznaczanie jej położeń w drodze do źródła dźwięku
    add_new_submarine(pool, submarine_positions)
    new_submarine_pos(submarine, submarine_positions, pool, z_scale)  # wyznaczanie położenia łodźi do wizualizacji
    change_camera_pos()  # zarządzanie kamerą


heightmap = 'Heightmaps/heightmap_demonstration.jpg'  # ścieżka mapy wysokości
z_scale = 1  # współczynnik skalowania wizualizacji pionowej osi

# tworzenie wodnego środowiska, źródła dźwięku oraz łodzi podwodnej
pool = Pool(get_max_height(heightmap) + 1, heightmap)  # basen jed o wysokości wyższej o 1 od maksymalnej wysokości terenu
pool.add_sound_source(enhanced_realism=True)
pool.add_submarine()

# wyciągam wymiary basenu
length = pool.length
width = pool.width

# wyznaczam wizuaizowane położenie źródła dźwięku i łodzi podwodnej
sound_source_pos = (pool.sound_source.x_position - length / 2,
                    (pool.sound_source.z_position + 0.5) * z_scale,
                    width - 1 - pool.sound_source.y_position - width / 2)
submarine_pos = (pool.submarine.x_position - length / 2,
                 (pool.submarine.z_position + 0.5) * z_scale,
                 width - 1 - pool.submarine.y_position - width / 2)

# tworzenie sceny
app = Ursina()
window.color = color.white
window.fullscreen = True
camera.position = (get_max_height(heightmap) * 6 / 108 * z_scale,
                   get_max_height(heightmap) * 33 / 108 * z_scale,
                   - get_max_height(heightmap) * 207 / 108 * z_scale)  # początkowe położenie kamery zależy od wysokości basenu

# dodaję oświetlenie
AmbientLight(color=(0.5, 0.5, 0.5, 1))
DirectionalLight(color=(0.5, 0.5, 0.5, 1), direction=(1, 1, 0))

# wizualizuję teren i dwie kuli, wizualizujące źródło dźwięku i łódż podwodną (czerwona i zielona odpowiednio)
landschaft = Entity(model=Terrain(heightmap, skip=1, pool_terrain=True),
                    scale=(length, z_scale, width),
                    # jeżeli istnieje odpowiedni plik z teksturą, trzeba odkomentować niższą linijkę
                    # texture=heightmap[:len(heightmap)-4]+'_texture.jpg',
                    # w przeciwnym przypadku zakomentować wyższą linijkę i odkomentować niższą
                    texture=heightmap
                    )
sound_source = Entity(model='sphere', position=sound_source_pos, color=color.red)
# płynna zmiana położenia łodzi podwodnej: niższy obiekt Entity płynnie podąża za położeniem łodzi
submarine = Entity(position=submarine_pos)
Entity(model='sphere', position=submarine_pos, color=color.green).add_script(SmoothFollow(speed=5,
                                                                                          target=submarine,
                                                                                          offset=(0, 0, 0)))
# imitacja wody - półprzezroczysty niebieski sześcian o wymiarach basenu
Entity(model='cube', scale=(landschaft.scale[0],
                            get_max_height(heightmap) * landschaft.scale[1] + 2,
                            landschaft.scale[2]),
       color=color.blue, alpha=0.15, position=(0, get_max_height(heightmap) * landschaft.scale[1] / 2, 0))

# wyznaczanie wszystkich punktów, odwiedzonych przez pierwszą submarynę, w drodze do źródła dźwięku
submarine_positions = pool.submarine.move(True)

# mouse.visible = False
EditorCamera()  # możliwość zarządzania kamerą myszką
app.run()
