# Copyright cocotb contributors
# Licensed under the Revised BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-3-Clause
"""
Test function and substitutablility of async coroutines
"""

import cocotb
from cocotb.triggers import Timer
from cocotb.outcomes import Value, Error


class produce:
    """ Test helpers that produce a value / exception in different ways """
    @staticmethod
    @cocotb.coroutine
    def coro(outcome):
        yield Timer(1)
        return outcome.get()

    @staticmethod
    @cocotb.coroutine
    async def async_annotated(outcome):
        await Timer(1)
        return outcome.get()

    @staticmethod
    async def async_(outcome):
        await Timer(1)
        return outcome.get()


class SomeException(Exception):
    """ Custom exception to test for that can't be thrown by internals """
    pass


@cocotb.test()
def test_annotated_async_from_coro(dut):
    """
    Test that normal coroutines are able to call async functions annotated
    with `@cocotb.coroutine`
    """
    v = yield produce.async_annotated(Value(1))
    assert v == 1

    try:
        yield produce.async_annotated(Error(SomeException))
    except SomeException:
        pass
    else:
        assert False


@cocotb.test()
async def test_annotated_async_from_async(dut):
    """ Test that async coroutines are able to call themselves """
    v = await produce.async_annotated(Value(1))
    assert v == 1

    try:
        await produce.async_annotated(Error(SomeException))
    except SomeException:
        pass
    else:
        assert False


@cocotb.test()
async def test_async_from_async(dut):
    """ Test that async coroutines are able to call raw async functions """
    v = await produce.async_(Value(1))
    assert v == 1

    try:
        await produce.async_(Error(SomeException))
    except SomeException:
        pass
    else:
        assert False


@cocotb.test()
async def test_coro_from_async(dut):
    """ Test that async coroutines are able to call regular ones """
    v = await produce.coro(Value(1))
    assert v == 1

    try:
        await produce.coro(Error(SomeException))
    except SomeException:
        pass
    else:
        assert False


@cocotb.test()
async def test_trigger_await_gives_self(dut):
    """ Test that await returns the trigger itself for triggers """
    t = Timer(1)
    t2 = await t
    assert t2 is t


@cocotb.test()
async def test_await_causes_start(dut):
    """ Test that an annotated async coroutine gets marked as started """
    coro = produce.async_annotated(Value(1))
    assert not coro.has_started()
    await coro
    assert coro.has_started()


@cocotb.test()
def test_undecorated_coroutine_fork(dut):
    ran = False

    async def example():
        nonlocal ran
        await cocotb.triggers.Timer(1, 'ns')
        ran = True

    yield cocotb.fork(example()).join()
    assert ran


@cocotb.test()
def test_undecorated_coroutine_yield(dut):
    ran = False

    async def example():
        nonlocal ran
        await cocotb.triggers.Timer(1, 'ns')
        ran = True

    yield example()
    assert ran
