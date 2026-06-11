"""Simple calculator: arithmetic functions plus a Tkinter GUI.

Run this file directly (``python calculator.py``) to open the calculator
window. The arithmetic functions can also be imported and used on their own.
"""

import tkinter as tk


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def subtract(a, b):
    """Return the difference of a and b (a - b)."""
    return a - b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def divide(a, b):
    """Return the quotient of a and b (a / b).

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def power(a, b):
    """Return a raised to the power of b (a ** b)."""
    return a ** b


class CalculatorApp:
    """A button-based calculator window built with Tkinter."""

    # Layout of the button grid: (label, row, column, column_span).
    BUTTONS = [
        ("C", 1, 0, 1), ("(", 1, 1, 1), (")", 1, 2, 1), ("/", 1, 3, 1),
        ("7", 2, 0, 1), ("8", 2, 1, 1), ("9", 2, 2, 1), ("*", 2, 3, 1),
        ("4", 3, 0, 1), ("5", 3, 1, 1), ("6", 3, 2, 1), ("-", 3, 3, 1),
        ("1", 4, 0, 1), ("2", 4, 1, 1), ("3", 4, 2, 1), ("+", 4, 3, 1),
        ("0", 5, 0, 1), (".", 5, 1, 1), ("^", 5, 2, 1), ("=", 5, 3, 1),
    ]

    def __init__(self, root):
        self.root = root
        root.title("Calculator")
        root.resizable(False, False)

        # "RCB: PLAYBOLD" tag banner across the top.
        tag = tk.Label(
            root,
            text="RCB: PLAYBOLD",
            font=("Segoe UI", 14, "bold"),
            fg="#FFD700",
            bg="#7B0000",
        )
        tag.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=6, pady=(6, 0))

        self.display_var = tk.StringVar(value="")
        display = tk.Entry(
            root,
            textvariable=self.display_var,
            font=("Segoe UI", 20),
            justify="right",
            bd=8,
            relief="ridge",
            state="readonly",
        )
        display.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=6, pady=6)

        # Buttons start one row lower to make room for the tag + display.
        for (label, row, col, span) in self.BUTTONS:
            btn = tk.Button(
                root,
                text=label,
                font=("Segoe UI", 14),
                width=4,
                height=2,
                command=lambda l=label: self.on_button(l),
            )
            btn.grid(row=row + 1, column=col, columnspan=span,
                     sticky="nsew", padx=2, pady=2)

        # Keyboard support.
        root.bind("<Key>", self.on_key)
        root.bind("<Return>", lambda e: self.evaluate())
        root.bind("<BackSpace>", lambda e: self.backspace())
        root.bind("<Escape>", lambda e: self.clear())

    def on_button(self, label):
        if label == "C":
            self.clear()
        elif label == "=":
            self.evaluate()
        elif label == "^":
            self.display_var.set(self.display_var.get() + "**")
        else:
            self.display_var.set(self.display_var.get() + label)

    def on_key(self, event):
        if event.char in "0123456789.+-*/()":
            self.display_var.set(self.display_var.get() + event.char)

    def backspace(self):
        self.display_var.set(self.display_var.get()[:-1])

    def clear(self):
        self.display_var.set("")

    def evaluate(self):
        expression = self.display_var.get()
        if not expression:
            return
        try:
            # Restrict eval to arithmetic characters only for safety.
            allowed = set("0123456789.+-*/() ")
            if not set(expression) <= allowed:
                raise ValueError("invalid characters")
            result = eval(expression, {"__builtins__": {}}, {})
            self.display_var.set(str(result))
        except ZeroDivisionError:
            self.display_var.set("Error: divide by zero")
        except Exception:
            self.display_var.set("Error")


def main():
    """Launch the calculator GUI."""
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
