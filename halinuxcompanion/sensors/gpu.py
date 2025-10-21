from types import MethodType
from halinuxcompanion.sensor import Sensor, logger
import subprocess

# Optional import for Jetson devices
try:
    from jtop import jtop
    HAS_JTOP = True
except ImportError:
    HAS_JTOP = False

Gpu = Sensor()
Gpu.config_name = "gpu"
Gpu.device_class = "power_factor"
Gpu.state_class = "measurement"
Gpu.icon = "mdi:expansion-card"
Gpu.name = "GPU Utilization"
Gpu.state = 0
Gpu.type = "sensor"
Gpu.unique_id = "gpu_utilization"
Gpu.unit_of_measurement = "%"

def updater(self):
    """Update the GPU utilization"""
    # nvidia gpu
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if output:
            gpu_util = float(output.split()[0])
            self.state = gpu_util
            logger.info("GPU utilization: %s", gpu_util)
        else:
            self.state = "unavailable"
    except (subprocess.CalledProcessError, ValueError, IndexError) as e:
        self.state = "unavailable"

    # nvidia jetson-orin-nano
    if HAS_JTOP:
        try:
            jetson = jtop()
            jetson.start()
            output = jetson.stats
            jetson.close()
            logger.info("GPU utilization: %s", output['GPU'])
            self.state = output['GPU']
        except Exception as e:
            logger.error("Error updating GPU utilization with jtop: %s", e)

Gpu.updater = MethodType(updater, Gpu)
