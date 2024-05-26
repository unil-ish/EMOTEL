import os
import openai
import cut_text
import json

parser = cut_text.parser
parser.add_argument(
    "-p",
    "--prompt-file",
    action="store",
    type=str,
    help="le fichier avec le prompt initial.",
    required=True,
)
parser.add_argument(
    "-k",
    "--api-key",
    action="store",
    type=str,
    help="l'api key",
    default=None,
)


def ask(prompt, chunks):
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

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response["choices"]


if __name__ == "__main__":
    args = cut_text._parsearguments()

    key = args.api_key
    if key is None:
        key = os.getenv["CHATGPT_API"]
        if key is None:
            raise ValueError("undefined environment variable: CHATGPT_API")

    openai.api_key = key

    chunks = cut_text.cut(args)
    fp_export = args.file + "_annotated.json"
    annotes = ask(chunks)
    destination = os.path.realpath(args.destination)
    with open(fp_export, "w") as f:
        json.dump(fp=f, obj=annotes)
