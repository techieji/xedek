from electric import *
import pytest

@pytest.fixture
def linear_circuit():
    terminal(0, voltage=5)
    wire(0, 1)
    lamp(1, 2)
    terminal(2, voltage=0)
    yield
    component.reset_class()

def test_linear_component_init(linear_circuit):
    assert component.get_component(1).voltage == 5
    assert component.get_component(1).p1 == 0
    assert component.get_component(2).p2 == 1

def test_linear_get_connected_components(linear_circuit):
    assert list(c.sid for c in component.get_component(2).get_connections()) == [1, 3]

def test_
