import os
import openai
import cut_text
import json

def aggregate_messages(prompt, chunks):
    messages = [
        {
            "role": "user",
            "content": prompt,
        },
        {
            "role": "assistant",
            "content": "i wait until you have sent all texts.",
        },
    ]
    x = [{"role": "user", "content": i} for i in chunks]
    messages.extend(x)
    return messages


def send_req(messages):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


def ask(prompt, chunks):
    messages = aggregate_messages(prompt, chunks)
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    args = cut_text.parser.parse_args()

    with open(args.prompt_file, "r") as f:
        prompt = f.read()

    chunks = cut_text.cut(args)
    fp_export = args.file + "_annotated.json"
    annotes = ask(prompt=prompt, chunks=chunks)

    if args.destination is None:
        print(annotes)
    else:
        destination = os.path.realpath(args.destination)
        with open(fp_export, "w") as f:
            json.dump(fp=f, obj=annotes)
