join.py
=======

A simple command line tool written in Python to perform joins on text files.

### Examples

File1
```
1 Matt Calder
2 John Somebody
3 Mark Dudeguy
```

File2
```
1,555-555-5555,Foo
2,666-666-6666,Bar
3,777-777-7777,Baz
```

```
join.py ./File1 ./File2 -c2 ","
```
produces the output

```

```


### ToDo
- [ ] ignore comments
