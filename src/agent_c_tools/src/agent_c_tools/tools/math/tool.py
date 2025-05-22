"""
Math Toolset for Agent C - Providing advanced mathematical calculation functionality
"""

import io
import numpy as np
import sympy as sp
from scipy import integrate, optimize, stats
import matplotlib.pyplot as plt
from base64 import b64encode
from typing import List, Dict, Union, Optional, Any

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.math.safe_eval import safe_eval, create_safe_function, safe_eval_with_x
from agent_c_tools.tools.math.prompt import MathSection


class MathTools(Toolset):
    """
    MathTools provides advanced mathematical calculation capabilities including:
    - Basic arithmetic
    - Calculus (differentiation, integration)
    - Algebra (solving equations, simplifying expressions)
    - Matrices and linear algebra
    - Statistics and probability
    - Function visualization
    - Numerical optimization
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the Math toolset.
        """
        super().__init__(**kwargs)
        # self.section = MathSection()
    
    # ------ Basic Math Tools ------
    
    @json_schema(
        description="Safely evaluate mathematical expressions",
        params={
            "expression": {
                "type": "string",
                "description": "Mathematical expression string, e.g., \"2 * (3 + 4) ** 2\"",
                "required": True
            }
        }
    )
    async def evaluate_expression(self, expression: str) -> float:
        """
        Safely evaluate mathematical expressions
        
        Args:
            expression: Mathematical expression string, e.g., "2 * (3 + 4) ** 2"
            
        Returns:
            The calculated result of the expression
        """
        return safe_eval(expression)
    
    @json_schema(
        description="Perform basic arithmetic operations",
        params={
            "a": {
                "type": "number",
                "description": "First number",
                "required": True
            },
            "operation": {
                "type": "string",
                "description": "Operation type, can be \"add\", \"subtract\", \"multiply\", \"divide\", \"power\"",
                "required": True,
                "enum": ["add", "subtract", "multiply", "divide", "power"]
            },
            "b": {
                "type": "number",
                "description": "Second number",
                "required": True
            }
        }
    )
    async def calculate(self, a: float, operation: str, b: float) -> float:
        """
        Perform basic arithmetic operations
        
        Args:
            a: First number
            operation: Operation type, can be "add", "subtract", "multiply", "divide", "power"
            b: Second number
            
        Returns:
            Calculation result
        """
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Divisor cannot be zero")
            return a / b
        elif operation == "power":
            return a ** b
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    # ------ Symbolic Computation Tools ------
    
    @json_schema(
        description="Calculate the derivative of a function",
        params={
            "expression": {
                "type": "string",
                "description": "Function expression, e.g., \"x**2 + 2*x\"",
                "required": True
            },
            "variable": {
                "type": "string",
                "description": "Differentiation variable, e.g., \"x\"",
                "required": True
            },
            "order": {
                "type": "integer",
                "description": "Order of the derivative, default is 1",
                "required": False
            }
        }
    )
    async def differentiate(self, expression: str, variable: str, order: int = 1) -> str:
        """
        Calculate the derivative of a function
        
        Args:
            expression: Function expression, e.g., "x**2 + 2*x"
            variable: Differentiation variable, e.g., "x"
            order: Order of the derivative, default is 1
            
        Returns:
            Expression of the derivative
        """
        x = sp.Symbol(variable)
        expr = sp.sympify(expression)
        result = sp.diff(expr, x, order)
        return str(result)
    
    @json_schema(
        description="Calculate the integral of a function",
        params={
            "expression": {
                "type": "string",
                "description": "Function expression, e.g., \"x**2 + 2*x\"",
                "required": True
            },
            "variable": {
                "type": "string",
                "description": "Integration variable, e.g., \"x\"",
                "required": True
            },
            "lower_bound": {
                "type": "string",
                "description": "Lower bound of integration (optional)",
                "required": False
            },
            "upper_bound": {
                "type": "string",
                "description": "Upper bound of integration (optional)",
                "required": False
            }
        }
    )
    async def integrate_symbolic(self, expression: str, variable: str, lower_bound: str = None, upper_bound: str = None) -> str:
        """
        Calculate the integral of a function
        
        Args:
            expression: Function expression, e.g., "x**2 + 2*x"
            variable: Integration variable, e.g., "x"
            lower_bound: Lower bound of integration (optional)
            upper_bound: Upper bound of integration (optional)
            
        Returns:
            Expression of the integration result
        """
        x = sp.Symbol(variable)
        expr = sp.sympify(expression)
        
        if lower_bound is not None and upper_bound is not None:
            # Definite integral
            lower = sp.sympify(lower_bound)
            upper = sp.sympify(upper_bound)
            result = sp.integrate(expr, (x, lower, upper))
        else:
            # Indefinite integral
            result = sp.integrate(expr, x)
        
        return str(result)
    
    @json_schema(
        description="Numerically calculate a definite integral",
        params={
            "expression": {
                "type": "string",
                "description": "Function expression, e.g., \"x**2 + 2*x\"",
                "required": True
            },
            "lower_bound": {
                "type": "number",
                "description": "Lower bound of integration",
                "required": True
            },
            "upper_bound": {
                "type": "number",
                "description": "Upper bound of integration",
                "required": True
            }
        }
    )
    async def integrate_numeric(self, expression: str, lower_bound: float, upper_bound: float) -> float:
        """
        Numerically calculate a definite integral
        
        Args:
            expression: Function expression, e.g., "x**2 + 2*x"
            lower_bound: Lower bound of integration
            upper_bound: Upper bound of integration
            
        Returns:
            Numerical result of the integral
        """
        # Safely create function
        f = create_safe_function(expression)
        result, error = integrate.quad(f, lower_bound, upper_bound)
        return result
    
    @json_schema(
        description="Solve an equation",
        params={
            "equation": {
                "type": "string",
                "description": "Equation expression, e.g., \"x**2 - 4 = 0\" or \"x**2 - 4\" (meaning x²=4)",
                "required": True
            },
            "variable": {
                "type": "string",
                "description": "Variable to solve for, e.g., \"x\"",
                "required": True
            }
        }
    )
    async def solve_equation(self, equation: str, variable: str) -> str:
        """
        Solve an equation
        
        Args:
            equation: Equation expression, e.g., "x**2 - 4 = 0" or "x**2 - 4" (meaning x²=4)
            variable: Variable to solve for, e.g., "x"
            
        Returns:
            Solution of the equation
        """
        x = sp.Symbol(variable)
        # Handle cases containing an equals sign
        if "=" in equation:
            left, right = equation.split("=", 1)
            left = sp.sympify(left.strip())
            right = sp.sympify(right.strip())
            expr = left - right
        else:
            expr = sp.sympify(equation)
        
        solutions = sp.solve(expr, x)
        return str(solutions)
    
    @json_schema(
        description="Solve a system of equations",
        params={
            "equations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of equations, e.g., [\"x + y = 10\", \"2*x - y = 5\"]",
                "required": True
            },
            "variables": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of variables, e.g., [\"x\", \"y\"]",
                "required": True
            }
        }
    )
    async def solve_system(self, equations: List[str], variables: List[str]) -> str:
        """
        Solve a system of equations
        
        Args:
            equations: List of equations, e.g., ["x + y = 10", "2*x - y = 5"]
            variables: List of variables, e.g., ["x", "y"]
            
        Returns:
            Solution of the equation system
        """
        # Create symbolic variables
        syms = [sp.Symbol(v) for v in variables]
        
        # Process equations
        exprs = []
        for eq in equations:
            if "=" in eq:
                left, right = eq.split("=", 1)
                left = sp.sympify(left.strip())
                right = sp.sympify(right.strip())
                exprs.append(left - right)
            else:
                exprs.append(sp.sympify(eq))
        
        # Solve
        solutions = sp.solve(exprs, syms)
        return str(solutions)
    
    @json_schema(
        description="Simplify algebraic expression",
        params={
            "expression": {
                "type": "string",
                "description": "Expression to simplify",
                "required": True
            }
        }
    )
    async def simplify_expression(self, expression: str) -> str:
        """
        Simplify algebraic expression
        
        Args:
            expression: Expression to simplify
            
        Returns:
            Simplified expression
        """
        expr = sp.sympify(expression)
        result = sp.simplify(expr)
        return str(result)
    
    @json_schema(
        description="Expand algebraic expression",
        params={
            "expression": {
                "type": "string",
                "description": "Expression to expand",
                "required": True
            }
        }
    )
    async def expand_expression(self, expression: str) -> str:
        """
        Expand algebraic expression
        
        Args:
            expression: Expression to expand
            
        Returns:
            Expanded expression
        """
        expr = sp.sympify(expression)
        result = sp.expand(expr)
        return str(result)
    
    @json_schema(
        description="Factor an expression",
        params={
            "expression": {
                "type": "string",
                "description": "Expression to factor",
                "required": True
            }
        }
    )
    async def factor_expression(self, expression: str) -> str:
        """
        Factor an expression
        
        Args:
            expression: Expression to factor
            
        Returns:
            Factored expression
        """
        expr = sp.sympify(expression)
        result = sp.factor(expr)
        return str(result)
    
    # ------ Numerical Optimization Tools ------
    
    @json_schema(
        description="Find the local minimum value of a function",
        params={
            "expression": {
                "type": "string",
                "description": "Function expression, e.g., \"x**2 + 2*x\"",
                "required": True
            },
            "lower_bound": {
                "type": "number",
                "description": "Lower bound of the search range",
                "required": True
            },
            "upper_bound": {
                "type": "number",
                "description": "Upper bound of the search range",
                "required": True
            }
        }
    )
    async def find_minimum(self, expression: str, lower_bound: float, upper_bound: float) -> Dict[str, Any]:
        """
        Find the local minimum value of a function
        
        Args:
            expression: Function expression, e.g., "x**2 + 2*x"
            lower_bound: Lower bound of the search range
            upper_bound: Upper bound of the search range
            
        Returns:
            Dictionary containing the minimum value and corresponding x value
        """
        f = create_safe_function(expression)
        result = optimize.minimize_scalar(f, bounds=(lower_bound, upper_bound), method='bounded')
        
        return {
            "x_value": float(result.x),
            "min_value": float(result.fun),
            "success": bool(result.success)
        }
    
    @json_schema(
        description="Find the root (zero) of a function",
        params={
            "expression": {
                "type": "string",
                "description": "Function expression, e.g., \"x**2 - 4\"",
                "required": True
            },
            "lower_bound": {
                "type": "number",
                "description": "Lower bound of the search range",
                "required": True
            },
            "upper_bound": {
                "type": "number",
                "description": "Upper bound of the search range",
                "required": True
            }
        }
    )
    async def find_root(self, expression: str, lower_bound: float, upper_bound: float) -> float:
        """
        Find the root (zero) of a function
        
        Args:
            expression: Function expression, e.g., "x**2 - 4"
            lower_bound: Lower bound of the search range
            upper_bound: Upper bound of the search range
            
        Returns:
            Root of the function
        """
        f = create_safe_function(expression)
        result = optimize.brentq(f, lower_bound, upper_bound)
        return float(result)
    
    # ------ Matrix Calculation Tools ------
    
    @json_schema(
        description="Perform matrix operations",
        params={
            "operation": {
                "type": "string",
                "description": "Operation type, e.g., \"multiply\", \"inverse\", \"determinant\", \"eigenvalues\", \"transpose\"",
                "required": True,
                "enum": ["multiply", "inverse", "determinant", "eigenvalues", "transpose", "add", "subtract"]
            },
            "matrix_a": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "number"}},
                "description": "First matrix, format like [[1, 2], [3, 4]]",
                "required": True
            },
            "matrix_b": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "number"}},
                "description": "Second matrix (if needed), same format as above",
                "required": False
            }
        }
    )
    async def matrix_operation(self, operation: str, matrix_a: List[List[float]], matrix_b: List[List[float]] = None) -> str:
        """
        Perform matrix operations
        
        Args:
            operation: Operation type, e.g., "multiply", "inverse", "determinant", "eigenvalues", "transpose"
            matrix_a: First matrix, format like [[1, 2], [3, 4]]
            matrix_b: Second matrix (if needed), same format as above
            
        Returns:
            Operation result
        """
        # Convert to numpy arrays
        mat_a = np.array(matrix_a)
        
        if matrix_b is not None:
            mat_b = np.array(matrix_b)
    
        if operation == "determinant":
            return str(np.linalg.det(mat_a))
        elif operation == "inverse":
            return str(np.linalg.inv(mat_a))
        elif operation == "eigenvalues":
            return str(np.linalg.eigvals(mat_a))
        elif operation == "transpose":
            return str(np.transpose(mat_a))
        elif operation == "multiply" and matrix_b is not None:
            return str(np.matmul(mat_a, mat_b))
        elif operation == "add" and matrix_b is not None:
            return str(mat_a + mat_b)
        elif operation == "subtract" and matrix_b is not None:
            return str(mat_a - mat_b)
        else:
            raise ValueError("Unsupported operation or missing parameters")
    
    # ------ Visualization Tools ------
    
    @json_schema(
        description="Plot a function graph",
        params={
            "expression": {
                "type": "string",
                "description": "Function expression, e.g., \"x**2 + 2*x\"",
                "required": True
            },
            "x_min": {
                "type": "number",
                "description": "Minimum x-axis value",
                "required": False
            },
            "x_max": {
                "type": "number",
                "description": "Maximum x-axis value",
                "required": False
            },
            "points": {
                "type": "integer",
                "description": "Number of sampling points",
                "required": False
            }
        }
    )
    async def plot_function(self, expression: str, x_min: float = -10, x_max: float = 10, points: int = 1000):
        """
        Plot a function graph
        
        Args:
            expression: Function expression, e.g., "x**2 + 2*x"
            x_min: Minimum x-axis value
            x_max: Maximum x-axis value
            points: Number of sampling points
            
        Returns:
            Function graph image
        """
        # Generate x values
        x_values = np.linspace(x_min, x_max, points)
        
        # Safely calculate y values
        try:
            f = create_safe_function(expression)
            y_values = [f(x_val) for x_val in x_values]
            
            # Create image
            plt.figure(figsize=(10, 6))
            plt.plot(x_values, y_values)
            plt.grid(True)
            plt.title(f"y = {expression}")
            plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            plt.xlabel('x')
            plt.ylabel('y')
            
            # Convert image to binary data
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Get binary data and base64 encode it
            img_bytes = buffer.getvalue()
            base64_img = b64encode(img_bytes).decode('utf-8')
            
            # Create a name for the plot
            img_name = f"plot_{expression.replace(' ', '_')[:30]}.png"
            
            # Return the image by raising a render media event
            await self._raise_render_media(
                sent_by_class=self.__class__.__name__,
                sent_by_function='plot_function',
                content_type="image/png",
                name=img_name,
                content_bytes=img_bytes,
                content=base64_img
            )
            
            return f"Plot created for y = {expression}"
        
        except Exception as e:
            plt.close()
            raise ValueError(f"Error when plotting function: {str(e)}")
    
    @json_schema(
        description="Plot graphs of multiple functions",
        params={
            "expressions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of function expressions, e.g., [\"x**2\", \"2*x + 1\"]",
                "required": True
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of legend labels (optional)",
                "required": False
            },
            "x_min": {
                "type": "number",
                "description": "Minimum x-axis value",
                "required": False
            },
            "x_max": {
                "type": "number",
                "description": "Maximum x-axis value",
                "required": False
            },
            "points": {
                "type": "integer",
                "description": "Number of sampling points",
                "required": False
            }
        }
    )
    async def plot_multiple_functions(self, expressions: List[str], labels: List[str] = None, 
                                     x_min: float = -10, x_max: float = 10, points: int = 500):
        """
        Plot graphs of multiple functions
        
        Args:
            expressions: List of function expressions, e.g., ["x**2", "2*x + 1"]
            labels: List of legend labels (optional)
            x_min: Minimum x-axis value
            x_max: Maximum x-axis value
            points: Number of sampling points
            
        Returns:
            Function graph image
        """
        if labels is None:
            labels = [f"f_{i+1}(x) = {expr}" for i, expr in enumerate(expressions)]
        
        if len(labels) != len(expressions):
            labels = [f"f_{i+1}(x) = {expr}" for i, expr in enumerate(expressions)]
        
        # Generate x values
        x_values = np.linspace(x_min, x_max, points)
        
        plt.figure(figsize=(10, 6))
        
        # Plot each function
        for i, expr in enumerate(expressions):
            try:
                f = create_safe_function(expr)
                y_values = [f(x_val) for x_val in x_values]
                plt.plot(x_values, y_values, label=labels[i])
            except Exception as e:
                await self._raise_message_event(f"Error when plotting function '{expr}': {str(e)}")
        
        plt.grid(True)
        plt.title("Function Comparison")
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        
        # Convert image to binary data
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        
        # Get binary data and base64 encode it
        img_bytes = buffer.getvalue()
        base64_img = b64encode(img_bytes).decode('utf-8')
        
        # Create a name for the plot
        img_name = f"multiplot_{len(expressions)}_functions.png"
        
        # Return the image by raising a render media event
        await self._raise_render_media(
            sent_by_class=self.__class__.__name__,
            sent_by_function='plot_multiple_functions',
            content_type="image/png",
            name=img_name,
            content_bytes=img_bytes,
            content=base64_img
        )
        
        return f"Plot created comparing {len(expressions)} functions"

    # ------ Statistics Analysis Tools ------

    @json_schema(
        description="Perform statistical analysis",
        params={
            "data": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of data points, e.g., [1, 2, 3, 4, 5]",
                "required": True
            },
            "operation": {
                "type": "string",
                "description": "Statistical operation, such as \"mean\", \"median\", \"std\", \"var\", \"min\", \"max\"",
                "required": True,
                "enum": ["mean", "median", "std", "var", "min", "max", "sum", "count"]
            }
        }
    )
    async def statistics(self, data: List[float], operation: str) -> float:
        """
        Perform statistical analysis
        
        Args:
            data: List of data points, e.g., [1, 2, 3, 4, 5]
            operation: Statistical operation, such as "mean", "median", "std", "var", "min", "max"
            
        Returns:
            Statistical result
        """
        values = np.array(data)
        
        if operation == "mean":
            return float(np.mean(values))
        elif operation == "median":
            return float(np.median(values))
        elif operation == "std":
            return float(np.std(values))
        elif operation == "var":
            return float(np.var(values))
        elif operation == "min":
            return float(np.min(values))
        elif operation == "max":
            return float(np.max(values))
        elif operation == "sum":
            return float(np.sum(values))
        elif operation == "count":
            return len(values)
        else:
            raise ValueError("Unsupported statistical operation")

    @json_schema(
        description="Generate statistical summary of data",
        params={
            "data": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of data points, e.g., [1, 2, 3, 4, 5]",
                "required": True
            }
        }
    )
    async def summarize_data(self, data: List[float]) -> Dict[str, float]:
        """
        Generate statistical summary of data
        
        Args:
            data: List of data points, e.g., [1, 2, 3, 4, 5]
            
        Returns:
            Dictionary containing multiple statistical values
        """
        values = np.array(data)
        
        return {
            "count": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "q1": float(np.percentile(values, 25)),
            "q3": float(np.percentile(values, 75)),
        }

    @json_schema(
        description="Calculate correlation between two sets of data",
        params={
            "data_x": {
                "type": "array",
                "items": {"type": "number"},
                "description": "First set of data, e.g., [1, 2, 3, 4, 5]",
                "required": True
            },
            "data_y": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Second set of data, e.g., [2, 3, 4, 5, 6]",
                "required": True
            }
        }
    )
    async def correlation(self, data_x: List[float], data_y: List[float]) -> Dict[str, float]:
        """
        Calculate correlation between two sets of data
        
        Args:
            data_x: First set of data, e.g., [1, 2, 3, 4, 5]
            data_y: Second set of data, e.g., [2, 3, 4, 5, 6]
            
        Returns:
            Dictionary containing correlation coefficient and p-value
        """
        x = np.array(data_x)
        y = np.array(data_y)
        
        if len(x) != len(y):
            raise ValueError("The two data sets must have the same length")
        
        r, p = stats.pearsonr(x, y)
        
        return {
            "correlation": float(r),
            "p_value": float(p)
        }


# Register the toolset
Toolset.register(MathTools)