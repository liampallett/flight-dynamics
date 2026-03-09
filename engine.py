from data import *
from engine_math import *

EARTH_GRAVITY = 9.80665

class Engine:
    def __init__(self, propellant, chamber_pressure, design_altitude):
        self.propellant = propellant
        self.chamber_pressure = chamber_pressure
        self.ambient_pressure = calculate_ambient_pressure(design_altitude)
        self.gamma = propellant.gamma
        self.r= propellant.calculate_gas_constant()

        self.exit_mach = mach_from_pressure_ratio(self.ambient_pressure / self.chamber_pressure, self.gamma, 2.5)
        self.expansion_ratio = calculate_area_ratio(self.gamma, self.exit_mach)

        temperature_ratio = calculate_temperature_ratio(self.gamma, self.exit_mach)
        self.exit_temperature = self.propellant.typical_chamber_temperature * temperature_ratio
        self.escape_velocity = self.exit_mach * propellant.calculate_speed_of_sound(self.exit_temperature)
        self.specific_impulse = self.escape_velocity / EARTH_GRAVITY

    def get_dimensions(self, target_thrust):
        mass_flow_rate = target_thrust / self.escape_velocity
        gamma_constant = math.sqrt(self.gamma) * \
                         (2 / (self.gamma + 1))**((self.gamma+1) / (2*(self.gamma-1)))

        chamber_temp = self.propellant.typical_chamber_temperature
        numerator = mass_flow_rate * math.sqrt(self.r * chamber_temp)
        denominator = self.chamber_pressure * gamma_constant

        throat_area_m2 = numerator / denominator

        throat_area_cm2 = throat_area_m2 * 10000
        exit_area_cm2 = throat_area_cm2 * self.expansion_ratio

        throat_diameter = 2 * math.sqrt(throat_area_cm2 / math.pi)
        exit_diameter = 2 * math.sqrt(exit_area_cm2 / math.pi)

        return {
            "mass_flow_rate": mass_flow_rate,
            "throat_diameter": throat_diameter,
            "exit_diameter": exit_diameter,
            "throat_area": throat_area_cm2,
            "exit_area": exit_area_cm2
        }