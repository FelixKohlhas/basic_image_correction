## Creating the correct Regular Expression (RegEx)

The regex should match properties that you want to group by into "named groups". In Python you can create these named groups by using the format `(?P<name>...)`, such as `(?P<Row>[A-H])` or `(?P<Column>[0-9]*)`. More information can be found in the [Python documentation on Regular Expressions](https://docs.python.org/3/howto/regex.html).

## Example

### Filenames
```
B - 02(fld 01 wv Cy5 - Cy5 wix 4).tif
B - 02(fld 01 wv Cy5 - Cy5 wix 8).tif
B - 02(fld 01 wv DAPI - DAPI wix 1).tif
B - 02(fld 01 wv DAPI - DAPI wix 5).tif
B - 02(fld 01 wv FITC - FITC2 wix 2).tif
B - 02(fld 01 wv FITC - FITC2 wix 6).tif
B - 02(fld 01 wv TexasRed - TexasRed wix 3).tif
B - 02(fld 01 wv TexasRed - TexasRed wix 7).tif
```

### Regex
```
^(?P<Row>[A-P]) - (?P<Column>[0-9]*)\(fld (?P<Field>[0-9]*) wv (?P<Channel>[^ ]*) .* wix (?P<Wix>[0-9]*)\).tif
```

### Result
```
Match 1
    Column	02
    Field	01
    Row	B
    Channel	Cy5
    Wix	4
Match 2
    Column	02
    Field	01
    Row	B
    Channel	Cy5
    Wix	8
Match 3
    Column	02
    Field	01
    Row	B
    Channel	DAPI
    Wix	1
...
```

You can test this RegEx and play around with it on [pythex.org](https://pythex.org/?regex=%5E(%3FP%3CRow%3E%5BA-P%5D)%20-%20(%3FP%3CColumn%3E%5B0-9%5D*)%5C(fld%20(%3FP%3CField%3E%5B0-9%5D*)%20wv%20(%3FP%3CChannel%3E%5B%5E%20%5D*)%20.*%20wix%20(%3FP%3CWix%3E%5B0-9%5D*)%5C).tif&test_string=B%20-%2002(fld%2001%20wv%20Cy5%20-%20Cy5%20wix%204).tif%0AB%20-%2002(fld%2001%20wv%20Cy5%20-%20Cy5%20wix%208).tif%0AB%20-%2002(fld%2001%20wv%20DAPI%20-%20DAPI%20wix%201).tif%0AB%20-%2002(fld%2001%20wv%20DAPI%20-%20DAPI%20wix%205).tif%0AB%20-%2002(fld%2001%20wv%20FITC%20-%20FITC2%20wix%202).tif%0AB%20-%2002(fld%2001%20wv%20FITC%20-%20FITC2%20wix%206).tif%0AB%20-%2002(fld%2001%20wv%20TexasRed%20-%20TexasRed%20wix%203).tif%0AB%20-%2002(fld%2001%20wv%20TexasRed%20-%20TexasRed%20wix%207).tif&ignorecase=0&multiline=1&dotall=0&verbose=0)