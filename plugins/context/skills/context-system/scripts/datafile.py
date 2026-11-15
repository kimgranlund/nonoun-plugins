"""Read a vocabulary or rules file: JSON with the standard library, or YAML when PyYAML happens to be installed.

JSON is the format the skill ships and checks. A `.yaml` or `.yml` file written before the switch is still read, but
only on a machine that has PyYAML; without it the caller gets a DataError that says how to move on. A top-level key
that starts with `$` (`$comment`, `$schema`) is a note for people and is dropped on load.

`load(path, lines=True)` also records each JSON object's (or YAML mapping's) 1-based start line under LINE_KEY, so a
finding can point at the line of the pattern or slot it is about.
"""
import json
from pathlib import Path

LINE_KEY = '__line__'


class DataError(ValueError):
    """The file is not valid JSON or YAML, or is YAML on a machine without PyYAML. `kind` names the format."""

    def __init__(self, kind, problem):
        super().__init__(problem)
        self.kind, self.problem = kind, problem


def _object_lines(text):
    """Start lines of the JSON objects in `text`, in the order their closing braces appear (the order a decoder's
    object_pairs_hook is called in)."""
    closed, stack, line, in_string, escaped = [], [], 1, False, False
    for ch in text:
        if ch == '\n':
            line += 1
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == '{':
            stack.append(line)
        elif ch == '}' and stack:
            closed.append(stack.pop())
    return closed


def _load_json(text, lines):
    try:
        if not lines:
            return json.loads(text)
        starts = iter(_object_lines(text))

        def hook(pairs):
            obj = dict(pairs)
            obj[LINE_KEY] = next(starts, 1)
            return obj
        return json.loads(text, object_pairs_hook=hook)
    except ValueError as exc:
        raise DataError('JSON', ' '.join(str(exc).split()))


def _load_yaml(text, lines):
    try:
        import yaml
    except ImportError:
        raise DataError('YAML', 'this is a YAML file and PyYAML is not installed; rewrite the file as JSON '
                                '(the format the templates use) or install PyYAML')
    loader = yaml.SafeLoader
    if lines:
        class LineLoader(yaml.SafeLoader):
            def construct_mapping(self, node, deep=False):
                mapping = super().construct_mapping(node, deep=deep)
                mapping[LINE_KEY] = node.start_mark.line + 1
                return mapping
        loader = LineLoader
    try:
        return yaml.load(text, Loader=loader)
    except yaml.YAMLError as exc:
        raise DataError('YAML', ' '.join(str(exc).split()))


def load(path, lines=False):
    """Parse the file at `path`. Raises OSError when it cannot be read and DataError when it cannot be parsed."""
    text = Path(path).read_text(encoding='utf-8')
    data = _load_yaml(text, lines) if Path(path).suffix.lower() in ('.yaml', '.yml') else _load_json(text, lines)
    if isinstance(data, dict):
        for key in [k for k in data if isinstance(k, str) and k.startswith('$')]:
            del data[key]
    return data


def front_matter(lines):
    """The `key: value` pairs of a Markdown front matter block, as strings. Nested values are ignored: the linter
    reads one flat key."""
    out = {}
    for line in lines:
        if line[:1] in (' ', '\t', '#', '-') or ':' not in line:
            continue
        key, value = line.split(':', 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        if key.strip() and value:
            out[key.strip()] = value
    return out
