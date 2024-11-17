import os
from pathlib import Path
import difflib
from tree_sitter_languages import get_parser
from codecombine import combine_imports, walk_top_level

def run_test(title, source_codes, destination_code, expected_code, combine_imports):
    """Run a single test and report results."""
    try:
        actual_code = combine_imports(source_codes, destination_code)
        actual_code = actual_code.strip()
        expected_code = expected_code.strip()

        if actual_code != expected_code:
            print(f"\n❌ Test failed: {title}")
            diff = list(
                difflib.unified_diff(expected_code.splitlines(keepends=True),
                                     actual_code.splitlines(keepends=True), fromfile='expected', tofile='actual'))
            print(''.join(diff))
            return False
        else:
            print(f"✅ Test passed: {title}")
            return True
    except Exception as e:
        print(f"\n❌ Test error in {title}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def extract_title(heading_node, content):
    """Extract the title from a heading node."""
    for child in heading_node.children:
        if child.type == "heading_content":
            return content[child.start_byte:child.end_byte].decode()
    return "Untitled Test"

def main():
    # Get the markdown parser
    parser = get_parser('markdown')

    # Find all test files
    test_dir = Path("tests")
    test_files = list(test_dir.glob("test_*.md"))

    if not test_files:
        print("No test files found in ./tests directory matching 'test_*.md'")
        return

    total_tests = 0
    passed_tests = 0

    # Process each test file
    for test_file in sorted(test_files):
        print(f"\nRunning tests from {test_file.name}")
        print("=" * 60)

        # Read and parse the file
        with open(test_file, 'rb') as f:
            content = f.read()
            tree = parser.parse(content)

        code_blocks_by_heading = []
        current_title = None

        for node in walk_top_level(tree):
            if node.type == "atx_heading":
                current_title = extract_title(node, content)
                code_blocks_by_heading.append({'title': current_title, 'blocks': []})
            elif node.type == "fenced_code_block":
                if not code_blocks_by_heading:
                    print("❌ Error: Found code block before any heading")
                    continue

                code_content = [x for x in node.children if x.type == "code_fence_content"]
                if code_content:
                    code_blocks_by_heading[-1]['blocks'].append(code_content[0].text.decode())

        # Process each test case
        for test_case in code_blocks_by_heading:
            total_tests += 1
            title = test_case['title']
            blocks = test_case['blocks']

            if len(blocks) < 3:
                print(f"❌ Error in {title}: Not enough code blocks (minimum 3 required)")
                continue

            # If more than 3 blocks, treat all but last 2 as source files
            source_codes = blocks[:-2]
            destination_code = blocks[-2]
            expected_code = blocks[-1]

            # For single source file, pass as string instead of list
            if len(source_codes) == 1:
                source_codes = source_codes[0]

            if run_test(title, source_codes, destination_code, expected_code, combine_imports):
                passed_tests += 1

    # Print summary
    print("\nTest Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    if total_tests > 0:
        print(f"Success rate: {(passed_tests/total_tests*100):.1f}%")

if __name__ == "__main__":
    main()
