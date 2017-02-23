# -*- coding: utf-8 -*-
import unittest
import pickle
import cPickle
import StringIO
import cStringIO
import pickletools
import copy_reg
import sys

from test import test_support as support
from test.test_support import TestFailed, verbose, have_unicode, TESTFN
try:
    from test.test_support import _2G, _1M, precisionbigmemtest
except ImportError:
    # this import might fail when run on older Python versions by test_xpickle
    _2G = _1M = 0
    def precisionbigmemtest(*args, **kwargs):
        return lambda self: None

# Tests that try a number of pickle protocols should have a
#     for proto in protocols:
# kind of outer loop.
assert pickle.HIGHEST_PROTOCOL == cPickle.HIGHEST_PROTOCOL == 2
protocols = range(pickle.HIGHEST_PROTOCOL + 1)

# Copy of test.test_support.run_with_locale. This is needed to support Python
# 2.4, which didn't include it. This is all to support test_xpickle, which
# bounces pickled objects through older Python versions to test backwards
# compatibility.
def run_with_locale(catstr, *locales):
    def decorator(func):
        def inner(*args, **kwds):
            try:
                import locale
                category = getattr(locale, catstr)
                orig_locale = locale.setlocale(category)
            except AttributeError:
                # if the test author gives us an invalid category string
                raise
            except:
                # cannot retrieve original locale, so do nothing
                locale = orig_locale = None
            else:
                for loc in locales:
                    try:
                        locale.setlocale(category, loc)
                        break
                    except:
                        pass

            # now run the function, resetting the locale on exceptions
            try:
                return func(*args, **kwds)
            finally:
                if locale and orig_locale:
                    locale.setlocale(category, orig_locale)
        inner.func_name = func.func_name
        inner.__doc__ = func.__doc__
        return inner
    return decorator

def no_tracing(func):
    """Decorator to temporarily turn off tracing for the duration of a test."""
    if not hasattr(sys, 'gettrace'):
        return func
    else:
        def wrapper(*args, **kwargs):
            original_trace = sys.gettrace()
            try:
                sys.settrace(None)
                return func(*args, **kwargs)
            finally:
                sys.settrace(original_trace)
        wrapper.__name__ = func.__name__
        return wrapper


# Return True if opcode code appears in the pickle, else False.
def opcode_in_pickle(code, pickle):
    for op, dummy, dummy in pickletools.genops(pickle):
        if op.code == code:
            return True
    return False

# Return the number of times opcode code appears in pickle.
def count_opcode(code, pickle):
    n = 0
    for op, dummy, dummy in pickletools.genops(pickle):
        if op.code == code:
            n += 1
    return n

class UnseekableIO(StringIO.StringIO):
    def peek(self, *args):
        raise NotImplementedError

    def seek(self, *args):
        raise NotImplementedError

    def tell(self):
        raise NotImplementedError

# We can't very well test the extension registry without putting known stuff
# in it, but we have to be careful to restore its original state.  Code
# should do this:
#
#     e = ExtensionSaver(extension_code)
#     try:
#         fiddle w/ the extension registry's stuff for extension_code
#     finally:
#         e.restore()

class ExtensionSaver:
    # Remember current registration for code (if any), and remove it (if
    # there is one).
    def __init__(self, code):
        self.code = code
        if code in copy_reg._inverted_registry:
            self.pair = copy_reg._inverted_registry[code]
            copy_reg.remove_extension(self.pair[0], self.pair[1], code)
        else:
            self.pair = None

    # Restore previous registration for code.
    def restore(self):
        code = self.code
        curpair = copy_reg._inverted_registry.get(code)
        if curpair is not None:
            copy_reg.remove_extension(curpair[0], curpair[1], code)
        pair = self.pair
        if pair is not None:
            copy_reg.add_extension(pair[0], pair[1], code)

class C:
    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

class D(C):
    def __init__(self, arg):
        pass

class E(C):
    def __getinitargs__(self):
        return ()

class H(object):
    pass

# Hashable mutable key
class K(object):
    def __init__(self, value):
        self.value = value

    def __reduce__(self):
        # Shouldn't support the recursion itself
        return K, (self.value,)

import __main__
__main__.C = C
C.__module__ = "__main__"
__main__.D = D
D.__module__ = "__main__"
__main__.E = E
E.__module__ = "__main__"
__main__.H = H
H.__module__ = "__main__"
__main__.K = K
K.__module__ = "__main__"

class myint(int):
    def __init__(self, x):
        self.str = str(x)

class initarg(C):

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __getinitargs__(self):
        return self.a, self.b

class metaclass(type):
    pass

class use_metaclass(object):
    __metaclass__ = metaclass

class pickling_metaclass(type):
    def __eq__(self, other):
        return (type(self) == type(other) and
                self.reduce_args == other.reduce_args)

    def __reduce__(self):
        return (create_dynamic_class, self.reduce_args)

    __hash__ = None

def create_dynamic_class(name, bases):
    result = pickling_metaclass(name, bases, dict())
    result.reduce_args = (name, bases)
    return result

# DATA0 .. DATA2 are the pickles we expect under the various protocols, for
# the object returned by create_data().

# break into multiple strings to avoid confusing font-lock-mode
DATA0 = """(lp1
I0
aL1L
aF2
ac__builtin__
complex
p2
""" + \
"""(F3
F0
tRp3
aI1
aI-1
aI255
aI-255
aI-256
aI65535
aI-65535
aI-65536
aI2147483647
aI-2147483647
aI-2147483648
a""" + \
"""(S'abc'
p4
g4
""" + \
"""(i__main__
C
p5
""" + \
"""(dp6
S'foo'
p7
I1
sS'bar'
p8
I2
sbg5
tp9
ag9
aI5
a.
"""

# Disassembly of DATA0.
DATA0_DIS = """\
    0: (    MARK
    1: l        LIST       (MARK at 0)
    2: p    PUT        1
    5: I    INT        0
    8: a    APPEND
    9: L    LONG       1L
   13: a    APPEND
   14: F    FLOAT      2.0
   17: a    APPEND
   18: c    GLOBAL     '__builtin__ complex'
   39: p    PUT        2
   42: (    MARK
   43: F        FLOAT      3.0
   46: F        FLOAT      0.0
   49: t        TUPLE      (MARK at 42)
   50: R    REDUCE
   51: p    PUT        3
   54: a    APPEND
   55: I    INT        1
   58: a    APPEND
   59: I    INT        -1
   63: a    APPEND
   64: I    INT        255
   69: a    APPEND
   70: I    INT        -255
   76: a    APPEND
   77: I    INT        -256
   83: a    APPEND
   84: I    INT        65535
   91: a    APPEND
   92: I    INT        -65535
  100: a    APPEND
  101: I    INT        -65536
  109: a    APPEND
  110: I    INT        2147483647
  122: a    APPEND
  123: I    INT        -2147483647
  136: a    APPEND
  137: I    INT        -2147483648
  150: a    APPEND
  151: (    MARK
  152: S        STRING     'abc'
  159: p        PUT        4
  162: g        GET        4
  165: (        MARK
  166: i            INST       '__main__ C' (MARK at 165)
  178: p        PUT        5
  181: (        MARK
  182: d            DICT       (MARK at 181)
  183: p        PUT        6
  186: S        STRING     'foo'
  193: p        PUT        7
  196: I        INT        1
  199: s        SETITEM
  200: S        STRING     'bar'
  207: p        PUT        8
  210: I        INT        2
  213: s        SETITEM
  214: b        BUILD
  215: g        GET        5
  218: t        TUPLE      (MARK at 151)
  219: p    PUT        9
  222: a    APPEND
  223: g    GET        9
  226: a    APPEND
  227: I    INT        5
  230: a    APPEND
  231: .    STOP
highest protocol among opcodes = 0
"""

