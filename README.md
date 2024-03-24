# sequencer
program for generating sequences by counting mathematical objects.

# Usage
Download the project and navigate to the folder in a terminal window.

Run the program with the python3 interpreter like

`python3 SequencerCLI.py ARGS`

where you can set ARGS in the following ways to specify what data to generate.

## Required Arguments

### Commands `-c | --command COMMAND`
The command you choose determines what mathematical objects the program will generate.
Each object type will have it's own parameters to further specify the objects to generate.

`COMMAND = command_name(/parameter_name:parameter_value)`

Current options:
* `catalan` - Catalan words.
    * `n` (required) - length of the word.
    * Ex) Catalan words of length 5 - `catalan/n:5`
* `fubini` - Fubini rankings.
    * `n` (required) - number of positions.
    * `k` - allow up to a k-way tie.
    * `t` - max number of ties.
    * Ex) Fubini ranking of 5 positions, and up to 3 way tie - `fubini/n:5/k:3`
* `parking_func` - Parking functions.
    * `n` (required) - number of cars/spots.
    * `unit` - if true, only allows cars to have maximum 1 displacement.
    * `r` - first r preferences are distinct if set.
    * Ex) unit parking functions with 7 cars - `parking_func/n:7/unit:true`
* `stirling` - Stirling permutations.
    * `n` (required) - maximum value for the permutation.
    * `k` - multiplicity of each number in the permutation (default is 2).
    * Ex) Stirling perms of order 7 with multiplicity 3 - `stirling/n:7/k:3`
* `type_b` - Type B set partitions.
    * `n` (required) - maximum value of the set to partition {-n,...,0,...,n}.
    * Ex) Type B set partitions of [-4,4] - `type_b/n:4`

### API `-a | -api API`

The API you choose determines the type of query you will be running.

`API = api_name(/parameter_name:parameter_value)`

* `point` - A point query returns size of the individual set specified by the command parameters.
    * `p` - If true, prints out the set of generated objects.
    * Example: `python3 SequencerCLI.py -a point -c fubini/n:5/t:2`
    * Output: `|FubiniRankings(n:5|t:2)| = 541`
