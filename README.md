# csv-merge

Command line tools to merge the most recent version of several CSV files
containing data on the same users, into one up-to-date CSV file, according
to a YAML configuration file.

```
usage: csv-merge [-h] [-y Y] [-p P] [-o O] [--verbose]

Merge the most recent version of several CSV files containing data on the same
users, into one up-to-date CSV file, according to a YAML configuration file.

optional arguments:
  -h, --help  show this help message and exit
  -y Y        name of the YAML job description.
  -p P        name of the YAML patch file (optional).
  -o O        output file name (optional, default /dev/stdout).
  --verbose   display informational messages (info+debug output).
```

## Example

Consider the following set of files:

- `data/sourceA.csv`:
  ```csv
  Username,email,total
  jsmith,joe@smith.com,13
  dkapoor,dk@gmail.com,17
  azhang,azhang@yahoo.net,19
  ```
- `data/sourceB.csv`:
  ```csv
  User,total
  dkapoor,32
  azhang,39
  ```
- `data/sourceC.csv`:
  ```csv
  Username,total
  jsmith,10
  azhang,11
  ```
- `data/sourceC_v2.csv`:
  ```csv
  Username,correct
  azhang,12
  jsmith,9
  ```
- `summary.yaml`:
  ```yaml
  defaults:
    path: "./data/"
    username: "Username"
    value: "total"
  output:
    username: "NetID"
  sources:
    "*A*.csv":
      caption: "PartA"
    "*B*.csv":
      caption: "PartB"
      username: "User"
    "*C*.csv":
      caption: "PartC"
      value: "correct"
  ```
  These files can be combined by calling `csv-merge`:

```
csv-merge -y summary.yaml -o output.csv
```

This will output a file, `summary.csv`:

```csv
NetID,PartA,PartB,PartC
jsmith,13,,9
dkapoor,17,32,
azhang,19,39,12
```
