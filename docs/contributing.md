# Contributing

Contributions are welcome.  The docker workspace is setup for development out of the box.

## Debugging
Once a workspace container is up, you can run a script using debugpy in your container and then connect with VSCode from the outside with its robust debugging tools.

Start debupy in container listening on port, waits for vscode before executing the Python script.

Running an example:
```
    cd examples/survey
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client ../../scripts/gen_heatmap config.json
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client simple_sap_map.py
```

Running a test:
```
    cd tests
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client test_simple_sap_map.py
```

Once debugpy is started, over in VSCode, set a breakpoint, Click `Debug` in the left menu, then click `Python Attach`.  It will attach to the debugpy port and then execute the script.
