#!/usr/bin/env python3
# @armor (Engine Core)
"""Validate a JSON file against a JSON Schema for vde_validate_json_schema.

Usage: vde-json-validate.py <schema.json> <data.json> <auto|builtin|jsonschema>

On success the validator that was used ("jsonschema" or "builtin") is printed
to stdout and the exit status is 0. On any failure a one-line reason is
printed to stderr and the exit status is 1.

Validator modes:
  auto        use the jsonschema module when importable, otherwise the
              built-in validator (default)
  builtin     always use the built-in validator
  jsonschema  require the jsonschema module; fail if it is missing

The built-in validator exists so hosts without the jsonschema module are not
left with a weaker check. It is deliberately NOT a general JSON Schema
implementation: it implements exactly the keywords the project schemas use,
with JSON Schema 2020-12 semantics, and it REFUSES (exit 1, explicit message)
anything else, including any unknown keyword, a non-local $ref, or a "$schema"
other than 2019-09/2020-12. Refusing instead of ignoring is what keeps it from
becoming a silent fake pass.

Constructs that are valid JSON Schema but deliberately NOT implemented, and so
refused: boolean schemas (for example "items": true), "$ref" with sibling
keywords, a "required" list with duplicate names, and every keyword outside the
supported list below (enum, const, oneOf, patternProperties, ...). A
"jsonschema" module older than 4.0 (no Draft202012Validator) is not used: its
default draft is version-dependent, so "auto" uses the built-in validator and
says so.
"""

import json
import re
import sys
from urllib.parse import unquote

VALIDATING = {
    "type",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minimum",
    "maximum",
    "minLength",
    "pattern",
    "$ref",
}
# Keys that carry no validation. "format" is annotation-only here, matching
# jsonschema's default (it does not enforce formats without a format checker).
ANNOTATIONS = {
    "$id",
    "$schema",
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "definitions",
    "$defs",
    "deprecated",
    "readOnly",
    "writeOnly",
    "format",
}
TYPES = {"object", "array", "string", "boolean", "null", "integer", "number"}
SUPPORTED_DRAFTS = {
    "https://json-schema.org/draft/2020-12/schema",
    "https://json-schema.org/draft/2019-09/schema",
}


class Refused(Exception):
    """The schema uses something the built-in validator does not implement."""


