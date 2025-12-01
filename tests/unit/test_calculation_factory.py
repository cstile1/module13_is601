# tests/unit/test_calculation_factory.py

import pytest
from app.operations.calculation_factory import CalculationFactory

def test_factory_addition():
    calc = CalculationFactory.create("addition", [2, 3, 5])
    assert calc.execute() == 10

def test_factory_subtraction():
    calc = CalculationFactory.create("subtraction", [10, 3, 2])
    assert calc.execute() == 5

def test_factory_multiplication():
    calc = CalculationFactory.create("multiplication", [2, 3, 4])
    assert calc.execute() == 24

def test_factory_division():
    calc = CalculationFactory.create("division", [100, 5, 2])
    assert calc.execute() == 10

def test_factory_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc = CalculationFactory.create("division", [10, 0])
        calc.execute()

def test_factory_invalid_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.create("power", [2, 3])
