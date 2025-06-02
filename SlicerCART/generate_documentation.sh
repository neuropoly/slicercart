#!/bin/bash
echo "Regenerating .rst files..."
sphinx-apidoc -f -o docs/ src/

echo "Building HTML..."
cd docs
make html
cd ..
echo "Docs ready at docs/_build/html/index.html"
