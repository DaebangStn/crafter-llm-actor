from langchain.callbacks import get_openai_callback
from ruamel.yaml import YAML
import os
import signal as sg
import sys
import logging

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from agent.PriorityRetrievalQA import PriorityRetrievalQA
import agent


def sigint_handler(_signal, _frame):
    global token_usage_limit
    global configs
    global yaml

    _llm_config = configs["defaults"]["llm"]
    configs[_llm_config]["token_usage_limit"] = token_usage_limit

    print('Saving configs... token_usage_limit:', token_usage_limit)

    with open("configs.yaml", "w") as f:
        yaml.dump(configs, f)
        print("configs.yaml updated")

    sys.exit(0)


if __name__ == '__main__':
    global token_usage_limit
    global configs
    global yaml

    sg.signal(sg.SIGINT, sigint_handler)

    yaml = YAML()
    with open("configs.yaml", "r") as f:
        configs = yaml.load(f)

    llm_config = configs["defaults"]["llm"]
    token_usage_limit = configs[llm_config]["token_usage_limit"]

    yaml2 = YAML()
    with open("secrets.yaml", "r") as f:
        secrets = yaml2.load(f)

    logger = logging.getLogger(__name__)

    llm = agent.initialize_llm(configs, secrets, logger)

    collections = [
        "solid",
        "Hafner_-_2022_-_Benchmarking_the_Spectrum_of_Agent_Capabilities",
    ]

    embedding = OpenAIEmbeddings()

    retrievers = []
    for collection in collections:
        retriever = Chroma(
            embedding_function=embedding,
            persist_directory="data/chroma",
            collection_name=collection,
        ).as_retriever()
        retrievers.append(retriever)

    qa = PriorityRetrievalQA(llm=llm, retrieverList=retrievers)

    while True:
        print()
        q = input("Your Question: ")

        with get_openai_callback() as cb:
            response = qa.query(q)

        print("token_usage:", cb.total_tokens, "token_usage_limit:", token_usage_limit)
        token_usage_limit -= cb.total_tokens

        if response is not None:
            print("answer:", response['result'])
            print("source:", response['source_documents'])

        if token_usage_limit < 0:
            print("token_usage_limit exceeded")
            os.kill(os.getpid(), sg.SIGINT)
