"""
SublimeLight - Editor Snippet Configuration Library
Defines macro abbreviation tracking lookups and multiline boilerplate code streams.
"""

SNIPPET_LIBRARY = {
    "main": (
        "if __name__ == \"__main__\":\n"
        "    main()"
    ),
    "def": (
        "def function_name(args):\n"
        "    \"\"\"Docstring description.\"\"\"\n"
        "    pass"
    ),
    "class": (
        "class ClassName:\n"
        "    def __init__(self):\n"
        "        pass"
    ),
    "try": (
        "try:\n"
        "    pass\n"
        "except Exception as e:\n"
        "    raise e"
    ),
    "for": (
        "for item in iterable:\n"
        "    pass"
    )
}
