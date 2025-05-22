"""
Safe mathematical expression evaluator, avoiding direct use of eval
"""

import ast
import math
import numpy as np
import operator as op

# 支持的操作
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

# 允许的函数和常量
math_functions = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'exp': math.exp,
    'log': math.log,
    'log10': math.log10,
    'sqrt': math.sqrt,
    'pi': math.pi,
    'e': math.e,
    'abs': abs,
    'round': round,
    'ceil': math.ceil,
    'floor': math.floor,
}

def safe_eval(expr, variables=None):
    """
    Safely evaluate a mathematical expression
    
    Args:
        expr (str): Mathematical expression
        variables (dict, optional): Variable dictionary, e.g., {'x': 2}
        
    Returns:
        float: Calculation result
    """
    if variables is None:
        variables = {}
    
    # Parse expression
    try:
        node = ast.parse(expr, mode='eval').body
    except SyntaxError:
        raise ValueError(f"Invalid expression: {expr}")
    
    def _eval(node):
        # Number
        if isinstance(node, ast.Num):
            return node.n
        # Name (variable or constant)
        elif isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            elif node.id in math_functions:
                return math_functions[node.id]
            raise ValueError(f"Unknown variable or function: {node.id}")
        # Unary operation (+x, -x)
        elif isinstance(node, ast.UnaryOp):
            op_func = operators.get(type(node.op))
            if op_func:
                return op_func(_eval(node.operand))
            raise ValueError(f"Unsupported unary operation: {type(node.op).__name__}")
        # Binary operation (x+y, x-y, etc)
        elif isinstance(node, ast.BinOp):
            op_func = operators.get(type(node.op))
            if op_func:
                return op_func(_eval(node.left), _eval(node.right))
            raise ValueError(f"Unsupported binary operation: {type(node.op).__name__}")
        # Function call
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name in math_functions:
                args = [_eval(arg) for arg in node.args]
                return math_functions[func_name](*args)
            raise ValueError(f"Unsupported function: {func_name}")
        # Constant
        elif isinstance(node, ast.Constant):
            return node.value
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")
    
    return _eval(node)

def safe_eval_with_x(expr, x_value):
    """Safe evaluator specialized for function plotting
    
    Args:
        expr (str): Mathematical expression, using x as variable
        x_value (float): x value
        
    Returns:
        float: Calculation result
    """
    return safe_eval(expr, {'x': x_value})

def create_safe_function(expr):
    """Create a safe function object
    
    Args:
        expr (str): Mathematical expression
        
    Returns:
        Function object, accepting one parameter x
    """
    def func(x):
        return safe_eval_with_x(expr, x)
    return func
