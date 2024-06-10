import nidaqmx
import numpy as np
import time

local_system = nidaqmx.system.System.local()
driver_version = local_system.driver_version

print(
    "DAQmx {0}.{1}.{2}".format(
        driver_version.major_version,
        driver_version.minor_version,
        driver_version.update_version,
    )
)

print(len(local_system.devices))

for device in local_system.devices:
    print(
        f"Device Name: {device.name}, Product Category: {device.product_category},"
        f"Product Type: {device.product_type}")


def daq_ramp(val_min, val_max, step):
    # Paramètres de la rampe de tension
    start_voltage = val_min  # Tension de départ en volts
    end_voltage = val_max # Tension finale en volts
    num_steps = 100  # Nombre de pas dans la rampe
    duration = 1  # Durée totale de la rampe en secondes

    # Calcul des paramètres de la rampe
    step_duration = duration / num_steps
    ramp = np.linspace(start_voltage, end_voltage, num_steps)

    # Créer une tâche pour générer la rampe de tension
    with nidaqmx.Task() as task:
        # Ajouter un canal de sortie analogique
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=start_voltage, max_val=end_voltage)

        # Démarrer la tâche
        task.start()

        # Générer la rampe de tension en écrivant chaque valeur successivement
        for voltage in ramp:
            task.write(voltage)
            time.sleep(step_duration)

        # Arrêter la tâche
        task.stop()

daq_ramp(0, 5, 0)