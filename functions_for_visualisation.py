"""
Created by Ivan Danylenko
Date 18.11.21
"""

from PIL import Image
from time import time
from functools import wraps
from ursina import Entity, camera, held_keys

# po raz pierwszy definiuję czas ostatniego wywołania funkcji z ograniczoną częstotliwością wywołań
lastNewSubmarinePosUse = [time()]
lastAddNewSubmarineUse = [time()]


def execution_frequency(cooldown, last_use):
    """ Dekorator, ograniczający częstotliwości wywołań dekorowanej funkcji do 1 razu przez zadany okres czasu.

    Args:
        cooldown (float|int): minimalny czas który musi minąć od poprzedniego wywołania funkcji dla możliwości
            jej ponwnego wywołania.
        last_use (list): lista jednoelementowa, zawierająca czas absolutny poprzedniego wywołania funkcji.

    """

    def _execution_frequency(f):

        @wraps(f)
        def inner(*args, **kwargs):
            if time() - last_use[0] >= cooldown:
                last_use[0] = time()
                f(*args, **kwargs)
        return inner

    return _execution_frequency


def get_max_height(heightmap):
    """ Funkcja zwraca wartość wysokości najwyższego punktu, która wynika z mapy wysokości.

    Args:
        heightmap (str): ścieżka mapy wysokości (miejsce znajdowania się pliku).

    Returns:
        (int): wysokość najwyższego punktu, wynikająca z mapy wysokości
            (wartość kanału R najjaśniejszego piksela na obrazie).

    """

    pixel_alpha = []
    for pixel in list(Image.open(heightmap, 'r').getdata()):
        pixel_alpha.append(round(pixel[0]))
    return max(pixel_alpha)


@execution_frequency(cooldown=0.15, last_use=lastNewSubmarinePosUse)
def new_submarine_pos(submarine: Entity, positions, pool, z_scale):
    """ Nadaje obiektowi który występuje na ekranie w roli łodzi podwodnej wartość pierwszej pozycji z listy i następnie
    usuwa tę warość z tablicy.

    Args:
        submarine (Entity): obiektowi który występuje na ekranie w roli łodzi podwodnej.
        positions (list): zbiór punktów które odwiedziła łódź podwodna.
        pool (Pool): basen do którego jest przypisana łódż podwodna.
        z_scale (float|int): współczynnik skalowania pionowej osi.

    """

    if positions:
        if held_keys['q'] != 0:
            submarine.position = (positions[0][0] - pool.length / 2,
                                  (positions[0][2] + 0.5) * z_scale,
                                  pool.width - 1 - positions[0][1] - pool.width / 2)
            positions.pop(0)


@execution_frequency(cooldown=0.5, last_use=lastAddNewSubmarineUse)
def add_new_submarine(pool, positions):
    """ Funkcja zamienia starą łódź podwodną w basenie nową, wywołuje metodę Pool().submarine.move() i
    zmienia listę odwiedzonych punktów przez poprzedną łódż na wynik wykonania tej metody, jednocześnie zwrazając
    jej wartość.

    Args:
        pool (Pool): basen w którym wystąpi zamiana łodzi podwodnej.
        positions (list): lista pozycji, które odwiedziła stara łódź podwodna.

    Returns:
        (list): lista punktów, które odwiedziła nowa łódź podwodna.

    """
    if held_keys['n'] != 0:
        pool.add_submarine()
        new_positions = pool.submarine.move(True)
        while positions:
            positions.pop()
        for pos in new_positions:
            positions.append(pos)
        return positions


def change_camera_pos():
    """ W zależności od naciśniętej klawiszy W|A|S|D, zmienia położenie kamery w przestrzeni XZ. """

    if held_keys['w'] != 0:
        camera.position = camera.position[0], camera.position[1] + 1, camera.position[2]
    if held_keys['s'] != 0:
        camera.position = camera.position[0], camera.position[1] - 1, camera.position[2]
    if held_keys['a'] != 0:
        camera.position = camera.position[0] - 1, camera.position[1], camera.position[2]
    if held_keys['d'] != 0:
        camera.position = camera.position[0] + 1, camera.position[1], camera.position[2]
