#!/usr/bin/env python3
"""
Evernote connector — wraps the evernote3 / evernote Python SDK.

Authentication:
  Set EVERNOTE_TOKEN env var to your developer/OAuth access token.
  Set EVERNOTE_NOTE_STORE_URL to your NoteStore URL (e.g. https://www.evernote.com/edam/note/sXXX).

Usage:
  python3 evernote.py list-notebooks
  python3 evernote.py list-notes [--notebook NOTEBOOK_GUID] [--query "search query"]
  python3 evernote.py get-note NOTE_GUID [--text-only]
  python3 evernote.py create-note --title "Title" --body "Plain text body" [--notebook NOTEBOOK_GUID] [--tags tag1,tag2]
  python3 evernote.py create-note --title "Title" --enml-file body.enml [--notebook NOTEBOOK_GUID]
  python3 evernote.py update-note NOTE_GUID --title "New Title" [--body "New body"] [--tags tag1,tag2]
  python3 evernote.py delete-note NOTE_GUID
  python3 evernote.py search "search query" [--max 20]
  python3 evernote.py list-tags
"""

import argparse
import os
import sys
import re

try:
    import evernote.api.client as ec
    from evernote.edam.type.ttypes import Note, Notebook, Tag
    from evernote.edam.notestore import NoteStore
    from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
except ImportError:
    print("ERROR: Install the evernote3 package: pip install evernote3", file=sys.stderr)
    sys.exit(1)


ENML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n'


def get_client():
    token = os.environ.get("EVERNOTE_TOKEN")
    if not token:
        print("ERROR: Set EVERNOTE_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)
    return ec.EvernoteClient(token=token, sandbox=False)


def get_note_store():
    token = os.environ.get("EVERNOTE_TOKEN")
    note_store_url = os.environ.get("EVERNOTE_NOTE_STORE_URL")
    if not token:
        print("ERROR: Set EVERNOTE_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)
    client = get_client()
    if note_store_url:
        from thrift.transport import THttpClient, TTransport
        from thrift.protocol import TBinaryProtocol
        from evernote.edam.notestore import NoteStore as NoteStoreModule
        http_client = THttpClient.THttpClient(note_store_url)
        http_client.setCustomHeaders({"User-Agent": "evernote-connector/1.0"})
        thrift_protocol = TBinaryProtocol.TBinaryProtocol(http_client)
        note_store = NoteStoreModule.Client(thrift_protocol)
        return note_store, token
    else:
        note_store = client.get_note_store()
        return note_store, token


def text_to_enml(text: str) -> str:
    """Wrap plain text in ENML, escaping HTML entities."""
    escaped = (text
               .replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))
    lines = escaped.split("\n")
    content = "".join(f"<p>{l if l.strip() else '&nbsp;'}</p>" for l in lines)
    return f"{ENML_HEADER}<en-note>{content}</en-note>"


def enml_to_text(enml: str) -> str:
    """Strip ENML tags to get readable plain text."""
    text = re.sub(r"<br\s*/?>", "\n", enml, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    return text.strip()


def cmd_list_notebooks(args):
    note_store, token = get_note_store()
    notebooks = note_store.listNotebooks(token)
    for nb in notebooks:
        print(f"{nb.guid}\t{nb.name}")


def cmd_list_notes(args):
    note_store, token = get_note_store()
    nf = NoteFilter()
    if args.notebook:
        nf.notebookGuid = args.notebook
    if args.query:
        nf.words = args.query
    spec = NotesMetadataResultSpec(includeTitle=True, includeNotebookGuid=True, includeCreated=True)
    result = note_store.findNotesMetadata(token, nf, 0, args.max, spec)
    for note in result.notes:
        print(f"{note.guid}\t{note.title}\t{note.notebookGuid}")


def cmd_get_note(args):
    note_store, token = get_note_store()
    note = note_store.getNote(token, args.guid, True, False, False, False)
    if args.text_only:
        print(enml_to_text(note.content))
    else:
        print(f"Title: {note.title}")
        print(f"GUID:  {note.guid}")
        if note.tagNames:
            print(f"Tags:  {', '.join(note.tagNames)}")
        print("---")
        print(enml_to_text(note.content))


def cmd_create_note(args):
    note_store, token = get_note_store()
    note = Note()
    note.title = args.title

    if args.enml_file:
        with open(args.enml_file) as f:
            note.content = f.read()
    elif args.body:
        note.content = text_to_enml(args.body)
    else:
        print("ERROR: Provide --body or --enml-file.", file=sys.stderr)
        sys.exit(1)

    if args.notebook:
        note.notebookGuid = args.notebook

    if args.tags:
        note.tagNames = [t.strip() for t in args.tags.split(",")]

    created = note_store.createNote(token, note)
    print(f"Created note: {created.guid}\t{created.title}")


def cmd_update_note(args):
    note_store, token = get_note_store()
    note = note_store.getNote(token, args.guid, True, False, False, False)
    if args.title:
        note.title = args.title
    if args.body:
        note.content = text_to_enml(args.body)
    if args.enml_file:
        with open(args.enml_file) as f:
            note.content = f.read()
    if args.tags:
        note.tagNames = [t.strip() for t in args.tags.split(",")]
    updated = note_store.updateNote(token, note)
    print(f"Updated note: {updated.guid}\t{updated.title}")


def cmd_delete_note(args):
    note_store, token = get_note_store()
    note_store.deleteNote(token, args.guid)
    print(f"Deleted (trashed) note: {args.guid}")


def cmd_search(args):
    note_store, token = get_note_store()
    nf = NoteFilter(words=args.query)
    spec = NotesMetadataResultSpec(includeTitle=True, includeNotebookGuid=True)
    result = note_store.findNotesMetadata(token, nf, 0, args.max, spec)
    print(f"Found {result.totalNotes} notes (showing up to {args.max}):")
    for note in result.notes:
        print(f"  {note.guid}\t{note.title}")


def cmd_list_tags(args):
    note_store, token = get_note_store()
    tags = note_store.listTags(token)
    for tag in tags:
        print(f"{tag.guid}\t{tag.name}")


def main():
    parser = argparse.ArgumentParser(description="Evernote connector CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-notebooks")

    p = sub.add_parser("list-notes")
    p.add_argument("--notebook", help="Filter by notebook GUID")
    p.add_argument("--query", help="Evernote search query")
    p.add_argument("--max", type=int, default=50)

    p = sub.add_parser("get-note")
    p.add_argument("guid")
    p.add_argument("--text-only", action="store_true")

    p = sub.add_parser("create-note")
    p.add_argument("--title", required=True)
    p.add_argument("--body", help="Plain text body")
    p.add_argument("--enml-file", help="Path to .enml file")
    p.add_argument("--notebook", help="Notebook GUID")
    p.add_argument("--tags", help="Comma-separated tag names")

    p = sub.add_parser("update-note")
    p.add_argument("guid")
    p.add_argument("--title")
    p.add_argument("--body")
    p.add_argument("--enml-file")
    p.add_argument("--tags", help="Comma-separated tag names (replaces existing)")

    p = sub.add_parser("delete-note")
    p.add_argument("guid")

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=20)

    sub.add_parser("list-tags")

    args = parser.parse_args()
    {
        "list-notebooks": cmd_list_notebooks,
        "list-notes": cmd_list_notes,
        "get-note": cmd_get_note,
        "create-note": cmd_create_note,
        "update-note": cmd_update_note,
        "delete-note": cmd_delete_note,
        "search": cmd_search,
        "list-tags": cmd_list_tags,
    }[args.command](args)


if __name__ == "__main__":
    main()
