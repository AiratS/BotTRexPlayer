"""
BotTRexPlayer 
===

Играет в игру из автономного режима Chrome 
Программа имеет такую особенность что, она учиться играть в игру сама. 
Для самообучения был применен генетический алгоритм.
===

Бот был протестирован на ноутбуке с разрешением экрана 1366x768
===

Для проверки бота выполните следующие шаги: 
- Откройте игру по сслыке http://www.trex-game.skipser.com/
- Один раз запустите эту игру нажатием на пробел
- Запустите данный скрипт. У вас есть 3 секунды до того как бот начнет работать 
- Бот начнет обучаться играть в эту игру
- После нескольких поколений особи начнут играть довольно таки хорошо 

(на 108 строчке есть список из обученных моделей)
"""

from time import sleep, time
from random import randint, uniform
import numpy as np
from PIL import ImageGrab, ImageOps
import pyautogui
import winsound


INDIVIDUALS_COUNT = 10
GENERATION_COUNT = 10
# -------------------------------
MIN_DISTANCE = 5
MAX_DISTANCE = 85
MIN_WINDOW_WIDTH = 35
MAX_WINDOW_WIDTH = 60
MIN_WINDOW_HEIGHT = 35
MAX_WINDOW_HEIGHT = 60
MIN_JUMP_LEVEL = 1980
MAX_JUMP_LEVEL = 5150
MIN_SPACE_PRESS_TIME = 0.01
MAX_SPACE_PRESS_TIME = 0.1
# -------------------------------
GAME_TIME = 0
DST = 1
W_WDTH = 2
W_HGTH = 3
JMP = 4
SP_TIME = 5
# -------------------------------

class Coords():
    dino_pos = 449
    ground_pos = 425
    reply_btn = (682, 391)
    reply_btn_pol = (668, 380, 670, 382)

class Control:
    @staticmethod
    def restart_game():
        while Control.is_game_over():
            pyautogui.doubleClick(Coords.reply_btn[0], Coords.reply_btn[1], interval=0.25)

    @staticmethod
    def jump(pressTime):
        pyautogui.keyDown("space")
        sleep(pressTime)
        pyautogui.keyUp("space")

    @staticmethod
    def beep():
        frequency = 2500
        duration = 200
        winsound.Beep(frequency, duration)

    @staticmethod
    def get_tree_value(distance, width, height):
        x1 = Coords.dino_pos + distance
        y1 = Coords.ground_pos - height
        x2 = x1 + width
        y2 = Coords.ground_pos
        img = ImageGrab.grab((x1, y1, x2, y2))
        gray_img = ImageOps.grayscale(img)
        arr = np.array(gray_img.getcolors())
        return arr.sum()

    @staticmethod
    def is_game_over():
        img = ImageGrab.grab(Coords.reply_btn_pol)
        gray_img = ImageOps.grayscale(img)
        arr = np.array(gray_img.getcolors())
        return arr.sum() == 87

def init_individuals_list():
    individuals_list_loc = []
    for i in range(0, INDIVIDUALS_COUNT):
        individuals_list_loc.append([
            0,  # GAME TIME
            randint(MIN_DISTANCE, MAX_DISTANCE),                  # DISTANCE
            randint(MIN_WINDOW_WIDTH, MAX_WINDOW_WIDTH),          # WINDOW_WIDTH
            randint(MIN_WINDOW_HEIGHT, MAX_WINDOW_HEIGHT),        # WINDOW_HEIGHT
            randint(MIN_JUMP_LEVEL, MAX_JUMP_LEVEL),              # JUMP LEVEL
            round(uniform(MIN_SPACE_PRESS_TIME, MAX_SPACE_PRESS_TIME), 2)   # SPACE PRESS TIME
        ])

        # Bunch of Trained models
        # individuals_list_loc = [[83.54577851295471, 69, 58, 40, 2571, 0.07], [83.54577851295471, 69, 58, 41, 2571, 0.03], [83.54577851295471, 69, 50, 40, 2571, 0.07], [83.54577851295471, 69, 50, 40, 2571, 0.07], [83.54577851295471, 69, 60, 40, 2571, 0.07], [83.54577851295471, 69, 58, 40, 2571, 0.07], [83.54577851295471, 69, 58, 40, 2571, 0.07], [83.54577851295471, 69, 58, 40, 2571, 0.07], [72.24413204193115, 69, 58, 40, 2571, 0.07], [83.54577851295471, 69, 58, 40, 2571, 0.07]]
    return individuals_list_loc

def play_individual(individual):
    Control.restart_game()
    bgn = time()
    while True:
        if Control.is_game_over():
            end = time()
            return end - bgn

        jump_level = individual[JMP]
        tree_value = Control.get_tree_value(individual[DST], individual[W_WDTH], individual[W_HGTH])
        if tree_value >= jump_level:
            press_time = individual[SP_TIME]
            Control.jump(press_time)


def sort_best_players(individuals_list):
    individuals_list.sort()

def chose_partner(max_count, except_num):
    while True:
        rand = randint(0, max_count - 1)
        if rand != except_num:
            return rand

def make_children(individuals_list):
    children = []
    len = individuals_list.__len__()
    medium = int(len / 2)
    best = individuals_list[medium:len]
    best_len = best.__len__()
    for i in range(0, best_len):
        male = best[i]
        female = best[chose_partner(best_len, i)]
        children.append(make_child(male, female))
        female = best[chose_partner(best_len, i)]
        children.append(make_child(male, female))
    return children

def mutate(gen):
    if gen == DST:
        return randint(MIN_DISTANCE, MAX_DISTANCE)  # DISTANCE
    elif gen == W_WDTH:
        return randint(MIN_WINDOW_WIDTH, MAX_WINDOW_WIDTH)  # WINDOW_WIDTH
    elif gen == W_HGTH:
        return randint(MIN_WINDOW_HEIGHT, MAX_WINDOW_HEIGHT)  # WINDOW_WIDTH
    elif gen == JMP:
        return randint(MIN_JUMP_LEVEL, MAX_JUMP_LEVEL)  # WINDOW_WIDTH
    elif gen == SP_TIME:
        return round(uniform(MIN_SPACE_PRESS_TIME, MAX_SPACE_PRESS_TIME), 2)  # SPACE PRESS TIME

def make_child(male, female):
    child = [
        0,
        male[DST],
        female[W_WDTH],
        male[W_HGTH],
        female[JMP],
        male[SP_TIME]
    ]

    mutated_gen = randint(0, 10)
    if mutated_gen != 0 and mutated_gen < 6:
        child[mutated_gen] = mutate(mutated_gen)
    return child

def main():
    sleep(3)

    individuals_list_loc = init_individuals_list()
    for gen in range(0, GENERATION_COUNT):
        for individual in individuals_list_loc:
            time = play_individual(individual)
            individual[GAME_TIME] = time

        #print(individuals_list_loc)
        sort_best_players(individuals_list_loc)
        individuals_list_loc = make_children(individuals_list_loc)

if __name__ == "__main__":
    main()