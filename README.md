# doc-cov 

doc-cov is a tool for measuring docstring coverage of Python project.

- Python versions >= 3.6 


## Quick start

1. Install doc-cov from pip.
2. Use `doccov PROJECT_PATH`

```
$ doccov tests/sample_project
function     3 /   5 60.00%
```

## Options
### Target object
doc-cov can measure docstring coverage of functions, classes and modules.

#### functions (default, `-f`) 

```
$ doccov tests/sample_project -f
function     3 /   5 60.00%

```

#### classes `-c`

```
$ doccov tests/sample_project -c
class        2 /   2 100.00%

```

#### modules `-m`

```
$ doccov tests/sample_project -m
module       3 /   7 42.86%

```

### Output 

#### str (default, `--output str`)

```
$ doccov tests/sample_project -fmc --output str
class        2 /   2 100.00%
module       3 /   7 42.86%
function     3 /   5 60.00%
```

#### csv `--output csv`

```
$ doccov tests/sample_project -fmc --output csv
coverage,class,2,2,100.00%
coverage,module,3,7,42.86%
coverage,function,3,5,60.00%
```

### Target 
#### Print coverage of whole (default)

```
$ doccov tests/sample_project
function     3 /   5 60.00%

```  
#### Print all coverage of modules `--all`

```
$ doccov tests/sample_project --all
=============================
module_fulldoc
-----------------------------
function     1 /   1 100.00%
=============================
package_A
-----------------------------
function     0 /   0 -
=============================
package_A.module_fulldoc
-----------------------------
function     1 /   1 100.00%
=============================
package_B
-----------------------------
function     0 /   0 -
=============================
package_B.module_shortdoc
-----------------------------
function     1 /   1 100.00%
=============================
package_B.package_B_1
-----------------------------
function     0 /   0 -
=============================
package_B.package_B_1.module_nodoc
-----------------------------
function     0 /   2 0.00%
=============================
coverage
-----------------------------
function     3 /   5 60.00%
```

## Report to pull request

Add comment to *github* pull request.

```
$ doccov <project> -fmc --output csv > doccov.csv
$ GITHUB_TOKEN=XXXXX doccov-report doccov.csv
```

**CircleCi**  
Add pull request comment using circle-ci environment.

**Other**  
Required following environment
- PROJECT_USERNAME
- PROJECT_REPONAME
- PR_NUMBER
 