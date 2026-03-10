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
EARTH_OMEGA = 7.2921159e-5

DRAG_COEFFICIENT = 0.2

def run_simulation(rocket_parameter, mission_parameter_dict, payload_mass, time_step, telemetry):
    current_time = 0
    x_pos, y_pos = 0, 0

    initial_v_x = EARTH_OMEGA*RADIUS_EARTH
    v_x, v_y = initial_v_x, 0
    total_stages = len(rocket_parameter)

    target_orbital_velocity = math.sqrt((GRAVITATIONAL_CONSTANT*MASS_EARTH) / (RADIUS_EARTH + mission_parameter_dict['target_apoapsis']))
    previous_state = mission_parameter_dict['mission_state']

    while True:
        r_x = x_pos
        r_y = y_pos + RADIUS_EARTH
        distance_to_centre = math.sqrt(r_x**2+r_y**2)
        altitude = distance_to_centre - RADIUS_EARTH

        active_stage = rocket_parameter[0]
        current_mass = payload_mass + sum(stage.get_total_mass() for stage in rocket_parameter)

        pitch_angle = 0
        current_thrust = 0
        total_velocity = math.sqrt(v_x ** 2 + v_y ** 2)

        if active_stage.is_empty():
            if len(rocket_parameter) > 1:
                rocket_parameter.pop(0)
                telemetry['eco_times'].append(current_time)
                active_stage = rocket_parameter[0]

                print(f"Stage Sep: t={current_time:.1f}s, alt={altitude / 1000:.1f}km, v={total_velocity:.0f}m/s, vx={v_x:.0f} vy={v_y:.0f}")
                print(f"Stage 2 theoretical delta-v: {active_stage.theoretical_delta_v:.0f} m/s")
            elif len(telemetry['eco_times']) < total_stages:
                telemetry['eco_times'].append(current_time)

        ambient_pressure, air_density = get_atmospheric_properties(altitude)
        v_atm_x = EARTH_OMEGA*r_y
        v_atm_y = -EARTH_OMEGA*r_x

        rel_v_x = v_x-v_atm_x
        rel_v_y = v_y-v_atm_y

        rel_velocity_total = math.sqrt(rel_v_x**2+rel_v_y**2)
        dynamic_pressure = 0.5*air_density*(rel_velocity_total**2)

        if mission_parameter_dict['mission_state'] != previous_state:
            print(f"State: {previous_state} -> {mission_parameter_dict['mission_state']} at alt={altitude / 1000:.1f}km, v={total_velocity:.0f}m/s")
        if mission_parameter_dict['mission_state'] == "LAUNCH":
            mu = GRAVITATIONAL_CONSTANT*MASS_EARTH
            specific_energy = (total_velocity**2)/2-mu/distance_to_centre

            h = abs(r_x*v_y-r_y*v_x)

            if specific_energy < 0:
                eccentricity = math.sqrt(max(0, 1+(2*specific_energy*h**2)/(mu**2)))
                semi_major_axis = -mu/(2*specific_energy)
                potential_apoapsis = semi_major_axis*(1+eccentricity)
            else:
                potential_apoapsis = float('inf')

            if (potential_apoapsis - RADIUS_EARTH) >= mission_parameter_dict['target_apoapsis'] and total_velocity > 5000:
                mission_parameter_dict['mission_state'] = "COASTING"
                current_thrust = 0
            elif not active_stage.is_empty():
                current_thrust = active_stage.get_thrust(ambient_pressure)
            else:
                current_thrust = 0

            local_vertical = math.atan2(r_y, r_x)

            if rel_velocity_total > 0.1:
                velocity_angle = math.atan2(rel_v_y, rel_v_x)
            else:
                velocity_angle = local_vertical

            kick_program_start = mission_parameter_dict['pitch_program_start']
            kick_program_end = mission_parameter_dict['pitch_program_end']
            kick_program_angle = mission_parameter_dict['pitch_program_angle']
            if altitude < kick_program_start:
                pitch_angle = local_vertical
            elif kick_program_start <= altitude < kick_program_end:
                fraction = (altitude-kick_program_start)/(kick_program_end-kick_program_start)
                kick_angle = math.radians(kick_program_angle)*fraction
                pitch_angle = local_vertical-kick_angle
            else:
                final_kick = math.radians(kick_program_angle)
                min_pitch = local_vertical - final_kick
                pitch_angle = max(velocity_angle, min_pitch)

        elif mission_parameter_dict['mission_state'] == "COASTING":
            current_thrust = 0
            pitch_angle = 0

            radial_velocity = (r_x*v_x+r_y*v_y)/distance_to_centre

            if radial_velocity <= 0:
                mission_parameter_dict['mission_state'] = "CIRCULARISING"
        elif mission_parameter_dict['mission_state'] == "CIRCULARISING":
            pitch_angle = math.atan2(r_y, r_x)-math.pi/2
            if total_velocity < target_orbital_velocity:
                if not active_stage.is_empty():
                    current_thrust = active_stage.get_thrust(ambient_pressure)
                else:
                    current_thrust = 0
            else:
                mission_parameter_dict['mission_state'] = "STABLE_ORBIT"
                current_thrust = 0
        elif mission_parameter_dict['mission_state'] == "STABLE_ORBIT":
            current_thrust = 0
            pitch_angle = 0

            current_angle = math.atan2(r_y, r_x)
            angle_delta = current_angle - mission_parameter_dict.get('last_angle', current_angle)

            if angle_delta > math.pi: angle_delta -= 2*math.pi
            if angle_delta < -math.pi: angle_delta += 2 * math.pi
            mission_parameter_dict['orbit_angle'] = mission_parameter_dict.get('orbit_angle', 0) + abs(angle_delta)
            mission_parameter_dict['last_angle'] = current_angle

            if mission_parameter_dict['orbit_angle'] >= 2*math.pi:
                print("Simulation Timeout (Stable Orbit Achieved)")
                break

        thrust_x = current_thrust*math.cos(pitch_angle)
        thrust_y = current_thrust*math.sin(pitch_angle)

        total_drag = dynamic_pressure*DRAG_COEFFICIENT*active_stage.area
        if rel_velocity_total > 0.1:
            velocity_angle = math.atan2(rel_v_y, rel_v_x)
            drag_x = -total_drag*math.cos(velocity_angle)
            drag_y = -total_drag*math.sin(velocity_angle)
        else:
            drag_x, drag_y = 0, 0

        if current_thrust > 0:
            active_stage.burn_propellant(time_step)

        gravity_force = (GRAVITATIONAL_CONSTANT*MASS_EARTH*current_mass)/distance_to_centre**2
        gravity_x = -gravity_force*(r_x/distance_to_centre)
        gravity_y = -gravity_force*(r_y/distance_to_centre)

        net_force_x = thrust_x+drag_x+gravity_x
        net_force_y = thrust_y+drag_y+gravity_y

        a_x = net_force_x/current_mass
        a_y = net_force_y/current_mass

        v_x += a_x*time_step
        v_y += a_y*time_step
        x_pos += v_x * time_step
        y_pos += v_y * time_step

        mech_a_x = (thrust_x-drag_x)/current_mass
        mech_a_y = (thrust_y-drag_y)/current_mass

        g_force = math.sqrt(mech_a_x**2+mech_a_y**2)/9.80665

        previous_state = mission_parameter_dict['mission_state']
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

    final_x = telemetry['x_positions'][-1000:]
    final_y = telemetry['y_positions'][-1000:]

    distances = []
    for i in range(len(final_x)):
        r = math.sqrt(final_x[i]**2+(final_y[i]+RADIUS_EARTH)**2)
        distances.append(r)

    apoapsis = max(distances)
    periapsis = min(distances)

    eccentricity = (apoapsis-periapsis)/(apoapsis+periapsis)

    print(f" --- Flight Results --- ")
    print(f"Max Altitude (Apoapsis): {max(telemetry['y_positions']) / 1000:.2f} km")
    print(f"Time to Apoapsis: {current_time / 60:.2f} minutes")
    print(f"Max G-Force: {max(telemetry['g_forces']):.1f} Gs")
    print(f"Orbit Eccentricity: {eccentricity:.5f}")

