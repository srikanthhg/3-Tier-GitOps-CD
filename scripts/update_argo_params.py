#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_yaml(path, data):
    with open(path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def add_or_update_param(file_path, name, value):
    data = load_yaml(file_path)
    params = data["spec"]["source"]["helm"].get("parameters", [])

    for p in params:
        if p["name"] == name:
            print(f"🔄 Updating parameter '{name}' -> '{value}'")
            p["value"] = value
            save_yaml(file_path, data)
            return

    print(f"➕ Adding new parameter '{name}' -> '{value}'")
    params.append({"name": name, "value": value})
    data["spec"]["source"]["helm"]["parameters"] = params
    save_yaml(file_path, data)

def delete_param(file_path, name):
    data = load_yaml(file_path)
    params = data["spec"]["source"]["helm"].get("parameters", [])
    new_params = [p for p in params if p["name"] != name]

    if len(new_params) == len(params):
        print(f"⚠️ Parameter '{name}' not found. Nothing deleted.")
    else:
        print(f"🗑️ Deleted parameter '{name}'")

    data["spec"]["source"]["helm"]["parameters"] = new_params
    save_yaml(file_path, data)

def main():
    if len(sys.argv) < 6:
        print("Usage:")
        print("  python update_argo_params.py add <app_folder> <chart_name> <env_file> <param_name> <param_value>")
        print("  python update_argo_params.py delete <app_folder> <chart_name> <env_file> <param_name>")
        sys.exit(1)

    action = sys.argv[1]
    app_folder = sys.argv[2]
    chart_name = sys.argv[3]
    env_file = sys.argv[4]
    file_path = Path(app_folder) / chart_name / env_file

    if not file_path.exists():
        print(f"❌ YAML file not found: {file_path}")
        sys.exit(1)

    if action == "add":
        if len(sys.argv) != 7:
            print("Usage: python update_argo_params.py add <app_folder> <chart_name> <env_file> <param_name> <param_value>")
            sys.exit(1)
        name, value = sys.argv[5], sys.argv[6]
        add_or_update_param(file_path, name, value)
    elif action == "delete":
        name = sys.argv[5]
        delete_param(file_path, name)
    else:
        print("Invalid action. Use 'add' or 'delete'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
