#!/usr/bin/python

import subprocess
import shlex
import sys

def send(line):

    line = line.strip().strip("\n") + "\n"  # Make sure there is one newline.
    print "vvvvvvvvvvvvvvvvvvvv"
    print "Sending " + line
    print "^^^^^^^^^^^^^^^^^^^^"
    proc.stdin.write(line)


def receive():

    end = False
    while not end:

        outLine = proc.stdout.readline()
        outLine = outLine.strip("\n")     # Remove line feeds for printing

        print outLine

        if (outLine.strip().startswith("<END>") or
            outLine.strip().startswith("<WAITING>") or
            outLine.strip().startswith("<READY>") or
            outLine.strip().startswith("<GOODBYE>")):
            end = True

print "\n\n\n\n\n"
print "--------------------------------------------------------------------------------"

command = "./eikonal"
commandList = shlex.split(command)

proc = subprocess.Popen(commandList,
                            # shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            )

receive()
send(".")
receive()
send("what")
receive()
send("x")
receive()

proc.wait()   # for it to finish

print "--------------------------------------------------------------------------------"