def plot_dashboard(telemetry, mission_parameters, rocket_name):
    plt.style.use('dark_background')
    plt.figure(figsize=(14, 10))

    plt.subplot(2, 2, 1)
    atmosphere_circle = plt.Circle((0, 0), RADIUS_EARTH+100000, color='skyblue', label='Atmosphere')
    earth_circle = plt.Circle((0, 0), RADIUS_EARTH, color='darkblue', label='Earth')
    plt.gca().add_patch(atmosphere_circle)
    plt.gca().add_patch(earth_circle)

    target_orbit = plt.Circle((0, 0), RADIUS_EARTH+mission_parameters['target_apoapsis'], color='lightgreen', fill=False, linestyle='--', alpha=0.5, label='Target Orbit')
    plt.gca().add_patch(target_orbit)

    global_x = [x for x in telemetry['x_positions']]
    global_y = [(y+RADIUS_EARTH) for y in telemetry['y_positions']]
    all_x = global_x + [0]
    all_y = global_y + [0]
    limit = max(max(map(abs, all_x)), max(map(abs, all_y)))*1.1
    plt.xlim(-limit, limit)
    plt.ylim(-limit, limit)
    plt.grid(True, linestyle=':', alpha=0.3)

    plt.plot(global_x, global_y, color='red', label='Trajectory')
    plt.axis('equal')
    plt.title('Orbital Trajectory')
    plt.xlabel("Distance from Center (m)")
    plt.ylabel("Distance from Center (m)")

    plt.scatter(global_x[-1], global_y[-1], color='white', s=50, zorder=5, label='Rocket')
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(telemetry['times'], telemetry['total_velocities'], color='darkblue')
    plt.title("Velocity vs. Time")
    plt.ylabel("M/S")
    plt.xlabel("Seconds")
    for i in range(len(telemetry['eco_times'])):
        plt.axvline(x=telemetry['eco_times'][i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(telemetry['times'], telemetry['g_forces'], color='darkblue')
    plt.title("G-Force vs. Time")
    plt.ylabel("Gs")
    plt.xlabel("Seconds")
    for i in range(len(telemetry['eco_times'])):
        plt.axvline(x=telemetry['eco_times'][i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
    plt.legend()

    max_q = max(telemetry['dynamic_pressures'])
    max_q_index = telemetry['dynamic_pressures'].index(max_q)
    max_q_time = telemetry['times'][max_q_index]

    plt.subplot(2, 2, 4)
    plt.plot(telemetry['times'], telemetry['dynamic_pressures'], color='darkblue')
    plt.annotate(f'Max Q ({max_q:.0f} PA)',
                 xy=(max_q_time, max_q),
                 xytext=(max_q_time+100, max_q*0.8),
                 arrowprops=dict(facecolor='white', shrink=0.05))
    plt.title("Dynamic Pressure (Max Q)")
    plt.ylabel("Pascals")
    plt.xlabel("Seconds")
    for i in range(len(telemetry['eco_times'])):
        plt.axvline(x=telemetry['eco_times'][i], color='gray', linestyle='--', label=f'ECO Stage {i+1}')
    plt.legend()

    plt.tight_layout()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    plt.savefig(f'images/flight_{timestamp}.png')
    plt.savefig('images/latest.png')
    plt.savefig(f'images/{rocket_name}.png')

    plt.show()

if __name__ == "__main__":
    PAYLOAD_MASS = 15000
    ROCKET_NAME = "Falcon9"

    # Falcon 9 Specifications
    kerelox = Propellant(1.24, 22.0, 3670)

    merlin_1d_vacuum = Engine(kerelox, 9700000, 70000)
    stage2 = Stage(merlin_1d_vacuum, 107500, 4000, 0.9, 3.7, PAYLOAD_MASS)

    merlin_1d_sea = Engine(kerelox, 9700000, 0)
    stage1 = Stage(merlin_1d_sea, 395000, 25000, 1.4, 3.7, stage2.get_total_mass()+PAYLOAD_MASS)

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

    mission_parameters = {
        'target_apoapsis': 200000,
        'mission_state': "LAUNCH",
        'pitch_program_start': 1000,
        'pitch_program_end': 80000,
        'pitch_program_angle': 80
    }

    print(f"Merlin sea level Isp: {merlin_1d_sea.specific_impulse:.1f}s")
    print(f"Merlin sea level Ve: {merlin_1d_sea.escape_velocity:.1f} m/s")
    print(f"Stage 1 burn time: {stage1.burn_time:.1f}s")
    print(f"Stage 1 delta-v: {stage1.theoretical_delta_v:.0f} m/s")

    run_simulation(rocket, mission_parameters, PAYLOAD_MASS, 0.05, telemetry)
    plot_dashboard(telemetry, mission_parameters, ROCKET_NAME)