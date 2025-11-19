"""
Custom Pylint Checkers for OMA Project
Detects common patterns and issues specific to this codebase
"""

from typing import TYPE_CHECKING
from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class DuplicatePatternChecker(BaseChecker):
    """
    Detects duplicate patterns and common anti-patterns in the codebase
    """

    __implements__ = IAstroidChecker

    name = "duplicate-pattern-checker"
    priority = -1
    msgs = {
        "W9001": (
            "Potential duplicate try-except pattern detected",
            "duplicate-try-except",
            "Consider extracting this error handling pattern into a decorator or utility function",
        ),
        "W9002": (
            "Duplicate API call pattern detected",
            "duplicate-api-call",
            "Consider creating a reusable API client method",
        ),
        "W9003": (
            "Hardcoded string detected that should be a constant",
            "hardcoded-string-constant",
            "Consider moving this to a constants file or configuration",
        ),
        "W9004": (
            "Missing error handling for async operation",
            "missing-async-error-handling",
            "Async operations should have proper error handling",
        ),
        "W9005": (
            "Nested function depth exceeds 3 levels",
            "excessive-nesting",
            "Consider refactoring to reduce complexity",
        ),
        "W9006": (
            "Function has too many local variables (>15)",
            "too-many-locals",
            "Consider breaking down this function into smaller functions",
        ),
    }

    def __init__(self, linter: "PyLinter" = None) -> None:
        super().__init__(linter)
        self.try_except_patterns = []
        self.api_call_patterns = []
        self._nesting_level = 0

    def visit_tryexcept(self, node: nodes.TryExcept) -> None:
        """Check for duplicate try-except patterns"""
        # Extract the pattern signature
        pattern = self._get_exception_pattern(node)

        if pattern in self.try_except_patterns:
            self.add_message("duplicate-try-except", node=node)
        else:
            self.try_except_patterns.append(pattern)

    def visit_asyncfunctiondef(self, node: nodes.AsyncFunctionDef) -> None:
        """Check async functions for proper error handling"""
        has_try_except = False

        for child in node.get_children():
            if isinstance(child, nodes.TryExcept):
                has_try_except = True
                break

        # Check if function body has API calls without error handling
        if not has_try_except and self._has_await_calls(node):
            # Only warn if there are actual await calls (async operations)
            self.add_message("missing-async-error-handling", node=node)

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        """Check function complexity"""
        # Check number of local variables
        local_vars = [n.name for n in node.nodes_of_class(nodes.AssignName)]
        if len(set(local_vars)) > 15:
            self.add_message("too-many-locals", node=node)

        # Check nesting depth
        max_depth = self._calculate_nesting_depth(node)
        if max_depth > 3:
            self.add_message("excessive-nesting", node=node)

    def visit_const(self, node: nodes.Const) -> None:
        """Check for hardcoded strings that should be constants"""
        if not isinstance(node.value, str):
            return

        # Check if it's a URL, API endpoint, or config value
        suspicious_patterns = [
            "http://", "https://", "api/", "/api/",
            "localhost:", "127.0.0.1", "0.0.0.0"
        ]

        for pattern in suspicious_patterns:
            if pattern in node.value:
                # Check if already in a constant (uppercase variable)
                parent = node.parent
                if isinstance(parent, nodes.Assign):
                    if any(isinstance(t, nodes.AssignName) and t.name.isupper()
                           for t in parent.targets):
                        return  # Already a constant

                self.add_message("hardcoded-string-constant", node=node)
                break

    def visit_call(self, node: nodes.Call) -> None:
        """Check for duplicate API call patterns"""
        # Look for common API client patterns
        if hasattr(node.func, "attrname"):
            if node.func.attrname in ["post", "get", "put", "delete", "request"]:
                call_signature = self._get_call_signature(node)

                if call_signature in self.api_call_patterns:
                    self.add_message("duplicate-api-call", node=node)
                else:
                    self.api_call_patterns.append(call_signature)

    def _get_exception_pattern(self, node: nodes.TryExcept) -> str:
        """Extract a signature from try-except pattern"""
        exceptions = []
        for handler in node.handlers:
            if handler.type:
                exceptions.append(handler.type.as_string())
        return "|".join(sorted(exceptions))

    def _has_await_calls(self, node: nodes.AsyncFunctionDef) -> bool:
        """Check if function has await calls"""
        for child in node.nodes_of_class(nodes.Await):
            return True
        return False

    def _calculate_nesting_depth(self, node: nodes.NodeNG, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth in a function"""
        max_depth = current_depth

        for child in node.get_children():
            if isinstance(child, (nodes.If, nodes.For, nodes.While, nodes.With, nodes.TryExcept)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _get_call_signature(self, node: nodes.Call) -> str:
        """Get a signature for an API call"""
        func_name = node.func.as_string() if node.func else ""
        args = [arg.as_string() for arg in node.args[:2]]  # First 2 args only
        return f"{func_name}({','.join(args)})"


class AgentPatternChecker(BaseChecker):
    """
    Specific checker for agent patterns in this multi-agent system
    """

    __implements__ = IAstroidChecker

    name = "agent-pattern-checker"
    priority = -1
    msgs = {
        "W9101": (
            "Agent class missing required method: %s",
            "agent-missing-method",
            "All agent classes should implement standard interface methods",
        ),
        "W9102": (
            "Agent state not properly validated",
            "agent-state-validation",
            "Agent state changes should be validated",
        ),
        "W9103": (
            "Missing logging in agent method",
            "agent-missing-logging",
            "Agent methods should include proper logging for debugging",
        ),
    }

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        """Check agent classes for required patterns"""
        # Check if this is an agent class
        if "agent" in node.name.lower():
            # Required methods for agents
            required_methods = ["run", "process", "execute"]
            class_methods = [m.name for m in node.methods()]

            # Check if at least one required method exists
            if not any(method in class_methods for method in required_methods):
                self.add_message(
                    "agent-missing-method",
                    node=node,
                    args=(" or ".join(required_methods),)
                )

            # Check methods for logging
            for method in node.methods():
                if method.name.startswith("_"):
                    continue  # Skip private methods

                has_logging = False
                for child in method.nodes_of_class(nodes.Call):
                    if hasattr(child.func, "attrname"):
                        if child.func.attrname in ["debug", "info", "warning", "error", "log"]:
                            has_logging = True
                            break

                if not has_logging and len(list(method.body)) > 3:  # Only check substantial methods
                    self.add_message("agent-missing-logging", node=method)


def register(linter: "PyLinter") -> None:
    """Required method to register the checker"""
    linter.register_checker(DuplicatePatternChecker(linter))
    linter.register_checker(AgentPatternChecker(linter))
