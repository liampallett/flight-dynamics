def calculate_pressure_ratio(gamma, mach):
    """
    Calculates the ratio between nozzle and combustion chamber pressures.
    
    :param gamma: The ratio of specific heats for the liquid fuel.
    :param mach: The local Mach number.
    :return: Dimensionless ratio.
    """
    return (1 + (gamma-1)/2 * mach**2)**(-gamma/(gamma-1))

def calculate_temperature_ratio(gamma, mach):
    """
    Calculates the ratio between nozzle and combustion chamber temperatures.

    :param gamma: The ratio of specific heats for the liquid fuel.
    :param mach: The local Mach number.
    :return: Dimensionless ratio.
    """
    return (1 + (gamma-1)/2 * mach**2)**-1

def calculate_density_ratio(gamma, mach):
    """
    Calculates the ratio between nozzle and combustion chamber densities.

    :param gamma: The ratio of specific heats for the liquid fuel.
    :param mach: The local Mach number.
    :return: Dimensionless ratio.
    """
    return (1 + (gamma-1)/2 * mach**2)**(-1/(gamma-1))

def calculate_area_ratio(gamma, mach):
    exponent = (gamma+1)/(2*(gamma-1))
    constant = ((gamma+1)/2)**-exponent
    mach_variable = (1+(gamma-1)/2*mach**2)**exponent
    return constant * mach_variable * (1/mach)

def mach_from_pressure_ratio(target_value, gamma, initial_guess):
    """
    Calculates the Mach number for a given pressure ratio using Newton-Raphson.

    :param target_value: The target pressure ratio P/P_t. Must be >= 1.0.
    :param gamma: The ratio of specific heats for the liquid fuel.
    :param initial_guess: The starting Mach number for iteration.
    :return: The converged Mach number.
    """
    tolerance = 1e-7
    max_iterations = 50
    current_mach = initial_guess
    delta = 0.0001

    for i in range(max_iterations):
        f_m = calculate_pressure_ratio(gamma, current_mach) - target_value
        f_m_plus_delta = calculate_pressure_ratio(gamma, current_mach + delta) - target_value
        slope = (f_m_plus_delta-f_m)/delta
        if slope == 0:
            break
        current_mach = current_mach - (f_m/slope)
        if abs(f_m) < tolerance:
            return current_mach
    return current_mach

def mach_from_area_ratio(target_value, gamma, initial_guess):
    """
    Calculates the Mach number for a given area ratio using Newton-Raphson.

    Since the area-mach relation is transcendental, this function iteratively solves for M. Note that for any
    A/A* > 1, there are two possible solutions. The converged solution purely depends on the initial_guess.

    :param target_value: The target area ratio (A/A*). Must be >= 1.0.
    :param gamma: The ratio of specific heats for the liquid fuel.
    :param initial_guess: The starting Mach number for iteration. Use < 1.0 for subsonic and > 1.0 for supersonic solutions.
    :return: The converged Mach number.
    """
    tolerance = 1e-7
    max_iterations = 50
    current_mach = initial_guess
    delta = 0.0001

    for i in range(max_iterations):
        f_m = calculate_area_ratio(gamma, current_mach) - target_value
        f_m_plus_delta = calculate_area_ratio(gamma, current_mach + delta) - target_value
        slope = (f_m_plus_delta-f_m)/delta
        if slope == 0:
            break
        current_mach = current_mach - (f_m/slope)
        if abs(f_m) < tolerance:
            return current_mach
    return current_mach
