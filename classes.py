"""
Created by Ivan Danylenko
Date 09.11.21
"""

from copy import deepcopy
from PIL import Image
from random import randint
from math import sqrt


class CubicMetre:
    """ Klasa "metr sześcienny". Egzemplarzami tej klasy wypełnia się basen - egzemplarz klasy Pool().

    Zgodnie ze swoim przeznaczeniem, wypełniacze są umownie podzielone na trzy rodzaje:
    wodny sześcian, ziemny sześcian, źródło dźwięku.
    Metr sześcienny wody może mieć liczbowo zdefiniowany parametr sound_intensity.
    Metr sześcienny terenu (ziemny) nie może mieć liczbowo zdefiniowanego parametru sound_intensity
    i działa również jako bariera.
    Z kolei źródło dźwięku jest pochodną metra sześciennego ziemi, ponieważ tak samo jest barierą,
    ale ma również liczbowo zdefiniowany parametr sound_intensity.

    Attributes:
        x_position (int): współrzędna sześcianu względem osi X.
        y_position (int): współrzędna sześcianu względem osi Y.
        z_position (int): współrzędna sześcianu względem osi Z.
        is_water (bool): True if a cube is composed of water, False otherwise.
        sound_intensity (None|float|int): natężenie dźwięku w danym sześcianie.
        neighbours (list): lista sąsiednich metrów sześciennych; całkowicie składa się z None, jeżeli nie ma sąsiadów,
        i częściowo, jeżeli owi są, ale nie wszyscy.

    """

    def __init__(self, x_position, y_position, z_position, is_water):
        """ Inicjalizacja metru sześciennego.

        Args:
            x_position (int): podawana współrzędna sześcianu względem osi X.
            y_position (int): podawana współrzędna sześcianu względem osi Y.
            z_position (int): podawana współrzędna sześcianu względem osi Z.
            is_water (bool): True if a cube is composed of water, False otherwise.

        """

        self.x_position = x_position
        self.y_position = y_position
        self.z_position = z_position
        self.is_water = is_water

        self.sound_intensity = None
        self.neighbours = deepcopy([None] * 26)


