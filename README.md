join.py
=======

A simple command line tool written in Python to perform joins on text files.
Email comments and suggestions to calderm at usc.edu.

### Examples

file1
```
1 Matt Calder
2 John Somebody
3 Mark Dudeguy
```

file2
```
1,555-555-5555,Foo,Matt
2,666-666-6666,Bar,John
3,777-777-7777,Baz,Mark
```

####Specify Delimiters

file1 and file2 have different delimiters. In join.py, 'space' is the default delimiter so we have specify ',' for file2.
```
$join.py file1 file2 -d2 ","
```
produces the output

```
1 Matt Calder 1,555-555-5555,Foo,Matt
2 John Somebody 2,666-666-6666,Bar,John
3 Mark Dudeguy 3,777-777-7777,Baz,Mark
```

####Different Columns

The default join column is 1 but we can join on different columns. The command below joins on the first name.

```
$join.py file1 file2 -c1 2 -c2 4 -d2 ","
```
produces the output

```
1 Matt Calder 1,555-555-5555,Foo,Matt
2 John Somebody 2,666-666-6666,Bar,John
3 Mark Dudeguy 3,777-777-7777,Baz,Mark
```

####Nicer Output

If we are joining files with different delimiters then we can get nicer output by specifying an output delimiter. We also eliminate the duplicate column1 that we joined on using the "-r" flag.

```
$join.py file2 file2 -d2 "," -o "|" -r
```
produces

```
1|Matt|Calder|555-555-5555|Foo|Matt
2|John|Somebody|666-666-6666|Bar|John
3|Mark|Dudeguy|777-777-7777|Baz|Mark
```

####All Options
```
$join.py -h
```

```
usage: join.py [-h] [-c1 COLUMN1] [-c2 COLUMN2] [-d1 DELIMITER1]
               [-d2 DELIMITER2] [-o OUTPUT_DELIMITER] [-s JOIN_SEPARATOR] [-f]
               [-r] [-v]
               file1 file2

Join two files.

positional arguments:
  file1                 Path to file 1
  file2                 Path to file 2

optional arguments:
  -h, --help            show this help message and exit
  -c1 COLUMN1, --column1 COLUMN1
                        Column number for file 1 (default: 1)
  -c2 COLUMN2, --column2 COLUMN2
                        Column number for file 2 (default: 1)
  -d1 DELIMITER1, --delimiter1 DELIMITER1
                        Delimiter for file 1 (default: " ")
  -d2 DELIMITER2, --delimiter2 DELIMITER2
                        Delimiter for file 2 (default: " ")
  -o OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Output delimiter. Default is to leave delimiters for
                        each file in place.
  -s JOIN_SEPARATOR, --join-separator JOIN_SEPARATOR
                        Separator between joined lines. This will be set to
                        --output-delimiter if not overridden. (default: " ")
  -f, --filter-mode     Only output matches from file1 (default: off)
  -r, --remove-duplicate
                        Only output one of the matching columns (default: off)
  -v, --version         show program's version number and exit
```

### ToDo
- [ ] ignore commented out lines
