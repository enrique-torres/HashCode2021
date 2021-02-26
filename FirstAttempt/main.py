import sys
import numpy as np
import re
import random

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
    for _ in range(n_cars):
        car_data = file.readline().split(' ')[:-1]
        streets_driven_by_car = car_data[1:]
        car_duration = sum(
            map(lambda name: streets_by_name[name][2], streets_driven_by_car))
        if car_duration <= duration:
            cars.append(streets_driven_by_car)

            # n_cars_by_street = {street_name : 0 for street_name in streets_driven_by_car}
            for street_name in streets_driven_by_car:
                if street_name in n_cars_by_street:
                    n_cars_by_street[street_name] += 1
                else:
                    n_cars_by_street[street_name] = 1

# ^^^^^ lectura input

# schedule: (id_vertice) -> (lista [(calle, duracion), (calle, duracion)])
schedule = dict()
for i in range(intersections):
    out_streets = np.argwhere(world[:, i] < 100_000_000).T[0]

    # street_names = list(map(lambda out: streets_by_pos[(out, i)], out_streets))
    # street_weights = list(
    #     map(lambda name: n_cars_by_street.get(name, 0), street_names))
    # total_weights = sum(street_weights)
    # for street_name in street_names:

    # schedule[i] = list(
    #     map(lambda out: (streets_by_pos[(out, i)], max()), out_streets))

    # round-robin algorithm
    # schedule[i] = list(
    #     map(lambda out: (streets_by_pos[(out, i)], 1), out_streets))

    # round-robin algorithm (filtering empty streets)
    schedule[i] = list()
    street_names = list(map(lambda out: streets_by_pos[(out, i)], out_streets))
    for out, street_name in zip(out_streets, street_names):
        if street_name in n_cars_by_street:
            schedule[i].append((street_name, 1))


# vvvvv escritura output

with open(result_filename, 'w+') as file:
    # A: no. of intersections
    file.write(f'{len(schedule)}\n')
    for vertex_id, schedule_streets in schedule.items():
        # i: id, e_i: number of incoming streets
        file.write(f'{vertex_id}\n{len(schedule_streets)}\n')
        for street_name, duration in schedule_streets:
            # street name y green light timing
            file.write(f'{street_name} {duration}\n')
