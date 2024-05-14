from openai import OpenAI
import os

# Get your OpenAI API key from the environment variables
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


print(api_key)
# Set up your OpenAI API key


if not api_key:
    print("Please set the OPENAI_API_KEY environment variable.")
    exit(1)

client = OpenAI(api_key=api_key)


def get_gpt3_response(prompt, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(model=model,
    messages=[
        {"role": "system", "content": "You are a hegpt-3.5-turbolpful assistant."},
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content

def main():
    print("Welcome to the GPT-3.5 Turbo Command Line Chat!")
    print("Type 'exit' to quit the program.")

    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        try:
            response = get_gpt3_response(user_input)
            print(f"GPT-3.5 Turbo: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
