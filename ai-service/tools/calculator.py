from langchain.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First number.
        b: Second number.
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number.
        b: Second number.
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide the first number by the second number.

    Args:
        a: First number.
        b: Second number.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a / b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first number.

    Args:
        a: First number.
        b: Second number.
    """
    return a - b


@tool
def percentage(a: int, b: int) -> float:
    """Calculate the percentage of the first number with respect to the second number.

    Args:
        a: First number.
        b: Second number.
    """
    if b == 0:
        raise ValueError("Cannot calculate percentage with respect to zero.")

    return (a / b) * 100
