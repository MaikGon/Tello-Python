# Tello Line Follower

Projekt na zajęcia z Autonomicznych Robotów Latających prowadzonych na Politechnice Poznańskiej.

## Opis projektu

W folderze 'Tello_Video' znajduje się plik line_follower.py, w którym zawarte zostały funkcje pozwalające na autonomiczne podążanie drona Tello po wyznaczonej trasie na ścianie danego pomieszczenia. Założeniem projektowym jest to, aby dron leciał zawsze w prawo.


## Funkcje

### threshold
Odpowiada za prawidłowe sprogowanie ścieżki, po które ma poruszać się dron. Ściężka powinna mieć kolor czerwony.

### contours
Odpowiada za wykrywanie konturów znaczników w postaci kwadratowych kartek, aby móc sterować odległością od ściany.

### getSensorOut
Odpowiada za zliczanie pikseli w 3 częściach obrazu (część górna, środkowa oraz dolna). Dron zostanie wysterowany w zależności od tego w których częściach obrazu zliczy odpowiednią ilość białych pikseli. Obiektem wyjściowym jest tablica 1x3 zawierająca wartości 0 lub 1.

1 - ścieżka

0 - brak ścieżki


### distance_control
Odpowiada za nadanie prędkości drona w zależności od tego w jakiej odległości znajduje się od ściany.

### send_commands
Na podstawie tablicy wartości funkcji getSensorOut oraz distance_control nadawane są odpowiednie prędkości góra/dół oraz przód/tył, aby dron utrzymał się na wytyczonej ścieżce.


## Dodatkowe pliki

### video_mod.py
Moduł pozwalający na nagrywanie obrazu, który widzi drona.

### color_setter.py
Moduł pozwalający na ręczne dobranie wartości hsv do progowania ścieżki oraz znaczników odległości.