DATA1 = (']q\x01(K\x00L1L\nG@\x00\x00\x00\x00\x00\x00\x00'
         'c__builtin__\ncomplex\nq\x02(G@\x08\x00\x00\x00\x00\x00'
         '\x00G\x00\x00\x00\x00\x00\x00\x00\x00tRq\x03K\x01J\xff\xff'
         '\xff\xffK\xffJ\x01\xff\xff\xffJ\x00\xff\xff\xffM\xff\xff'
         'J\x01\x00\xff\xffJ\x00\x00\xff\xffJ\xff\xff\xff\x7fJ\x01\x00'
         '\x00\x80J\x00\x00\x00\x80(U\x03abcq\x04h\x04(c__main__\n'
         'C\nq\x05oq\x06}q\x07(U\x03fooq\x08K\x01U\x03barq\tK\x02ubh'
         '\x06tq\nh\nK\x05e.'
        )

# Disassembly of DATA1.
DATA1_DIS = """\
    0: ]    EMPTY_LIST
    1: q    BINPUT     1
    3: (    MARK
    4: K        BININT1    0
    6: L        LONG       1L
   10: G        BINFLOAT   2.0
   19: c        GLOBAL     '__builtin__ complex'
   40: q        BINPUT     2
   42: (        MARK
   43: G            BINFLOAT   3.0
   52: G            BINFLOAT   0.0
   61: t            TUPLE      (MARK at 42)
   62: R        REDUCE
   63: q        BINPUT     3
   65: K        BININT1    1
   67: J        BININT     -1
   72: K        BININT1    255
   74: J        BININT     -255
   79: J        BININT     -256
   84: M        BININT2    65535
   87: J        BININT     -65535
   92: J        BININT     -65536
   97: J        BININT     2147483647
  102: J        BININT     -2147483647
  107: J        BININT     -2147483648
  112: (        MARK
  113: U            SHORT_BINSTRING 'abc'
  118: q            BINPUT     4
  120: h            BINGET     4
  122: (            MARK
  123: c                GLOBAL     '__main__ C'
  135: q                BINPUT     5
  137: o                OBJ        (MARK at 122)
  138: q            BINPUT     6
  140: }            EMPTY_DICT
  141: q            BINPUT     7
  143: (            MARK
  144: U                SHORT_BINSTRING 'foo'
  149: q                BINPUT     8
  151: K                BININT1    1
  153: U                SHORT_BINSTRING 'bar'
  158: q                BINPUT     9
  160: K                BININT1    2
  162: u                SETITEMS   (MARK at 143)
  163: b            BUILD
  164: h            BINGET     6
  166: t            TUPLE      (MARK at 112)
  167: q        BINPUT     10
  169: h        BINGET     10
  171: K        BININT1    5
  173: e        APPENDS    (MARK at 3)
  174: .    STOP
highest protocol among opcodes = 1
"""

DATA2 = ('\x80\x02]q\x01(K\x00\x8a\x01\x01G@\x00\x00\x00\x00\x00\x00\x00'
         'c__builtin__\ncomplex\nq\x02G@\x08\x00\x00\x00\x00\x00\x00G\x00'
         '\x00\x00\x00\x00\x00\x00\x00\x86Rq\x03K\x01J\xff\xff\xff\xffK'
         '\xffJ\x01\xff\xff\xffJ\x00\xff\xff\xffM\xff\xffJ\x01\x00\xff\xff'
         'J\x00\x00\xff\xffJ\xff\xff\xff\x7fJ\x01\x00\x00\x80J\x00\x00\x00'
         '\x80(U\x03abcq\x04h\x04(c__main__\nC\nq\x05oq\x06}q\x07(U\x03foo'
         'q\x08K\x01U\x03barq\tK\x02ubh\x06tq\nh\nK\x05e.')

# Disassembly of DATA2.
DATA2_DIS = """\
    0: \x80 PROTO      2
    2: ]    EMPTY_LIST
    3: q    BINPUT     1
    5: (    MARK
    6: K        BININT1    0
    8: \x8a     LONG1      1L
   11: G        BINFLOAT   2.0
   20: c        GLOBAL     '__builtin__ complex'
   41: q        BINPUT     2
   43: G        BINFLOAT   3.0
   52: G        BINFLOAT   0.0
   61: \x86     TUPLE2
   62: R        REDUCE
   63: q        BINPUT     3
   65: K        BININT1    1
   67: J        BININT     -1
   72: K        BININT1    255
   74: J        BININT     -255
   79: J        BININT     -256
   84: M        BININT2    65535
   87: J        BININT     -65535
   92: J        BININT     -65536
   97: J        BININT     2147483647
  102: J        BININT     -2147483647
  107: J        BININT     -2147483648
  112: (        MARK
  113: U            SHORT_BINSTRING 'abc'
  118: q            BINPUT     4
  120: h            BINGET     4
  122: (            MARK
  123: c                GLOBAL     '__main__ C'
  135: q                BINPUT     5
  137: o                OBJ        (MARK at 122)
  138: q            BINPUT     6
  140: }            EMPTY_DICT
  141: q            BINPUT     7
  143: (            MARK
  144: U                SHORT_BINSTRING 'foo'
  149: q                BINPUT     8
  151: K                BININT1    1
  153: U                SHORT_BINSTRING 'bar'
  158: q                BINPUT     9
  160: K                BININT1    2
  162: u                SETITEMS   (MARK at 143)
  163: b            BUILD
  164: h            BINGET     6
  166: t            TUPLE      (MARK at 112)
  167: q        BINPUT     10
  169: h        BINGET     10
  171: K        BININT1    5
  173: e        APPENDS    (MARK at 5)
  174: .    STOP
highest protocol among opcodes = 2
"""

def create_data():
    c = C()
    c.foo = 1
    c.bar = 2
    x = [0, 1L, 2.0, 3.0+0j]
    # Append some integer test cases at cPickle.c's internal size
    # cutoffs.
    uint1max = 0xff
    uint2max = 0xffff
    int4max = 0x7fffffff
    x.extend([1, -1,
              uint1max, -uint1max, -uint1max-1,
              uint2max, -uint2max, -uint2max-1,
               int4max,  -int4max,  -int4max-1])
    y = ('abc', 'abc', c, c)
    x.append(y)
    x.append(y)
    x.append(5)
    return x


