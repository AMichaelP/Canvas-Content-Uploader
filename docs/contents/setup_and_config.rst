Setup and Configuration
***********************

Installation
------------
#. Install Python 3 (https://python.org).
#. Install `canvasapi`_:

.. _canvasapi: https://github.com/ucfopen/canvasapi

.. code::

   pip install canvasapi

3. Clone the project or download it as a ZIP and extract the contents.

.. code::

   git clone https://github.com/AMichaelP/canvas_content_uploader.git


Configuration
-------------
Edit **config.ini**.

The only line you are required to change is *canvas_url =*, which will need to be set to the target Canvas site.

For example:

.. code::

    canvas_url = https://example.beta.instructure.com/

Other customizations that can be set in this file include:
 * The icon (which is the Tcl feather icon by default)
 * The window title (which defaults to "Canvas Content Uploader")
