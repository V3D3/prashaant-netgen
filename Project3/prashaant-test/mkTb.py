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

@cocotb.test()
def hello_world_test(dut): # dut: design under test
    # creating a clock called dut.CLK, having a time duration of 10 su
    # su: simulation units (could be any real time unit)
    cocotb.fork(Clock(dut.CLK, 10,).start())
    dut.RST_N = 0 # reset negative

    # RST_N CLK are default and created by bluespec

    # wait for a rising edge
    clkedge = RisingEdge(dut.CLK)

    dut.RST_N <= 1
    yield clkedge
    for i in range(500):
        yield clkedge
