"""
    This is a solution in Python for the Lifeguard problem (see https://ocw.mit.edu/courses/mechanical-engineering/
2-71-optics-spring-2009/assignments/MIT2_71S09_usol1.pdf)

    To run this program, enter the following command:
    python life_guard.py
    Then enter input data from the keyboard (stdin) by following the prompts.

    The program prints the results to the terminal (stdout).

    Author: Konstantin Kuzmin
    Email: kmkuzmin@gmail.com
    Date: 6/5/2026
"""

import math

FEET_IN_YARD = 3
FEET_IN_MILE = 5280
MINS_IN_HOUR = 60
SECS_IN_MIN = 60

d1 = input("Введите кратчайшее расстояние между спасателем и кромкой воды, d1 (ярды) => ")
print(d1)
d1 = float(d1)

d2 = input("Введите кратчайшее расстояние от утопающего до берега, d2 (футы) => ")
print(d2)
d2 = float(d2) / FEET_IN_YARD
h = input("Введите боковое смещение между спасателем и утопающим, h (ярды) => ")
print(h)
h = float(h)

v_sand = input("Введите скорость движения спасателя по песку, v_sand (мили в час) => ")
print(v_sand)
v_sand = float(v_sand) * FEET_IN_MILE / FEET_IN_YARD

n = input("Введите коэффициент замедления спасателя при движении в воде, n => ")
print(n)
n = float(n)

theta1 = input("Введите направление движения спасателя по песку, theta1 (градусы) => ")
print(theta1)
theta1_deg = float(theta1)
theta1_rad = math.radians(theta1_deg)

x = d1 * math.tan(theta1_rad)
L1 = math.sqrt(x**2 + d1**2)
L2 = math.sqrt((h - x)**2 + d2**2)
t = (L1 + n * L2) / v_sand
t = t * MINS_IN_HOUR * SECS_IN_MIN
print(f"Если спасатель начнёт движение под углом theta1, равным {round(theta1_deg)} градусам, он")
print(f"достигнет утопающего через {t:.1f} секунды")