class AbstractUnpickleTests(unittest.TestCase):
    # Subclass must define self.loads, self.error.

    _testdata = create_data()

    def assert_is_copy(self, obj, objcopy, msg=None):
        """Utility method to verify if two objects are copies of each others.
        """
        if msg is None:
            msg = "{!r} is not a copy of {!r}".format(obj, objcopy)
        self.assertEqual(obj, objcopy, msg=msg)
        self.assertIs(type(obj), type(objcopy), msg=msg)
        if hasattr(obj, '__dict__'):
            self.assertDictEqual(obj.__dict__, objcopy.__dict__, msg=msg)
            self.assertIsNot(obj.__dict__, objcopy.__dict__, msg=msg)
        if hasattr(obj, '__slots__'):
            self.assertListEqual(obj.__slots__, objcopy.__slots__, msg=msg)
            for slot in obj.__slots__:
                self.assertEqual(
                    hasattr(obj, slot), hasattr(objcopy, slot), msg=msg)
                self.assertEqual(getattr(obj, slot, None),
                                 getattr(objcopy, slot, None), msg=msg)

    def check_unpickling_error(self, errors, data):
        try:
            try:
                self.loads(data)
            except:
                if support.verbose > 1:
                    exc_type, exc, tb = sys.exc_info()
                    print '%-32r - %s: %s' % (data, exc_type.__name__, exc)
                raise
        except errors:
            pass
        else:
            try:
                exc_name = errors.__name__
            except AttributeError:
                exc_name = str(errors)
            raise self.failureException('%s not raised' % exc_name)

    def test_load_from_canned_string(self):
        expected = self._testdata
        for canned in DATA0, DATA1, DATA2:
            got = self.loads(canned)
            self.assert_is_copy(expected, got)

    def test_garyp(self):
        self.check_unpickling_error(self.error, 'garyp')

    def test_maxint64(self):
        maxint64 = (1L << 63) - 1
        data = 'I' + str(maxint64) + '\n.'
        got = self.loads(data)
        self.assertEqual(got, maxint64)

        # Try too with a bogus literal.
        data = 'I' + str(maxint64) + 'JUNK\n.'
        self.check_unpickling_error(ValueError, data)

    def test_insecure_strings(self):
        insecure = ["abc", "2 + 2", # not quoted
                    #"'abc' + 'def'", # not a single quoted string
                    "'abc", # quote is not closed
                    "'abc\"", # open quote and close quote don't match
                    "'abc'   ?", # junk after close quote
                    "'\\'", # trailing backslash
                    # issue #17710
                    "'", '"',
                    "' ", '" ',
                    '\'"', '"\'',
                    " ''", ' ""',
                    ' ',
                    # some tests of the quoting rules
                    #"'abc\"\''",
                    #"'\\\\a\'\'\'\\\'\\\\\''",
                    ]
        for s in insecure:
            buf = "S" + s + "\n."
            self.check_unpickling_error(ValueError, buf)

    def test_correctly_quoted_string(self):
        goodpickles = [("S''\n.", ''),
                       ('S""\n.', ''),
                       ('S"\\n"\n.', '\n'),
                       ("S'\\n'\n.", '\n')]
        for p, expected in goodpickles:
            self.assertEqual(self.loads(p), expected)

    def test_load_classic_instance(self):
        # See issue5180.  Test loading 2.x pickles that
        # contain an instance of old style class.
        for X, args in [(C, ()), (D, ('x',)), (E, ())]:
            xname = X.__name__.encode('ascii')
            # Protocol 0 (text mode pickle):
            """
             0: (    MARK
             1: i        INST       '__main__ X' (MARK at 0)
            13: p    PUT        0
            16: (    MARK
            17: d        DICT       (MARK at 16)
            18: p    PUT        1
            21: b    BUILD
            22: .    STOP
            """
            pickle0 = ("(i__main__\n"
                       "X\n"
                       "p0\n"
                       "(dp1\nb.").replace('X', xname)
            self.assert_is_copy(X(*args), self.loads(pickle0))

            # Protocol 1 (binary mode pickle)
            """
             0: (    MARK
             1: c        GLOBAL     '__main__ X'
            13: q        BINPUT     0
            15: o        OBJ        (MARK at 0)
            16: q    BINPUT     1
            18: }    EMPTY_DICT
            19: q    BINPUT     2
            21: b    BUILD
            22: .    STOP
            """
            pickle1 = ('(c__main__\n'
                       'X\n'
                       'q\x00oq\x01}q\x02b.').replace('X', xname)
            self.assert_is_copy(X(*args), self.loads(pickle1))

            # Protocol 2 (pickle2 = '\x80\x02' + pickle1)
            """
             0: \x80 PROTO      2
             2: (    MARK
             3: c        GLOBAL     '__main__ X'
            15: q        BINPUT     0
            17: o        OBJ        (MARK at 2)
            18: q    BINPUT     1
            20: }    EMPTY_DICT
            21: q    BINPUT     2
            23: b    BUILD
            24: .    STOP
            """
            pickle2 = ('\x80\x02(c__main__\n'
                       'X\n'
                       'q\x00oq\x01}q\x02b.').replace('X', xname)
            self.assert_is_copy(X(*args), self.loads(pickle2))

    def test_load_str(self):
        # From Python 2: pickle.dumps('a\x00\xa0', protocol=0)
        self.assertEqual(self.loads("S'a\\x00\\xa0'\n."), 'a\x00\xa0')
        # From Python 2: pickle.dumps('a\x00\xa0', protocol=1)
        self.assertEqual(self.loads('U\x03a\x00\xa0.'), 'a\x00\xa0')
        # From Python 2: pickle.dumps('a\x00\xa0', protocol=2)
        self.assertEqual(self.loads('\x80\x02U\x03a\x00\xa0.'), 'a\x00\xa0')

    def test_load_unicode(self):
        # From Python 2: pickle.dumps(u'π', protocol=0)
        self.assertEqual(self.loads('V\\u03c0\n.'), u'π')
        # From Python 2: pickle.dumps(u'π', protocol=1)
        self.assertEqual(self.loads('X\x02\x00\x00\x00\xcf\x80.'), u'π')
        # From Python 2: pickle.dumps(u'π', protocol=2)
        self.assertEqual(self.loads('\x80\x02X\x02\x00\x00\x00\xcf\x80.'), u'π')

    def test_constants(self):
        self.assertIsNone(self.loads('N.'))
        self.assertIs(self.loads('\x88.'), True)
        self.assertIs(self.loads('\x89.'), False)
        self.assertIs(self.loads('I01\n.'), True)
        self.assertIs(self.loads('I00\n.'), False)

    def test_misc_get(self):
        self.check_unpickling_error(self.error, 'g0\np0\n')
        self.check_unpickling_error(self.error, 'h\x00q\x00')

    def test_get(self):
        pickled = '((lp100000\ng100000\nt.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    def test_binget(self):
        pickled = '(]q\xffh\xfft.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    def test_long_binget(self):
        pickled = '(]r\x00\x00\x01\x00j\x00\x00\x01\x00t.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    def test_dup(self):
        pickled = '((l2t.'
        unpickled = self.loads(pickled)
        self.assertEqual(unpickled, ([],)*2)
        self.assertIs(unpickled[0], unpickled[1])

    def test_bad_stack(self):
        badpickles = [
            '.',                        # STOP
            '0',                        # POP
            '1',                        # POP_MARK
            '2',                        # DUP
            # '(2',                     # PyUnpickler doesn't raise
            'R',                        # REDUCE
            ')R',
            'a',                        # APPEND
            'Na',
            'b',                        # BUILD
            'Nb',
            'd',                        # DICT
            'e',                        # APPENDS
            # '(e',                     # PyUnpickler raises AttributeError
            'i__builtin__\nlist\n',     # INST
            'l',                        # LIST
            'o',                        # OBJ
            '(o',
            'p1\n',                     # PUT
            'q\x00',                    # BINPUT
            'r\x00\x00\x00\x00',        # LONG_BINPUT
            's',                        # SETITEM
            'Ns',
            'NNs',
            't',                        # TUPLE
            'u',                        # SETITEMS
            # '(u',                     # PyUnpickler doesn't raise
            '}(Nu',
            '\x81',                     # NEWOBJ
            ')\x81',
            '\x85',                     # TUPLE1
            '\x86',                     # TUPLE2
            'N\x86',
            '\x87',                     # TUPLE3
            'N\x87',
            'NN\x87',
        ]
        for p in badpickles:
            self.check_unpickling_error(self.bad_stack_errors, p)

    def test_bad_mark(self):
        badpickles = [
            # 'N(.',                      # STOP
            'N(2',                      # DUP
            'c__builtin__\nlist\n)(R',  # REDUCE
            'c__builtin__\nlist\n()R',
            ']N(a',                     # APPEND
                                        # BUILD
            'c__builtin__\nValueError\n)R}(b',
            'c__builtin__\nValueError\n)R(}b',
            '(Nd',                      # DICT
            'N(p1\n',                   # PUT
            'N(q\x00',                  # BINPUT
            'N(r\x00\x00\x00\x00',      # LONG_BINPUT
            '}NN(s',                    # SETITEM
            '}N(Ns',
            '}(NNs',
            '}((u',                     # SETITEMS
                                        # NEWOBJ
            'c__builtin__\nlist\n)(\x81',
            'c__builtin__\nlist\n()\x81',
            'N(\x85',                   # TUPLE1
            'NN(\x86',                  # TUPLE2
            'N(N\x86',
            'NNN(\x87',                 # TUPLE3
            'NN(N\x87',
            'N(NN\x87',
        ]
        for p in badpickles:
            self.check_unpickling_error(self.bad_mark_errors, p)

    def test_truncated_data(self):
        self.check_unpickling_error(EOFError, '')
        self.check_unpickling_error(EOFError, 'N')
        badpickles = [
            'F',                        # FLOAT
            'F0.0',
            'F0.00',
            'G',                        # BINFLOAT
            'G\x00\x00\x00\x00\x00\x00\x00',
            'I',                        # INT
            'I0',
            'J',                        # BININT
            'J\x00\x00\x00',
            'K',                        # BININT1
            'L',                        # LONG
            'L0',
            'L10',
            'L0L',
            'L10L',
            'M',                        # BININT2
            'M\x00',
            # 'P',                        # PERSID
            # 'Pabc',
            'S',                        # STRING
            "S'abc'",
            'T',                        # BINSTRING
            'T\x03\x00\x00',
            'T\x03\x00\x00\x00',
            'T\x03\x00\x00\x00ab',
            'U',                        # SHORT_BINSTRING
            'U\x03',
            'U\x03ab',
            'V',                        # UNICODE
            'Vabc',
            'X',                        # BINUNICODE
            'X\x03\x00\x00',
            'X\x03\x00\x00\x00',
            'X\x03\x00\x00\x00ab',
            '(c',                       # GLOBAL
            '(c__builtin__',
            '(c__builtin__\n',
            '(c__builtin__\nlist',
            'Ng',                       # GET
            'Ng0',
            '(i',                       # INST
            '(i__builtin__',
            '(i__builtin__\n',
            '(i__builtin__\nlist',
            'Nh',                       # BINGET
            'Nj',                       # LONG_BINGET
            'Nj\x00\x00\x00',
            'Np',                       # PUT
            'Np0',
            'Nq',                       # BINPUT
            'Nr',                       # LONG_BINPUT
            'Nr\x00\x00\x00',
            '\x80',                     # PROTO
            '\x82',                     # EXT1
            '\x83',                     # EXT2
            '\x84\x01',
            '\x84',                     # EXT4
            '\x84\x01\x00\x00',
            '\x8a',                     # LONG1
            '\x8b',                     # LONG4
            '\x8b\x00\x00\x00',
        ]
        for p in badpickles:
            self.check_unpickling_error(self.truncated_errors, p)


