import sys
import numpy as np
import re
import random
from collections import deque

# USO: main.py <nombre del fichero>
if len(sys.argv) == 1:
    print('Te falta el nombre del txt')
filename = sys.argv[1]
result_filename = f'result_{filename}.txt'
filename = filename if filename.startswith('input') else f'input/{filename}'
filename = filename if filename.endswith('txt') else f'{filename}.txt'
pattern = re.compile(r'/(.*).txt')

# leer datos del programa
with open(filename, 'r') as file:
    duration, intersections, n_streets, n_cars, bonus = file.readline().split(' ')
    duration = int(duration)
    intersections = int(intersections)
    n_streets = int(n_streets)
    n_cars = int(n_cars)
    bonus = int(bonus)
    # Creates a NxN intersection Matrix
    # Bounding weight is defined by the cost of pass throught
    world = np.ones((intersections, intersections),
                    dtype=np.uint64) * np.iinfo(np.int64).max

    # diccionario nombre -> vertice_1, vertice_2, peso
    streets_by_name = dict()
    streets_by_pos = dict()
    for _ in range(n_streets):
        begin_inter, end_inter, street_name, street_length = file.readline().split(' ')
        begin_inter = int(begin_inter)
        end_inter = int(end_inter)
        street_length = int(street_length)
        world[begin_inter, end_inter] = street_length
        streets_by_name[street_name] = (begin_inter, end_inter, street_length)
        streets_by_pos[(begin_inter, end_inter)] = street_name

    cars = []
    i = 0

    #  list of cars -> [calle1,calle2,calleN]
    n_cars_by_street = dict()
    scores_by_street = dict()
    for _ in range(n_cars):
        car_data = file.readline().split(' ')[:-1]
        streets_driven_by_car = car_data[1:]
        car_duration = sum(
            map(lambda name: streets_by_name[name][2], streets_driven_by_car))
        if car_duration <= duration:
            car_score = bonus + (duration - car_duration)
            cars.append(streets_driven_by_car)

            # n_cars_by_street = {street_name : 0 for street_name in streets_driven_by_car}
            for street_name in streets_driven_by_car:
                if street_name in n_cars_by_street:
                    n_cars_by_street[street_name] += 1
                else:
                    n_cars_by_street[street_name] = 1
                if street_name in scores_by_street:
                    scores_by_street[street_name] += car_score
                else:
                    scores_by_street[street_name] = car_score

# ^^^^^ lectura input

# schedule: (id_vertice) -> (lista [(calle, duracion), (calle, duracion)])


def get_schedule():
    schedule = dict()
    for i in range(intersections):
        out_streets = np.argwhere(world[:, i] < 100_000_000).T[0]

        street_names = list(
            map(lambda out: streets_by_pos[(out, i)], out_streets))

        if any(street_name in n_cars_by_street for street_name in street_names):
            street_names = list(
                filter(lambda name: name in n_cars_by_street, street_names))
            street_weights = list(
                map(lambda name: scores_by_street[name], street_names))
            min_weight = min(street_weights)
            schedule[i] = list()
            t = 0
            for name, weight in sorted(zip(street_names, street_weights), key=lambda t: t[1], reverse=True):
                duration = max(int(np.sqrt(weight // min_weight) + 0.5),  1)
                schedule[i].append((name, duration, t))
                t += duration

        # round-robin algorithm
        # schedule[i] = list(
        #     map(lambda out: (streets_by_pos[(out, i)], 1), out_streets))

        # round-robin algorithm (filtering empty streets)
        # schedule[i] = list()
        # street_names = list(map(lambda out: streets_by_pos[(out, i)], out_streets))
        # if any(street_name in n_cars_by_street for street_name in street_names):
        #     for out, street_name in zip(out_streets, street_names):
        #         if street_name in n_cars_by_street:
        #             schedule[i].append((street_name, 1))
        # round-robin algorithm (filtering empty streets)
    return schedule


class Car:
    current_street = 0
    Time_2_Intersect = 0

    def nextTime(self, time):
        self.Time_2_Intersect -= time


def update_score(kars):

    def wait_at_stoplight(street_name, t):
        intersection = streets_by_name[street_name][1]  # end-inter
        inter_schedule = schedule[intersection]
        total_schedule_length = sum(map(lambda t: t[1], inter_schedule))
        mod_t = t % total_schedule_length
        my_street_schedule = next(
            filter(lambda t: t[0] == street_name, inter_schedule))
        green_light_t = my_street_schedule[2]
        my_street_duration = my_street_schedule[1]
        if t >= green_light_t and t < green_light_t + my_street_duration:
            return 0
        else:
            return (mod_t - green_light_t) % total_schedule_length

    def get_n_cars_by_street(cars):
        n_cars_by_street = dict()
        car_by_steet = dict()
        for car in cars:
            street_name = car[1][car[0]]
            if street_name in n_cars_by_street:
                car_by_steet[street_name] = car
                n_cars_by_street[street_name] += 1
            else:
                n_cars_by_street[street_name] = 1
        return n_cars_by_street, car_by_steet

    kars = [(0, car) for car in kars]

    t = 0
    history = dict()
    while t < duration:
        n_cars_by_street, car_by_steet = get_n_cars_by_street(kars)
        for street_name, car in car_by_steet.items():
            if wait_at_stoplight(street_name, t) == 0:
                car = (car[0] + 1, car[1])
                # if car[0] == len(car[1]):
                #     cars.remove(car)
            if street_name not in history:
                history[street_name] = n_cars_by_street[street_name]
            else:
                history[street_name] += n_cars_by_street[street_name]
        for street_name, street_history in history.items():
            scores_by_street[street_name] += int(72 *
                                                 street_history // duration)
        # for street_name, n_c in n_cars_by_street.items():
        #     scores_by_street[street_name] += n_c * 72
        t += 1

    # t = 0
    # total_wait = 0
    # # Stops along all our driving way
    # scores = []
    # for street_name in car:
    #     wait = wait_at_stoplight(street_name, t)
    #     scores.append((street_name, wait))
    #     t += wait
    #     total_wait += wait
    #     t += streets_by_name[street_name][2]

    # if t < duration * 0.9:
    #     bonus = 72
    # else:
    #     bonus = 7.2

    # for street_name, wait in scores:
    #     scores_by_street[street_name] += bonus * wait
    #     scores_by_street[street_name] = max(1, scores_by_street[street_name])


for i in range(10):
    print(i)
    schedule = get_schedule()
    update_score(cars)


# vvvvv escritura output
with open(result_filename, 'w+') as file:
    # A: no. of intersections
    file.write(f'{len(schedule)}\n')
    for vertex_id, schedule_streets in schedule.items():
        # i: id, e_i: number of incoming streets
        file.write(f'{vertex_id}\n{len(schedule_streets)}\n')
        for street_name, duration, _ in schedule_streets:
            # street name y green light timing
            file.write(f'{street_name} {duration}\n')
