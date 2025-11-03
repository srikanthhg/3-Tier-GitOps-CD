#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path

YAML_FILE = Path("argocd-app.yaml")  # Adjust if your manifest is in another path

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def add_or_update_param(name, value):
    data = load_yaml(YAML_FILE)
    params = data["spec"]["source"]["helm"].get("parameters", [])
    for p in params:
        if p["name"] == name:
            print(f"Updating existing parameter '{name}' -> '{value}'")
            p["value"] = value
            save_yaml(YAML_FILE, data)
            return
    print(f"Adding new parameter '{name}' -> '{value}'")
    params.append({"name": name, "value": value})
    data["spec"]["source"]["helm"]["parameters"] = params
    save_yaml(YAML_FILE, data)

def delete_param(name):
    data = load_yaml(YAML_FILE)
    params = data["spec"]["source"]["helm"].get("parameters", [])
    new_params = [p for p in params if p["name"] != name]
    if len(new_params) == len(params):
        print(f"No parameter found with name '{name}'. Nothing to delete.")
    else:
        print(f"Deleted parameter '{name}'")
    data["spec"]["source"]["helm"]["parameters"] = new_params
    save_yaml(YAML_FILE, data)

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python update_argo_params.py add <name> <value>")
        print("  python update_argo_params.py delete <name>")
        sys.exit(1)

    action = sys.argv[1]

    if action == "add":
        if len(sys.argv) != 4:
            print("Usage: python update_argo_params.py add <name> <value>")
            sys.exit(1)
        name, value = sys.argv[2], sys.argv[3]
        add_or_update_param(name, value)
    elif action == "delete":
        name = sys.argv[2]
        delete_param(name)
    else:
        print("Invalid action. Use 'add' or 'delete'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
