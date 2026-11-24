import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STORE_PATH = Path.home() / ".envvault" / "vault.json"


def load_vault() -> dict:
    if not STORE_PATH.exists():
        return {"entries": []}
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"entries": []}


def save_vault(data: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Restrict permissions on Unix-like systems; Windows ignores chmod bits safely
    STORE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(STORE_PATH, 0o600)
    except OSError:
        pass


def copy_to_clipboard(text: str) -> bool:
    try:
        import pyperclip  # type: ignore

        pyperclip.copy(text)
        return True
    except Exception:
        pass

    if sys.platform.startswith("win"):
        try:
            subprocess.run(["clip"], input=text.encode("utf-16le"), check=True)
            return True
        except Exception:
            return False
    elif sys.platform == "darwin":
        try:
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        except Exception:
            return False
    else:
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                return True
            except Exception:
                continue
    return False


def cmd_add(args: argparse.Namespace) -> None:
    vault = load_vault()
    tags = [t.strip().lower() for t in (args.tags or "").split(",") if t.strip()]
    entry = {
        "name": args.name.strip(),
        "value": args.value,
        "tags": tags,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Replace existing entry with same name if present
    vault["entries"] = [e for e in vault["entries"] if e["name"].lower() != entry["name"].lower()]
    vault["entries"].append(entry)
    save_vault(vault)
    print(f"Saved '{entry['name']}' to {STORE_PATH}")


def cmd_list(args: argparse.Namespace) -> None:
    vault = load_vault()
    entries = vault["entries"]
    if args.tag:
        target_tag = args.tag.strip().lower()
        entries = [e for e in entries if target_tag in e.get("tags", [])]

    if not entries:
        print("No matching entries found.")
        return

    for e in sorted(entries, key=lambda x: x["name"].lower()):
        tags_str = ", ".join(e.get("tags", [])) or "none"
        print(f"- {e['name']}  [tags: {tags_str}]")


def cmd_search(args: argparse.Namespace) -> None:
    query = args.query.strip().lower()
    vault = load_vault()
    matches = [
        e
        for e in vault["entries"]
        if query in e["name"].lower()
        or any(query in t.lower() for t in e.get("tags", []))
    ]

    if not matches:
        print(f"No entries matching '{args.query}'.")
        return

    for e in matches:
        tags_str = ", ".join(e.get("tags", [])) or "none"
        print(f"- {e['name']}  [tags: {tags_str}]")


def cmd_get(args: argparse.Namespace) -> None:
    vault = load_vault()
    target = args.name.strip().lower()
    match = next((e for e in vault["entries"] if e["name"].lower() == target), None)

    if not match:
        print(f"Entry '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.copy:
        if copy_to_clipboard(match["value"]):
            print(f"Copied '{match['name']}' to clipboard.")
        else:
            print("Could not copy automatically; value:")
            print(match["value"])
    else:
        print(match["value"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envvault",
        description="Local CLI vault for environment values and command snippets.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add or update a secret/snippet")
    p_add.add_argument("name", help="Unique key/snippet name (e.g., RENDER_API_KEY)")
    p_add.add_argument("value", help="Value or command string")
    p_add.add_argument("--tags", default="", help="Comma-separated tags (e.g., api,deploy)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List saved entry names and tags")
    p_list.add_argument("--tag", default="", help="Filter by tag")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Search entries by name or tag")
    p_search.add_argument("query", help="Search keyword")
    p_search.set_defaults(func=cmd_search)

    p_get = sub.add_parser("get", help="Print or copy a saved value")
    p_get.add_argument("name", help="Entry name")
    p_get.add_argument("--copy", action="store_true", help="Copy value to clipboard")
    p_get.set_defaults(func=cmd_get)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()