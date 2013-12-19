join.py
=======

A simple command line tool written in Python to perform joins on text files.

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

### ToDo
- [ ] ignore commented out lines
