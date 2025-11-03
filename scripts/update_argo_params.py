#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path

def load_yaml(path: Path):
    with path.open("r") as f:
        return yaml.safe_load(f)

def save_yaml(path: Path, data):
    with path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def find_env_file(app_folder: Path, chart_name: str, env_file: str) -> Path | None:
    """
    Search recursively under app_folder for files named env_file
    and return the first whose path contains chart_name.
    """
    candidates = [p for p in app_folder.rglob(env_file) if chart_name in p.parts]
    if not candidates:
        return None
    if len(candidates) > 1:
        print("⚠️  Multiple matching files found; using the first one:")
        for c in candidates:
            print("  -", c)
    chosen = candidates[0]
    return chosen

def ensure_parameters_structure(data: dict):
    # Ensure nested keys exist: spec -> source -> helm -> parameters
    if data is None:
        data = {}
    spec = data.setdefault("spec", {})
    source = spec.setdefault("source", {})
    helm = source.setdefault("helm", {})
    helm.setdefault("parameters", [])
    return data

def add_or_update_param(file_path: Path, name: str, value: str):
    data = load_yaml(file_path)
    data = ensure_parameters_structure(data)
    params = data["spec"]["source"]["helm"]["parameters"]

    for p in params:
        if p.get("name") == name:
            print(f"🔄 Updating parameter '{name}' -> '{value}' in {file_path}")
            p["value"] = value
            save_yaml(file_path, data)
            return

    print(f"➕ Adding new parameter '{name}' -> '{value}' in {file_path}")
    params.append({"name": name, "value": value})
    data["spec"]["source"]["helm"]["parameters"] = params
    save_yaml(file_path, data)

def delete_param(file_path: Path, name: str):
    data = load_yaml(file_path)
    data = ensure_parameters_structure(data)
    params = data["spec"]["source"]["helm"].get("parameters", [])
    new_params = [p for p in params if p.get("name") != name]

    if len(new_params) == len(params):
        print(f"⚠️ Parameter '{name}' not found in {file_path}. Nothing deleted.")
    else:
        print(f"🗑️ Deleted parameter '{name}' from {file_path}")

    data["spec"]["source"]["helm"]["parameters"] = new_params
    save_yaml(file_path, data)

def main():
    if len(sys.argv) < 6:
        print("Usage:")
        print("  python update_argo_params.py add <app_folder> <chart_name> <env_file> <param_name> <param_value>")
        print("  python update_argo_params.py delete <app_folder> <chart_name> <env_file> <param_name>")
        sys.exit(1)

    action = sys.argv[1]
    app_folder = Path(sys.argv[2])
    chart_name = sys.argv[3]
    env_file = sys.argv[4]

    if not app_folder.exists() or not app_folder.is_dir():
        print(f"❌ Application folder not found or not a directory: {app_folder}")
        sys.exit(1)

    found = find_env_file(app_folder, chart_name, env_file)
    if not found:
        print(f"❌ YAML file not found: no '{env_file}' under '{app_folder}' containing '{chart_name}' in the path.")
        sys.exit(1)

    print(f"➡️ Using file: {found}")

    if action == "add":
        if len(sys.argv) != 7:
            print("Usage: python update_argo_params.py add <app_folder> <chart_name> <env_file> <param_name> <param_value>")
            sys.exit(1)
        name, value = sys.argv[5], sys.argv[6]
        add_or_update_param(found, name, value)
    elif action == "delete":
        if len(sys.argv) != 6:
            print("Usage: python update_argo_params.py delete <app_folder> <chart_name> <env_file> <param_name>")
            sys.exit(1)
        name = sys.argv[5]
        delete_param(found, name)
    else:
        print("Invalid action. Use 'add' or 'delete'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
