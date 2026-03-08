from data import *
from engine import *
import matplotlib.pyplot as plt

EARTH_GRAVITY = 9.80665
THRUST_CONSTANT = 1.5

lox_rp1 = Propellant(1.24, 21.9, 3571)
engine = Engine(lox_rp1, 7000000, 0)

dry_mass = 10000
wet_mass = 40000
total_mass = dry_mass + wet_mass
thrust_needed = total_mass * THRUST_CONSTANT * EARTH_GRAVITY

dims = engine.get_dimensions(thrust_needed)

burn_rate = dims['mass_flow_rate']
burn_time = wet_mass / burn_rate

time_step = 1.0
current_time = 0
altitude = 0
velocity = 0

altitudes = []
thrusts = []
times = []

print(f"Total burn time: {burn_time:.2f} seconds")

while wet_mass > 0:
    ambient_pressure = calculate_ambient_pressure(altitude)

    pressure_thrust = (engine.AmbientPressure - ambient_pressure) * (dims['exit_area'] / 10000)
    current_thrust = (burn_rate * engine.EscapeVelocity) + pressure_thrust

    acceleration = (current_thrust / total_mass) - EARTH_GRAVITY
    velocity += acceleration * time_step
    altitude += velocity * time_step

    wet_mass -= burn_rate * time_step
    total_mass -= burn_rate * time_step
    current_time += time_step

    times.append(current_time)
    altitudes.append(altitude)
    thrusts.append(current_thrust)

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(times, altitudes)
plt.title("Altitude vs. Time")
plt.ylabel("Meters")

plt.subplot(1, 2, 2)
plt.plot(times, thrusts)
plt.title("Thrust vs. Time")
plt.ylabel("Newtons")

plt.show()