class AbstractPickleTests(unittest.TestCase):
    # Subclass must define self.dumps, self.loads.

    _testdata = AbstractUnpickleTests._testdata

    def setUp(self):
        pass

    def test_misc(self):
        # test various datatypes not tested by testdata
        for proto in protocols:
            x = myint(4)
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)

            x = (1, ())
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)

            x = initarg(1, x)
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)

        # XXX test __reduce__ protocol?

    def test_roundtrip_equality(self):
        expected = self._testdata
        for proto in protocols:
            s = self.dumps(expected, proto)
            got = self.loads(s)
            self.assertEqual(expected, got)

    # There are gratuitous differences between pickles produced by
    # pickle and cPickle, largely because cPickle starts PUT indices at
    # 1 and pickle starts them at 0.  See XXX comment in cPickle's put2() --
    # there's a comment with an exclamation point there whose meaning
    # is a mystery.  cPickle also suppresses PUT for objects with a refcount
    # of 1.
    def dont_test_disassembly(self):
        from pickletools import dis

        for proto, expected in (0, DATA0_DIS), (1, DATA1_DIS):
            s = self.dumps(self._testdata, proto)
            filelike = cStringIO.StringIO()
            dis(s, out=filelike)
            got = filelike.getvalue()
            self.assertEqual(expected, got)

    def test_recursive_list(self):
        l = []
        l.append(l)
        for proto in protocols:
            s = self.dumps(l, proto)
            x = self.loads(s)
            self.assertIsInstance(x, list)
            self.assertEqual(len(x), 1)
            self.assertIs(x[0], x)

    def test_recursive_tuple_and_list(self):
        t = ([],)
        t[0].append(t)
        for proto in protocols:
            s = self.dumps(t, proto)
            x = self.loads(s)
            self.assertIsInstance(x, tuple)
            self.assertEqual(len(x), 1)
            self.assertIsInstance(x[0], list)
            self.assertEqual(len(x[0]), 1)
            self.assertIs(x[0][0], x)

    def test_recursive_dict(self):
        d = {}
        d[1] = d
        for proto in protocols:
            s = self.dumps(d, proto)
            x = self.loads(s)
            self.assertIsInstance(x, dict)
            self.assertEqual(x.keys(), [1])
            self.assertIs(x[1], x)

    def test_recursive_dict_key(self):
        d = {}
        k = K(d)
        d[k] = 1
        for proto in protocols:
            s = self.dumps(d, proto)
            x = self.loads(s)
            self.assertIsInstance(x, dict)
            self.assertEqual(len(x.keys()), 1)
            self.assertIsInstance(x.keys()[0], K)
            self.assertIs(x.keys()[0].value, x)

    def test_recursive_list_subclass(self):
        y = MyList()
        y.append(y)
        s = self.dumps(y, 2)
        x = self.loads(s)
        self.assertIsInstance(x, MyList)
        self.assertEqual(len(x), 1)
        self.assertIs(x[0], x)

    def test_recursive_dict_subclass(self):
        d = MyDict()
        d[1] = d
        s = self.dumps(d, 2)
        x = self.loads(s)
        self.assertIsInstance(x, MyDict)
        self.assertEqual(x.keys(), [1])
        self.assertIs(x[1], x)

    def test_recursive_dict_subclass_key(self):
        d = MyDict()
        k = K(d)
        d[k] = 1
        s = self.dumps(d, 2)
        x = self.loads(s)
        self.assertIsInstance(x, MyDict)
        self.assertEqual(len(x.keys()), 1)
        self.assertIsInstance(x.keys()[0], K)
        self.assertIs(x.keys()[0].value, x)

    def test_recursive_inst(self):
        i = C()
        i.attr = i
        for proto in protocols:
            s = self.dumps(i, proto)
            x = self.loads(s)
            self.assertIsInstance(x, C)
            self.assertEqual(dir(x), dir(i))
            self.assertIs(x.attr, x)

    def test_recursive_multi(self):
        l = []
        d = {1:l}
        i = C()
        i.attr = d
        l.append(i)
        for proto in protocols:
            s = self.dumps(l, proto)
            x = self.loads(s)
            self.assertIsInstance(x, list)
            self.assertEqual(len(x), 1)
            self.assertEqual(dir(x[0]), dir(i))
            self.assertEqual(x[0].attr.keys(), [1])
            self.assertTrue(x[0].attr[1] is x)

    def check_recursive_collection_and_inst(self, factory):
        h = H()
        y = factory([h])
        h.attr = y
        for proto in protocols:
            s = self.dumps(y, proto)
            x = self.loads(s)
            self.assertIsInstance(x, type(y))
            self.assertEqual(len(x), 1)
            self.assertIsInstance(list(x)[0], H)
            self.assertIs(list(x)[0].attr, x)

    def test_recursive_list_and_inst(self):
        self.check_recursive_collection_and_inst(list)

    def test_recursive_tuple_and_inst(self):
        self.check_recursive_collection_and_inst(tuple)

    def test_recursive_dict_and_inst(self):
        self.check_recursive_collection_and_inst(dict.fromkeys)

    def test_recursive_set_and_inst(self):
        self.check_recursive_collection_and_inst(set)

    def test_recursive_frozenset_and_inst(self):
        self.check_recursive_collection_and_inst(frozenset)

    def test_recursive_list_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyList)

    def test_recursive_tuple_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyTuple)

    def test_recursive_dict_subclass_and_inst(self):
        self.check_recursive_collection_and_inst(MyDict.fromkeys)

    if have_unicode:
        def test_unicode(self):
            endcases = [u'', u'<\\u>', u'<\\\u1234>', u'<\n>',
                        u'<\\>', u'<\\\U00012345>',
                        # surrogates
                        u'<\udc80>']
            for proto in protocols:
                for u in endcases:
                    p = self.dumps(u, proto)
                    u2 = self.loads(p)
                    self.assertEqual(u2, u)

        def test_unicode_high_plane(self):
            t = u'\U00012345'
            for proto in protocols:
                p = self.dumps(t, proto)
                t2 = self.loads(p)
                self.assertEqual(t2, t)

    def test_ints(self):
        import sys
        for proto in protocols:
            n = sys.maxint
            while n:
                for expected in (-n, n):
                    s = self.dumps(expected, proto)
                    n2 = self.loads(s)
                    self.assertEqual(expected, n2)
                n = n >> 1

    def test_long(self):
        for proto in protocols:
            # 256 bytes is where LONG4 begins.
            for nbits in 1, 8, 8*254, 8*255, 8*256, 8*257:
                nbase = 1L << nbits
                for npos in nbase-1, nbase, nbase+1:
                    for n in npos, -npos:
                        pickle = self.dumps(n, proto)
                        got = self.loads(pickle)
                        self.assertEqual(n, got)
        # Try a monster.  This is quadratic-time in protos 0 & 1, so don't
        # bother with those.
        nbase = long("deadbeeffeedface", 16)
        nbase += nbase << 1000000
        for n in nbase, -nbase:
            p = self.dumps(n, 2)
            got = self.loads(p)
            self.assertEqual(n, got)

    def test_float(self):
        test_values = [0.0, 4.94e-324, 1e-310, 7e-308, 6.626e-34, 0.1, 0.5,
                       3.14, 263.44582062374053, 6.022e23, 1e30]
        test_values = test_values + [-x for x in test_values]
        for proto in protocols:
            for value in test_values:
                pickle = self.dumps(value, proto)
                got = self.loads(pickle)
                self.assertEqual(value, got)

    @run_with_locale('LC_ALL', 'de_DE', 'fr_FR')
    def test_float_format(self):
        # make sure that floats are formatted locale independent
        self.assertEqual(self.dumps(1.2)[0:3], 'F1.')

    def test_reduce(self):
        pass

    def test_getinitargs(self):
        pass

    def test_metaclass(self):
        a = use_metaclass()
        for proto in protocols:
            s = self.dumps(a, proto)
            b = self.loads(s)
            self.assertEqual(a.__class__, b.__class__)

    def test_dynamic_class(self):
        a = create_dynamic_class("my_dynamic_class", (object,))
        copy_reg.pickle(pickling_metaclass, pickling_metaclass.__reduce__)
        for proto in protocols:
            s = self.dumps(a, proto)
            b = self.loads(s)
            self.assertEqual(a, b)
            self.assertIs(a.__class__, b.__class__)

    def test_structseq(self):
        import time
        import os

        t = time.localtime()
        for proto in protocols:
            s = self.dumps(t, proto)
            u = self.loads(s)
            self.assertEqual(t, u)
            if hasattr(os, "stat"):
                t = os.stat(os.curdir)
                s = self.dumps(t, proto)
                u = self.loads(s)
                self.assertEqual(t, u)
            if hasattr(os, "statvfs"):
                t = os.statvfs(os.curdir)
                s = self.dumps(t, proto)
                u = self.loads(s)
                self.assertEqual(t, u)

    # Tests for protocol 2

    def test_proto(self):
        build_none = pickle.NONE + pickle.STOP
        for proto in protocols:
            expected = build_none
            if proto >= 2:
                expected = pickle.PROTO + chr(proto) + expected
            p = self.dumps(None, proto)
            self.assertEqual(p, expected)

        oob = protocols[-1] + 1     # a future protocol
        badpickle = pickle.PROTO + chr(oob) + build_none
        try:
            self.loads(badpickle)
        except ValueError, detail:
            self.assertTrue(str(detail).startswith(
                                            "unsupported pickle protocol"))
        else:
            self.fail("expected bad protocol number to raise ValueError")

    def test_long1(self):
        x = 12345678910111213141516178920L
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)
            self.assertEqual(opcode_in_pickle(pickle.LONG1, s), proto >= 2)

    def test_long4(self):
        x = 12345678910111213141516178920L << (256*8)
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)
            self.assertEqual(opcode_in_pickle(pickle.LONG4, s), proto >= 2)

    def test_short_tuples(self):
        # Map (proto, len(tuple)) to expected opcode.
        expected_opcode = {(0, 0): pickle.TUPLE,
                           (0, 1): pickle.TUPLE,
                           (0, 2): pickle.TUPLE,
                           (0, 3): pickle.TUPLE,
                           (0, 4): pickle.TUPLE,

                           (1, 0): pickle.EMPTY_TUPLE,
                           (1, 1): pickle.TUPLE,
                           (1, 2): pickle.TUPLE,
                           (1, 3): pickle.TUPLE,
                           (1, 4): pickle.TUPLE,

                           (2, 0): pickle.EMPTY_TUPLE,
                           (2, 1): pickle.TUPLE1,
                           (2, 2): pickle.TUPLE2,
                           (2, 3): pickle.TUPLE3,
                           (2, 4): pickle.TUPLE,
                          }
        a = ()
        b = (1,)
        c = (1, 2)
        d = (1, 2, 3)
        e = (1, 2, 3, 4)
        for proto in protocols:
            for x in a, b, c, d, e:
                s = self.dumps(x, proto)
                y = self.loads(s)
                self.assertEqual(x, y, (proto, x, s, y))
                expected = expected_opcode[proto, len(x)]
                self.assertEqual(opcode_in_pickle(expected, s), True)

    def test_singletons(self):
        # Map (proto, singleton) to expected opcode.
        expected_opcode = {(0, None): pickle.NONE,
                           (1, None): pickle.NONE,
                           (2, None): pickle.NONE,

                           (0, True): pickle.INT,
                           (1, True): pickle.INT,
                           (2, True): pickle.NEWTRUE,

                           (0, False): pickle.INT,
                           (1, False): pickle.INT,
                           (2, False): pickle.NEWFALSE,
                          }
        for proto in protocols:
            for x in None, False, True:
                s = self.dumps(x, proto)
                y = self.loads(s)
                self.assertTrue(x is y, (proto, x, s, y))
                expected = expected_opcode[proto, x]
                self.assertEqual(opcode_in_pickle(expected, s), True)

    def test_newobj_tuple(self):
        x = MyTuple([1, 2, 3])
        x.foo = 42
        x.bar = "hello"
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(tuple(x), tuple(y))
            self.assertEqual(x.__dict__, y.__dict__)

    def test_newobj_list(self):
        x = MyList([1, 2, 3])
        x.foo = 42
        x.bar = "hello"
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(list(x), list(y))
            self.assertEqual(x.__dict__, y.__dict__)

    def test_newobj_generic(self):
        for proto in protocols:
            for C in myclasses:
                B = C.__base__
                x = C(C.sample)
                x.foo = 42
                s = self.dumps(x, proto)
                y = self.loads(s)
                detail = (proto, C, B, x, y, type(y))
                self.assertEqual(B(x), B(y), detail)
                self.assertEqual(x.__dict__, y.__dict__, detail)

    def test_newobj_proxies(self):
        # NEWOBJ should use the __class__ rather than the raw type
        import weakref
        classes = myclasses[:]
        # Cannot create weakproxies to these classes
        for c in (MyInt, MyLong, MyStr, MyTuple):
            classes.remove(c)
        for proto in protocols:
            for C in classes:
                B = C.__base__
                x = C(C.sample)
                x.foo = 42
                p = weakref.proxy(x)
                s = self.dumps(p, proto)
                y = self.loads(s)
                self.assertEqual(type(y), type(x))  # rather than type(p)
                detail = (proto, C, B, x, y, type(y))
                self.assertEqual(B(x), B(y), detail)
                self.assertEqual(x.__dict__, y.__dict__, detail)

    # Register a type with copy_reg, with extension code extcode.  Pickle
    # an object of that type.  Check that the resulting pickle uses opcode
    # (EXT[124]) under proto 2, and not in proto 1.

    def produce_global_ext(self, extcode, opcode):
        e = ExtensionSaver(extcode)
        try:
            copy_reg.add_extension(__name__, "MyList", extcode)
            x = MyList([1, 2, 3])
            x.foo = 42
            x.bar = "hello"

            # Dump using protocol 1 for comparison.
            s1 = self.dumps(x, 1)
            self.assertIn(__name__, s1)
            self.assertIn("MyList", s1)
            self.assertEqual(opcode_in_pickle(opcode, s1), False)

            y = self.loads(s1)
            self.assertEqual(list(x), list(y))
            self.assertEqual(x.__dict__, y.__dict__)

            # Dump using protocol 2 for test.
            s2 = self.dumps(x, 2)
            self.assertNotIn(__name__, s2)
            self.assertNotIn("MyList", s2)
            self.assertEqual(opcode_in_pickle(opcode, s2), True)

            y = self.loads(s2)
            self.assertEqual(list(x), list(y))
            self.assertEqual(x.__dict__, y.__dict__)

        finally:
            e.restore()

    def test_global_ext1(self):
        self.produce_global_ext(0x00000001, pickle.EXT1)  # smallest EXT1 code
        self.produce_global_ext(0x000000ff, pickle.EXT1)  # largest EXT1 code

    def test_global_ext2(self):
        self.produce_global_ext(0x00000100, pickle.EXT2)  # smallest EXT2 code
        self.produce_global_ext(0x0000ffff, pickle.EXT2)  # largest EXT2 code
        self.produce_global_ext(0x0000abcd, pickle.EXT2)  # check endianness

    def test_global_ext4(self):
        self.produce_global_ext(0x00010000, pickle.EXT4)  # smallest EXT4 code
        self.produce_global_ext(0x7fffffff, pickle.EXT4)  # largest EXT4 code
        self.produce_global_ext(0x12abcdef, pickle.EXT4)  # check endianness

    def test_list_chunking(self):
        n = 10  # too small to chunk
        x = range(n)
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)
            num_appends = count_opcode(pickle.APPENDS, s)
            self.assertEqual(num_appends, proto > 0)

        n = 2500  # expect at least two chunks when proto > 0
        x = range(n)
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)
            num_appends = count_opcode(pickle.APPENDS, s)
            if proto == 0:
                self.assertEqual(num_appends, 0)
            else:
                self.assertTrue(num_appends >= 2)

    def test_dict_chunking(self):
        n = 10  # too small to chunk
        x = dict.fromkeys(range(n))
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)
            num_setitems = count_opcode(pickle.SETITEMS, s)
            self.assertEqual(num_setitems, proto > 0)

        n = 2500  # expect at least two chunks when proto > 0
        x = dict.fromkeys(range(n))
        for proto in protocols:
            s = self.dumps(x, proto)
            y = self.loads(s)
            self.assertEqual(x, y)
            num_setitems = count_opcode(pickle.SETITEMS, s)
            if proto == 0:
                self.assertEqual(num_setitems, 0)
            else:
                self.assertTrue(num_setitems >= 2)

    def test_simple_newobj(self):
        x = SimpleNewObj.__new__(SimpleNewObj, 0xface)  # avoid __init__
        x.abc = 666
        for proto in protocols:
            s = self.dumps(x, proto)
            if proto < 1:
                self.assertIn('\nI64206', s)  # INT
            else:
                self.assertIn('M\xce\xfa', s)  # BININT2
            self.assertEqual(opcode_in_pickle(pickle.NEWOBJ, s), proto >= 2)
            y = self.loads(s)   # will raise TypeError if __init__ called
            self.assertEqual(y.abc, 666)
            self.assertEqual(x.__dict__, y.__dict__)

    def test_complex_newobj(self):
        x = ComplexNewObj.__new__(ComplexNewObj, 0xface)  # avoid __init__
        x.abc = 666
        for proto in protocols:
            s = self.dumps(x, proto)
            if proto < 1:
                self.assertIn('\nI64206', s)  # INT
            elif proto < 2:
                self.assertIn('M\xce\xfa', s)  # BININT2
            else:
                self.assertIn('U\x04FACE', s)  # SHORT_BINSTRING
            self.assertEqual(opcode_in_pickle(pickle.NEWOBJ, s), proto >= 2)
            y = self.loads(s)   # will raise TypeError if __init__ called
            self.assertEqual(y.abc, 666)
            self.assertEqual(x.__dict__, y.__dict__)

    def test_newobj_list_slots(self):
        x = SlotList([1, 2, 3])
        x.foo = 42
        x.bar = "hello"
        s = self.dumps(x, 2)
        y = self.loads(s)
        self.assertEqual(list(x), list(y))
        self.assertEqual(x.__dict__, y.__dict__)
        self.assertEqual(x.foo, y.foo)
        self.assertEqual(x.bar, y.bar)

    def test_reduce_overrides_default_reduce_ex(self):
        for proto in protocols:
            x = REX_one()
            self.assertEqual(x._reduce_called, 0)
            s = self.dumps(x, proto)
            self.assertEqual(x._reduce_called, 1)
            y = self.loads(s)
            self.assertEqual(y._reduce_called, 0)

    def test_reduce_ex_called(self):
        for proto in protocols:
            x = REX_two()
            self.assertEqual(x._proto, None)
            s = self.dumps(x, proto)
            self.assertEqual(x._proto, proto)
            y = self.loads(s)
            self.assertEqual(y._proto, None)

    def test_reduce_ex_overrides_reduce(self):
        for proto in protocols:
            x = REX_three()
            self.assertEqual(x._proto, None)
            s = self.dumps(x, proto)
            self.assertEqual(x._proto, proto)
            y = self.loads(s)
            self.assertEqual(y._proto, None)

    def test_reduce_ex_calls_base(self):
        for proto in protocols:
            x = REX_four()
            self.assertEqual(x._proto, None)
            s = self.dumps(x, proto)
            self.assertEqual(x._proto, proto)
            y = self.loads(s)
            self.assertEqual(y._proto, proto)

    def test_reduce_calls_base(self):
        for proto in protocols:
            x = REX_five()
            self.assertEqual(x._reduce_called, 0)
            s = self.dumps(x, proto)
            self.assertEqual(x._reduce_called, 1)
            y = self.loads(s)
            self.assertEqual(y._reduce_called, 1)

    @no_tracing
    def test_bad_getattr(self):
        # Issue #3514: crash when there is an infinite loop in __getattr__
        x = BadGetattr()
        for proto in protocols:
            self.assertRaises(RuntimeError, self.dumps, x, proto)

    def test_reduce_bad_iterator(self):
        # Issue4176: crash when 4th and 5th items of __reduce__()
        # are not iterators
        class C(object):
            def __reduce__(self):
                # 4th item is not an iterator
                return list, (), None, [], None
        class D(object):
            def __reduce__(self):
                # 5th item is not an iterator
                return dict, (), None, None, []

        # Protocol 0 in Python implementation is less strict and also accepts
        # iterables.
        for proto in protocols:
            try:
                self.dumps(C(), proto)
            except (AttributeError, pickle.PicklingError, cPickle.PicklingError):
                pass
            try:
                self.dumps(D(), proto)
            except (AttributeError, pickle.PicklingError, cPickle.PicklingError):
                pass

    def test_many_puts_and_gets(self):
        # Test that internal data structures correctly deal with lots of
        # puts/gets.
        keys = ("aaa" + str(i) for i in xrange(100))
        large_dict = dict((k, [4, 5, 6]) for k in keys)
        obj = [dict(large_dict), dict(large_dict), dict(large_dict)]

        for proto in protocols:
            dumped = self.dumps(obj, proto)
            loaded = self.loads(dumped)
            self.assertEqual(loaded, obj,
                             "Failed protocol %d: %r != %r"
                             % (proto, obj, loaded))

    def test_attribute_name_interning(self):
        # Test that attribute names of pickled objects are interned when
        # unpickling.
        for proto in protocols:
            x = C()
            x.foo = 42
            x.bar = "hello"
            s = self.dumps(x, proto)
            y = self.loads(s)
            x_keys = sorted(x.__dict__)
            y_keys = sorted(y.__dict__)
            for x_key, y_key in zip(x_keys, y_keys):
                self.assertIs(x_key, y_key)

    def test_large_pickles(self):
        # Test the correctness of internal buffering routines when handling
        # large data.
        for proto in protocols:
            data = (1, min, 'xy' * (30 * 1024), len)
            dumped = self.dumps(data, proto)
            loaded = self.loads(dumped)
            self.assertEqual(len(loaded), len(data))
            self.assertEqual(loaded, data)

    def _check_pickling_with_opcode(self, obj, opcode, proto):
        pickled = self.dumps(obj, proto)
        self.assertTrue(opcode_in_pickle(opcode, pickled))
        unpickled = self.loads(pickled)
        self.assertEqual(obj, unpickled)

    def test_appends_on_non_lists(self):
        # Issue #17720
        obj = REX_six([1, 2, 3])
        for proto in protocols:
            if proto == 0:
                self._check_pickling_with_opcode(obj, pickle.APPEND, proto)
            else:
                self._check_pickling_with_opcode(obj, pickle.APPENDS, proto)

    def test_setitems_on_non_dicts(self):
        obj = REX_seven({1: -1, 2: -2, 3: -3})
        for proto in protocols:
            if proto == 0:
                self._check_pickling_with_opcode(obj, pickle.SETITEM, proto)
            else:
                self._check_pickling_with_opcode(obj, pickle.SETITEMS, proto)