* `range` - A range query takes in a dimension list of parameters and computed statistics and produces counts grouped by those dimensions.
    * `dimensions` (required) - a comma separated list of dimensions to group over. Format for each dimension is `dimension_name-(p|c)`
        * `dimension_name-p` means that the dimension is a parameter to the command. We use the command's given parameter setting as the maximum value, and iterate from the parameter type's minimum value to that maxmimum.
        * `dimension_name-c` means that the dimension is a calculated statistic. See (TODO: make section about calculated dimensions) to see all available calculated stats.
    * `p` - If true, prints out the set of generated objects, grouped by the parameter dimensions, with calculated stats printed per element.
    * `out` - How to output the generated information.
        * `oeis` (default for dim = 1) - Space separated list of values fit for lookup on the OEIS website.
            * Example: `python3 SequencerCLI.py -a range/dimensions:n-p -c parking_func/n:4`
            * Output: `n: 1 1 3 16 125 1296 16807`
        * `ascii` (default for dim > 2) - formatted ascii table(s) where the first dimension is used for row values and the second dimension is used for column values. If there are more than two dimensions, then a table for each combination of the dimensions > 2 is printed.
            * Example: `python3 SequencerCLI.py -a range/dimensions:n-p,r-p -c parking_func/n:7/r:7`
            * Output:
                ```
                -----------------------------------------------------------------------------
                | n \ r |      0 |      1 |      2 |      3 |      4 |     5 |     6 |    7 |
                |---------------------------------------------------------------------------|
                |     0 |      1 |      1 |      1 |      1 |      1 |     1 |     1 |    1 |
                |---------------------------------------------------------------------------|
                |     1 |      1 |      1 |      1 |      1 |      1 |     1 |     1 |    1 |
                |---------------------------------------------------------------------------|
                |     2 |      3 |      3 |      2 |      2 |      2 |     2 |     2 |    2 |
                |---------------------------------------------------------------------------|
                |     3 |     16 |     16 |     12 |      6 |      6 |     6 |     6 |    6 |
                |---------------------------------------------------------------------------|
                |     4 |    125 |    125 |    100 |     60 |     24 |    24 |    24 |   24 |
                |---------------------------------------------------------------------------|
                |     5 |   1296 |   1296 |   1080 |    720 |    360 |   120 |   120 |  120 |
                |---------------------------------------------------------------------------|
                |     6 |  16807 |  16807 |  14406 |  10290 |   5880 |  2520 |   720 |  720 |
                |---------------------------------------------------------------------------|
                |     7 | 262144 | 262144 | 229376 | 172032 | 107520 | 53760 | 20160 | 5040 |
                -----------------------------------------------------------------------------
                ```
            * Example: `python3 SequencerCLI.py -a range/dimensions:n-p,r-p,mult_g_1-c,unit-p -c parking_func/n:4/r:4/unit:true`
            * Output:
                ```
                Print Table for (unit=0;mult_g_1=0):
                ----------------------------------
                | n \ r |  0 |  1 |  2 |  3 |  4 |
                |--------------------------------|
                |     0 |  1 |  1 |  1 |  1 |  1 |
                |--------------------------------|
                |     1 |  1 |  1 |  1 |  1 |  1 |
                |--------------------------------|
                |     2 |  2 |  2 |  2 |  2 |  2 |
                |--------------------------------|
                |     3 |  6 |  6 |  6 |  6 |  6 |
                |--------------------------------|
                |     4 | 24 | 24 | 24 | 24 | 24 |
                ----------------------------------
                Print Table for (unit=0;mult_g_1=1):
                -----------------------------
                | n \ r |  0 |  1 |  2 |  3 |
                |---------------------------|
                |     2 |  1 |  1 |    |    |
                |---------------------------|
                |     3 | 10 | 10 |  6 |    |
                |---------------------------|
                |     4 | 89 | 89 | 68 | 36 |
                -----------------------------
                Print Table for (unit=0;mult_g_1=2):
                -----------------------
                | n \ r |  0 |  1 | 2 |
                |---------------------|
                |     4 | 12 | 12 | 8 |
                -----------------------
                Print Table for (unit=1;mult_g_1=0):
                ----------------------------------
                | n \ r |  0 |  1 |  2 |  3 |  4 |
                |--------------------------------|
                |     0 |  1 |  1 |  1 |  1 |  1 |
                |--------------------------------|
                |     1 |  1 |  1 |  1 |  1 |  1 |
                |--------------------------------|
                |     2 |  2 |  2 |  2 |  2 |  2 |
                |--------------------------------|
                |     3 |  6 |  6 |  6 |  6 |  6 |
                |--------------------------------|
                |     4 | 24 | 24 | 24 | 24 | 24 |
                ----------------------------------
                Print Table for (unit=1;mult_g_1=1):
                -----------------------------
                | n \ r |  0 |  1 |  2 |  3 |
                |---------------------------|
                |     2 |  1 |  1 |    |    |
                |---------------------------|
                |     3 |  7 |  7 |  4 |    |
                |---------------------------|
                |     4 | 45 | 45 | 34 | 18 |
                -----------------------------
                Print Table for (unit=1;mult_g_1=2):
                ---------------------
                | n \ r | 0 | 1 | 2 |
                |-------------------|
                |     4 | 6 | 6 | 4 |
                ---------------------
                ```

## Optional Arguments

### Restrictions `-r | --restrictions RESTRICTIONS`

`RESTRICTION = restriction_name(/parameter_name:parameter_value*)`

`RESTRICTIONS = RESTRICTION(//RESTRICTION*)`

Essentially you give a restriction and its parameters as usual, and you can pass in more by delimiting with '//'. Here are the currently available restrictions.

* `flat` - Omits words that are not flat. A word is flat if it has weakly increasing runs. A word's runs form the maximal weakly increasing subsequence decomposition of the word.
* `peaks` - Omits words that do not have peaks (> than both neighbors) at the given index.
    * `peaks` - The '1-indexed' set of peaks to check against.
* Example: `python3 SequencerCLI.py -a range/dimensions:mult_g_1-c/p:true -c parking_func/n:4/unit:true -r flat//peaks/peaks:3`
* Output: 
    ```
    Elements:
            [1, 1, 4, 2] (mult_g_1=1)
            [1, 1, 4, 3] (mult_g_1=1)
            [1, 2, 4, 2] (mult_g_1=1)
            [1, 2, 4, 3] (mult_g_1=0)
            [1, 3, 4, 1] (mult_g_1=1)
            [1, 3, 4, 2] (mult_g_1=0)
    mult_g_1: 2 4
    ```