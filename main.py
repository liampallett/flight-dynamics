import matplotlib.pyplot as plt
import datetime
import math

from engine import Engine
from stage import Stage
from data import Propellant, get_atmospheric_properties

# Earth Data
GRAVITATIONAL_CONSTANT = 6.67430e-11
MASS_EARTH = 5.972e24
RADIUS_EARTH = 6371000

THRUST_CONSTANT = 2
DRAG_COEFFICIENT = 0.2
EFFICIENCY_FACTOR = 0.97

def run_simulation(rocket, payload_mass, time_step=0.1):
    current_time = 0
    x_pos, y_pos = 0, 0
    v_x, v_y = 0, 0
    total_stages = len(rocket)

    print(f"Total burn time: {rocket[0].burn_time:.2f} seconds")
    print(f"Theoretical Delta-V: {rocket[0].theoretical_delta_v:.2f} ms^-1")

    while True:
        r_x = x_pos
        r_y = y_pos + RADIUS_EARTH
        distance_to_centre = math.sqrt(r_x**2+r_y**2)
        altitude = distance_to_centre - RADIUS_EARTH

        active_stage = rocket[0]
        current_mass = payload_mass
        for stage in rocket:
            current_mass += stage.get_total_mass()

        ambient_pressure, air_density = get_atmospheric_properties(altitude)
        velocity_total = math.sqrt(v_x**2+v_y**2)
        dynamic_pressure = 0.5*air_density*(velocity_total**2)

        if not active_stage.is_empty():
            current_thrust = active_stage.get_thrust(ambient_pressure)
            active_stage.burn_propellant(time_step)
        else:
            current_thrust = 0
            if len(rocket) > 1:
                rocket.pop(0)
                telemetry['eco_times'].append(current_time)
                active_stage = rocket[0]
            elif len(telemetry['eco_times']) < total_stages:
                telemetry['eco_times'].append(current_time)

        if 1000 < altitude < 50000:
            fraction = (altitude-1000)/(50000-1000)
            pitch_angle = math.radians(90-(fraction*90))
        elif altitude >= 50000:
            pitch_angle = 0.0
        else:
            pitch_angle = math.radians(90)

        thrust_x = current_thrust*math.cos(pitch_angle)
        thrust_y = current_thrust*math.sin(pitch_angle)

        total_drag = dynamic_pressure*DRAG_COEFFICIENT*active_stage.area
        if velocity_total > 0:
            velocity_angle = math.atan2(v_y, v_x)
            drag_x = total_drag*math.cos(velocity_angle)
            drag_y = total_drag*math.sin(velocity_angle)
        else:
            drag_x, drag_y = 0, 0

        gravity_force = (GRAVITATIONAL_CONSTANT*MASS_EARTH*current_mass)/distance_to_centre**2
        gravity_x = -gravity_force*(r_x/distance_to_centre)
        gravity_y = -gravity_force*(r_y/distance_to_centre)

        net_force_x = thrust_x - drag_x + gravity_x
        net_force_y = thrust_y - drag_y + gravity_y

        a_x = net_force_x/current_mass
        a_y = net_force_y/current_mass

        v_x += a_x*time_step
        v_y += a_y*time_step
        total_velocity = math.sqrt(v_x**2+v_y**2)
        x_pos += v_x * time_step
        y_pos += v_y * time_step

        g_force = math.sqrt(a_x**2+a_y**2)/9.80665

        current_time += time_step

        telemetry['times'].append(current_time)
        telemetry['x_positions'].append(x_pos)
        telemetry['y_positions'].append(y_pos)
        telemetry['total_velocities'].append(total_velocity)
        telemetry['thrusts'].append(current_thrust)
        telemetry['dynamic_pressures'].append(dynamic_pressure)
        telemetry['g_forces'].append(g_force)

        if altitude < 0 and current_time > 1.0:
            break
        elif current_time > 10000:
            print("Simulation Timeout (Stable Orbit Achieved)")
            break

    print(f" --- Flight Results --- ")
    print(f"Max Altitude (Apoapsis): {max(telemetry['y_positions']) / 1000:.2f} km")
    print(f"Time to Apoapsis: {current_time / 60:.2f} minutes")
    print(f"Max G-Force: {max(telemetry['g_forces']):.1f} Gs")

def plot_dashboard(telemetry):
    plt.figure(figsize=(10, 10))
    plt.subplot(2, 2, 1)
    plt.plot(telemetry['x_positions'], telemetry['y_positions'])
    plt.title("Flight Trajectory")
    plt.ylabel("Altitude (metres)")
    plt.xlabel("Downrange Distance (metres)")

    plt.subplot(2, 2, 2)
    plt.plot(telemetry['times'], telemetry['total_velocities'])
    plt.title("Velocity vs. Time")
    plt.ylabel("M/S")
    plt.xlabel("Seconds")
    for i in range(len(telemetry['eco_times'])):
        plt.axvline(x=telemetry['eco_times'][i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(telemetry['times'], telemetry['thrusts'])
    plt.title("Thrust vs. Time")
    plt.ylabel("Newtons")
    plt.xlabel("Seconds")
    for i in range(len(telemetry['eco_times'])):
        plt.axvline(x=telemetry['eco_times'][i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(telemetry['times'], telemetry['dynamic_pressures'])
    plt.title("Dynamic Pressure (Max Q)")
    plt.ylabel("Pascals")
    plt.xlabel("Seconds")

    plt.tight_layout()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    plt.savefig(f'images/flight_{timestamp}.png')
    plt.savefig('images/latest.png')

    plt.show()

if __name__ == "__main__":
    PAYLOAD_MASS = 500

    # V2 Specifications
    lox_b_stoff = Propellant(1.2, 33.16, 2700)

    engine2 = Engine(lox_b_stoff, 1500000, 30000)
    stage2 = Stage(engine2, 3000, 800, 1.2, PAYLOAD_MASS)

    engine1 = Engine(lox_b_stoff, 1500000, 0)
    stage1 = Stage(engine1, 25000, 4500, 2.5, stage2.get_total_mass() + PAYLOAD_MASS)

    rocket = [stage1, stage2]

    telemetry = {
        'x_positions': [],
        'y_positions': [],
        'total_velocities': [],
        'dynamic_pressures': [],
        'thrusts': [],
        'times': [],
        'g_forces': [],
        'eco_times': []
    }

    run_simulation(rocket, PAYLOAD_MASS, time_step=0.1)
    plot_dashboard(telemetry)