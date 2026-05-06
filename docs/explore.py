#!/usr/bin/env python3
"""
OpenAPI YAML file explorer
Usage:
  python3 explore.py categories <spec.yaml>
  python3 explore.py endpoints <spec.yaml> <category>
  python3 explore.py category <spec.yaml> <category>
  python3 explore.py endpoint <spec.yaml> <endpoint>
"""

import sys
import os
import yaml

# ----------------------------
# Load spec
# ----------------------------
def load_spec(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ----------------------------
# Lazy $ref resolver
# ----------------------------
ref_cache = {}

def resolve_ref(ref, api):
    if ref in ref_cache:
        return ref_cache[ref]

    if not ref.startswith("#/"):
        return {"$ref": ref}

    node = api
    for part in ref.lstrip("#/").split("/"):
        if not isinstance(node, dict):
            node = None
            break
        node = node.get(part)

    if isinstance(node, dict) and "$ref" in node:
        node = resolve_ref(node["$ref"], api)

    ref_cache[ref] = node
    return node


def resolve_if_ref(obj, api):
    if isinstance(obj, dict) and "$ref" in obj:
        return resolve_ref(obj["$ref"], api)
    return obj


# ----------------------------
# Extract schema fields
# ----------------------------
def extract_fields(schema, api, prefix=""):
    schema = resolve_if_ref(schema, api)
    fields = []

    if not isinstance(schema, dict):
        return fields

    if "allOf" in schema:
        for sub in schema["allOf"]:
            fields.extend(extract_fields(sub, api, prefix))
        return fields

    props = schema.get("properties", {})

    for name, prop in props.items():
        prop = resolve_if_ref(prop, api)

        full_name = f"{prefix}{name}"
        fields.append((full_name, prop))

        if prop.get("type") == "object":
            fields.extend(
                extract_fields(prop, api, prefix=full_name + ".")
            )

        if prop.get("type") == "array":
            items = resolve_if_ref(prop.get("items"), api)
            if isinstance(items, dict):
                fields.extend(
                    extract_fields(items, api, prefix=full_name + "[]")
                )

    return fields


# ----------------------------
# Parameter formatting
# ----------------------------
def format_param(name, schema, required):
    def get(field):
        val = schema.get(field)
        if isinstance(val, list):
            return "[" + ",".join(map(str, val)) + "]"
        return val if val is not None else "-"

    return (
        f"{name} - required: {'yes' if required else 'no'}, "
        f"type: {get('type')}, "
        f"format: {get('format')}, "
        f"enum: {get('enum')}, "
        f"pattern: {get('pattern')}, "
        f"maxLength: {get('maxLength')}, "
        f"minLength: {get('minLength')}"
    )


# ----------------------------
# Build unified parameters
# ----------------------------
def build_parameters(api, operation):
    params = []

    # query/path/header params
    for p in operation.get("parameters", []):
        p = resolve_if_ref(p, api)

        name = p.get("name", "unknown")
        required = p.get("required", False)
        schema = resolve_if_ref(p.get("schema", {}), api)

        params.append((name, schema, required))

    # requestBody → flatten to parameters
    if operation.get("requestBody"):
        rb = resolve_if_ref(operation["requestBody"], api)
        content = rb.get("content", {})

        for _, details in content.items():
            schema = details.get("schema")
            for name, sch in extract_fields(schema, api):
                params.append((name, sch, False))

    return params


# ----------------------------
# Print endpoint (UPDATED)
# ----------------------------
def print_endpoint(api, path, method, operation):
    print(f"\n--- {method} {path} ---")

    summary = operation.get("summary", "-")
    print(f"Summary: {summary}")

    print("\nParameters:")
    params = build_parameters(api, operation)

    if not params:
        print("  None")
        return

    for i, (name, schema, required) in enumerate(params, 1):
        print(f"  {i}. {format_param(name, schema, required)}")


# ----------------------------
# Category index
# ----------------------------
def build_index(api):
    index = {}

    for path, item in api.get("paths", {}).items():
        for method, op in item.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete", "options", "head"]:
                continue

            tags = op.get("tags", ["uncategorized"])
            for t in tags:
                index.setdefault(t.lower(), []).append((path, method.upper(), op))

    return index


# ----------------------------
# Commands
# ----------------------------
def categories(api):
    index = build_index(api)

    print("\nCategories:")
    for k in sorted(index):
        print(f"- {k}")


def endpoints(api, category):
    index = build_index(api)
    category = category.lower()

    for path, method, op in index.get(category, []):
        print(f"{method} {path} - {op.get('summary','')}")


def category_extract(api, category):
    index = build_index(api)
    category = category.lower()

    for path, method, op in index.get(category, []):
        print_endpoint(api, path, method, op)


def endpoint_extract(api, target):
    paths = api.get("paths", {})

    if target not in paths:
        print("Not found")
        return

    for method, op in paths[target].items():
        if method.lower() not in ["get", "post", "put", "patch", "delete", "options", "head"]:
            continue
        print_endpoint(api, target, method.upper(), op)


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print("Usage:")
        print("  categories <spec>")
        print("  endpoints <spec> <category>")
        print("  category <spec> <category>")
        print("  endpoint <spec> <endpoint>")
        return

    cmd = args[0]
    api = load_spec(os.path.abspath(args[1]))

    if cmd == "categories":
        categories(api)

    elif cmd == "endpoints":
        endpoints(api, args[2])

    elif cmd == "category":
        category_extract(api, args[2])

    elif cmd == "endpoint":
        endpoint_extract(api, args[2])

    else:
        print("Unknown command")


if __name__ == "__main__":
    main()