class Pool:
    """ Klasa "basen". Wewnątrz egzemplarza tej klasy przebiega symulacja wodnego środowiska i
    działania łodzi podwodnej.

    Składa się z egzemlarzy klasy CubicMetre() i zawiera w sobie egzemplarze klas CubicMetre() oraz Submarine().
    Prawie całkowicie zależy od wgranej mapy wysokości.

    Args:
        heightmap (str): ścieżka mapy wysokości (miejsce znajdowania się pliku).

    Attributes:
        length (int): długość basenu (wymiar względem osi X).
        width (int): szerokość basenu (wymiar względem osi Y).
        height (int): wysokość basenu (wymiar względem osi Z).
        filling (list): wypełnienie basenu - trójwymiarowa lista, składająca się z egzemplarzy klasy CubicMetre().
        sound_source (CubicMetre): źródło dźwięku - egzemplarz klasy CubicMetre().
        submarine (Submarine): łódź podwodna, aparat autonomiczny - egzemplarz klasy Submarine().

    Methods:
        add_sound_source: dodaje źródło dźwięku do basenu i definiuje sound_intensity dla każdego wodnego sześcianu.
        add_submarine: dodaje łódź podwodną do basenu.

    """

    def __init__(self, height, heightmap):
        """ Inicjalizacja basenu: wypełnienie metrami sześciennymi, tworzenie referencji między sąsiednimi sześcianami,
        dodanie przeszkód (tworzenie terenu).

        Args:
            height (int): wysokość basenu.
            heightmap (str): ścieżka mapy wysokości (miejsce znajdowania się pliku), jako pliku .jpg.

        Raises:
            ValueError: jeżeli podawana wysokość basenu jest niższa lub równa się maksymalnej wysokości terenu,
             wynikającej z mapy wysokości.

        """

        im = Image.open(heightmap, 'r')  # otwieram mapę wysokości jako obrazek
        assert height > max(round(pixel[0]) for pixel in list(im.getdata())), \
            ValueError('The height parameter must be greater than ' + str(max(round(pixel[0]) for pixel in list(im.getdata()))))

        length, width = im.size  # wyciągam parametry mapy według których zbuduje się basen

        # definiuję wymiary basenu
        self.height = height  # z
        self.width = width  # y
        self.length = length  # x

        # Blok, w którym wypełniam basen wodnymi metrami sześciennymi:
        print('Wypełniam basen wodnymi metrami sześciennymi:')
        self.filling = []
        for z_position in range(height):
            layer = []
            for y_position in range(width):
                layer.append(deepcopy([None] * length))
            self.filling.append(deepcopy(layer))

        for z_position in range(height):
            for y_position in range(width):
                for x_position in range(length):
                    self.filling[z_position][y_position][x_position] = CubicMetre(x_position, y_position, z_position, True)
            print('\tLayer', z_position, 'completed.')

        # Blok, w którym tworzę referencje pomiędzy sąsiednimi metrami sześciennymi
        print('Tworzę referencje pomiędzy sąsiednimi metrami sześciennymi:')
        change = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0),
                  (1, 0, -1), (1, 0, 1), (1, 1, 0), (1, -1, 0),
                  (-1, 0, -1), (-1, 0, 1), (-1, 1, 0), (-1, -1, 0),
                  (0, 1, -1), (0, 1, 1), (0, -1, 1), (0, -1, -1),
                  (1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1),
                  (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)]
        for z_position in range(self.height):
            for y_position in range(self.width):
                for x_position in range(self.length):
                    for i in range(26):
                        if x_position + change[i][0] < 0 or x_position + change[i][0] > self.length - 1:
                            continue
                        if y_position + change[i][1] < 0 or y_position + change[i][1] > self.width - 1:
                            continue
                        if z_position + change[i][2] < 0 or z_position + change[i][2] > self.height - 1:
                            continue
                        self.filling[z_position][y_position][x_position].neighbours[i] = \
                        self.filling[z_position + change[i][2]][y_position + change[i][1]][x_position + change[i][0]]
            print('\tLayer', z_position, 'completed.')

        # Blok, w którym zamieniam niektóre sześciany wodne na ziemne, zgodnie z mapą wysokości:
        print('Zamieniam niektóre sześciany wodne na ziemne, zgodnie z mapą wysokości...')
        pixel_values = list(im.getdata())
        pixel_alpha = []
        z = []

        for pixel in pixel_values:
            pixel_alpha.append(round(pixel[0]))

        # tworzę dwuwymiarową liste wartości wysokości "dna" basenu h od położenia względem płaszczyzny XY
        for i in range(0, len(pixel_alpha), width):
            z.append(pixel_alpha[i:i + width])

        for x_position in range(length):
            for y_position in range(width):
                # przez całą wysokość h dna w punkcie (x; y) wodne sześciany zamieniają się na ziemne
                h = z[y_position][x_position]
                for z_position in range(h):
                    self.filling[z_position][y_position][x_position].is_water = False

    def add_sound_source(self, sound_intensity=1000, x_position=None, y_position=None, z_position=None, enhanced_realism=True):
        """ Metoda dodaje źródło dźwięku do basenu i definiuje parametr sound_intensity dla każdego wodnego sześcianu
        (natężenie dźwięku w nim).

        Args:
            sound_intensity (float|int): natężenie dźwięku produkowanego przez źródło dźwięku.
            x_position (int|None): współrzędna źródła dźwięku względem osi X.
            y_position (int|None): współrzędna źródła dźwięku względem osi Y.
            z_position (int|None): współrzędna źródła dźwięku względem osi Z.
            enhanced_realism (bool): jeżeli True - bardziej realistyczne ugięcie fal dźwiękowych wokół przeszkód,
                ale gigantyczna złożoność obliczeniowa. W innym przypadku - względnie niska złożoność obliczeniowa, ale
                mało realistyczne rozchodzenie się fal.

        """

        print('Dodaję źródło dźwięku...')
        # Blok definiowania współrzędnych źródła dźwięku
        # (jeżeli parametry nie zostały podane, współrzędne definiują się losowo):
        if x_position is not None and 0 <= x_position < self.length:  # względem osi X
            x_position = x_position
        else:
            x_position = randint(0, self.length - 1)

        if y_position is not None and 0 <= y_position < self.width:  # względem osi Y
            y_position = y_position
        else:
            y_position = randint(0, self.width - 1)

        # wyznaczam minimalnie możliwe położenie względem pionowej osi (Z)
        z_min = 1
        while self.filling[z_min][y_position][x_position].is_water is False:
            z_min += 1
        # "kładę" źródło dźwięku na samo dno, lub na podaną wysokość
        if z_position is not None and z_min <= z_position < self.height:
            z_position = z_position
        else:
            z_position = z_min

        # dodaję do basenu źródło dźwięku, zastępując nim wodny metr sześcienny o tych samych współrzędnych
        self.filling[z_position][y_position][x_position].sound_intensity = sound_intensity
        self.filling[z_position][y_position][x_position].is_water = False
        self.sound_source = self.filling[z_position][y_position][x_position]

        # Blok, w którym skanuję cały basem i wyznaczam wymiary prostopadłościanu w ramach którego będziemy dokonywać
        # wyboru kolejnego wierzchołku łamanej linii - odległości od źródła dźwięku do pewnego sześcianu wodnego:
        parallelepiped_length = self.length  # x
        parallelepiped_width = self.width  # y

        for z_position in range(self.height):
            # wzdłuż X
            for y_position in range(self.width):
                x_count = 0
                for x_position in range(self.length):
                    if self.filling[z_position][y_position][x_position].is_water is False:
                        x_count += 1
                    elif x_count < parallelepiped_length and x_count != 0:
                        parallelepiped_length = x_count
                        x_count = 0
                if x_count < parallelepiped_length and x_count != 0:
                    parallelepiped_length = x_count

            # wzdłuż Y
            for x_position in range(self.width):
                y_count = 0
                for y_position in range(self.length):
                    if self.filling[z_position][y_position][x_position].is_water is False:
                        y_count += 1
                    elif y_count < parallelepiped_width and y_count != 0:
                        parallelepiped_width = y_count
                        y_count = 0
                if y_count < parallelepiped_width and y_count != 0:
                    parallelepiped_width = y_count

        # definiuję natężenie dźwięku dla każdego wodnego metru sześciennego w basenie
        print('Definiuję natężenie dźwięku dla każdego wodnego metru sześciennego w basenie...')
        for z_position in range(self.height):
            for y_position in range(self.width):
                for x_position in range(self.length):
                    if self.filling[z_position][y_position][x_position].is_water is True:
                        curve_length = shortest_curve(self, (self.sound_source.x_position, self.sound_source.y_position, self.sound_source.z_position),
                                                      (x_position, y_position, z_position),
                                                      (parallelepiped_length, parallelepiped_width),
                                                      enhanced_realism)
                        self.filling[z_position][y_position][x_position].sound_intensity = self.sound_source.sound_intensity / (curve_length ** 2)
            print('\tLayer', z_position, 'completed.')

    def add_submarine(self, x_position=None, y_position=None, z_position=None):
        """ Metoda, dodająca łódź podwodną (aparat autonomicznny) do basenu.

        Args:
            x_position (int|None): współrzędna łodzi podwodnej względem osi X.
            y_position (int|None): współrzędna łodzi podwodnej względem osi Y.
            z_position (int|None): współrzędna łodzi podwodnej względem osi Z.

        """

        self.submarine = Submarine(self, x_position, y_position, z_position)


