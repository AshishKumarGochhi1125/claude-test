# Exercise 3: Debugging

## The Problem
This calculator module has a bug. When you run the tests, 2 out of 9 tests fail.

## Setup
```bash
cd exercise-3-debugging
npm install
npm test
```

You should see output like:
```
✓ Calculator > add > adds two positive numbers
✓ Calculator > add > adds negative numbers
✓ Calculator > add > adds zero
✓ Calculator > subtract > subtracts two numbers
✓ Calculator > subtract > handles negative results
✓ Calculator > multiply > multiplies two numbers
✓ Calculator > multiply > multiplies by zero
✓ Calculator > multiply > multiplies negative numbers
✓ Calculator > divide > divides two numbers
✓ Calculator > divide > handles decimal results
✓ Calculator > divide > divides negative numbers
✗ Calculator > divide > throws DivisionByZeroError when dividing by zero
✗ Calculator > divide > throws DivisionByZeroError with correct message
```

## Your Task
Ask Claude Code: "Fix the failing tests"

Watch how Claude Code:
1. Reads the test file to understand what's expected
2. Reads the source file to understand the implementation
3. Identifies the mismatch
4. Edits the fix
5. Runs tests to verify
