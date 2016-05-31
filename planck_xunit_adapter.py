#!/usr/bin/env python3
import re
import sys

def writeXunitTag(tagname, attributes=None):
    if attributes is None:
        attributes = {}

    print("<{tag} ".format(tag=tagname), end="")
    for key,val in attributes.items():
        print("{key}=\"{val}\" ".format(key=key, val=val), end="")
    print(">")

def adaptPlanckFile(targetfile, destinationfile=None):
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

    suiteattrs = {
        "name": "PlanckUnit Output",
        "reports": 1,
        "test-cases": len(testcases),
        "tests": len(testcases),
        "skip": 0,
        "errors": summary["total_failed"],
        "errors-detail": summary["total_failed"],
        "failures": summary["total_failed"],
        "failures-detail": summary["total_failed"],
    }

    writeXunitTag("test-suite", suiteattrs)

    for i,case in enumerate(testcases):
        caseattrs = {
            "tests": 1,
            "errors": 0 if case["line"] == "-1" else 1,
            "failures": 0 if case["line"] == "-1" else 1,
            "name": "Test #{}".format(i),
            "label": "A unit test",
        }

        writeXunitTag("test-case", caseattrs)

        if case["line"] != "-1": #if fail
            writeXunitTag("error")
            print("Failed in function '{func}', at {filen}:{line}: {msg}\n".format(func=case["function"],
                                                                                   filen=case["file"],
                                                                                   line=case["line"],
                                                                                   msg=case["message"]))
            writeXunitTag("/error")

        writeXunitTag("/test-case")

    writeXunitTag("/test-suite")

    # Clean-up changes
    sys.stdout = oldstdout
