# app/operations/calculation_factory.py

from abc import ABC, abstractmethod
from typing import List

# ----------------------------------------------------------------------------
# Base Strategy / Interface
# ----------------------------------------------------------------------------
class Calculation(ABC):
    def __init__(self, inputs: List[float]):
        self.inputs = inputs

    @abstractmethod
    def execute(self) -> float:
        pass


# ----------------------------------------------------------------------------
# Concrete Strategies
# ----------------------------------------------------------------------------
class Addition(Calculation):
    def execute(self) -> float:
        return sum(self.inputs)


class Subtraction(Calculation):
    def execute(self) -> float:
        result = self.inputs[0]
        for num in self.inputs[1:]:
            result -= num
        return result


class Multiplication(Calculation):
    def execute(self) -> float:
        result = 1
        for num in self.inputs:
            result *= num
        return result


class Division(Calculation):
    def execute(self) -> float:
        result = self.inputs[0]
        for num in self.inputs[1:]:
            if num == 0:
                raise ValueError("Cannot divide by zero")
            result /= num
        return result


# ----------------------------------------------------------------------------
# Factory Class
# ----------------------------------------------------------------------------
class CalculationFactory:
    """Factory that returns the correct calculation class based on type."""

    @staticmethod
    def create(calc_type: str, inputs: List[float]) -> Calculation:
        calc_type = calc_type.lower()
        if calc_type == "addition":
            return Addition(inputs)
        elif calc_type == "subtraction":
            return Subtraction(inputs)
        elif calc_type == "multiplication":
            return Multiplication(inputs)
        elif calc_type == "division":
            return Division(inputs)
        else:
            raise ValueError(f"Unsupported calculation type: {calc_type}")
