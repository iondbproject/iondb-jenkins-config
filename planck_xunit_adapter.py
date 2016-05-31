#!/usr/bin/env python3
import re
import sys

# Outputs PlanckUnit test results in JUnit XML spec.

def writeXMLHeader():
    print('<?xml version="1.0" encoding="UTF-8"?>')

def writeXunitTag(tagname, attributes=None):
    if attributes is None:
        attributes = {}

    print("<{tag} ".format(tag=tagname), end="")
    for key,val in attributes.items():
        print("{key}=\"{val}\" ".format(key=key, val=val), end="")
    print(">")

def adaptPlanckFile(suitename, targetfile, destinationfile=None):
    oldstdout = sys.stdout
    if destinationfile is not None:
        sys.stdout = destinationfile

    testcases = []
    summary = {}
    for line in targetfile:
        line = line.strip()

        matchobj = re.search(r"<test>line:\"(?P<line>.*?)\",file:\"(?P<file>.*?)\",function:\"(?P<function>.*?)\",message:\"(?P<message>.*?)\"<\/test>", line)
        if matchobj:
            testcases.append(matchobj.groupdict())

        summobj = re.search(r"<summary>total_tests:\"(?P<total_tests>.*?)\",total_passed:\"(?P<total_passed>.*?)\"<\/summary>", line)
        if summobj:
            summary = summobj.groupdict()

    # for test in testcases:
    #     print(test)
    # print()
    # print(summary)

    summary["total_failed"] = int(summary["total_tests"]) - int(summary["total_passed"])

    runattrs = {
        "name": suitename,
        "project": "IonDB",
        "tests": len(testcases),
        "started": len(testcases),
        "failures": summary["total_failed"],
        "errors": 0,
        "ignored": 0,
    }

    writeXMLHeader()
    writeXunitTag("testrun", runattrs)
    writeXunitTag("testsuite", {"name": suitename, "time": "0.0"})

    for i,case in enumerate(testcases):
        caseattrs = {
            "name": "_test #{num}".format(num=i),
            "classname": suitename,
            "time": "0.0",
        }

        writeXunitTag("testcase", caseattrs)

        if case["line"] != "-1": #if fail
            writeXunitTag("failure")
            print("Failed in function '{func}', at {filen}:{line}: {msg}\n".format(func=case["function"],
                                                                                   filen=case["file"],
                                                                                   line=case["line"],
                                                                                   msg=case["message"]))
            writeXunitTag("/failure")

        writeXunitTag("/testcase")

    writeXunitTag("/testsuite")
    writeXunitTag("/testrun")

    # Clean-up changes
    sys.stdout = oldstdout
