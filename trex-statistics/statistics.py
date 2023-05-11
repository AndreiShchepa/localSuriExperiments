import lbr_trex_client.paths
import matplotlib.transforms as mtransforms
from trex_client import CTRexClient
import matplotlib.pyplot as plt
from trex_stl_lib.api import *
import subprocess
import math
import time
import sys
import os
import re

pwd = os.getcwd()
suri_path = pwd + "/installSuri/usr/bin/suricata"
pref_path = pwd + "/suricata/dpdk/prefilter/build/prefilter"
tcpreplay_nic = "enp4s0f1"
pcap_file = "/home/shared/pcap/crash.pcap"

class Configuration:
    def generate_dict_subconf(
            self,
            pref_conf_path,
            suri_rules_path,
            suri_sleep_time,
            arr_speedup,
            pkt_cnt
    ):
        return {
            'pf_conf_path': pref_conf_path,
            'suri_rules_path': suri_rules_path,
            'suri_sleep_time': suri_sleep_time,
            'arr_speedup': arr_speedup,
            'actual_rates': [],
            'results': [],
            'pkt_cnt': pkt_cnt,
        }

    def generate_dict_conf(
        self,
        pf_workers,
        pref_conf_metadata_path,
        pref_conf_no_metadata_path,
        suri_conf_path,
        speedup_without_rules,
        speedup_with_rules,
        pkt_cnt_without_rules,
        pkt_cnt_with_rules,
    ):
        suri_sleep_time_rules = 9
        suri_sleep_time_no_rules = 3
        suri_rules = "/home/shared/suricata/rules/suricata.rules"
        suri_no_rules = "dev/null"

        return {
            'pf_workers': pf_workers,
            'suri_conf_path': suri_conf_path,
            'test_conf': {
                'without_rules_metadata_on': self.generate_dict_subconf(
                    pref_conf_path=pref_conf_metadata_path,
                    suri_rules_path=suri_no_rules,
                    suri_sleep_time=suri_sleep_time_no_rules,
                    arr_speedup=speedup_without_rules,
                    pkt_cnt=pkt_cnt_without_rules,
                ),
                'with_rules_metadata_on': self.generate_dict_subconf(
                    pref_conf_path=pref_conf_metadata_path,
                    suri_rules_path=suri_rules,
                    suri_sleep_time=suri_sleep_time_rules,
                    arr_speedup=speedup_with_rules,
                    pkt_cnt=pkt_cnt_with_rules,
                ),
                'without_rules_metadata_off': self.generate_dict_subconf(
                    pref_conf_path=pref_conf_no_metadata_path,
                    suri_rules_path=suri_no_rules,
                    suri_sleep_time=suri_sleep_time_no_rules,
                    arr_speedup=speedup_without_rules,
                    pkt_cnt=pkt_cnt_without_rules,
                ),
                'with_rules_metadata_off': self.generate_dict_subconf(
                    pref_conf_path=pref_conf_no_metadata_path,
                    suri_rules_path=suri_rules,
                    suri_sleep_time=suri_sleep_time_rules,
                    arr_speedup=speedup_with_rules,
                    pkt_cnt=pkt_cnt_with_rules,
                ),
            }
        }

    def __init__(self):
        self.conf = {
            '1pf-1suri' : self.generate_dict_conf(
                '10',
                pref_conf_metadata_path=pwd + "/configureFilesSuricata/prefilter_1PF-1Suri.metadata.yaml",
                pref_conf_no_metadata_path=pwd + "/configureFilesSuricata/prefilter_1PF-1Suri.without_metadata.yaml",
                suri_conf_path=pwd + "/configureFilesSuricata/suricata_1PF-1Suri.yaml",
                speedup_without_rules=[0.18, 0.36, 0.47, 0.57, 0.65, 0.74],
                speedup_with_rules=[0.045, 0.049, 0.053, 0.056, 0.059, 0.063],
                pkt_cnt_without_rules=[4, 7, 10, 13, 16, 19],
                pkt_cnt_with_rules=[1, 1, 1, 1, 2, 2],
            ),
            '1pf-3suri': self.generate_dict_conf(
                '10',
                pref_conf_metadata_path=pwd + "/configureFilesSuricata/prefilter_1PF-3Suri.metadata.yaml",
                pref_conf_no_metadata_path=pwd + "/configureFilesSuricata/prefilter_1PF-3Suri.without_metadata.yaml",
                suri_conf_path=pwd + "/configureFilesSuricata/suricata_1PF-3Suri.yaml",
                speedup_without_rules=[2, 2.5, 2.9, 3.3, 4.2, 6],
                speedup_with_rules=[0.13, 0.14, 0.15, 0.16, 0.17, 0.18],
                pkt_cnt_without_rules=[40, 40, 60, 60, 80, 80],
                pkt_cnt_with_rules=[4, 5, 6, 7, 8, 9],
            ),
        }

    def get_conf(self):
        return self.conf

