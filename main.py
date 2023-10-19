import signal as sg
import sys
import os
from collections import deque
from datetime import datetime
import logging.config
import loggerConfig

import cv2
import crafter
from ruamel.yaml import YAML

from langchain.callbacks import get_openai_callback

import agent
import subsystem


def handle_exception(exc_type, exc_value, exc_traceback):
    _logger = logging.getLogger("rich")

    _logger.error("Unexpected exception", exc_info=(exc_type, exc_value, exc_traceback))


# SIGINT handler to record the llm token usage
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


if __name__ == "__main__":
    # global variables to record the llm token usage
    global token_usage_limit
    global configs
    global yaml

    # register SIGINT handler
    sg.signal(sg.SIGINT, sigint_handler)

    # load configs and secrets
    yaml = YAML()
    with open("configs.yaml", "r") as f:
        configs = yaml.load(f)
    base_path = configs["defaults"]["base_path"]

    # update configs
    logdir_name = datetime.now().strftime("%Y%m%d-%H%M%S")
    configs["defaults"]["logdir"] = os.path.join(base_path, "logs", logdir_name)
    configs["defaults"]["log_every"] = 30
    configs["defaults"]["reload_after_death"] = True

    # initialize logger
    log_dir_path = configs["defaults"]["logdir"]
    os.makedirs(log_dir_path, exist_ok=True)
    logging.config.dictConfig(loggerConfig.get_config(
        logfilename=os.path.join(log_dir_path, "main.log").replace("\\", "\\\\")
    ))
    sys.excepthook = handle_exception
    logger = logging.getLogger()

    # PIL logging is too noisy
    logging.getLogger('PIL').setLevel(logging.WARNING)

    # save updated configs
    with open("configs.yaml", "w") as f:
        yaml.dump(configs, f)
        logger.debug("configs.yaml updated")

    # retrieve token usage limit
    _llm_config = configs["defaults"]["llm"]
    token_usage_limit = configs[_llm_config]["token_usage_limit"]

    # initialize LLM
    secrets = subsystem.yaml_loader(os.path.join(base_path, configs["defaults"]["secrets_path"]))
    llm = agent.initialize_llm(configs, secrets, logger)

    # initialize retrievers
    retrievers = agent.initialize_retrievers(configs, secrets, logger)
    with open(os.path.join(base_path, configs["defaults"]["knowledge_text_path"]), "r") as f:
        knowledge_text = f.read()
    #    qa = PriorityRetrievalQA(llm=llm, retrieverList=retrievers)

    # initialize crafter environment
    env = crafter.Env(seed=configs["defaults"]["seed"])
    env = crafter.Recorder(
        env, log_dir_path,
        save_stats=True,
        save_video=True,
        save_episode=True,
    )
    env.reset()

    # initialize value savers
    running = True
    inventory_deque = deque(maxlen=2)
    image_deque = deque(maxlen=2)
    surrounding_deque = deque(maxlen=2)
    last_action = None
    isNight = False
    playerOrientation = agent.PlayerOrientation()

    # retrieve some resources
    reference_image_dir_path = os.path.join(base_path, configs["defaults"]["reference_image_dir_path"])
    assert os.path.isdir(reference_image_dir_path), "reference_image_dir_path not found"
    actions_dict = subsystem.load_actions_from_csv(os.path.join(base_path, configs["defaults"]["action_list_path"]))

    # initialize agent
    listAction = agent.ListActions(llm, logging.getLogger('LIST'), retrievers[1])
    requirementChecker = agent.RequirementChecker(llm, logging.getLogger('REQ_C'))
    actionSuccessChecker = agent.ActionSuccessChecker(llm, logging.getLogger('SUC_C'))

    while running:
        # observe the environment
        image = env.render((600, 600))
        print(image.shape)
        print(image.size)
        image_deque.append(image)
        surrounding, isNight = agent.surrounding_recognizer(image, reference_image_dir_path)
        surrounding_deque.append(surrounding)

        if surrounding_deque:
            logger.debug("serialized surrounding_deque")
            logger.debug(agent.serializer_surrounding_deque(surrounding_deque).replace("\n", " "))
        if inventory_deque:
            logger.debug("serialized inventory_deque")
            logger.debug(agent.serializer_inventory_deque(inventory_deque).replace("\n", " "))

        cv2.imshow("image", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        cv2.waitKey(1)

        # retrieve the action
        with get_openai_callback() as cb:
            actionSuccession = actionSuccessChecker.run(actions_dict, last_action, surrounding_deque, inventory_deque)
            action_list = listAction.run(
                actions_dict,
                surrounding_deque,
                inventory_deque,
                Task="collect wood",
                helpful_knowledge=knowledge_text,
                player_orientation=playerOrientation.get_orientation(),
            )
            action_string = requirementChecker.run(action_list, surrounding_deque, inventory_deque, task="collect wood")

        token_usage_limit -= cb.total_tokens
        logger.debug("used tokens: %d", cb.total_tokens)

        action = None
        try:
            action = subsystem.find_word_index(action_string, env.action_names)
            if action is None:
                raise ValueError
        except ValueError:
            action = env.action_names.index('noop')

        # do action, step the environment
        _, reward, done, status = env.step(action)

        last_action = env.action_names[action]
        playerOrientation.update_action(last_action)
        inventory = status['inventory']
        inventory_deque.append(inventory)

        # check if the environment is done
        if done:
            if configs["defaults"]["auto_reload"]:
                env.reset()
            else:
                running = False
