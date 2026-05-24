from agent import run_agent


if __name__ == "__main__":
    while True:
        user_input = input("\nAsk agent > ").strip()

        if user_input.lower() in ["exit", "quit"]:
            break

        result = run_agent(user_input)

        print("\nAnswer:")
        print(result["answer"])

        print("\nTrace:")
        for event in result["trace"]:
            print(event)