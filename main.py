from data import *
from engine import *
import matplotlib.pyplot as plt

EARTH_GRAVITY = 9.80665
THRUST_CONSTANT = 1.5
DRAG_COEFFICIENT = 0.5

lox_rp1 = Propellant(1.24, 21.9, 3571)
engine = Engine(lox_rp1, 7000000, 0)

dry_mass = 10000
wet_mass = 40000
total_mass = dry_mass + wet_mass
rocket_diameter = 3
rocket_area = math.pi*(rocket_diameter/2)**2
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
dynamic_pressures = []

print(f"Total burn time: {burn_time:.2f} seconds")

while wet_mass > 0:
    ambient_pressure = calculate_ambient_pressure(altitude)
    air_density = calculate_air_density(altitude)
    dynamic_pressure = 0.5*air_density*(velocity**2)

    pressure_thrust = (engine.AmbientPressure-ambient_pressure)*(dims['exit_area']/10000)
    current_thrust = (burn_rate * engine.EscapeVelocity) + pressure_thrust

    drag_force = dynamic_pressure*DRAG_COEFFICIENT*rocket_area

    net_force = current_thrust-drag_force-(total_mass*EARTH_GRAVITY)
    acceleration = net_force/total_mass
    velocity += acceleration*time_step
    altitude += velocity*time_step

    wet_mass -= burn_rate*time_step
    total_mass -= burn_rate*time_step
    current_time += time_step

    times.append(current_time)
    altitudes.append(altitude)
    thrusts.append(current_thrust)
    dynamic_pressures.append(dynamic_pressure)

plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.plot(times, altitudes)
plt.title("Altitude vs. Time")
plt.ylabel("Meters")
plt.xlabel("Seconds")

plt.subplot(1, 3, 2)
plt.plot(times, thrusts)
plt.title("Thrust vs. Time")
plt.ylabel("Newtons")
plt.xlabel("Seconds")

plt.subplot(1, 3, 3)
plt.plot(times, dynamic_pressures)
plt.title("Dynamic Pressure (Max Q)")
plt.ylabel("Pascals")
plt.xlabel("Seconds")

plt.tight_layout()
plt.show()