import math

EARTH_GRAVITY = 9.80665
DRAG_COEFFICIENT = 0.2
EFFICIENCY_FACTOR = 0.97

class Stage:
    def __init__(self, engine, propellant_mass, dry_mass, thrust_weight_ratio, diameter, carried_mass):
        self.engine = engine
        self.propellant_mass = propellant_mass
        self.dry_mass = dry_mass
        self.wet_mass = dry_mass+propellant_mass
        self.carried_mass = carried_mass
        self.diameter = diameter
        self.area = math.pi*(diameter/2)**2

        self.thrust_needed = (self.wet_mass+self.carried_mass)*thrust_weight_ratio*EARTH_GRAVITY
        self.dims = engine.get_dimensions(self.thrust_needed)

        self.burn_rate = self.dims['mass_flow_rate']
        self.burn_time = self.propellant_mass/self.burn_rate

        self.effective_exhaust_velocity = engine.escape_velocity*EFFICIENCY_FACTOR
        self.theoretical_delta_v = self.effective_exhaust_velocity*math.log((self.wet_mass+self.carried_mass)/(self.dry_mass+self.carried_mass))

    def get_total_mass(self):
        return self.propellant_mass+self.dry_mass

    def get_thrust(self, ambient_pressure):
        pressure_thrust = (self.engine.ambient_pressure-ambient_pressure)*(self.dims['exit_area']/10000)
        return self.burn_rate*(self.engine.escape_velocity*EFFICIENCY_FACTOR)+pressure_thrust

    def burn_propellant(self, time_step):
        self.propellant_mass -= self.burn_rate * time_step
        if self.propellant_mass < 0:
            self.propellant_mass = 0

    def is_empty(self):
        if self.propellant_mass > 0:
            return False
        else:
            return True