class Invalid(Exception):
    """The data does not satisfy the schema."""


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def type_name(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def is_type(value, name):
    if name == "integer":
        if isinstance(value, bool):
            return False
        return isinstance(value, int) or (isinstance(value, float) and value.is_integer())
    if name == "number":
        return is_number(value)
    return type_name(value) == name


class BuiltinValidator:
    def __init__(self, schema):
        self.schema = schema
        self.checked_refs = set()
        self.check_schema(schema, "$")

    @staticmethod
    def refuse(path, what):
        raise Refused(
            f"Schema keyword '{what}' at {path} is unsupported by the built-in "
            "validator; install python3-jsonschema (pip install jsonschema) "
            "to validate this schema"
        )

    def check_schema(self, schema, path):
        """Refuse anything in this (sub)schema the validator does not implement."""
        if not isinstance(schema, dict):
            self.refuse(path, "non-object schema")
        declared = schema.get("$schema")
        if declared is not None:
            # A trailing "#" is the same draft ("...schema#" and "...schema").
            normalized = declared.rstrip("#") if isinstance(declared, str) else declared
            if normalized not in SUPPORTED_DRAFTS:
                self.refuse(path, f"$schema {declared!r}")
        if "$id" in schema and path != "$":
            # A nested $id changes the base URI for $ref resolution, which this
            # validator does not model.
            self.refuse(path, "$id (nested)")
        siblings = [
            key
            for key in schema
            if key not in ANNOTATIONS and not key.startswith("@") and key != "$ref"
        ]
        if "$ref" in schema and siblings:
            self.refuse(path, "$ref with sibling keyword " + siblings[0])
        for key, value in schema.items():
            if key in ANNOTATIONS or key.startswith("@"):
                continue
            if key not in VALIDATING:
                self.refuse(path, key)
            self.check_keyword(key, value, path)
        for container in ("definitions", "$defs"):
            subschemas = schema.get(container)
            if isinstance(subschemas, dict):
                for name, sub in subschemas.items():
                    self.check_schema(sub, f"{path}/{container}/{name}")

    def check_keyword(self, key, value, path):
        if key == "$ref":
            if not (isinstance(value, str) and value.startswith("#")):
                self.refuse(path, "$ref (non-local)")
        elif key == "type":
            names = value if isinstance(value, list) else [value]
            if not all(isinstance(name, str) and name in TYPES for name in names):
                self.refuse(path, f"type {value!r}")
        elif key == "required":
            if not (isinstance(value, list) and all(isinstance(n, str) for n in value)):
                self.refuse(path, "required (not a list of names)")
            if len(value) != len(set(value)):
                # jsonschema's metaschema requires the names to be unique.
                self.refuse(path, "required (duplicate names)")
        elif key == "properties":
            if not isinstance(value, dict):
                self.refuse(path, "properties (not an object)")
            for name, sub in value.items():
                self.check_schema(sub, f"{path}/properties/{name}")
        elif key == "additionalProperties":
            if isinstance(value, dict):
                self.check_schema(value, f"{path}/additionalProperties")
            elif not isinstance(value, bool):
                self.refuse(path, "additionalProperties")
        elif key == "items":
            self.check_schema(value, f"{path}/items")
        elif key in ("minimum", "maximum"):
            if not is_number(value):
                self.refuse(path, f"{key} (not a number)")
        elif key == "minLength":
            if not (isinstance(value, int) and not isinstance(value, bool) and value >= 0):
                self.refuse(path, "minLength (not a non-negative integer)")
        elif key == "pattern":
            try:
                re.compile(value)
            except (re.error, TypeError):
                raise Refused(
                    f"Schema pattern at {path} is not a valid regular expression: {value!r}"
                ) from None

    def resolve(self, ref):
        if ref == "#":
            return self.schema
        if not ref.startswith("#/"):
            self.refuse("$ref", ref)
        node = self.schema
        for part in ref[2:].split("/"):
            # URI fragment: percent-decode first, then JSON-pointer unescape.
            part = unquote(part).replace("~1", "/").replace("~0", "~")
            if not isinstance(node, dict) or part not in node:
                raise Refused(f"unresolvable $ref '{ref}'")
            node = node[part]
        return node

    def validate(self, data):
        self.check(data, self.schema, "")

    def check(self, value, schema, path):
        where = path or "$"
        if "$ref" in schema:
            ref = schema["$ref"]
            target = self.resolve(ref)
            if ref not in self.checked_refs:
                # A $ref can point anywhere, including a subtree no walk of
                # properties/items/definitions reaches: check what it reaches.
                self.checked_refs.add(ref)
                # The root schema keeps its own path, so its "$id" is not
                # mistaken for a nested one.
                self.check_schema(target, "$" if target is self.schema else ref)
            self.check(value, target, path)
            return
        declared = schema.get("type")
        if declared is not None:
            names = declared if isinstance(declared, list) else [declared]
            if not any(is_type(value, name) for name in names):
                raise Invalid(
                    f"{where}: expected {' or '.join(names)}, got {type_name(value)}"
                )
        if isinstance(value, dict):
            self.check_object(value, schema, path, where)
        if isinstance(value, list) and "items" in schema:
            for index, item in enumerate(value):
                self.check(item, schema["items"], f"{path}[{index}]")
        if isinstance(value, str):
            self.check_string(value, schema, where)
        if is_number(value):
            self.check_number(value, schema, where)

    def check_object(self, value, schema, path, where):
        for name in schema.get("required", []):
            if name not in value:
                raise Invalid(f"{where}: missing required property '{name}'")
        properties = schema.get("properties", {})
        for name, sub in properties.items():
            if name in value:
                self.check(value[name], sub, f"{path}/{name}")
        extra = schema.get("additionalProperties", True)
        if extra is True:
            return
        for name in value:
            if name in properties:
                continue
            if extra is False:
                raise Invalid(f"{where}: additional property '{name}' is not allowed")
            self.check(value[name], extra, f"{path}/{name}")

    @staticmethod
    def check_string(value, schema, where):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise Invalid(f"{where}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise Invalid(f"{where}: {value!r} does not match pattern {schema['pattern']!r}")

    @staticmethod
    def check_number(value, schema, where):
        if "minimum" in schema and value < schema["minimum"]:
            raise Invalid(f"{where}: {value} is less than minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise Invalid(f"{where}: {value} is greater than maximum {schema['maximum']}")


def fail(message):
    print(message, file=sys.stderr)
    return 1


def main(argv):
    if len(argv) != 4:
        return fail(f"usage: {argv[0]} <schema.json> <data.json> <auto|builtin|jsonschema>")
    schema_path, data_path, mode = argv[1], argv[2], argv[3]
    if mode not in ("auto", "builtin", "jsonschema"):
        return fail(f"Unknown VDE_SCHEMA_VALIDATOR '{mode}' (use auto, builtin or jsonschema)")
    try:
        with open(schema_path, encoding="utf-8") as handle:
            schema = json.load(handle)
        with open(data_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except RecursionError:
        return fail("Validation script error: JSON is nested too deeply to load")
    except (OSError, ValueError) as error:
        return fail(f"Validation script error: {error}")

    validator = "builtin"
    if mode != "builtin":
        try:
            import jsonschema

            if hasattr(jsonschema, "Draft202012Validator"):
                validator = "jsonschema"
            elif mode == "jsonschema":
                return fail(
                    "VDE_SCHEMA_VALIDATOR=jsonschema but the installed jsonschema module has no "
                    "Draft202012Validator (it is older than 4.0); upgrade it or use auto/builtin"
                )
            # In auto mode an older module is not used: its default draft is
            # version-dependent, so the built-in validator (2020-12) is used and
            # reported by name instead.
        except ImportError:
            if mode == "jsonschema":
                return fail(
                    "VDE_SCHEMA_VALIDATOR=jsonschema but the jsonschema module is not installed"
                )

    if validator == "jsonschema":
        try:
            # Pin the default draft to 2020-12 (what the built-in validator
            # implements); an explicit "$schema" in the schema still wins.
            validator_class = jsonschema.validators.validator_for(
                schema, default=jsonschema.Draft202012Validator
            )
            validator_class.check_schema(schema)
            validator_class(schema).validate(data)
        except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError) as error:
            return fail(f"Schema validation error: {error}")
        except Exception as error:  # noqa: BLE001
            # Anything else raised while validating (for example an unresolvable
            # $ref) must still fail closed, with a message instead of a traceback.
            return fail(f"Schema validation error: {error}")
    else:
        try:
            BuiltinValidator(schema).validate(data)
        except (Refused, Invalid) as error:
            return fail(f"Schema validation error: {error}")
        except RecursionError:
            return fail("Schema validation error: schema is too deeply nested or self-referencing")

    print(validator)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