# Test classes for reduce_ex

class REX_one(object):
    _reduce_called = 0
    def __reduce__(self):
        self._reduce_called = 1
        return REX_one, ()
    # No __reduce_ex__ here, but inheriting it from object

class REX_two(object):
    _proto = None
    def __reduce_ex__(self, proto):
        self._proto = proto
        return REX_two, ()
    # No __reduce__ here, but inheriting it from object

class REX_three(object):
    _proto = None
    def __reduce_ex__(self, proto):
        self._proto = proto
        return REX_two, ()
    def __reduce__(self):
        raise TestFailed, "This __reduce__ shouldn't be called"

class REX_four(object):
    _proto = None
    def __reduce_ex__(self, proto):
        self._proto = proto
        return object.__reduce_ex__(self, proto)
    # Calling base class method should succeed

class REX_five(object):
    _reduce_called = 0
    def __reduce__(self):
        self._reduce_called = 1
        return object.__reduce__(self)
    # This one used to fail with infinite recursion

class REX_six(object):
    """This class is used to check the 4th argument (list iterator) of
    the reduce protocol.
    """
    def __init__(self, items=None):
        if items is None:
            items = []
        self.items = items
    def __eq__(self, other):
        return type(self) is type(other) and self.items == other.items
    __hash__ = None
    def append(self, item):
        self.items.append(item)
    def extend(self, items):
        for item in items:
            self.append(item)
    def __reduce__(self):
        return type(self), (), None, iter(self.items), None

