"""
MCP Math Calculation Assistant - Providing advanced mathematical calculation functionality
"""

from mcp.server.fastmcp import FastMCP, Image, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import numpy as np
import sympy as sp
from scipy import integrate, optimize, stats
import matplotlib.pyplot as plt
import io
from safe_eval import safe_eval, create_safe_function, safe_eval_with_x

# Define server context
@dataclass
class AppContext:
    version: str = "1.1.0"

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle"""
    print("Starting Math Calculation Assistant service...")
    try:
        yield AppContext()
    finally:
        print("Shutting down Math Calculation Assistant service...")

# Create MCP server
mcp = FastMCP(
    "Math Calculation Assistant", 
    lifespan=app_lifespan,
    # List dependencies for user installation
    dependencies=["numpy", "scipy", "sympy", "matplotlib"]
)

# ------ Basic Math Tools ------

@mcp.tool()
def evaluate_expression(expression: str) -> float:
    """Safely evaluate mathematical expressions
    
    Args:
        expression: Mathematical expression string, e.g., "2 * (3 + 4) ** 2"
        
    Returns:
        The calculated result of the expression
    """
    return safe_eval(expression)

@mcp.tool()
def calculate(a: float, operation: str, b: float) -> float:
    """Perform basic arithmetic operations
    
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

@mcp.tool()
def solve_ode(equation: str, variable: str, func: str, order: int = 1) -> str:
    """Solve ordinary differential equations
    
    Args:
        equation: Differential equation, e.g., "y''(x) + y'(x) + y(x) = sin(x)"
        variable: Independent variable, e.g., "x"
        func: Dependent function name, e.g., "y"
        order: Order of the differential equation
        
    Returns:
        General solution of the differential equation
    """
    # Create symbolic variables
    x = sp.Symbol(variable)
    y = sp.Function(func)(x)
    
    # Create derivatives
    derivatives = [y]
    for i in range(1, order + 1):
        derivatives.append(y.diff(x, i))
    
    # Parse equation
    if "=" in equation:
        left, right = equation.split("=", 1)
        left = left.strip()
        right = right.strip()
        eq_expr = sp.sympify(left) - sp.sympify(right)
    else:
        eq_expr = sp.sympify(equation)
    
    # Replace derivative notations in the expression
    for i in range(order, 0, -1):
        # Replace y^(n)(x) or y^(n) notation
        eq_expr = eq_expr.subs(sp.Symbol(f"{func}^({i})"), derivatives[i])
        eq_expr = eq_expr.subs(sp.Symbol(f"{func}^({i})({variable})"), derivatives[i])
        
        # Replace y''... notation
        prime_notation = func + "'" * i
        eq_expr = eq_expr.subs(sp.Symbol(prime_notation), derivatives[i])
        eq_expr = eq_expr.subs(sp.Symbol(f"{prime_notation}({variable})"), derivatives[i])
    
    # Replace y(x) or y notation
    eq_expr = eq_expr.subs(sp.Symbol(func), derivatives[0])
    eq_expr = eq_expr.subs(sp.Symbol(f"{func}({variable})"), derivatives[0])
    
    # Solve ODE
    try:
        solution = sp.dsolve(eq_expr, y)
        return str(solution)
    except Exception as e:
        return f"Could not solve the differential equation: {str(e)}"

@mcp.tool()
def partial_derivative(expression: str, variables: list, wrt_vars: list) -> str:
    """Calculate partial derivatives of multivariate functions
    
    Args:
        expression: Multivariate function expression, e.g., "x**2 + y**2"
        variables: List of all variables, e.g., ["x", "y", "z"]
        wrt_vars: Variables to differentiate with respect to, e.g., ["x", "y"]
        
    Returns:
        Partial derivative expression
    """
    # Handle string input for lists
    if isinstance(variables, str):
        try:
            variables = safe_eval(variables)
        except:
            variables = [variables]
            
    if isinstance(wrt_vars, str):
        try:
            wrt_vars = safe_eval(wrt_vars)
        except:
            wrt_vars = [wrt_vars]
    
    # Create symbolic variables
    syms = {}
    for var in variables:
        syms[var] = sp.Symbol(var)
    
    # Parse expression
    expr = sp.sympify(expression, locals=syms)
    
    # Calculate partial derivative
    for var in wrt_vars:
        if var not in syms:
            raise ValueError(f"Variable {var} not in the provided variables list")
        expr = sp.diff(expr, syms[var])
    
    return str(expr)

