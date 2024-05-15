from openai import OpenAI
import os
from dotenv import load_dotenv
from runTerminalCommands import ShellSession

# Load environment variables from .env file
load_dotenv()

# Get your OpenAI API key from the environment variables
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Please set the OPENAI_API_KEY environment variable.")
    exit(1)

client = OpenAI(api_key=api_key)

MAX_HISTORY_LENGTH = 20  # Adjust this limit as needed


# Initialize the conversation history
conversation_history = [
    {"role": "system", "content": "You are designed to work with the linux terminal.  You will be provided with terminal output at each step and will be expected to do nothing except provide the next command.  DO NOT PROVIDE ANY TEXT THAT IS NOT A COMMAND AS IT WILL BE ENTERED INTO THE TERMINAL AND MAY CAUSE ERRORS.  DO NOT PROVIDE MULTIPLE LINES AT ONCE. Your goal is set by the user and is as follows: <--BEGIN GOAL--> Create a new folder with 3 text files, and confirm that the files are created. <--END GOAL--> Once you have completed the goal, type 'PROGRAM COMPLETE' to end the program."},
]

# Set a limit on the number of messages in the conversation history

def get_gpt3_response(prompt, model="gpt-3.5-turbo"):
    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Trim the conversation history if it exceeds the maximum length
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history.pop(1)  # Remove the second element (index 1), keeping the system message

    response = client.chat.completions.create(
        model=model,
        messages=conversation_history
    )

    # Get the response message
    response_message = response.choices[0].message.content

    # Add the response to the conversation history
    conversation_history.append({"role": "assistant", "content": response_message})

    return response_message

def main():
    print("Welcome to the GPT-3.5 Turbo Command Line Chat!")
    shell = ShellSession()
    shell_result = shell.run_command('pwd')

    while True:
        try:
            response = get_gpt3_response(shell_result)
            
            print(f"GPT-3.5 Turbo: {response}")
            if response == "PROGRAM COMPLETE":
                print("Program complete. Exiting...")
                break
            # wait for the user to press enter before running the next command
            input("Press Enter to continue...")
            # run the next command
            shell_result = shell.run_command(response)
            
        except Exception as e:
            print(f"Error: {e}")
            # exit the loop on error
            break

if __name__ == "__main__":
    main()
