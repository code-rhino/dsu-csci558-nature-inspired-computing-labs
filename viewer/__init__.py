"""viewer: everything 3D. No lab logic lives here.

    python3 -m viewer        start the server and open the viewer
    python3 -m viewer.demo   send a demo trace to check it works
    python3 -m viewer.show   replay a saved trace (or list a folder of them)

    viewer/index.html        the three.js page
    viewer/trace.py          Trace: how a lab sends a run to the page
    viewer/TRACE_FORMAT.md   the JSON format, if you want to write traces another way
"""
