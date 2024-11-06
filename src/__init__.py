from collections import defaultdict

from tree_sitter_languages import get_parser, get_language

def walk_all(parser, code):
    tree = parser.parse(code.encode())
    cursor = tree.walk()
    visited_children = False

    while True:
        if not visited_children:
            yield cursor.node
            if not cursor.goto_first_child():
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent():
            break

def walk_top_level(tree):
    cursor = tree.walk()
    cursor.goto_first_child()
    yield cursor.node

    while cursor.goto_next_sibling():
        yield cursor.node

def dbg(node, indent_level=0):
    width = 100
    left = " "*indent_level*4 + node.text.decode()
    info = f"{len(node.children)} {node.type}"

    print(f"{left}{info:>{width-len(left)}}")

def import_insert_at(node):
    last_import = None
    for node2 in walk_all(node):
        if node2.type == "identifier":
            last_import = node2

    assert last_import
    return last_import

def import_from_statement_serialize(node):
    if node.type != "import_from_statement":
        raise ValueError("Node must be import_from_statement")

    module = next(n for n in node.named_children if n.type == "dotted_name").text.decode()
    imports = set()
    for child in node.named_children:
        if child.type == "dotted_name" and child.text.decode() != module:
            imports.add(child.text.decode())
        elif child.type == "aliased_import":
            name = child.child_by_field_name("name").text.decode()
            alias = child.child_by_field_name("alias").text.decode()
            imports.add(f"{name} as {alias}")

    return module, imports

def import_statement_serialize(node):
    if node.type != "import_statement":
        raise ValueError("Node must be import_statement")

    imports = set()
    for child in node.named_children:
        if child.type == "dotted_name":
            imports.add(child.text.decode())
        elif child.type == "aliased_import":
            name = child.child_by_field_name("name").text.decode()
            alias = child.child_by_field_name("alias").text.decode()
            imports.add(f"{name} as {alias}")

    return imports

def imports_serialize(tree):
    imports_from, imports = defaultdict(set), set()
    for node in walk_top_level(tree):
        if node.type == "import_from_statement":
            module, module_imports = import_from_statement_serialize(node)
            imports_from[module] |= module_imports
        elif node.type == "import_statement":
            imports |= import_statement_serialize(node)

    return imports_from, imports

def parse(parser, code):
    new_code = code
    imports = defaultdict(list)
    offset = 0
    for node in walk_top_level(parser, code):
        dbg(node)
        if node.type == "import_from_statement":
            continue
            print(import_from_statement_serialize(node))
            import_at = import_insert_at(node)
            addition = ", foo"
            new_code = new_code[:import_at.end_byte + offset] + addition + new_code[import_at.end_byte + offset:]
            offset += len(addition)
        elif node.type == "import_statement":
            print(import_statement_serialize(node))
            import_at = import_insert_at(node)
            addition = ", foo"
            new_code = new_code[:import_at.end_byte + offset] + addition + new_code[import_at.end_byte + offset:]
            offset += len(addition)

    from pprint import pprint
    pprint(dict(imports))
    print(new_code)

def combine(source_or_sources_code, destination_code):
    if type(source_or_sources_code) is str:
        source_or_sources_code = [source_or_sources_code]

    parser = get_parser('python')
    source_imports_from, source_imports = defaultdict(set), set()

    for source_code in source_or_sources_code:
        tree = parser.parse(source_code.encode())
        imports_from, imports = imports_serialize(tree)
        for module, module_imports in imports_from.items():
            source_imports_from[module] |= module_imports
        source_imports |= imports

    print(dict(source_imports_from), source_imports)

combine(
    """
from a import (b, c as d)
from e import f as g, h
import zop.bop, zip.zop, b.a as pof, asdoij
""".strip(), """
from x import zoop

def zoop():
    pass
""".strip())
"""
import d
import e.f

def bar():
    pass
"""
