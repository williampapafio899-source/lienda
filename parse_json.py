#!/usr/bin/env python3
"""Parse JSON from a file or stdin, optionally extract a value by path, and print it.

Examples:
    python parse_json.py data.json
    python parse_json.py data.json --path users.0.name
    cat data.json | python parse_json.py --path config.debug
"""
import argparse
import json
import sys


def load_json(source):
    """Load JSON from a file path, or from stdin if source is None or '-'."""
    if source in (None, "-"):
        return json.load(sys.stdin)
    with open(source, encoding="utf-8") as f:
        return json.load(f)


def get_path(data, path):
    """Walk a dot-separated path like 'users.0.name' through dicts and lists."""
    for key in path.split("."):
        if isinstance(data, list):
            try:
                data = data[int(key)]
            except (ValueError, IndexError):
                raise KeyError(f"invalid list index '{key}'")
        elif isinstance(data, dict):
            if key not in data:
                raise KeyError(f"key '{key}' not found")
            data = data[key]
        else:
            raise KeyError(f"cannot index into {type(data).__name__} with '{key}'")
    return data


def main():
    parser = argparse.ArgumentParser(description="Parse and query JSON.")
    parser.add_argument("file", nargs="?", help="JSON file (omit or '-' for stdin)")
    parser.add_argument("-p", "--path", help="dot-separated path to extract, e.g. users.0.name")
    parser.add_argument("-i", "--indent", type=int, default=2, help="indent for output (default 2)")
    args = parser.parse_args()

    try:
        data = load_json(args.file)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {args.file}")
    except json.JSONDecodeError as e:
        sys.exit(f"Error: invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")

    if args.path:
        try:
            data = get_path(data, args.path)
        except KeyError as e:
            sys.exit(f"Error: {e.args[0]}")

    # Print plain strings without quotes; everything else as formatted JSON.
    if isinstance(data, str):
        print(data)
    else:
        print(json.dumps(data, indent=args.indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