@mcp.tool()
def multiple_integral(expression: str, variables: list, bounds: list) -> str:
    """Calculate multiple integrals
    
    Args:
        expression: Integrand expression, e.g., "x*y"
        variables: List of integration variables, e.g., ["x", "y"]
        bounds: Integration limits, e.g., [[0, 1], [0, 2]]
        
    Returns:
        Multiple integral result
    """
    # Handle string input for lists
    if isinstance(variables, str):
        try:
            variables = safe_eval(variables)
        except:
            variables = [variables]
            
    if isinstance(bounds, str):
        try:
            bounds = safe_eval(bounds)
        except:
            raise ValueError("Bounds must be a valid list of pairs")
    
    # Verify input dimensions
    if len(variables) != len(bounds):
        raise ValueError("Number of variables must match number of bound pairs")
    
    # Create symbolic variables
    syms = {}
    for var in variables:
        syms[var] = sp.Symbol(var)
    
    # Parse expression
    expr = sp.sympify(expression, locals=syms)
    
    # Set up integration
    integrations = []
    for i, var in enumerate(variables):
        if not isinstance(bounds[i], list) or len(bounds[i]) != 2:
            raise ValueError(f"Bounds for {var} must be a pair [lower, upper]")
        
        lower = sp.sympify(bounds[i][0])
        upper = sp.sympify(bounds[i][1])
        integrations.append((syms[var], lower, upper))
    
    # Calculate multiple integral
    result = sp.integrate(expr, *integrations)
    return str(result)

@mcp.tool()
def differentiate(expression: str, variable: str, order: int = 1) -> str:
    """Calculate the derivative of a function
    
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

@mcp.tool()
def integrate_symbolic(expression: str, variable: str, lower_bound: str = None, upper_bound: str = None) -> str:
    """Calculate the integral of a function
    
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

@mcp.tool()
def integrate_numeric(expression: str, lower_bound: float, upper_bound: float) -> float:
    """Numerically calculate a definite integral
    
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

@mcp.tool()
def solve_equation(equation: str, variable: str) -> str:
    """Solve an equation
    
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

@mcp.tool()
def solve_system(equations, variables) -> str:
    """Solve a system of equations
    
    Args:
        equations: List of equations, e.g., ["x + y = 10", "2*x - y = 5"] or ["x + y = 10", "2*x - y = 5"]
        variables: List of variables, e.g., ["x", "y"] or ["x", "y"]
        
    Returns:
        Solution of the equation system
    """
    # 处理引号包裹的字符串列表的情况
    if isinstance(equations, str):
        try:
            equations = safe_eval(equations)
        except:
            equations = [equations]  # If parsing fails, treat as a single equation
    
    if isinstance(variables, str):
        try:
            variables = safe_eval(variables)
        except:
            variables = [variables]  # If parsing fails, treat as a single variable
            
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

@mcp.tool()
def simplify_expression(expression: str) -> str:
    """Simplify algebraic expression
    
    Args:
        expression: Expression to simplify
        
    Returns:
        Simplified expression
    """
    expr = sp.sympify(expression)
    result = sp.simplify(expr)
    return str(result)

@mcp.tool()
def expand_expression(expression: str) -> str:
    """Expand algebraic expression
    
    Args:
        expression: Expression to expand
        
    Returns:
        Expanded expression
    """
    expr = sp.sympify(expression)
    result = sp.expand(expr)
    return str(result)

