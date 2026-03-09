import math

UNIVERSAL_GAS_CONSTANT = 8314.46
# US Standard Atmosphere 1976 (Sample)
# Format: (Altitude in meters, Pressure in Pascals, Density in kg/m^3)
ATMOSPHERE_TABLE = [
    (0, 101325.0, 1.2250),
    (1000, 89874.6, 1.1117),
    (2000, 79501.4, 1.0066),
    (3000, 70108.5, 0.9093),
    (5000, 54019.9, 0.7361),
    (10000, 26499.9, 0.4127),
    (20000, 5529.3, 0.0880),
    (30000, 1197.0, 0.0184),
    (50000, 79.78, 0.0010),
    (80000, 1.05, 0.00001),
    (100000, 0.03, 0.0000005), # Kármán line
    (1000000, 0.0, 0.0)        # Deep Space
]

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

def get_atmospheric_properties(altitude):
    if altitude <= ATMOSPHERE_TABLE[0][0]:
        return ATMOSPHERE_TABLE[0][1], ATMOSPHERE_TABLE[0][2]
    if altitude >= ATMOSPHERE_TABLE[-1][0]:
        return ATMOSPHERE_TABLE[-1][1], ATMOSPHERE_TABLE[-1][2]

    for i in range(len(ATMOSPHERE_TABLE)-1):
        alt1, p1, d1 = ATMOSPHERE_TABLE[i]
        alt2, p2, d2 = ATMOSPHERE_TABLE[i+1]

        if alt1 <= altitude <= alt2:
            fraction = (altitude-alt1)/(alt2-alt1)
            interpolate_pressure = p1+fraction*(p2-p1)
            interpolate_density = d1+fraction*(d2-d1)
            return interpolate_pressure, interpolate_density

    return ATMOSPHERE_TABLE[-1][1], ATMOSPHERE_TABLE[-1][2]