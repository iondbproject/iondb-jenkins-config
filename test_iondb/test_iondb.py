#!/usr/bin/env python3

import sys
import os
import os.path
import shutil

sys.path.append("../")

import planck_xunit_adapter as pxa

BIN_PATH = "../../build_iondb/iondb/build/bin/"

print("Start IonDB Test Phase.")

try:
    shutil.rmtree("output/")
except FileNotFoundError:
    print("output/ didn't exist. No remove.")
os.makedirs("output/", exist_ok=True)
os.chdir("output/")

for testexec in os.listdir(BIN_PATH):
    abstest_path = os.path.join(BIN_PATH, testexec)
    planck_outputfname = "planckunit_{testname}_output.txt".format(testname=testexec)
    xunit_outputfname = "xunit_{testname}_output.txt".format(testname=testexec)
    os.system("chmod +x {execfp}".format(execfp=abstest_path))
    os.system("{testfp} | tee {planckfp}".format(testfp=abstest_path, planckfp=planck_outputfname))

    print("Adapting {pl} -> {xl}...".format(pl=planck_outputfname, xl=xunit_outputfname))
    with open(planck_outputfname, "r+") as planck_file, open(xunit_outputfname, "w+") as xunit_file:
        pxa.adaptPlanckFile(testexec, planck_file, xunit_file)

print("Test IonDB done.")