class Submarine:
    """ Łódź podwodna albo inaczej aparat autonomiczny. Egzemplarz tej klasy ma na celu przemieszczać się w kierunku
    źródła dźwięku w basenie, w tym celu potrzebuje przypisania do konkretnego basenu klasy Pool().

    Note:
        Dla poprawnego działania egzemplarza, w basenie, do którego jest przypisana łódź podwodna, musi być
        zdefiniowany atrybut sound_source poprzez wywołanie metody Pool().add_sound_source().

    Attributes:
        x_position (int): współrzędna łodzi podwodnej względem osi X.
        y_position (int): współrzędna łodzi podwodnej względem osi Y.
        z_position (int): współrzędna łodzi podwodnej względem osi Z.
        pool (Pool): basen - egzemplarz klasy Pool(), do którego będzie przypisana łódź podwodna.

    Methods:
        move: przesuwa łódź podwodną w kierunku źródła dźwięku i zwraca zbiór punktów odwiedzonych przez łódź.

    """

    def __init__(self, pool: Pool, x_position=None, y_position=None, z_position=None):
        """ Inicjalizacja łodzi podwodnej.

        Args:
            pool (Pool): basen, do którego zostanie przypisana łódź podwodna.
            x_position (int): współrzędna łodzi podwodnej względem osi X.
            y_position (int): współrzędna łodzi podwodnej względem osi Y.
            z_position (int): współrzędna łodzi podwodnej względem osi Z.

        """

        # Blok definiowania współrzędnych łodźi podwodnej
        # (jeżeli parametry nie zostały podane, współrzędne definiują się losowo):
        if x_position is not None and 0 <= x_position < pool.length:  # względem osi X
            x_position = x_position
        else:
            x_position = randint(0, pool.length - 1)

        if y_position is not None and 0 <= y_position < pool.width:  # względem osi Y
            y_position = y_position
        else:
            y_position = randint(0, pool.width - 1)

        # wyznaczam minimalnie możliwe położenie względem pionowej osi (Z)
        z_min = 1
        while pool.filling[z_min][y_position][x_position].is_water is False:
            z_min += 1
        # zmieszczam łódź podwodną na wysokości w zakresie [z_min; pool.height), lub na podanej wysokości
        if z_position is not None and z_min <= z_position < pool.height:
            z_position = z_position
        else:
            z_position = randint(z_min, pool.height - 1)

        self.x_position = x_position
        self.y_position = y_position
        self.z_position = z_position
        self.pool = pool

    def move(self, moves=1):
        """ Metoda przesuwa łódź podwodną w ramach basenu w kierunku źródła dźwięku zmieniając jej współrzędne
        po każdym ruchu i na koniec zwraca zbiór punktów (współrzędne wodnych metrów sześciennych), które
        odwiedziła łódź podczas wykonywania metody.

        Note:
            Jeżeli argument moves, podany w postaci liczby całkowitej, przekroczy liczbę ruchów potrzebną do
            "dopłynięcia" do źródła dźwięku, to będzie równoznaczne podaniu jego jako logicznej wartości True.

        Args:
            moves (int|bool): ilość ruchów do wykonania [1; ∞). Jeżeli True, to przemieszczać się do momentu
                "dopłynięcia" do źródła dźwięku.

        Returns:
            list: zbiór punktów (współrzędne wodnych metrów sześciennych), które odwiedziła łódź
                podczas wykonywania metody.

        Raises:
            ValueError: jeżeli parametr moves został podany niewłaściwie.

        """

        assert (moves >= 1) or (moves is True), ValueError('Parameter "metres" must be greater integer than 0 or boolean True.')

        # punkt początkowy (współrzędne wodnego sześcianu w którym "znajduje się" łódź podwodna
        xyz_to_move = (self.x_position, self.y_position, self.z_position)

        positions = []  # lista przeznaczona do zapisu wszystkich odwiedzonych punktów, łącznie z początkowym
        while moves:

            positions.append(xyz_to_move)  # dodaję do listy współrzędne odwiedzonego punktu (sześcianu)
            # lista zawierająca listy danych w postaci [natężenie dźwięku które ma sąsiad, (współrzędne sąsiada)]
            comparison = []

            for neighbour in self.pool.filling[self.z_position][self.y_position][self.x_position].neighbours:  # iteruje się po wszystkich sąsiadach
                if (neighbour is not None) and (neighbour.sound_intensity is not None):
                    # jeżeli sąsiad istnieje i ma liczbowo zdefiniowane natężenie dźwięku
                    sound_intensity = neighbour.sound_intensity
                    xyz_to_move = (neighbour.x_position, neighbour.y_position, neighbour.z_position)
                    comparison.append([sound_intensity, xyz_to_move])
            comparison.sort(key=lambda x: x[0])  # sortuje w porządku rosnącym natężeń dźwięku

            xyz_to_move = comparison[-1][1]  # wybieram sąsiada z największym natężeniem dźwięku
            # jeżeli wybrany sąsiad ma takie same natężenie dźwięku co i sześcian wodny w którym w danym momencie
            # znajduje się łódź podwodna, to oznacza, że łódź znajduje się obok źródła dźwięku ("dopłynęła")
            if comparison[-1][0] == self.pool.filling[self.z_position][self.y_position][self.x_position].sound_intensity:
                return positions
            if moves is not True:
                moves -= 1

            # jeżeli jeszcze nie "dopłynęła", zmieniam współrzędne łodzi podwodnej na współrzędne wybranego sąsiedniego sześcianu
            self.x_position = xyz_to_move[0]
            self.y_position = xyz_to_move[1]
            self.z_position = xyz_to_move[2]

        return positions


