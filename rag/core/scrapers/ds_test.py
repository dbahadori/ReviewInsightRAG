from deepseek import DeepSeekAPI  # Hypothetical DeepSeek SDK
from openai import OpenAI


def main():
    # Please install OpenAI SDK first: `pip3 install openai`


    client = OpenAI(api_key="sk-60abf91dbc1b4b3991cfa5362f0e4c1b", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
