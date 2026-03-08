from data import *
from engine_math import *

EARTH_GRAVITY = 9.80665

class Engine:
    def __init__(self, propellant, chamber_pressure, design_altitude):
        self.Propellant = propellant
        self.ChamberPressure = chamber_pressure
        self.AmbientPressure = calculate_ambient_pressure(design_altitude)
        self.Gamma = propellant.specificHeatRatio
        self.R = propellant.calculate_gas_constant()

        self.ExitMach = mach_from_pressure_ratio(self.AmbientPressure / self.ChamberPressure, self.Gamma, 2.5)
        self.ExpansionRatio = calculate_area_ratio(self.Gamma, self.ExitMach)

        temperature_ratio = calculate_temperature_ratio(self.Gamma, self.ExitMach)
        self.ExitTemperature = self.Propellant.typicalChamberTemperature * temperature_ratio
        self.EscapeVelocity = self.ExitMach * propellant.calculate_speed_of_sound(self.ExitTemperature)
        self.SpecificImpulse = self.EscapeVelocity / EARTH_GRAVITY

    def get_dimensions(self, target_thrust):
        mass_flow_rate = target_thrust / self.EscapeVelocity
        gamma_constant = math.sqrt(self.Gamma) * \
                         (2 / (self.Gamma + 1))**((self.Gamma+1) / (2*(self.Gamma-1)))

        chamber_temp = self.Propellant.typicalChamberTemperature
        numerator = mass_flow_rate * math.sqrt(self.R * chamber_temp)
        denominator = self.ChamberPressure * gamma_constant

        throat_area_m2 = numerator / denominator

        throat_area_cm2 = throat_area_m2 * 10000
        exit_area_cm2 = throat_area_cm2 * self.ExpansionRatio

        throat_diameter = 2 * math.sqrt(throat_area_cm2 / math.pi)
        exit_diameter = 2 * math.sqrt(exit_area_cm2 / math.pi)

        return {
            "mass_flow_rate": mass_flow_rate,
            "throat_diameter": throat_diameter,
            "exit_diameter": exit_diameter,
            "throat_area": throat_area_cm2,
            "exit_area": exit_area_cm2
        }