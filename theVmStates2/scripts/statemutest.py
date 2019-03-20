import sys
import os
import re
import subprocess
import argparse
import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import shutil


vQuit = False
vLock = threading.Lock()


def exec_proc(desc, proc):
    if not vQuit:
        with vLock:
            print("Processing", desc, "with Thread", threading.current_thread().getName())
        proc.wait()


def exec_batch(desc, batch_cmd, output_file):
    if not vQuit:
        with vLock:
            print("Processing", desc, "with Thread", threading.current_thread().getName())
            print("Logging", desc, "to", output_file)
        if output_file:
            with open(output_file, 'w') as writer:
                subprocess.call(batch_cmd, stdout=writer)
        else:
            subprocess.call(batch_cmd)


def process_dirs(param_dir, dest):
    setups = [x for x in os.listdir(param_dir) if x.startswith("setup_t_")]

    with ThreadPoolExecutor(max_workers=2) as executor:
        for setup in setups:
            tau = 0.5
            while tau <= 5.0:
                for r in range(1, 6):
                    for i in range(5000, 206000, 20000):
                        dest_tran = os.path.join(dest, re.match(r"^setup_(t_[\w_]+).yaml", setup).group(1))
                        dest_res = os.path.join(dest_tran, "{:.2f}_{:06d}_{:1d}".format(tau, i, r).replace(".", "-"))
                        setup_file = os.path.join(dest_res, "setup.yaml")

                        if os.path.exists(setup_file):
                            print("Found configuration", setup_file)
                            continue

                        try:
                            os.makedirs(dest_res)
                        except OSError as e:
                            pass
                        changes = [
                            ("tau", tau),
                            ("numberOfIterations", i),
                            ("numberOfIndependentRuns", r)
                        ]
                        shutil.copyfile(os.path.join(param_dir, setup), setup_file)

                        for change in changes:
                            cmd = "python setups.py %s %s %s %s" % (setup_file, change[0], change[1], setup_file)
                            future = executor.submit(exec_batch, setup_file, cmd, None)
                tau += 0.25


def process_statemutest(tests_dir, workers, clean):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for transition in os.listdir(tests_dir):
            transition_dir = os.path.join(tests_dir, transition)
            if os.path.isdir(transition_dir):
                for configuration in os.listdir(transition_dir):
                    configuration_dir = os.path.join(transition_dir, configuration)
                    if os.path.isdir(configuration_dir):
                        others = [x for x in os.listdir(configuration_dir) if
                                  os.path.isdir(os.path.join(configuration_dir, x))]
                        logs = [x for x in os.listdir(configuration_dir) if
                                x.endswith(".log")]
                        if clean:
                            for other in others:
                                try:
                                    shutil.rmtree(os.path.join(configuration_dir, other))
                                    print("Removed", os.path.join(configuration_dir, other))
                                except Exception:
                                    print("Error trying to remove a configuration",
                                          os.path.join(configuration_dir, other))
                            for log in logs:
                                os.remove(os.path.join(configuration_dir, log))
                                print("Removed", os.path.join(configuration_dir, log))
                            continue
                        setup_file = os.path.join(configuration_dir, "setup.yaml")
                        if os.path.exists(setup_file):
                            fdate = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                            log = os.path.join(configuration_dir, fdate + ".log")
                            dest = os.path.join(configuration_dir, fdate)
                            os.mkdir(dest)
                            #proc = subprocess.Popen("statemutest.bat %s %s" % (dest, setup_file), shell=True)
                            future = executor.submit(exec_batch, setup_file, "statemutest.bat %s %s" % (dest, setup_file),
                                                     log)


if __name__ == "__main__":
    def statemutest_args(args):
        process_statemutest(args.test_dirs, args.workers, args.clean)

    def dirs_args(args):
        process_dirs(args.param_dir, args.dest)

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()

    statemutest = sub.add_parser("statemutest")
    statemutest.add_argument("test_dirs", type=str)
    statemutest.add_argument("workers", type=int, default=2)
    statemutest.add_argument("--clean", action="store_true")
    statemutest.set_defaults(func=statemutest_args)

    param = sub.add_parser("param")
    param.add_argument("param_dir", type=str)
    param.add_argument("dest", type=str)
    param.set_defaults(func=dirs_args)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        vQuit = True
    print("Finished.")
