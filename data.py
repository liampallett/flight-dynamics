import math

UNIVERSAL_GAS_CONSTANT = 8314.46

class Propellant:
    def __init__(self, specific_heat_ratio, molecular_weight, typical_chamber_temperature):
        self.specificHeatRatio = specific_heat_ratio
        self.molecularWeight = molecular_weight
        self.typicalChamberTemperature = typical_chamber_temperature

    def calculate_gas_constant(self):
        return UNIVERSAL_GAS_CONSTANT / self.molecularWeight

    def calculate_speed_of_sound(self, temperature):
        return math.sqrt(self.specificHeatRatio * self.calculate_gas_constant() * temperature)

def calculate_ambient_pressure(altitude):
    if altitude > 44330:
        return 0
    return 101325 * (1 - 2.25577E-5* altitude)**5.25588 # https://www.engineeringtoolbox.com/air-altitude-pressure-d_462.html