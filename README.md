# IonDB Build Scripts
This repository contains build scripts and configurations for IonDB.

# PyPlanck
Python script to read PlanckUnit XML-style output from a serial port (including some syntax checking) and copy to file.

## Restrictions

* PlanckUnit tests must use the XML output format.
* Test results must not include any messages containing the following tags:
* `<suite>`, `</suite>`
* `<test>`, `</test>`
* `<summary>`, `</summary>`

## Usage

PyPlanck can be run using Python at the command line with the following syntax:

`pyplanck.py [-h] [-t TIMEOUT] [-b RATE] [-f OUT] [-i] [-c] port`

Positional arguments:
* `port`
 * The serial port to receive data from

Optional arguments:
* `-h`, `--help`
 * Show this help message and exit
* `-t TIMEOUT`, `--timeout TIMEOUT`
 * Time to wait for a line before giving up (including at end of program)
* `-b RATE`, `--baud RATE`
 * Baud rate to listen for data
* `-f OUT`, `--folder OUT`
 * Folder to write output data to
* `-i`
 * Set to print input to console as it is being read
* `-c`
 * Set to clear folder when producing tests


## Dependencies

PyPlanck:
* [pySerial](https://github.com/pyserial/pyserial) "pySerial plugin on GitHub"

-----------------

# Contributors

Graeme Douglas, Wade Penson, Kris Wallperington (Eric Huang), Eliana Wardle