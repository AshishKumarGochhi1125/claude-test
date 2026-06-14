"""
Session 3, Block 3: Evaluation Exercise

Automated evaluation harness for the TechFlow agent.
Imports the agent, runs 5 test cases, and auto-checks results
using deterministic keyword matching.

Run with: python eval.py

This demonstrates the eval pattern:
  1. Define test cases with expected behavior
  2. Run each case through the agent automatically
  3. Check results with deterministic criteria (keywords, tool calls)
  4. Report PASS/FAIL with reasons
  5. Calculate an overall score
"""

from agent_solution import run_agent

# ============================================================
# TEST CASES (the "golden dataset")
#
# Each test case defines:
#   - name: human-readable description
#   - query: the input to the agent
#   - check_keywords: at least ONE must appear in the response (case-insensitive)
#   - pass_reason: explanation when the check passes
#   - fail_reason: explanation when the check fails
# ============================================================

test_cases = [
    {
        "name": "Happy path: simple order lookup",
        "query": "What's the status of order ORD-5678?",
        "check_keywords": ["shipped"],
        "pass_reason": "Correctly identified order as shipped",
        "fail_reason": "Did not mention 'shipped' status",
    },
    {
        "name": "Multi-step: lookup + check + ticket",
        "query": "Check order ORD-1234 for customer alice@example.com and create a ticket if it's delayed",
        "check_keywords": ["ticket"],
        "pass_reason": "Created ticket for delayed order",
        "fail_reason": "Did not create a support ticket",
    },
    {
        "name": "Edge case: customer not found",
        "query": "Look up customer nobody@example.com",
        "check_keywords": ["not found", "no customer", "couldn't find", "don't have", "unable to find"],
        "pass_reason": "Gracefully handled missing customer",
        "fail_reason": "Did not communicate that the customer was not found",
    },
    {
        "name": "Edge case: order not found",
        "query": "What's the status of order ORD-0000?",
        "check_keywords": ["not found", "no order", "couldn't find", "don't have", "unable to find"],
        "pass_reason": "Gracefully handled missing order",
        "fail_reason": "Did not communicate that the order was not found",
    },
    {
        "name": "Simple customer lookup",
        "query": "Tell me about customer carol@example.com",
        "check_keywords": ["carol", "enterprise"],
        "pass_reason": "Correctly returned Carol's info with Enterprise plan",
        "fail_reason": "Missing customer details (name or plan)",
    },
]

# ============================================================
# DETERMINISTIC CHECKER
# ============================================================

def check_response(response, keywords):
    """Check if at least one keyword appears in the response (case-insensitive)."""
    response_lower = response.lower()
    return any(kw.lower() in response_lower for kw in keywords)

# ============================================================
# EVALUATION RUNNER
# ============================================================

def run_evaluation():
    print("\n" + "=" * 60)
    print("  TechFlow Agent — Automated Evaluation Suite")
    print("=" * 60)
    print(f"\nRunning {len(test_cases)} test cases...\n")

    passed = 0
    failed = 0
    results = []

    for i, tc in enumerate(test_cases, 1):
        print(f"{'─' * 60}")
        print(f"Test {i}/{len(test_cases)}: {tc['name']}")
        print(f"  Query: \"{tc['query']}\"")

        try:
            # Run the agent and capture the response
            response = run_agent(tc["query"])

            # Deterministic check: does the response contain expected keywords?
            is_pass = check_response(response, tc["check_keywords"])

            if is_pass:
                passed += 1
                status = "PASS"
                reason = tc["pass_reason"]
            else:
                failed += 1
                status = "FAIL"
                reason = tc["fail_reason"]

            print(f"\n  Result: {status}")
            print(f"  Reason: {reason}")
            results.append({"name": tc["name"], "status": status, "reason": reason})

        except Exception as e:
            failed += 1
            print(f"\n  Result: ERROR")
            print(f"  Reason: {e}")
            results.append({"name": tc["name"], "status": "ERROR", "reason": str(e)})

    # ============================================================
    # SCORECARD
    # ============================================================
    total = len(test_cases)
    score_pct = (passed / total) * 100 if total > 0 else 0

    print(f"\n{'=' * 60}")
    print(f"  SCORECARD")
    print(f"{'=' * 60}")
    for r in results:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        print(f"  [{icon}] {r['name']}")
    print(f"\n  Score: {passed}/{total} ({score_pct:.0f}%)")
    print(f"{'=' * 60}")

    if failed > 0:
        print(f"\n  {failed} test(s) failed.")
        print("  Try tweaking the SYSTEM_PROMPT in agent_solution.py and re-run!")
    else:
        print("\n  All tests passed!")

    return passed, total


if __name__ == "__main__":
    run_evaluation()
