from langchain.chains import LLMChain
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_experimental.chat_models import Llama2Chat


import os
import requests
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def download_model(model_url:str, model_path:str):
    """
    This function downloads the model from the provided URL and saves it to the specified path.

    Args:
        model_url (str): The URL of the model to be downloaded.
        model_path (str): The path where the model should be saved.
    """
    logging.info(f"Downloading model from {model_url} to {model_path}")
    response = requests.get(model_url)
    response.raise_for_status()  # Raise an exception if the GET request was unsuccessful
    logging.info(f"Saving model to {model_path}")
    with open(model_path, 'wb') as f:
        f.write(response.content)

def ensure_model_exists(model_url:str, model_path:str):
    """
    This function checks if the model exists at the specified path, and if not, downloads it.

    Args:
        model_url (str): The URL of the model to be downloaded.
        model_path (str): The path where the model should be saved.
    """
    if not os.path.exists(model_path):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        download_model(model_url, model_path)


def invoke_llm_chain(input_text : str, n_batch : int=512, verbose: bool=False):
    """
    This function creates an instance of LLMChain with the provided Llama model, prompt template, and memory,
    and invokes it with the provided input text.

    Args:
        input_text (str): The input text to be processed by the LLMChain.
        n_batch (int, optional): The batch size for the model. Defaults to 512.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        dict: The response from the LLMChain as dictiona.
    """

    model_url = "https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_0.gguf"
    model_path = "models/llama-2-7b-chat.Q4_0.gguf"

    ensure_model_exists(model_url, model_path)

    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    llm = LlamaCpp(
        model_path="models/llama-2-7b-chat.Q4_0.gguf",
        temperature=0.1,
        n_batch=n_batch,
        callback_manager=callback_manager,
        verbose=verbose,
    )

    model = Llama2Chat(llm=llm)

    template_messages = [
        SystemMessage(content="You are a helpful assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
    prompt_template = ChatPromptTemplate.from_messages(template_messages)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chain = LLMChain(llm=model, prompt=prompt_template, memory=memory)
    logging.info(f"Invoking LLMChain with input: {input_text}")
    return chain.invoke(input=input_text)

print(invoke_llm_chain("How do I convert the selected code into a function and add a Google-style docstring?"))