@mcp.tool()
def factor_expression(expression: str) -> str:
    """Factor an expression
    
    Args:
        expression: Expression to factor
        
    Returns:
        Factored expression
    """
    expr = sp.sympify(expression)
    result = sp.factor(expr)
    return str(result)

# ------ Discrete Mathematics and Combinatorics ------

@mcp.tool()
def combinatorics(n: int, k: int, type: str = "combination") -> int:
    """Calculate combinatorial values (combinations and permutations)
    
    Args:
        n: Total number of items
        k: Number of items to select
        type: Calculation type, "combination" or "permutation"
        
    Returns:
        Number of combinations C(n,k) or permutations P(n,k)
    """
    if n < 0 or k < 0:
        raise ValueError("Both n and k must be non-negative integers")
    
    if k > n:
        raise ValueError("k cannot be greater than n")
    
    if type.lower() == "combination":
        return int(sp.binomial(n, k))
    elif type.lower() == "permutation":
        return int(sp.factorial(n) / sp.factorial(n - k))
    else:
        raise ValueError("Type must be either 'combination' or 'permutation'")

@mcp.tool()
def graph_shortest_path(graph: dict, start: str, end: str) -> dict:
    """Calculate the shortest path in a graph
    
    Args:
        graph: Graph represented as an adjacency dict, e.g., {"A": {"B": 1, "C": 4}, "B": {"D": 3}, ...}
        start: Starting node
        end: Ending node
        
    Returns:
        Dictionary with path and distance
    """
    # Handle string input for graph
    if isinstance(graph, str):
        try:
            graph = safe_eval(graph)
        except:
            raise ValueError("Graph must be a valid dictionary")
    
    # Check if start and end nodes exist in the graph
    if start not in graph:
        raise ValueError(f"Start node '{start}' not in graph")
    if end not in graph and end not in [node for adj in graph.values() for node in adj]:
        raise ValueError(f"End node '{end}' not in graph")
    
    # Initialize distances and predecessors
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    predecessors = {node: None for node in graph}
    unvisited = list(graph.keys())
    
    # Dijkstra's algorithm
    while unvisited:
        # Find the unvisited node with the smallest distance
        current = min(unvisited, key=lambda node: distances[node])
        
        # If we've reached the end node or all remaining nodes are unreachable
        if current == end or distances[current] == float('infinity'):
            break
        
        # Remove the current node from unvisited set
        unvisited.remove(current)
        
        # Update distances to neighbors
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor not in distances:
                distances[neighbor] = float('infinity')
                predecessors[neighbor] = None
                
            distance = distances[current] + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current
    
    # Reconstruct the path
    if end not in distances or distances[end] == float('infinity'):
        return {"path": [], "distance": float('infinity')}
    
    path = [end]
    current = end
    while current != start:
        current = predecessors[current]
        if current is None:  # No path exists
            return {"path": [], "distance": float('infinity')}
        path.append(current)
    
    return {
        "path": path[::-1],  # Reverse to get path from start to end
        "distance": distances[end]
    }

# ------ Numerical Optimization Tools ------

@mcp.tool()
def find_minimum(expression: str, lower_bound: float, upper_bound: float) -> dict:
    """Find the local minimum value of a function
    
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

@mcp.tool()
def find_root(expression: str, lower_bound: float, upper_bound: float) -> float:
    """Find the root (zero) of a function
    
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

@mcp.tool()
def matrix_operation(operation: str, matrix_a, matrix_b = None) -> str:
    """Perform matrix operations
    
    Args:
        operation: Operation type, e.g., "multiply", "inverse", "determinant", "eigenvalues", "transpose"
        matrix_a: First matrix, format like "[[1, 2], [3, 4]]" or [[1, 2], [3, 4]]
        matrix_b: Second matrix (if needed), same format as above
        
    Returns:
        Operation result
    """
    # Safely parse matrices
    try:
        # 确保参数是适当的格式
        if isinstance(matrix_a, str):
            mat_a_list = safe_eval(matrix_a)
        else:
            mat_a_list = matrix_a
        
        mat_a = np.array(mat_a_list)
        
        if matrix_b is not None:
            if isinstance(matrix_b, str):
                mat_b_list = safe_eval(matrix_b)
            else:
                mat_b_list = matrix_b
                
            mat_b = np.array(mat_b_list)
    except Exception as e:
        raise ValueError(f"Matrix format error: {str(e)}")
    
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