class REX_seven(object):
    """This class is used to check the 5th argument (dict iterator) of
    the reduce protocol.
    """
    def __init__(self, table=None):
        if table is None:
            table = {}
        self.table = table
    def __eq__(self, other):
        return type(self) is type(other) and self.table == other.table
    __hash__ = None
    def __setitem__(self, key, value):
        self.table[key] = value
    def __reduce__(self):
        return type(self), (), None, None, iter(self.table.items())

# Test classes for newobj

class MyInt(int):
    sample = 1

class MyLong(long):
    sample = 1L

class MyFloat(float):
    sample = 1.0

class MyComplex(complex):
    sample = 1.0 + 0.0j

class MyStr(str):
    sample = "hello"

class MyUnicode(unicode):
    sample = u"hello \u1234"

class MyTuple(tuple):
    sample = (1, 2, 3)

class MyList(list):
    sample = [1, 2, 3]

class MyDict(dict):
    sample = {"a": 1, "b": 2}

myclasses = [MyInt, MyLong, MyFloat,
             MyComplex,
             MyStr, MyUnicode,
             MyTuple, MyList, MyDict]


class SlotList(MyList):
    __slots__ = ["foo"]

class SimpleNewObj(int):
    def __init__(self, *args, **kwargs):
        # raise an error, to make sure this isn't called
        raise TypeError("SimpleNewObj.__init__() didn't expect to get called")
    def __eq__(self, other):
        return int(self) == int(other) and self.__dict__ == other.__dict__
    __hash__ = None

