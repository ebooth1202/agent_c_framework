import argparse, io, os, sys

from typing import Optional

from agent_c_tools.tools.workspace.util.trees.builders.local_file_system import LocalFileSystemTreeBuilder
from agent_c_tools.tools.workspace.util.trees.renderers.ascii import  AsciiTreeRenderer
from agent_c_tools.tools.workspace.util.trees.renderers.json import JsonTreeRenderer
from agent_c_tools.tools.workspace.util.trees.renderers.html import HtmlTreeRenderer

# Set the default encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """
    Tree generation and rendering with multiple output formats.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Directory Tree Generator")
    parser.add_argument("path", nargs="?", default=".", help="Path to generate tree from (default: current directory)")
    parser.add_argument("--output", "-o", choices=["ascii", "json", "html"], default="ascii", help="Output format")
    parser.add_argument("--max-depth", "-d", type=int, help="Maximum depth to display")
    parser.add_argument("--max-files-depth", "-f", type=int, help="Maximum depth for displaying files")
    parser.add_argument("--ignore", "-i", action="append", help="Patterns to ignore (can be specified multiple times)")
    parser.add_argument("--ignore-file", type=str, help="Path to a .gitignore style file with patterns to ignore")
    parser.add_argument("--output-file", type=str, help="File to write output to (prints to stdout if not specified)")
    args = parser.parse_args()

    # Process ignore patterns
    ignore_patterns = []

    # Add patterns from command-line arguments
    if args.ignore:
        ignore_patterns.extend(args.ignore)

    # Add patterns from ignore file if specified
    if args.ignore_file and os.path.exists(args.ignore_file):
        with open(args.ignore_file, "r") as f:
            ignore_content = f.read()
            ignore_patterns.append(ignore_content)

    # Create a tree builder
    builder = LocalFileSystemTreeBuilder(ignore_patterns=ignore_patterns)

    # Build the directory tree
    tree = builder.build_tree(start_path=args.path)

    # Choose renderer based on output format
    if args.output == "ascii":
        renderer = AsciiTreeRenderer()
        output = "\n".join(renderer.render(
            tree=tree,
            max_depth=args.max_depth,
            max_files_depth=args.max_files_depth,
            include_root=True
        ))
    elif args.output == "json":
        renderer = JsonTreeRenderer()
        output = renderer.render(
            tree=tree,
            max_depth=args.max_depth,
            max_files_depth=args.max_files_depth,
            pretty_print=True
        )
    elif args.output == "html":
        renderer = HtmlTreeRenderer()
        title = f"Directory Tree for {os.path.abspath(args.path)}"
        output = renderer.render(
            tree=tree,
            max_depth=args.max_depth,
            max_files_depth=args.max_files_depth,
            title=title
        )

    # Write output to file or print to stdout
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(output)
        print(f"Tree written to {args.output_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
