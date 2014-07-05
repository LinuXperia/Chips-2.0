#!/usr/bin/env python

import subprocess
import atexit
from math import pi
from chips.api.api import *

try:
    import scipy as s
    from scipy.signal import firwin
except ImportError:
    print "You need scipy to run this script!"
    exit(0)

try:
    import numpy as n
except ImportError:
    print "You need numpy to run this script!"
    exit(0)

try:
    from matplotlib import pyplot
except ImportError:
    print "You need matplotlib to run this script!"
    exit(0)

def test():

    #create a chip
    chip = Chip("filter_example")

    #low pass filter half nyquist 50 tap
    kernel = Stimulus(chip, "kernel", "float", firwin(50, 0.5, window="blackman"))

    #impulse response
    input_ = Stimulus(chip, "input", "float", [1.0] + [0.0 for i in range(1024)])
    output = Response(chip, "output", "float", 1024)
    
    #create a filter component using the C code
    fir_comp = Component("fir.c")

    #add an instance to the chip
    fir_inst_1 = fir_comp(
        chip, 
        inputs = {
            "a":input_,
            "k":kernel,
        },
        outputs = {
            "z":output,
        },
        parameters = {
            "N":len(kernel)-1,
        },
    )

    #run the simulation
    chip.simulation_reset()
    chip.simulation_run()
        
    #plot the result
    pyplot.semilogy(n.abs(s.fft(list(output)))[0:len(output)/2])
    pyplot.title("Magnitude of Impulse Response")
    pyplot.xlim(0, 512)
    pyplot.xlabel("X Sample")
    pyplot.savefig("../docs/source/examples/images/example_6.png")
    pyplot.show()



def indent(lines):
    return "\n    ".join(lines.splitlines())

def generate_docs():

    documentation = """

FIR Filter
----------

An FIR filter contains a tapped delay line. By applying a weighting to each
tap, and summing the results we can create a filter. The coefficients of the
filter are critical. Here we create the coefficients using the firwin function
from the SciPy package. In this example we create a low pass filter using a
Blackman window. The Blackman window gives good attenuation in the stop band.

The C code includes a simple test routine that calculates the frequency
spectrum of a 64 point sine wave.


.. code-block:: c

    %s

Increasing the length of the filter kernel results in a faster roll-off and
greater attenuation.

.. image:: images/example_6.png

While in this example, we calculate all the coefficients inside a single
process, it is possible to generate a pipelined implementation, and allow the
work to be carried out by multiple processes resulting in an increase in the
throughput rate.

`The Scientist and Engineer's Guide to Digital Signal Processing <http://www.dspguide.com/>`_ 
gives a straight forward introduction, and can be viewed on-line for free. 

"""%indent(open("fir.c").read())

    document = open("../docs/source/examples/example_6.rst", "w").write(documentation)

test()
generate_docs()
