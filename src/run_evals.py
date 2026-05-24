from agent import run_agent
from eval_cases import EVAL_CASES


def tools_used(trace: list[dict]) -> list[str]:
    return [event["tool"] for event in trace]


def check_expected_tools(case: dict, trace: list[dict]) -> tuple[bool, str]:
    used = tools_used(trace)

    missing = [
        tool for tool in case["expected_tools"]
        if tool not in used
    ]

    if missing:
        return False, f"Missing expected tools: {missing}. Used: {used}"

    return True, "Expected tools were used."


def check_forbidden_tools(case: dict, trace: list[dict]) -> tuple[bool, str]:
    used = tools_used(trace)

    forbidden_used = [
        tool for tool in case["forbidden_tools"]
        if tool in used
    ]

    if forbidden_used:
        return False, f"Used forbidden tools: {forbidden_used}"

    return True, "No forbidden tools were used."


def check_answer_contains(case: dict, answer: str) -> tuple[bool, str]:
    answer_lower = answer.lower()

    missing = [
        text for text in case["answer_should_contain"]
        if text.lower() not in answer_lower
    ]

    if missing:
        return False, f"Answer missing expected text: {missing}. Answer: {answer}"

    return True, "Answer contains expected text."


def check_tool_args(case: dict, trace: list[dict]) -> tuple[bool, str]:
    expected_args = case.get("expected_args", {})

    for expected_tool, expected_fields in expected_args.items():
        matching_calls = [
            event for event in trace
            if event["tool"] == expected_tool
        ]

        if not matching_calls:
            return False, f"No call found for expected tool: {expected_tool}"

        matched = False

        for call in matching_calls:
            actual_args = call["args"]

            if all(
                actual_args.get(key) == value
                for key, value in expected_fields.items()
            ):
                matched = True
                break

        if not matched:
            return False, (
                f"Tool {expected_tool} did not receive expected args. "
                f"Expected fields: {expected_fields}. "
                f"Actual calls: {matching_calls}"
            )

    return True, "Tool arguments look correct."


def evaluate_case(case: dict) -> dict:
    result = run_agent(case["input"])

    checks = [
        check_expected_tools(case, result["trace"]),
        check_forbidden_tools(case, result["trace"]),
        check_answer_contains(case, result["answer"]),
        check_tool_args(case, result["trace"]),
    ]

    passed = all(check[0] for check in checks)

    return {
        "case": case["name"],
        "passed": passed,
        "answer": result["answer"],
        "trace": result["trace"],
        "checks": checks,
    }


def main():
    results = []

    for case in EVAL_CASES:
        print(f"\nRunning: {case['name']}")
        result = evaluate_case(case)
        results.append(result)

        print("PASSED" if result["passed"] else "FAILED")

        for ok, message in result["checks"]:
            status = "OK" if ok else "FAIL"
            print(f"  [{status}] {message}")

        print(f"  Answer: {result['answer']}")

    passed = sum(1 for result in results if result["passed"])
    total = len(results)

    print("\nSummary")
    print(f"Passed: {passed}/{total}")


if __name__ == "__main__":
    main()