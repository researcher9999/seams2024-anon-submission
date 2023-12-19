# Coordinated online reinforcement learning for self-adaptive systems -- Submitted @SEAMS2024

Tested against Java 17. The file run_experiments.sh exports the
`JAVA_HOME` variable.  May require adjustment.


Requires a Python 3.12 virtual environment called `venv_312`. Source the
venv and install the required Python packages using:

```
pip install -r requirements.txt
```
First, generate the Python classes from protobuf sources, using:

```
bash compile_proto_python.sh
```

Run the experiments using:

```
bash run_experiments.sh
```

The experiments will take a while. The results are stored in
`results_#motes_good.sqlite3`, where # is the number of motes in that
experiment.

Plot the results for one `*.sqlite3` using (Figure 4 in the paper):

```
python plot_results.py [file_path]
```

Plot the scalability results (Figure 5 in the paper) using:

```
python plot_result_scalability.py
```

Output the data from Table 1 for one *.sqlite3 using:

```
python plot_table.py [file_path]
```

Note: The data used for the Experimental Evaluation part of the paper
is in `seams2024_results.zip`. To download them use:

```
git lfs install
git lfs pull
```

# DingNet
The source code for the DingNet simulator.

Current up to date version: **1.2.1.**


## Building the simulator

To build the simulator, simply run the command `mvn compile`. The generated source are placed in the `target` folder.
The simulator can then be run with the following command: `mvn exec:java`.

Alternatively, run the command `mvn package`. This will generate a jar file under the target directory: `DingNet-{version}-jar-with-dependencies.jar`.

Similarly to the previously listed commands, `mvn test` runs the tests for the project.

## Running the simulator

Either run the jar file generated from the previous step, or use the maven exec plugin.
<!-- A jar file is exported to the folder DingNetExe which also contains the correct file structure. Run the jar file to run the simulator.
The simulator can also be started from the main method in the MainGUI class. -->



## Libraries

DingNet uses the following libraries:
- AnnotationsDoclets (included in the lib folder, since it is not available online (yet))
- jfreechart-1.5.0
- jxmapviewer2-2.4


## Future goals

- [ ] Refactor Inputprofile
- [ ] Refactor QualityOfService
- [ ] Realistic data generation
- [ ] Rewrite transmission logic (moveTo, transmission power, ...)
- [ ] \(Not important) Allow creation of circular routes for motes
