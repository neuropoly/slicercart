To build the documentation locally (to review it before it is used to update the GitHub pages), do the following:

1. Create a conda/mamba environment with the requisite packages:

```bash
mamba create --name slicercart_docs --file requirements.txt
```

2. Activate the environment:

```bash
mamba activate slicercart_docs
```

3. Rebuild the documentation in HTML format:

```bash
make html
```

If everything ran correctly, a new directory named `_build` should appear next to `_source`. You can view the "splash" page of the docs by opening the `index.html` within it with a web browser of your choice (click and drag the file onto your browser if it doesn't open automatically).