def shortest_curve(pool: Pool, ss_xyz, cube_xyz, prl_lw, enhanced_realism=True):
    """ Funkcja zwraca długość najkrótszej możliwej łamanej linii (w ramach możliwości algorytmu), którą musi pokonać
    fala dźwiękowa, żeby dotrzeć do pewnego wodnego metru sześciennego (od źródła dźwięku). Jako wierzchołki łamanej
    wybierają się jedynie wodne metry sześcienne, co imituje mechanizm ugięcia fali dźwiękowej wokół przeszkód.

    Note:
        Parametr prl_lw musi definiować się jako minimalnie możliwe wymiary X i Y przeszkód, które występują w basenie.
        Taki prostopadłościan pozwala na wybór wierzchołku łamanej tak, by było to bardziej zbliżone do rzeczywistości,
        a parametr prl_lw eliminuje możliwość całkowitego przejścia odcinka przez przeszkodę (możliwe jest tylko
        "ścinanie" przeszkód przy dyżych wymiarach prostopadłościanu).

        W trybie enhanced_realism=True fale dokonują ugięcia najkrótszym możliwym sposobem, natomiast bez tego trybu
        fale dokonują ugięcia wyłącznie nad przeszkodą (czyli nie uginają się z boku przeszkody) niezależnie od
        wysokości i szerokości przeszkody.

    Args:
        pool (Pool): basen.
        ss_xyz (tuple|list): współrzędne lokalizacji źródła dźwięku (sound source XYZ).
        cube_xyz (tuple|list): współrzędne lokalizacji wodnego sześcianu do którego obliczamy długość łamanej.
        prl_lw (tuple|list): wymiary prostopadłościanu, w ramach którego można dokonać wyboru nowego wierzchołka
            łamanej, nie zaburzając zbytnio mechanizmu ugięcia fali (parallelepiped length, width).
        enhanced_realism (bool): jeżeli True - bardziej realistyczne ugięcie fal dźwiękowych wokół przeszkód,
            ale gigantyczna złożoność obliczeniowa. W innym przypadku - względnie niska złożoność obliczeniowa, ale
            mało realistyczne rozchodzenie się fal.

    Returns:
        float|int: curve_len - długość łamanej od źródła dźwieku do podanego sześcianu wodnego.

    Raises:
        ValueError: jeżeli sześcian-target według podanych współrzędnych cube_xyz nie jest wodnym:
            CubicMetre().is_water is False.

    """

    # sprawdzam, czy wybrany metr sześcienny jest wodny
    assert pool.filling[cube_xyz[2]][cube_xyz[1]][cube_xyz[0]].is_water is True, \
        ValueError('To determine the intensity of the sound, the cube must be composed of water')
    # jeżeli sześcian już ma zdefiniowane natężenie dźwięku
    if pool.filling[cube_xyz[2]][cube_xyz[1]][cube_xyz[0]].sound_intensity is not None:
        return sqrt(pool.filling[cube_xyz[2]][cube_xyz[1]][cube_xyz[0]].sound_intensity / pool.sound_source.sound_intensity)

    # definiuję odległości od wierzchołku do sześcianu-targetu
    x_dto = abs(cube_xyz[0] - ss_xyz[0])  # dto - distance to overcome
    y_dto = abs(cube_xyz[1] - ss_xyz[1])
    z_dto = abs(cube_xyz[2] - ss_xyz[2])

    # wyznaczam najlepsze pozycje na osi Z, sortując od najbliższej do współrzędnej Z sześcianu-targetu do najdalszej
    z_poss = []
    for z_pos in range(pool.height):
        z_poss.append([abs(cube_xyz[2] - z_pos), z_pos])
    z_poss.sort(key=lambda x: x[0])

    curve_len = 0

    while x_dto + y_dto + z_dto != 0:
        np_xyz = ss_xyz  # new point XYZ - współrzędne nowego wierzchołku łamanej

        if enhanced_realism is True:
            xyz_poss = []
            for z_pos in range(pool.height):  # w zakresie wysokości basenu

                for y_pos in range(ss_xyz[1] - prl_lw[1], ss_xyz[1] + prl_lw[1] + 1):  # Y w ramach prostopadłościanu wyboru
                    if 0 <= y_pos < pool.width:  # jeżeli wybrany punkt znajduje się w ramach basenu

                        for x_pos in range(ss_xyz[0] - prl_lw[0], ss_xyz[0] + prl_lw[0] + 1):  # X w ramach prostopadłościanu wyboru
                            if 0 <= x_pos < pool.length:  # jeżeli wybrany punkt znajduje się w ramach basenu

                                # wyznaczam odległości od ewentualnie nowego wierzchołku do sześcianu-targetu
                                x_dto = abs(cube_xyz[0] - x_pos)
                                y_dto = abs(cube_xyz[1] - y_pos)
                                z_dto = abs(cube_xyz[2] - z_pos)

                                # dodaję do listy sumę pozostałych odległości oraz nowe współrzędne, żeby później wybrać jak najlepsze
                                xyz_poss.append([x_dto + y_dto + z_dto, x_dto + y_dto, (x_pos, y_pos, z_pos)])

            xyz_poss.sort(key=lambda x: x[0])  # sortuję od najlepszej pozycji do najgorszej (rośnie suma odległości)

            for i in range(len(xyz_poss)):
                if xyz_poss[i][0] < abs(cube_xyz[0] - ss_xyz[0]) + abs(cube_xyz[1] - ss_xyz[1]) + abs(cube_xyz[2] - ss_xyz[2]):
                    # jeżeli zbliżamy się do celu względem trzech osi (czyli nie oddalamy się ani nie stoimy na miejscu)
                    if xyz_poss[i][1] <= abs(cube_xyz[0] - ss_xyz[0]) + abs(cube_xyz[1] - ss_xyz[1]):
                        # jeżeli nie oddalamy się od punktu końcowego w płaszczyźnie XY (ten warunek nie pozwala zrabić ruch do tyłu)
                        x_pos = xyz_poss[i][2][0]
                        y_pos = xyz_poss[i][2][1]
                        z_pos = xyz_poss[i][2][2]
                        if pool.filling[z_pos][y_pos][x_pos].is_water is True:
                            # jeżeli metr sześcienny o tych współrzędnych jest wodny, wybieram jego współrzędne jako nowy wierzchołek
                            np_xyz = (x_pos, y_pos, z_pos)
                            break

        # jeżeli nie udało się wybrać najlepszego sześcianu z poprzednich warunków, lub nie został wybrany tryb enhanced_realist
        if np_xyz == ss_xyz:
            xy_poss = []
            for y_pos in range(ss_xyz[1] - prl_lw[1], ss_xyz[1] + prl_lw[1] + 1):  # Y w ramach prostopadłościanu wyboru
                if 0 <= y_pos < pool.width:  # jeżeli wybrany punkt znajduje się w ramach basenu

                    for x_pos in range(ss_xyz[0] - prl_lw[0], ss_xyz[0] + prl_lw[0] + 1):  # X w ramach prostopadłościanu wyboru
                        if 0 <= x_pos < pool.length:  # jeżeli wybrany punkt znajduje się w ramach basenu

                            # wyznaczam odległości od ewentualnie nowego wierzchołku do sześcianu-targetu
                            x_dto = abs(cube_xyz[0] - x_pos)
                            y_dto = abs(cube_xyz[1] - y_pos)

                            # dodaję do listy sumę pozostałych odległości oraz nowe współrzędne, żeby później wybrać jak najlepsze
                            xy_poss.append([x_dto + y_dto, (x_pos, y_pos)])

            xy_poss.sort(key=lambda x: x[0])  # sortuję od najlepszej pozycji do najgorszej (rośnie suma odległości)

            for i in range(len(xy_poss)):
                # wybieram najlepsze możliwe współrzędne w płaszczyźnie XY
                x_pos = xy_poss[i][1][0]
                y_pos = xy_poss[i][1][1]
                for j in range(len(z_poss)):
                    # wybieram najlepszą współrzędną na osi Z
                    z_pos = z_poss[j][1]
                    if pool.filling[z_pos][y_pos][x_pos].is_water is True:
                        # jeżeli metr sześcienny o tych współrzędnych jest wodny, wybieram jego współrzędne jako nowy wierzchołek łamanej
                        np_xyz = (x_pos, y_pos, z_pos)
                        break
                if np_xyz != ss_xyz:
                    break

        # po wybraniu nowego wierzchołka z twierdzenia Pitagorasa obliczam jego odległość od poprzedniego wierzchołka
        # i zwiększam długość łamanej o obliczoną wartość
        curve_len += sqrt((np_xyz[0] - ss_xyz[0]) ** 2 + (np_xyz[1] - ss_xyz[1]) ** 2 + (np_xyz[2] - ss_xyz[2]) ** 2)
        ss_xyz = np_xyz  # redefiniuję poprzedni wierzchołek

        # wyznaczam odległości od ostatniego wierzchołku do sześcianu-targetu, żeby w kolejnej iteracji sprawdzić,
        # czy nie trafiłem jeszcze do celu
        x_dto = abs(cube_xyz[0] - ss_xyz[0])
        y_dto = abs(cube_xyz[1] - ss_xyz[1])
        z_dto = abs(cube_xyz[2] - ss_xyz[2])

    return curve_len
