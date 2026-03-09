from engine import *
from stage import *
from data import *
import matplotlib.pyplot as plt
import datetime

EARTH_GRAVITY = 9.80665
THRUST_CONSTANT = 2
DRAG_COEFFICIENT = 0.2
EFFICIENCY_FACTOR = 0.97
PAYLOAD_MASS = 500

# V2 Specifications
lox_b_stoff = Propellant(1.2, 33.16, 2700)
engine2 = Engine(lox_b_stoff, 1500000, 30000)
stage2 = Stage(engine2, 3000, 800, 1.2, PAYLOAD_MASS)
engine1 = Engine(lox_b_stoff, 1500000, 0)
stage1 = Stage(engine1, 25000, 4500, 2.5, stage2.get_total_mass() + PAYLOAD_MASS)
rocket = [stage1, stage2]
total_stages = len(rocket)

time_step = 0.1
current_time = 0
altitude = 0
velocity = 0

altitudes = []
velocities = []
dynamic_pressures = []
thrusts = []
times = []
g_forces = []
eco_times = []

print(f"Total burn time: {rocket[0].burn_time:.2f} seconds")
print(f"Theoretical Delta-V: {rocket[0].theoretical_delta_v:.2f} ms^-1")

while True:
    active_stage = rocket[0]
    current_mass = PAYLOAD_MASS
    for stage in rocket:
        current_mass += stage.get_total_mass()

    ambient_pressure, air_density = get_atmospheric_properties(altitude)
    dynamic_pressure = 0.5*air_density*(velocity**2)

    if not active_stage.is_empty():
        current_thrust = active_stage.get_thrust(ambient_pressure)
        active_stage.burn_propellant(time_step)
    else:
        current_thrust = 0
        if len(rocket) > 1:
            rocket.pop(0)
            eco_times.append(current_time)
            active_stage = rocket[0]
        elif len(eco_times) < total_stages:
            eco_times.append(current_time)

    drag_force = dynamic_pressure*DRAG_COEFFICIENT*active_stage.area
    net_force = current_thrust-drag_force-(current_mass*EARTH_GRAVITY)

    acceleration = net_force/current_mass
    velocity += acceleration*time_step
    altitude += velocity*time_step
    g_force = acceleration/EARTH_GRAVITY

    current_time += time_step

    times.append(current_time)
    altitudes.append(altitude)
    velocities.append(velocity)
    thrusts.append(current_thrust)
    dynamic_pressures.append(dynamic_pressure)
    g_forces.append(g_force)

    if velocity < 0:
        break

print(f" --- Flight Results --- ")
print(f"Max Altitude (Apoapsis): {max(altitudes) / 1000:.2f} km")
print(f"Time to Apoapsis: {current_time / 60:.2f} minutes")
print(f"Max G-Force: {max(g_forces):.1f} Gs")

plt.figure(figsize=(10, 10))
plt.subplot(2, 2, 1)
plt.plot(times, altitudes)
plt.title("Altitude vs. Time")
plt.ylabel("Meters")
plt.xlabel("Seconds")
for i in range(len(eco_times)):
    plt.axvline(x=eco_times[i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(times, velocities)
plt.title("Velocity vs. Time")
plt.ylabel("M/S")
plt.xlabel("Seconds")
for i in range(len(eco_times)):
    plt.axvline(x=eco_times[i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(times, thrusts)
plt.title("Thrust vs. Time")
plt.ylabel("Newtons")
plt.xlabel("Seconds")
for i in range(len(eco_times)):
    plt.axvline(x=eco_times[i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(times, dynamic_pressures)
plt.title("Dynamic Pressure (Max Q)")
plt.ylabel("Pascals")
plt.xlabel("Seconds")

plt.tight_layout()

timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
plt.savefig(f'images/flight_{timestamp}.png')
plt.savefig('images/latest.png')

plt.show()