class ComplexNewObj(SimpleNewObj):
    def __getnewargs__(self):
        return ('%X' % self, 16)

class BadGetattr:
    def __getattr__(self, key):
        self.foo

class AbstractPickleModuleTests(unittest.TestCase):

    def test_dump_closed_file(self):
        import os
        f = open(TESTFN, "w")
        try:
            f.close()
            self.assertRaises(ValueError, self.module.dump, 123, f)
        finally:
            os.remove(TESTFN)

    def test_load_closed_file(self):
        import os
        f = open(TESTFN, "w")
        try:
            f.close()
            self.assertRaises(ValueError, self.module.dump, 123, f)
        finally:
            os.remove(TESTFN)

    def test_load_from_and_dump_to_file(self):
        stream = cStringIO.StringIO()
        data = [123, {}, 124]
        self.module.dump(data, stream)
        stream.seek(0)
        unpickled = self.module.load(stream)
        self.assertEqual(unpickled, data)

    def test_highest_protocol(self):
        # Of course this needs to be changed when HIGHEST_PROTOCOL changes.
        self.assertEqual(self.module.HIGHEST_PROTOCOL, 2)

    def test_callapi(self):
        f = cStringIO.StringIO()
        # With and without keyword arguments
        self.module.dump(123, f, -1)
        self.module.dump(123, file=f, protocol=-1)
        self.module.dumps(123, -1)
        self.module.dumps(123, protocol=-1)
        self.module.Pickler(f, -1)
        self.module.Pickler(f, protocol=-1)

    def test_incomplete_input(self):
        s = StringIO.StringIO("X''.")
        self.assertRaises(EOFError, self.module.load, s)

    def test_restricted(self):
        # issue7128: cPickle failed in restricted mode
        builtins = {self.module.__name__: self.module,
                    '__import__': __import__}
        d = {}
        teststr = "def f(): {0}.dumps(0)".format(self.module.__name__)
        exec teststr in {'__builtins__': builtins}, d
        d['f']()

    def test_bad_input(self):
        # Test issue4298
        s = '\x58\0\0\0\x54'
        self.assertRaises(EOFError, self.module.loads, s)


