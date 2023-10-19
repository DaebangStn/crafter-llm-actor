import os
import csv
from typing import Dict, Any, List
from ruamel.yaml import YAML


def yaml_loader(yaml_path: str) -> Dict[str, Any]:
    assert os.path.isfile(yaml_path), f"path: {yaml_path} is not a file"

    yaml = YAML()
    with open(yaml_path, "r") as f:
        loaded = yaml.load(f)
    assert loaded is not None, f"failed to load yaml file: {yaml_path}"

    return loaded


def load_actions_from_csv(csv_path: str) -> List[Dict[str, str]]:
    assert os.path.isfile(csv_path), f"path: {csv_path} is not a file"

    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        action_list: List[List[str, str]] = list(reader)
        action_list = [[s.strip() for s in sublist] for sublist in action_list]

        header = action_list[0]
        elements = action_list[1:]
        action_dict = [{header[0]: e[0], header[1]: e[1]} for e in elements]

    assert len(action_dict) > 0, f"failed to load actions from csv file: {csv_path}"

    return action_dict
