from data import *
from engine import *

EARTH_GRAVITY = 9.80665
THRUST_CONSTANT = 1.5

lox_rp1 = Propellant(1.24, 21.9, 3571)
engine = Engine(lox_rp1, 7000000, 0)

rocket_mass = 50000
thrust_needed = rocket_mass * THRUST_CONSTANT * EARTH_GRAVITY

dims = engine.get_dimensions(thrust_needed)
print(f"--- Engine Design (SL) ---")
print(f"Isp: {engine.SpecificImpulse:.2f} s")
print(f"Exit Mach: {engine.ExitMach:.2f}")
print(f"Throat Diameter: {dims['throat_diameter']:.1f} cm")
print(f"Exit Diameter: {dims['exit_diameter']:.1f} cm")
print(f"Burn Rate: {dims['mass_flow_rate']:.2f} kg/s")