#!/usr/bin/env python3


from subprocess import check_output
from time import sleep
import importlib.util
import sys
import subprocess
import os
# import signal
# import gi
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk, AppIndicator3, GObject
# from threading import Thread


class FanControl():
    def __init__(self):
        self.status = ["", ""]
        self.short_status = "NVIDIA"
        pass

    def enable_fan_control(self, id):
        check_output([
            "nvidia-settings",
            "-a",
            id + "/GPUFanControlState=1"
        ])

    def disable_fan_control(self, id):
        check_output([
            "nvidia-settings",
            "-a",
            id + "/GPUFanControlState=0"
        ])

    def get_core_temperature(self, id):
        return int(check_output([
            "nvidia-settings",
            "-t",
            "-q",
            id + "/GPUCoreTemp"
        ]).decode())

    def get_core_total_mem(self, id):
        return int(check_output([
            "nvidia-settings",
            "-t",
            "-q",
            id + "/TotalDedicatedGPUMemory"
        ]).decode())

    def get_core_used_mem(self, id):
        return int(check_output([
            "nvidia-settings",
            "-t",
            "-q",
            id + "/UsedDedicatedGPUMemory"
        ]).decode())

    def get_driver_version(self, id):
        return float(check_output([
            "nvidia-settings",
            "-t",
            "-q",
            id + "/NvidiaDriverVersion"
        ]).decode())

    def get_fan_speed(self, id):
        return int(check_output([
            "nvidia-settings",
            "-t",
            "-q",
            id + "/GPUCurrentFanSpeed"
        ]).decode())

    def set_fan_speed(self, speed, id):
        check_output([
            "nvidia-settings",
            "-a",
            id + "/GPUTargetFanSpeed=" + str(speed)
        ])

    def fan_curve(self, temperature, gpu_id):
        if gpu_id == 1:
            if temperature < 40:
                return 0
            if temperature < 50:
                return 25
            if temperature < 60:
                return 30
            if temperature < 70:
                return 50
            if temperature < 80:
                return 60
            if temperature < 90:
                return 70
            else:
                return 80
        else:
            if temperature < 50:
                return 25

            if temperature > 90:
                return 85
            return int(((temperature ** 2) / 90) + 4)
     

    def load_config(self, path="/etc/nvidia_fancontrol.py"):
        spec  = importlib.util.spec_from_file_location("module.name", path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config

    def plot_fan_curves(self, config):
        try:
            from matplotlib import pyplot as plt
        except:
            print("no pyplot")
            return

        T = list(range(0, 100))

        plt.figure(figsize=(6, 6))

        plt.grid()

        plt.xlim(0, 100)
        plt.ylim(0, 105)
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

        plt.xlabel("temperature / °C")
        plt.ylabel("percental fan speed")

        for fan, control in config.fan_controls.items():
            gpu_id = int(control[0][5])   
            if not control[1]:
                speed = [self.fan_curve(T_, gpu_id) for T_ in T]
            else:
                try:
                    f = getattr(config, control[1])
                    speed = [f(T_) for T_ in T]
                except:
                    speed = [self.fan_curve(T_, gpu_id) for T_ in T]
            plt.plot(T, speed, label=fan)
        title = plt.title("nvidia-fancontrol fan curves")
        legend = plt.legend(loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, -0.1))
        plt.savefig("/tmp/nvidia_fancontrol.pdf", bbox_extra_artists=(legend, title,), bbox_inches='tight')

    def process(self, d, driver):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Driver Version: %.2f" % driver)
        for gpu in d:
            for line in d[gpu]:
                print(line)

    def shellquote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"


    def run(self):
        config = self.load_config()
        
        self.plot_fan_curves(config)
        driver = "No Driver Found"
        for _, control in config.fan_controls.items():
            self.enable_fan_control(control[0])
            driver = self.get_driver_version(control[0])



        while True:
            # status = "V%.2f" % (driver) 
            short_status = ["",""]    
            output = {-1: [""]}
            for fan, control in config.fan_controls.items():

                core_temp = self.get_core_temperature(control[0])
                current_speed = self.get_fan_speed(fan)
                gpu_id = int(control[0][5])

                # if core_temp > 60:
                #     kill_command = "kill $(nvidia-smi | awk '$2==\"Processes:\" {p=1} p && $2 == " + str(gpu_id) + \
                #     " && $3 > 0 {print $3}')"
                #     print(kill_command)
                #     subprocess.call(kill_command.split(" "))
                if not control[1]:
                    target_speed = self.fan_curve(core_temp, gpu_id)
                else:
                    try:
                        target_speed = control[1](core_temp)
                    except:
                        target_speed = self.fan_curve(core_temp, gpu_id)

                if target_speed != current_speed:
                    self.set_fan_speed(target_speed, fan)
                if not gpu_id in output:
                    output[gpu_id] = []
                used = self.get_core_used_mem(control[0])
                total = self.get_core_total_mem(control[0])
                mem = str(used) + "MiB / " + str(total) + "MiB"
                output[gpu_id].append(control[0] + fan)
                output[gpu_id].append("\t" + mem)
                output[gpu_id].append("\t%d -> %d" % (current_speed, target_speed))
                output[gpu_id].append("\tTemp: %dC" % core_temp)
                self.status[gpu_id] = "%s 🌡️%dC %d%% %dMiB" % (control[0], core_temp, current_speed, used)
                short_status[gpu_id] = "🌡️%dC" % (core_temp)
                # status += " [:%d] %dC %d%%" % (gpu_id, core_temp, current_speed)

            self.process(output, driver)
            self.short_status = short_status[0] + " " + short_status[1] 
            sleep(config.interval)

if __name__ == "__main__":
    FanControl().run()