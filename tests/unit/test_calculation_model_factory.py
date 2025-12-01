from app.models.calculation import Calculation, Addition, Subtraction, Multiplication, Division
import uuid
import pytest


def test_factory_creates_correct_subclass():
    user_id = uuid.uuid4()

    add = Calculation.create("addition", user_id, [1, 2, 3])
    sub = Calculation.create("subtraction", user_id, [10, 3])
    mult = Calculation.create("multiplication", user_id, [2, 3, 4])
    div = Calculation.create("division", user_id, [100, 5])

    assert isinstance(add, Addition)
    assert isinstance(sub, Subtraction)
    assert isinstance(mult, Multiplication)
    assert isinstance(div, Division)


def test_factory_invalid_type():
    with pytest.raises(ValueError) as e:
        Calculation.create("modulus", uuid.uuid4(), [10, 2])
    assert "Unsupported calculation type" in str(e.value)


def test_get_result_methods_work():
    user_id = uuid.uuid4()

    add = Calculation.create("addition", user_id, [1, 2, 3])
    sub = Calculation.create("subtraction", user_id, [10, 3, 2])
    mult = Calculation.create("multiplication", user_id, [2, 3, 4])
    div = Calculation.create("division", user_id, [100, 2, 5])

    assert add.get_result() == 6
    assert sub.get_result() == 5
    assert mult.get_result() == 24
    assert div.get_result() == 10
