# Acknowledgement : Author - Prof. Kamakoti V, Dept. of CSE, IIT Madras
# Simple tests for an adder module
import cocotb
import random
import os

from cocotb.clock import Clock
from cocotb.decorators import coroutine
from cocotb.triggers import Timer, RisingEdge, ReadOnly, FallingEdge
from cocotb_bus.monitors import Monitor
from cocotb_bus.drivers import BitDriver
from cocotb.binary import BinaryValue
from cocotb.regression import TestFactory
from cocotb_bus.scoreboard import Scoreboard
from cocotb.result import TestFailure, TestSuccess

#------------------------------------Test for signed Division------------------------------------------------------
#count = int(os.environ['COUNT'])
@cocotb.test()
def noc_sim(dut):  #14
    cocotb.fork(Clock(dut.CLK, 10,).start())
    dut.RST_N = 0
    clkedge = RisingEdge(dut.CLK)
    yield clkedge
    clkedge = RisingEdge(dut.CLK)
    dut.RST_N <= 1

    for i in range(5000):
        yield clkedge
