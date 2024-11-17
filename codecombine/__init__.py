from collections import defaultdict

from tree_sitter_languages import get_parser, get_language

from ordered_set import OrderedSet as oset

def walk_all_children(node):
    for child in node.children:
        yield from walk_all_children(child)
        yield child

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
    for node2 in walk_all_children(node):
        if node2.type == "identifier":
            last_import = node2

    assert last_import
    return last_import

def import_from_statement_serialize(node):
    if node.type != "import_from_statement":
        raise ValueError("Node must be import_from_statement")

    module = next(n for n in node.named_children if n.type == "dotted_name").text.decode()
    imports = oset()
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

    imports = oset()
    for child in node.named_children:
        if child.type == "dotted_name":
            imports.add(child.text.decode())
        elif child.type == "aliased_import":
            name = child.child_by_field_name("name").text.decode()
            alias = child.child_by_field_name("alias").text.decode()
            imports.add(f"{name} as {alias}")

    return imports

def imports_serialize(tree):
    imports_from, imports = defaultdict(set), oset()
    for node in walk_top_level(tree):
        if node.type == "import_from_statement":
            module, module_imports = import_from_statement_serialize(node)
            imports_from[module] |= module_imports
        elif node.type == "import_statement":
            imports |= import_statement_serialize(node)

    return imports_from, imports

def get_missing_imports(source_imports_from, destination_imports_from, source_imports, destination_imports):
    missing_from = defaultdict(set)
    for module, items in source_imports_from.items():
        if module not in destination_imports_from:
            missing_from[module] = items
        else:
            missing_items = items - destination_imports_from[module]
            if missing_items:
                missing_from[module] = missing_items

    missing = source_imports - destination_imports
    return missing_from, missing

def insert_after(code, node, addition, offset):
    return code[:node.end_byte + offset] + addition + code[node.end_byte + offset:], offset + len(addition)

def combine_imports(source_or_sources_code, destination_code):
    result_code = destination_code

    if type(source_or_sources_code) is str:
        source_or_sources_code = [source_or_sources_code]

    parser = get_parser('python')
    source_imports_from, source_imports = defaultdict(set), oset()

    for source_code in source_or_sources_code:
        tree = parser.parse(source_code.encode())
        imports_from, imports = imports_serialize(tree)
        for module, module_imports in imports_from.items():
            source_imports_from[module] |= module_imports
        source_imports |= imports

    tree = parser.parse(destination_code.encode())
    destination_imports_from, destination_imports = imports_serialize(tree)

    missing_imports_from, missing_imports = get_missing_imports(source_imports_from, destination_imports_from,
                                                                source_imports, destination_imports)

    prev_import, last_import = None, None
    offset = 0
    for node in walk_top_level(tree):
        if node.type == "import_from_statement":
            prev_import = node
            module, module_imports = import_from_statement_serialize(node)
            if module in missing_imports_from:
                import_at = import_insert_at(node)
                addition = ", " + ", ".join(missing_imports_from[module])
                result_code, offset = insert_after(result_code, import_at, addition, offset)
                del missing_imports_from[module]

        elif node.type == "import_statement":
            prev_import = node
            imports = import_statement_serialize(node)
        elif node.type in ["comment", "expression_statement"]:
            pass
        else:
            if prev_import and last_import is None:
                last_import = prev_import

    if last_import is None:
        last_import = prev_import

    missing_imports_code = []
    if missing_imports_from:
        missing_imports_code.extend([f"from {k} import {', '.join(v)}" for k, v in missing_imports_from.items()])
    if missing_imports:
        missing_imports_code.extend([f"import {x}" for x in missing_imports])

    result_code, offset = insert_after(result_code, last_import, "\n" + "\n".join(missing_imports_code), offset)

    return result_code