class AbstractPersistentPicklerTests(unittest.TestCase):

    # This class defines persistent_id() and persistent_load()
    # functions that should be used by the pickler.  All even integers
    # are pickled using persistent ids.

    def persistent_id(self, object):
        if isinstance(object, int) and object % 2 == 0:
            self.id_count += 1
            return str(object)
        elif object == "test_false_value":
            self.false_count += 1
            return ""
        else:
            return None

    def persistent_load(self, oid):
        if not oid:
            self.load_false_count += 1
            return "test_false_value"
        else:
            self.load_count += 1
            object = int(oid)
            assert object % 2 == 0
            return object

    def test_persistence(self):
        L = range(10) + ["test_false_value"]
        for proto in protocols:
            self.id_count = 0
            self.false_count = 0
            self.load_false_count = 0
            self.load_count = 0
            self.assertEqual(self.loads(self.dumps(L, proto)), L)
            self.assertEqual(self.id_count, 5)
            self.assertEqual(self.false_count, 1)
            self.assertEqual(self.load_count, 5)
            self.assertEqual(self.load_false_count, 1)

class AbstractPicklerUnpicklerObjectTests(unittest.TestCase):

    pickler_class = None
    unpickler_class = None

    def setUp(self):
        assert self.pickler_class
        assert self.unpickler_class

    def test_clear_pickler_memo(self):
        # To test whether clear_memo() has any effect, we pickle an object,
        # then pickle it again without clearing the memo; the two serialized
        # forms should be different. If we clear_memo() and then pickle the
        # object again, the third serialized form should be identical to the
        # first one we obtained.
        data = ["abcdefg", "abcdefg", 44]
        f = cStringIO.StringIO()
        pickler = self.pickler_class(f)

        pickler.dump(data)
        first_pickled = f.getvalue()

        # Reset StringIO object.
        f.seek(0)
        f.truncate()

        pickler.dump(data)
        second_pickled = f.getvalue()

        # Reset the Pickler and StringIO objects.
        pickler.clear_memo()
        f.seek(0)
        f.truncate()

        pickler.dump(data)
        third_pickled = f.getvalue()

        self.assertNotEqual(first_pickled, second_pickled)
        self.assertEqual(first_pickled, third_pickled)

    def test_priming_pickler_memo(self):
        # Verify that we can set the Pickler's memo attribute.
        data = ["abcdefg", "abcdefg", 44]
        f = cStringIO.StringIO()
        pickler = self.pickler_class(f)

        pickler.dump(data)
        first_pickled = f.getvalue()

        f = cStringIO.StringIO()
        primed = self.pickler_class(f)
        primed.memo = pickler.memo

        primed.dump(data)
        primed_pickled = f.getvalue()

        self.assertNotEqual(first_pickled, primed_pickled)

    def test_priming_unpickler_memo(self):
        # Verify that we can set the Unpickler's memo attribute.
        data = ["abcdefg", "abcdefg", 44]
        f = cStringIO.StringIO()
        pickler = self.pickler_class(f)

        pickler.dump(data)
        first_pickled = f.getvalue()

        f = cStringIO.StringIO()
        primed = self.pickler_class(f)
        primed.memo = pickler.memo

        primed.dump(data)
        primed_pickled = f.getvalue()

        unpickler = self.unpickler_class(cStringIO.StringIO(first_pickled))
        unpickled_data1 = unpickler.load()

        self.assertEqual(unpickled_data1, data)

        primed = self.unpickler_class(cStringIO.StringIO(primed_pickled))
        primed.memo = unpickler.memo
        unpickled_data2 = primed.load()

        primed.memo.clear()

        self.assertEqual(unpickled_data2, data)
        self.assertTrue(unpickled_data2 is unpickled_data1)

    def test_reusing_unpickler_objects(self):
        data1 = ["abcdefg", "abcdefg", 44]
        f = cStringIO.StringIO()
        pickler = self.pickler_class(f)
        pickler.dump(data1)
        pickled1 = f.getvalue()

        data2 = ["abcdefg", 44, 44]
        f = cStringIO.StringIO()
        pickler = self.pickler_class(f)
        pickler.dump(data2)
        pickled2 = f.getvalue()

        f = cStringIO.StringIO()
        f.write(pickled1)
        f.seek(0)
        unpickler = self.unpickler_class(f)
        self.assertEqual(unpickler.load(), data1)

        f.seek(0)
        f.truncate()
        f.write(pickled2)
        f.seek(0)
        self.assertEqual(unpickler.load(), data2)

    def _check_multiple_unpicklings(self, ioclass, seekable):
        for proto in protocols:
            data1 = [(x, str(x)) for x in xrange(2000)] + ["abcde", len]
            f = ioclass()
            pickler = self.pickler_class(f, protocol=proto)
            pickler.dump(data1)
            pickled = f.getvalue()

            N = 5
            f = ioclass(pickled * N)
            unpickler = self.unpickler_class(f)
            for i in xrange(N):
                if seekable:
                    pos = f.tell()
                self.assertEqual(unpickler.load(), data1)
                if seekable:
                    self.assertEqual(f.tell(), pos + len(pickled))
            self.assertRaises(EOFError, unpickler.load)

    def test_multiple_unpicklings_seekable(self):
        self._check_multiple_unpicklings(StringIO.StringIO, True)

    def test_multiple_unpicklings_unseekable(self):
        self._check_multiple_unpicklings(UnseekableIO, False)

    def test_unpickling_buffering_readline(self):
        # Issue #12687: the unpickler's buffering logic could fail with
        # text mode opcodes.
        import io
        data = list(xrange(10))
        for proto in protocols:
            for buf_size in xrange(1, 11):
                f = io.BufferedRandom(io.BytesIO(), buffer_size=buf_size)
                pickler = self.pickler_class(f, protocol=proto)
                pickler.dump(data)
                f.seek(0)
                unpickler = self.unpickler_class(f)
                self.assertEqual(unpickler.load(), data)


class BigmemPickleTests(unittest.TestCase):

    # Memory requirements: 1 byte per character for input strings, 1 byte
    # for pickled data, 1 byte for unpickled strings, 1 byte for internal
    # buffer and 1 byte of free space for resizing of internal buffer.

    @precisionbigmemtest(size=_2G + 100*_1M, memuse=5)
    def test_huge_strlist(self, size):
        chunksize = 2**20
        data = []
        while size > chunksize:
            data.append('x' * chunksize)
            size -= chunksize
            chunksize += 1
        data.append('y' * size)

        try:
            for proto in protocols:
                try:
                    pickled = self.dumps(data, proto)
                    res = self.loads(pickled)
                    self.assertEqual(res, data)
                finally:
                    res = None
                    pickled = None
        finally:
            data = None
