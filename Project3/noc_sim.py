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
    yield clkedge #Step 0
    yield clkedge #Step 1
    yield clkedge #Step 2
    yield clkedge #Step 3
    yield clkedge #Step 4
    yield clkedge #Step 5
    yield clkedge #Step 6
    yield clkedge #Step 7
    yield clkedge #Step 8
    yield clkedge #Step 9
    yield clkedge #Step 10
    yield clkedge #Step 11
    yield clkedge #Step 12
    yield clkedge #Step 13
    yield clkedge #Step 14
    yield clkedge #Step 15
    yield clkedge #Step 16
    yield clkedge #Step 17
    yield clkedge #Step 18