class Trex:
    def __init__(self, speedup, cnt):
        self.speedup = speedup
        self.cnt = cnt

    def runTrex(self):
        trex_daemon_handler = CTRexClient(trex_host='ryzlink.liberouter.org', trex_daemon_port=8090)
        trex_daemon_handler.force_kill(confirm=False)
        trex_daemon_handler.start_stateless(cfg='/etc/trex_cfg.yaml')

        c = STLClient(server='ryzlink.liberouter.org', sync_port=4501, async_port=4500)
        c.connect()

        try:
            c.reset(ports=0, restart=True)
            c.push_remote(pcap_file, ports=0, speedup=self.speedup, count=self.cnt)
            c.wait_on_traffic()

            stats = c.get_stats()
            c.disconnect()

            return stats[0]
        except STLError as e:
            print(e)

class Test:
    def __init__(self, pref_conf_path, rules, speedup, cnt, lcores, suri_conf_path, suri_sleep_time):
        self.pref_args = ["sudo", pref_path, "-l", lcores, "--file-prefix", "suricata", "--", "-c", pref_conf_path]
        self.suri_args = ["sudo", suri_path, "-c", suri_conf_path, "-S", rules, "--dpdk"]
        self.trex_args = {"speedup": speedup, "cnt": cnt}
        self.suri_sleep_time = suri_sleep_time

    def get_speed_from_stats(self, stats):
        pattern = r"'tx_bps': ([0-9]+\.[0-9]+)"
        match = re.search(pattern, str(stats))
        return round(float(match.group(1)) / 1000000)

    def restart_network_interfaces(self):
        command = "sudo dpdk/usertools/dpdk-devbind.py -b"
        os.system(f"{command} i40e 0000:43:00.0")
        os.system(f"{command} i40e 0000:43:00.1")
        os.system(f"{command} ixgbe 0000:04:00.0")
        os.system(f"{command} ixgbe 0000:04:00.1")
        os.system(f"{command} vfio-pci 0000:43:00.0")
        os.system(f"{command} vfio-pci 0000:43:00.1")
        os.system(f"{command} uio_pci_generic 0000:04:00.0")
        os.system(f"{command} uio_pci_generic 0000:04:00.1")

    def run_test(self):
        print("Restart network interfaces")
        self.restart_network_interfaces()

        print("Run Prefilter")
        pref_proc = subprocess.Popen(self.pref_args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        time.sleep(4)

        print("Run Suricata")
        suri_proc = subprocess.Popen(self.suri_args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        time.sleep(self.suri_sleep_time)

        print("Send packets")
        trex = Trex(self.trex_args["speedup"], self.trex_args["cnt"])
        # add check for stats
        stats = trex.runTrex()
        print(f"Statistics: {stats}")

        print("Kill both Prefilter and Suricata processes")
        os.system(f"sudo kill -2 {pref_proc.pid + 1}")
        os.system(f"sudo kill -2 {suri_proc.pid + 1}")
        print("Kill process trex")
        os.system("sudo kill -9 $(ps -aux | grep '_t-rex-64' -m 1 | awk '{print $2}')")
        time.sleep(6)

        return self.get_speed_from_stats(stats), pref_proc.stdout.read().decode("utf-8")

    def find_pkts(self, pref_output):
        pattern_attempts = r"enqueue attempts (\d+)"
        pattern_enqueued = r"enqueued to Suricata (\d+)"

        desired_line = pref_output.splitlines()[-3]
        match_attempts = re.search(pattern_attempts, desired_line)
        match_enqueued = re.search(pattern_enqueued, desired_line)

        if match_attempts and match_enqueued:
            num_attempts = int(match_attempts.group(1))
            num_enqueued = int(match_enqueued.group(1))
            percent_enqueued = 100.0 * num_enqueued / num_attempts
            print(f'num_enqueued = {num_enqueued}, num_attempts = {num_attempts}')
            return percent_enqueued
        else:
            print('Error')

class GraphPlotter:
    def __init__(self, x_vals, metadata_y, no_metadata_y, metadata_legend, no_metadata_legend, pdf_name, last_id):
        self.y_LL = int(min(metadata_y[last_id], no_metadata_y[last_id]) // 5) * 5
        self.y_UL = 100 + (100 - self.y_LL)/12.0
        self.x_LL, self.x_UL = x_vals[0], x_vals[last_id]
        self.metadata_legend, self.no_metadata_legend = metadata_legend, no_metadata_legend
        self.metadata_y, self.no_metadata_y = metadata_y, no_metadata_y
        self.x_vals = x_vals
        self.pdf_name = pdf_name

    def plot_graph(self):
        print(f'x values = {self.x_vals}')
        fig, ax = plt.subplots(1, 1, figsize=(16, 9), dpi=80)
        ax.grid(True)

        plt.plot(self.x_vals, self.metadata_y, lw=1.5, color='tab:red', label=self.metadata_legend)
        plt.plot(self.x_vals, self.no_metadata_y, lw=1.5, color='tab:blue', label=self.no_metadata_legend)
        plt.subplots_adjust(left=0.06, right=0.97, top=0.97, bottom=0.08)

        for y in range(self.y_LL, math.ceil(self.y_UL), 5):
            plt.hlines(y, xmin=0, xmax=70, colors='black', alpha=0.3, linestyles="--", lw=0.5)

        plt.tick_params(axis="both", which="both", bottom=False, top=False,
                        labelbottom=True, left=False, right=False, labelleft=True)

        offset = mtransforms.ScaledTranslation(0, 10 / 70, fig.dpi_scale_trans)
        ax.yaxis.set_label_coords(0.5, -0.1, transform=ax.transAxes + offset)

        for spine in plt.gca().spines.values():
            spine.set_alpha(.3)

        ax.set_ylabel('Processed packets [%]', rotation=90, fontsize=14)
        ax.yaxis.set_label_coords(-0.03, 0.5)
        plt.xlabel('Transmit speed [Mbps]', fontsize=14)

        ax.set_ylim(self.y_LL, self.y_UL)
        ax.set_xlim(self.x_LL - self.x_LL / 25.0, self.x_UL + self.x_LL / 10.0)

        plt.legend(fontsize=14)
        plt.savefig(self.pdf_name)

def run_configuration(subconf, conf_value):
    for speedup, cnt in zip(subconf['arr_speedup'], subconf['pkt_cnt']):
        all_rates = []
        all_res = []
        for i in range(1):
            test = Test(subconf['pf_conf_path'], subconf['suri_rules_path'], speedup, cnt,
                        conf_value['pf_workers'], conf_value['suri_conf_path'], subconf['suri_sleep_time'])
            actual_speed, output = test.run_test()
            all_rates.append(actual_speed)
            all_res.append(test.find_pkts(output))

        subconf['results'].append(sum(all_res) / len(all_res))
        subconf['actual_rates'].append(sum(all_rates) / len(all_rates))
        print(f'rate = {speedup}, arr_rates = {subconf["actual_rates"]}, arr_res = {subconf["results"]}')

def create_plot(conf_value, conf_key):
    for plot_type in ["with_rules", "without_rules"]:
        rates_metadata = conf_value['test_conf'][f"{plot_type}_metadata_on"]["actual_rates"]
        rates_no_metadata = conf_value['test_conf'][f"{plot_type}_metadata_off"]["actual_rates"]
        results_metadata = conf_value['test_conf'][f"{plot_type}_metadata_on"]["results"]
        results_no_metadata = conf_value['test_conf'][f"{plot_type}_metadata_off"]["results"]

        plot_obj = GraphPlotter([(x + y) / 2 for x, y in zip(rates_metadata, rates_no_metadata)],
                                results_metadata, results_no_metadata,
                                "Using metadata for IPv4, IPv6, TCP, UDP protocols", "Without metadata",
                                f"{plot_type}_conf.{conf_key}.pdf", len(rates_metadata) - 1)
        plot_obj.plot_graph()

def main():
    conf_program = Configuration()

    for conf_key, conf_value in conf_program.get_conf().items():
        for subconf in conf_value['test_conf'].values():
            run_configuration(subconf, conf_value)
            print('The end of the subconf test')

        create_plot(conf_value, conf_key)
        print('The end of the conf test')

if __name__ == "__main__":
    sys.exit(main())
