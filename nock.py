"""
A noun is an atom or a cell.
An atom is any natural number.
A cell is any ordered pair of nouns.

1  ::    [a b c]           [a [b c]]
2  ::    nock(a)           *a
3  ::
4  ::    ?[a b]            0
5  ::    ?a                1
6  ::    +a                1 + a
7  ::    =[a a]            0
8  ::    =[a b]            1
9  ::
10 ::    /[1 a]            a
11 ::    /[2 a b]          a
12 ::    /[3 a b]          b
13 ::    /[(a + a) b]      /[2 /[a b]]
14 ::    /[(a + a + 1) b]  /[3 /[a b]]
15 ::
16 ::    *[a [b c] d]      [*[a b c] *[a d]]
17 ::
18 ::    *[a 0 b]          /[b a]
19 ::    *[a 1 b]          b
20 ::    *[a 2 b c]        *[*[a b] *[a c]]
21 ::    *[a 3 b]          ?*[a b]
22 ::    *[a 4 b]          +*[a b]
23 ::    *[a 5 b]          =*[a b]
24 ::
25 ::    *[a 6 b c d]      *[a 2 [0 1] 2 [1 c d] [1 0] 2 [1 2 3] [1 0] 4 4 b]
26 ::    *[a 7 b c]        *[a 2 b 1 c]
27 ::    *[a 8 b c]        *[a 7 [[7 [0 1] b] 0 1] c]
28 ::    *[a 9 b c]        *[a 7 c [2 [0 1] [0 b]]]
29 ::    *[a 10 b c]       *[a c]
30 ::    *[a 10 [b c] d]   *[a 8 c 7 [0 2] d]
31 ::
32 ::    +[a b]            +[a b]
33 ::    =a                =a
34 ::    /a                /a
35 ::    *a                *a

"""

DEBUG = True

def debug(name, args, out):
    if DEBUG:
        print('%s: %s -> %s' % (name, args, out))
    return out


def fmt(lst):
    if type(lst) == tuple:
        if len(lst) >= 2:
            return debug('fmt', lst, (fmt(lst[0]), fmt(lst[1:])))
        return debug('fmt', lst, fmt(lst[0]))
    return lst

assert fmt((1, 2, 3, 4)) == (1, (2, (3, 4)))
assert fmt((1, 2)) == (1, 2)


def nock(noun):
    return debug('nock', noun, star(noun))


def isatom(noun):
    return debug('isatom', noun, isinstance(noun, int) and 1 or 0)

assert isatom(1) == 1
assert isatom((1, 2)) == 0


def addone(atom):
    assert isatom(atom) == 1
    return debug('addone', atom, atom + 1)


assert addone(1) == 2
assert addone(1336) == 1337


def equal(cell):
    cell = fmt(cell)
    assert len(cell) == 2
    return debug('equal', cell, (cell[0] != cell[1] and 1 or 0))

assert equal((1, 1)) == 0
assert equal((1, 2)) == 1


def slash(cell):
    cell = fmt(cell)
    assert len(cell) == 2
    assert isinstance(cell[0], int)
    if cell[0] == 1:
        res = cell[1]
    elif cell[0] == 2:
        res = cell[1][0]
    elif cell[0] == 3:
        res = cell[1][1]
    elif cell[0] % 2 == 0:
        res = slash((2, slash((int(cell[0]/2), cell[1]))))
    else:
        res = slash((3, slash((int((cell[0]-1)/2), cell[1]))))
    return debug('slash', cell, res)

assert slash((1, 3)) == 3
assert slash((2, 3, 4)) == 3
assert slash((3, 3, 4)) == 4
assert slash((2, (4, 5), (6, 14, 15))) == (4, 5)
assert slash((3, ((4, 5), (6, 14, 15)))) == (6, (14, 15))
assert slash((7, ((4, 5), (6, 14, 15)))) == (14, 15)


def star(cell):
    cell = fmt(cell)
    assert isatom(cell) == 0
    assert len(cell) > 1
    assert len(cell[1]) > 1
    arg = cell[1][0]
    if not isatom(arg):
        res = (star((cell[0], arg)), star((cell[0], cell[1][1])))
    elif arg == 0:
        res = slash((cell[1][1], cell[0]))
    elif arg == 1:
        res = cell[1][1]
    elif arg == 2:
        assert isatom(cell[1][1]) == 0
        res = star((star((cell[0], cell[1][1][0])), star((cell[0], cell[1][1][1]))))
    elif arg == 3:
        res = isatom(star((cell[0], cell[1][1])))
    elif arg == 4:
        res = addone(star((cell[0], cell[1][1])))
    elif arg == 5:
        res = equal(star((cell[0], cell[1][1])))
    elif arg == 6:
        assert isatom(cell[1][1][1]) == 0
        a = cell[0]
        b = cell[1][1][0]
        c = cell[1][1][1][0]
        d = cell[1][1][1][1]
        res = star((a, 2, (0, 1), 2, (1, c, d), (1, 0), 2, (1, 2, 3), (1, 0), 4, 4, b))
    elif arg == 7:
        assert isatom(cell[1][1]) == 0
        res = star((cell[0], 2, cell[1][1][0], 1, cell[1][1][1]))
    elif arg == 8:
        assert isatom(cell[1][1]) == 0
        res = star((cell[0], 7, ((7, (0, 1), cell[1][1][0]), 0, 1), cell[1][1][1]))
    elif arg == 9:
        assert isatom(cell[1][1]) == 0
        res = star((cell[0], 7, cell[1][1][1], (2, (0, 1), (0, cell[1][1][0]))))
    elif arg == 10:
        assert isatom(cell[1][1]) == 0
        a = cell[0]
        b = cell[1][0]
        c = cell[1][1][0]
        if isatom(b):
            res = star((a, c))
        else:
            res = star((a, 8, b[1], 7, (0, 2), c))
    else:
        print("error, could not find anything for argument", arg)
    return debug('star', cell, res)

assert star((1337, (1, 42), (1, 23))) == (42, 23)
assert star((1, 0, 1)) == slash((1, 1))
assert star((((4, 5), (6, 14, 15)), 0, 7)) == slash((7, ((4, 5), (6, 14, 15))))
assert star((1337, 1, 23)) == 23
assert star((1337, 2, (1, 23), (1, (1, 42)))) == 42
assert star((1337, (2, (1, 42), (1, 1, 153, 218)))) == (153, 218)
assert star((1337, 3, (1, 23))) == 1
assert star((1337, 3, (1, (23, 42)))) == 0
assert star((1337, 4, (1, 23))) == 24
assert star((42, (4, 0, 1))) == 43
assert star((1337, 5, (1, (1, 1)))) == 0
assert star((1337, 5, (1, (1, 2)))) == 1
assert star((42, (6, (1, 0), (4, 0, 1), (1, 233)))) == 43
assert star((42, (6, (1, 1), (4, 0, 1), (1, 233)))) == 233
assert star((42, (7, (4, 0, 1), (7, (4, 0, 1), (4, 0, 1))))) == 45
assert star((42, (8, (4, 0, 1), (0, 1)))) == (43, 42)
assert star((42, (8, (4, 0, 1), (4, 0, 3)))) == 43
assert star((42, (8, (1, 0), 8, (1, 6, (5, (0, 7), 4, 0, 6), (0, 6), 9, 2, (0, 2), (4, 0, 6), 0, 7), 9, 2, 0, 1))) == 41

if __name__ == "__main__":
    pass