@mcp.tool()
def plot_function(expression: str, x_min: float = -10, x_max: float = 10, points: int = 1000) -> Image:
    """Plot a function graph
    
    Args:
        expression: Function expression, e.g., "x**2 + 2*x"
        x_min: Minimum x-axis value
        x_max: Maximum x-axis value
        points: Number of sampling points
        
    Returns:
        Function graph
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
        
        # Create and return image
        return Image(data=buffer.getvalue(), format="png")
    except Exception as e:
        plt.close()
        raise ValueError(f"Error when plotting function: {str(e)}")

@mcp.tool()
def plot_multiple_functions(expressions, labels = None, x_min: float = -10, x_max: float = 10, points: int = 500) -> Image:
    """Plot graphs of multiple functions
    
    Args:
        expressions: List of function expressions, e.g., ["x**2", "2*x + 1"] or ["x**2", "2*x + 1"]
        labels: List of legend labels (optional)
        x_min: Minimum x-axis value
        x_max: Maximum x-axis value
        points: Number of sampling points
        
    Returns:
        Function graph
    """
    # 处理引号包裹的字符串列表的情况
    if isinstance(expressions, str):
        try:
            expressions = safe_eval(expressions)
        except:
            expressions = [expressions]  # If parsing fails, treat as a single expression
    
    if labels is not None:
        if isinstance(labels, str):
            try:
                labels = safe_eval(labels)
            except:
                labels = [labels]  # If parsing fails, treat as a single label
    
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
            print(f"Error when plotting function '{expr}': {str(e)}")
    
    plt.grid(True)
    plt.title("Function Comparison")
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    
    # 将图像转换为二进制数据
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    
    # Create and return image
    return Image(data=buffer.getvalue(), format="png")

# ------ Statistics Analysis Tools ------

@mcp.tool()
def statistics(data, operation: str) -> float:
    """Perform statistical analysis
    
    Args:
        data: List of data points, format like "[1, 2, 3, 4, 5]" or [1, 2, 3, 4, 5]
        operation: Statistical operation, such as "mean", "median", "std", "var", "min", "max"
        
    Returns:
        Statistical result
    """
    try:
        # Handle different input formats
        if isinstance(data, str):
            values_list = safe_eval(data)
        else:
            values_list = data
            
        values = np.array(values_list)
    except Exception as e:
        raise ValueError(f"Data format error: {str(e)}")
    
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

@mcp.tool()
def summarize_data(data) -> dict:
    """Generate statistical summary of data
    
    Args:
        data: List of data points, format like "[1, 2, 3, 4, 5]" or [1, 2, 3, 4, 5]
        
    Returns:
        Dictionary containing multiple statistical values
    """
    try:
        # Handle different input formats
        if isinstance(data, str):
            values_list = safe_eval(data)
        else:
            values_list = data
            
        values = np.array(values_list)
    except Exception as e:
        raise ValueError(f"Data format error: {str(e)}")
    
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

@mcp.tool()
def correlation(data_x, data_y) -> dict:
    """Calculate correlation between two sets of data
    
    Args:
        data_x: First set of data, format like "[1, 2, 3, 4, 5]" or [1, 2, 3, 4, 5]
        data_y: Second set of data, format like "[2, 3, 4, 5, 6]" or [2, 3, 4, 5, 6]
        
    Returns:
        Dictionary containing correlation coefficient and p-value
    """
    try:
        # Handle different input formats
        if isinstance(data_x, str):
            x_list = safe_eval(data_x)
        else:
            x_list = data_x
            
        if isinstance(data_y, str):
            y_list = safe_eval(data_y)
        else:
            y_list = data_y
            
        x = np.array(x_list)
        y = np.array(y_list)
    except Exception as e:
        raise ValueError(f"Data format error: {str(e)}")
    
    if len(x) != len(y):
        raise ValueError("The two data sets must have the same length")
    
    r, p = stats.pearsonr(x, y)
    
    return {
        "correlation": float(r),
        "p_value": float(p)
    }

@mcp.resource("math://help")
def get_help() -> str:
    """Get help information for the math calculation assistant"""
    return """
    Math Calculation Assistant Usage Guide:
    
    [Basic Calculations]
    - evaluate_expression: Calculate mathematical expression value
    - calculate: Perform basic arithmetic operations
    
    [Symbolic Computation]
    - differentiate: Calculate function derivatives
    - integrate_symbolic: Symbolic integration
    - integrate_numeric: Numerical integration
    - solve_equation: Solve equations
    - solve_system: Solve systems of equations
    - simplify_expression: Simplify expressions
    - expand_expression: Expand expressions
    - factor_expression: Factor expressions
    
    [Optimization]
    - find_minimum: Find function minimum values
    - find_root: Find function zeros (roots)
    
    [Matrix Calculations]
    - matrix_operation: Perform matrix operations
    
    [Visualization]
    - plot_function: Plot function graphs
    - plot_multiple_functions: Compare multiple function graphs
    
    [Statistical Analysis]
    - statistics: Calculate basic statistical values
    - summarize_data: Generate statistical data summaries
    - correlation: Calculate correlation between data sets
    
    Usage examples:
    1. Calculate derivative: differentiate("x**2 + 2*x", "x")
    2. Plot function: plot_function("sin(x) + cos(x)")
    3. Solve equation: solve_equation("x**2 - 4 = 0", "x")
    """

@mcp.resource("math://examples")
def get_examples() -> str:
    """Get examples of using the math calculation assistant"""
    return """
    Math Calculation Assistant Examples:
    
    Basic Calculations:
    - Calculate expression: evaluate_expression("2 * (3 + 4) ** 2")
    - Basic operation: calculate(5, "multiply", 3)
    
    Calculus:
    - Calculate derivative: differentiate("x**2 + 2*x", "x")
    - Calculate second derivative: differentiate("sin(x)", "x", 2)
    - Indefinite integral: integrate_symbolic("x**2 + 2*x", "x")
    - Definite integral: integrate_symbolic("x**2", "x", "0", "1")
    - Numerical integration: integrate_numeric("sin(x) + cos(x)", 0, 3.14)
    
    Algebra:
    - Solve equation: solve_equation("x**2 - 4 = 0", "x")
    - Solve system of equations: solve_system(["x + y = 10", "2*x - y = 5"], ["x", "y"])
    
    Expression Manipulation:
    - Simplify expression: simplify_expression("(x**2 + 2*x + 1) / (x + 1)")
    - Expand expression: expand_expression("(x + 1)**3")
    - Factor expression: factor_expression("x**2 - 4")
    
    Optimization:
    - Find minimum: find_minimum("x**2 + 2*x + 1", -10, 10)
    - Find root: find_root("x**2 - 4", 0, 10)
    
    Matrix Operations:
    - Matrix multiplication: matrix_operation("multiply", "[[1, 2], [3, 4]]", "[[5, 6], [7, 8]]")
    - Matrix transpose: matrix_operation("transpose", "[[1, 2], [3, 4]]")
    - Calculate determinant: matrix_operation("determinant", "[[1, 2], [3, 4]]")
    
    Visualization:
    - Plot function: plot_function("sin(x) + cos(x)", -3.14, 3.14)
    - Plot multiple functions: plot_multiple_functions(["x**2", "2*x + 1"], ["Quadratic function", "Linear function"])
    
    Statistical Analysis:
    - Calculate mean: statistics("[1, 2, 3, 4, 5]", "mean")
    - Data summary: summarize_data("[12, 15, 18, 22, 27, 31, 35]")
    - Correlation analysis: correlation("[1, 2, 3, 4, 5]", "[2, 3, 4, 5, 6]")
    """

@mcp.resource("math://version")
def get_version() -> str:
    """Get the version of the math calculation assistant"""
    return f"Math Calculation Assistant Version: 1.0.0"

# ------ Probability and Statistics Extensions ------

@mcp.tool()
def probability_distribution(dist_type: str, params: dict, x: float, calc_type: str = "pdf") -> float:
    """Calculate probability distribution functions, CDFs, or quantiles
    
    Args:
        dist_type: Distribution type, e.g., "normal", "binomial", "poisson", etc.
        params: Distribution parameters, e.g., {"mean": 0, "std": 1}
        x: Value to calculate at
        calc_type: Calculation type, "pdf", "cdf", or "quantile"
        
    Returns:
        Probability density, cumulative probability, or quantile value
    """
    # Handle string input for params
    if isinstance(params, str):
        try:
            params = safe_eval(params)
        except:
            raise ValueError("Parameters must be a valid dictionary")
    
    # Create the distribution object
    if dist_type.lower() == "normal" or dist_type.lower() == "gaussian":
        loc = params.get("mean", params.get("mu", 0))
        scale = params.get("std", params.get("sigma", 1))
        dist = stats.norm(loc=loc, scale=scale)
    
    elif dist_type.lower() == "binomial":
        n = params.get("n", 1)
        p = params.get("p", 0.5)
        dist = stats.binom(n=n, p=p)
    
    elif dist_type.lower() == "poisson":
        mu = params.get("mu", params.get("lambda", 1))
        dist = stats.poisson(mu=mu)
    
    elif dist_type.lower() == "exponential":
        scale = 1 / params.get("lambda", 1)  # lambda is rate, scale is 1/rate
        dist = stats.expon(scale=scale)
    
    elif dist_type.lower() == "uniform":
        a = params.get("a", params.get("min", 0))
        b = params.get("b", params.get("max", 1))
        dist = stats.uniform(loc=a, scale=b-a)
    
    elif dist_type.lower() == "t" or dist_type.lower() == "student":
        df = params.get("df", 1)
        dist = stats.t(df=df)
    
    elif dist_type.lower() == "f":
        dfn = params.get("dfn", 1)
        dfd = params.get("dfd", 1)
        dist = stats.f(dfn=dfn, dfd=dfd)
    
    elif dist_type.lower() == "chi2" or dist_type.lower() == "chi_square":
        df = params.get("df", 1)
        dist = stats.chi2(df=df)
    
    elif dist_type.lower() == "gamma":
        a = params.get("shape", params.get("alpha", 1))
        scale = params.get("scale", params.get("beta", 1))
        dist = stats.gamma(a=a, scale=scale)
    
    elif dist_type.lower() == "beta":
        a = params.get("alpha", params.get("a", 1))
        b = params.get("beta", params.get("b", 1))
        dist = stats.beta(a=a, b=b)
    
    else:
        raise ValueError(f"Unsupported distribution type: {dist_type}")
    
    # Calculate the requested probability function
    if calc_type.lower() == "pdf" or calc_type.lower() == "pmf":
        if hasattr(dist, 'pmf'):
            return float(dist.pmf(x))
        else:
            return float(dist.pdf(x))
    
    elif calc_type.lower() == "cdf":
        return float(dist.cdf(x))
    
    elif calc_type.lower() == "quantile" or calc_type.lower() == "ppf":
        if x < 0 or x > 1:
            raise ValueError("Quantile input must be between 0 and 1")
        return float(dist.ppf(x))
    
    elif calc_type.lower() == "sf" or calc_type.lower() == "survival":
        return float(dist.sf(x))  # Survival function: 1 - CDF
    
    else:
        raise ValueError(f"Unsupported calculation type: {calc_type}")

@mcp.tool()
def hypothesis_test(test_type: str, data, alpha: float = 0.05) -> dict:
    """Perform statistical hypothesis tests
    
    Args:
        test_type: Test type, e.g., "t_test", "z_test", "chi_square", etc.
        data: Test data. Format depends on the test type.
        alpha: Significance level, default = 0.05
        
    Returns:
        Dictionary with test results, including p-value, test statistic, etc.
    """
    # Handle string input for data
    if isinstance(data, str):
        try:
            data = safe_eval(data)
        except:
            raise ValueError("Data must be in a valid format")
    
    # One-sample t-test
    if test_type.lower() == "t_test_1samp" or test_type.lower() == "one_sample_t_test":
        sample = np.array(data["sample"])
        popmean = data.get("popmean", 0)
        t_stat, p_value = stats.ttest_1samp(sample, popmean)
        result = {
            "test_type": "One-sample t-test", 
            "t_statistic": float(t_stat), 
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "df": len(sample) - 1
        }
    
    # Two-sample t-test
    elif test_type.lower() == "t_test_ind" or test_type.lower() == "two_sample_t_test":
        sample1 = np.array(data["sample1"])
        sample2 = np.array(data["sample2"])
        equal_var = data.get("equal_var", True)
        t_stat, p_value = stats.ttest_ind(sample1, sample2, equal_var=equal_var)
        result = {
            "test_type": "Independent two-sample t-test", 
            "t_statistic": float(t_stat), 
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "equal_variances_assumed": equal_var
        }
    
    # Paired t-test
    elif test_type.lower() == "t_test_rel" or test_type.lower() == "paired_t_test":
        sample1 = np.array(data["sample1"])
        sample2 = np.array(data["sample2"])
        t_stat, p_value = stats.ttest_rel(sample1, sample2)
        result = {
            "test_type": "Paired-sample t-test", 
            "t_statistic": float(t_stat), 
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "df": len(sample1) - 1
        }
    
    # One-way ANOVA
    elif test_type.lower() == "anova" or test_type.lower() == "one_way_anova":
        samples = [np.array(sample) for sample in data["samples"]]
        f_stat, p_value = stats.f_oneway(*samples)
        result = {
            "test_type": "One-way ANOVA", 
            "f_statistic": float(f_stat), 
            "p_value": float(p_value),
            "significant": p_value < alpha
        }
    
    # Chi-square test of independence
    elif test_type.lower() == "chi2_contingency" or test_type.lower() == "chi_square":
        contingency_table = np.array(data["table"])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        result = {
            "test_type": "Chi-square test of independence", 
            "chi2_statistic": float(chi2), 
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "df": dof
        }
    
    # Shapiro-Wilk test for normality
    elif test_type.lower() == "shapiro" or test_type.lower() == "normality_test":
        sample = np.array(data["sample"])
        stat, p_value = stats.shapiro(sample)
        result = {
            "test_type": "Shapiro-Wilk test for normality", 
            "statistic": float(stat), 
            "p_value": float(p_value),
            "is_normal": p_value >= alpha  # Null hypothesis is that data is normal
        }
    
    else:
        raise ValueError(f"Unsupported test type: {test_type}")
    
    return result

# ------ Complex Numbers and Special Functions ------

@mcp.tool()
def complex_arithmetic(z1: str, z2: str, operation: str) -> str:
    """Perform complex number operations
    
    Args:
        z1: First complex number, e.g., "3+4j" or "3+4i"
        z2: Second complex number, e.g., "1-2j" or "1-2i"
        operation: Operation type, "add", "subtract", "multiply", "divide", "power"
        
    Returns:
        Result of complex number operation
    """
    # Handle input with 'i' instead of 'j' for imaginary unit
    z1 = z1.replace('i', 'j')
    z2 = z2.replace('i', 'j')
    
    # Parse complex numbers
    try:
        c1 = complex(z1)
        c2 = complex(z2)
    except ValueError:
        raise ValueError("Invalid complex number format. Use format like '3+4j' or '3+4i'")
    
    # Perform operation
    if operation.lower() == "add":
        result = c1 + c2
    elif operation.lower() == "subtract":
        result = c1 - c2
    elif operation.lower() == "multiply":
        result = c1 * c2
    elif operation.lower() == "divide":
        if c2 == 0:
            raise ValueError("Division by zero")
        result = c1 / c2
    elif operation.lower() == "power":
        result = c1 ** c2
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    
    # Format result
    real = result.real
    imag = result.imag
    
    # Format with proper precision and handle very small values
    if abs(real) < 1e-10:
        real = 0
    if abs(imag) < 1e-10:
        imag = 0
    
    if imag == 0:
        return str(real)
    elif real == 0:
        return f"{imag}j"
    elif imag < 0:
        return f"{real}{imag}j"
    else:
        return f"{real}+{imag}j"

@mcp.tool()
def special_function(func_type: str, x: float) -> float:
    """Calculate values of special mathematical functions
    
    Args:
        func_type: Function type, e.g., "gamma", "beta", "bessel", etc.
        x: Function argument
        
    Returns:
        Function value
    """
    try:
        if func_type.lower() == "gamma":
            return float(sp.gamma(x))
        
        elif func_type.lower() == "log_gamma" or func_type.lower() == "lgamma":
            return float(sp.loggamma(x))
        
        elif func_type.lower() == "factorial":
            return float(sp.factorial(x))
        
        elif func_type.lower() == "beta":
            # The beta function takes two arguments, so we parse x as a tuple or list
            if isinstance(x, (list, tuple)) and len(x) >= 2:
                a, b = x[0], x[1]
                return float(sp.beta(a, b))
            else:
                raise ValueError("Beta function requires two parameters [a, b]")
        
        elif func_type.lower().startswith("bessel_j"):
            # Bessel function of first kind
            if isinstance(x, (list, tuple)) and len(x) >= 2:
                n, z = x[0], x[1]
                return float(sp.besselj(n, z))
            else:
                raise ValueError("Bessel J function requires order and value [n, z]")
        
        elif func_type.lower().startswith("bessel_y"):
            # Bessel function of second kind
            if isinstance(x, (list, tuple)) and len(x) >= 2:
                n, z = x[0], x[1]
                return float(sp.bessely(n, z))
            else:
                raise ValueError("Bessel Y function requires order and value [n, z]")
        
        elif func_type.lower() == "erf" or func_type.lower() == "error_function":
            return float(sp.erf(x))
        
        elif func_type.lower() == "erfc" or func_type.lower() == "error_function_complement":
            return float(sp.erfc(x))
        
        elif func_type.lower() == "zeta" or func_type.lower() == "riemann_zeta":
            return float(sp.zeta(x))
            
        else:
            raise ValueError(f"Unsupported special function: {func_type}")
    
    except Exception as e:
        raise ValueError(f"Error calculating {func_type}({x}): {str(e)}")

# ------ Prompts ------

@mcp.prompt()
def math_problem_template(problem_type: str) -> str:
    """Create a math problem template
    
    Args:
        problem_type: Problem type, such as "calculus", "algebra", "statistics"
        
    Returns:
        Prompt template
    """
    if problem_type == "calculus":
        return """
        Please help me solve the following calculus problem:
        
        Function: {function}
        Task: {task}
        
        If it's a derivative problem, please provide detailed differentiation steps.
        If it's an integration problem, please provide integration methods and detailed calculation process.
        """
    elif problem_type == "algebra":
        return """
        Please help me solve the following algebra problem:
        
        Equation: {equation}
        
        Please provide a complete solution process, including all steps and intermediate results.
        """
    elif problem_type == "statistics":
        return """
        Please help me analyze the following data:
        
        Dataset: {data}
        
        Please provide basic statistics, such as mean, median, standard deviation, etc., and explain the meaning of these data.
        """
    else:
        return """
        Please help me solve the following math problem:
        
        Problem: {problem}
        
        Please provide detailed solution steps and the final result.
        """

# Main program
if __name__ == "__main__":
    mcp.run()
