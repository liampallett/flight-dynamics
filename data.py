import math

UNIVERSAL_GAS_CONSTANT = 8314.46
BAROMETRIC_ALTITUDE_CONSTANT = 44330 # Simplified International Standard Atmosphere Model

class Propellant:
    """
    Stores thermochemical properties of a liquid fuel rocket propellant.


    """
    def __init__(self, gamma, molecular_weight, typical_chamber_temperature):
        self.gamma = gamma
        self.molecular_weight = molecular_weight
        self.typical_chamber_temperature = typical_chamber_temperature

    def calculate_gas_constant(self):
        return UNIVERSAL_GAS_CONSTANT/self.molecular_weight

    def calculate_speed_of_sound(self, temperature):
        return math.sqrt(self.gamma*self.calculate_gas_constant()*temperature)

def calculate_ambient_pressure(altitude):
    if altitude > BAROMETRIC_ALTITUDE_CONSTANT:
        return 0
    return 101325*(1-2.25577E-5*altitude)**5.25588 # https://www.engineeringtoolbox.com/air-altitude-pressure-d_462.html

def calculate_air_density(altitude):
    if altitude > BAROMETRIC_ALTITUDE_CONSTANT:
        return 0.0
    return 1.225 * (1-2.25577E-5*altitude)**4.25588