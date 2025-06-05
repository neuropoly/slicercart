# combine_dot_files.py
import sys

dot_files = sys.argv[1:]
output_file = sys.argv[2] if len(sys.argv) > 2 else "combined.dot"

all_lines = []

all_lines.append("digraph G {")

for file in dot_files:
    with open(file, "r") as f:
        lines = f.readlines()
        # skip first and last lines (digraph G { ... })
        content = lines[1:-1]
        all_lines.extend(content)

all_lines.append("}")

with open(output_file, "w") as f:
    f.writelines(all_lines)

print(f"Combined {len(dot_files)} files into {output_file}")
