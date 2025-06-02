Class Organization
=================

This page shows the class organization diagram of SlicerCART. The diagram is automatically generated using `pyreverse`.

To regenerate this diagram, run the following command from the src subfolder of
the repository:

.. code-block:: bash

   # Install pylint if not already installed
   pip install pylint

   # Generate the class diagram
   pyreverse -o dot -p SlicerCART slicerCART.py
   pyreverse -o dot -p Scripts scripts/*.py
   pyreverse -o dot -p Utils utils/*.py

   python combine_dot_files.py classes_Scripts.dot classes_SlicerCART.dot classes_Utils.dot

   # Generate both PNG and SVG versions
   dot -Tpng classes_SlicerCART.dot -o ../docs/_static/images/class_diagram.png
   dot -Tsvg classes_SlicerCART.dot -o ../docs/_static/images/class_diagram.svg

This will create class diagrams in the `docs/_static/images` directory.

.. raw:: html

   <div style="position: relative; width: 100%; height: 800px; overflow: hidden; border: 1px solid #ccc;">
     <object id="svgObject" data="_static/images/class_diagram.svg" type="image/svg+xml"
             style="width: 100%; height: 100%;">
       <img src="_static/images/class_diagram.png" alt="Class Diagram" style="width: 100%;">
     </object>
   </div>

   <script>
     document.addEventListener('DOMContentLoaded', function () {
       const obj = document.getElementById('svgObject');

       obj.addEventListener('load', function () {
         const svgDoc = obj.contentDocument;
         const svg = svgDoc.querySelector('svg');
         if (!svg) return;

         // Ensure SVG has a viewBox, necessary for proper zooming/panning
         if (!svg.getAttribute('viewBox')) {
           const width = svg.getAttribute('width') || 1000;
           const height = svg.getAttribute('height') || 1000;
           svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
         }

         // Find or create the transformable group
         let viewport = svg.querySelector('#viewport');
         if (!viewport) {
           viewport = document.createElementNS('http://www.w3.org/2000/svg', 'g');
           viewport.setAttribute('id', 'viewport');
           while (svg.firstChild) {
             viewport.appendChild(svg.firstChild);
           }
           svg.appendChild(viewport);
         }

         let scale = 1;
         let offsetX = 0;
         let offsetY = 0;
         let isDragging = false;
         let startX, startY;

         function updateTransform() {
           viewport.setAttribute('transform', `translate(${offsetX} ${offsetY}) scale(${scale})`);
         }

         svg.addEventListener('wheel', function (e) {
           e.preventDefault();
           const factor = e.deltaY > 0 ? 0.9 : 1.1;
           const mouseX = e.clientX;
           const mouseY = e.clientY;

           scale *= factor;
           scale = Math.min(Math.max(0.1, scale), 10);

           updateTransform();
         });

         svg.addEventListener('mousedown', function (e) {
           isDragging = true;
           startX = e.clientX;
           startY = e.clientY;
         });

         svg.addEventListener('mousemove', function (e) {
           if (isDragging) {
             offsetX += (e.clientX - startX) / scale;
             offsetY += (e.clientY - startY) / scale;
             startX = e.clientX;
             startY = e.clientY;
             updateTransform();
           }
         });

         svg.addEventListener('mouseup', () => isDragging = false);
         svg.addEventListener('mouseleave', () => isDragging = false);

         updateTransform();
       });
     });
   </script>



.. note::
   You can interact with the diagram above:
   
   * Use the mouse wheel to zoom in and out
   * Click and drag to pan around the diagram
   * If the interactive version doesn't load, a static PNG version will be shown instead

This documentation was last updated on |today|.