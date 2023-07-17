from GTPInterface import run_conversation


if __name__ == "__main__":
    while True:
        prompt = input("Enter a prompt: ")

        if prompt.lower() == "q":
            break

        run_conversation(prompt, "3.5")
