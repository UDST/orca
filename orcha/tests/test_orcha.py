import os
import tempfile

import pandas as pd
import pytest
from pandas.util import testing as pdt

from .. import orcha
from ..utils.testing import assert_frames_equal


def setup_function(func):
    orcha.clear_sim()
    orcha.enable_cache()


def teardown_function(func):
    orcha.clear_sim()
    orcha.enable_cache()


@pytest.fixture
def df():
    return pd.DataFrame(
        {'a': [1, 2, 3],
         'b': [4, 5, 6]},
        index=['x', 'y', 'z'])


def test_tables(df):
    wrapped_df = orcha.add_table('test_frame', df)

    @orcha.table()
    def test_func(test_frame):
        return test_frame.to_frame() / 2

    assert set(orcha.list_tables()) == {'test_frame', 'test_func'}

    table = orcha.get_table('test_frame')
    assert table is wrapped_df
    assert table.columns == ['a', 'b']
    assert table.local_columns == ['a', 'b']
    assert len(table) == 3
    pdt.assert_index_equal(table.index, df.index)
    pdt.assert_series_equal(table.get_column('a'), df.a)
    pdt.assert_series_equal(table.a, df.a)
    pdt.assert_series_equal(table['b'], df['b'])

    table = orcha._TABLES['test_func']
    assert table.index is None
    assert table.columns == []
    assert len(table) is 0
    pdt.assert_frame_equal(table.to_frame(), df / 2)
    pdt.assert_frame_equal(table.to_frame(columns=['a']), df[['a']] / 2)
    pdt.assert_index_equal(table.index, df.index)
    pdt.assert_series_equal(table.get_column('a'), df.a / 2)
    pdt.assert_series_equal(table.a, df.a / 2)
    pdt.assert_series_equal(table['b'], df['b'] / 2)
    assert len(table) == 3
    assert table.columns == ['a', 'b']


def test_table_func_cache(df):
    orcha.add_injectable('x', 2)

    @orcha.table(cache=True)
    def table(variable='x'):
        return df * variable

    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 2)
    orcha.add_injectable('x', 3)
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 2)
    orcha.get_table('table').clear_cached()
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 3)
    orcha.add_injectable('x', 4)
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 3)
    orcha.clear_cache()
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 4)
    orcha.add_injectable('x', 5)
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 4)
    orcha.add_table('table', table)
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 5)


def test_table_func_cache_disabled(df):
    orcha.add_injectable('x', 2)

    @orcha.table('table', cache=True)
    def asdf(x):
        return df * x

    orcha.disable_cache()

    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 2)
    orcha.add_injectable('x', 3)
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 3)

    orcha.enable_cache()

    orcha.add_injectable('x', 4)
    pdt.assert_frame_equal(orcha.get_table('table').to_frame(), df * 3)


def test_table_copy(df):
    orcha.add_table('test_frame_copied', df, copy_col=True)
    orcha.add_table('test_frame_uncopied', df, copy_col=False)
    orcha.add_table('test_func_copied', lambda: df, copy_col=True)
    orcha.add_table('test_func_uncopied', lambda: df, copy_col=False)

    @orcha.table(copy_col=True)
    def test_funcd_copied():
        return df

    @orcha.table(copy_col=False)
    def test_funcd_uncopied():
        return df

    @orcha.table(copy_col=True)
    def test_funcd_copied2(test_frame_copied):
        # local returns original, but it is copied by copy_col.
        return test_frame_copied.local

    @orcha.table(copy_col=True)
    def test_funcd_copied3(test_frame_uncopied):
        # local returns original, but it is copied by copy_col.
        return test_frame_uncopied.local

    @orcha.table(copy_col=False)
    def test_funcd_uncopied2(test_frame_copied):
        # local returns original.
        return test_frame_copied.local

    @orcha.table(copy_col=False)
    def test_funcd_uncopied3(test_frame_uncopied):
        # local returns original.
        return test_frame_uncopied.local

    orcha.add_table('test_cache_copied', lambda: df, cache=True, copy_col=True)
    orcha.add_table(
        'test_cache_uncopied', lambda: df, cache=True, copy_col=False)

    @orcha.table(cache=True, copy_col=True)
    def test_cached_copied():
        return df

    @orcha.table(cache=True, copy_col=False)
    def test_cached_uncopied():
        return df

    # Create tables with computed columns.
    orcha.add_table(
        'test_copied_columns', pd.DataFrame(index=df.index), copy_col=True)
    orcha.add_table(
        'test_uncopied_columns', pd.DataFrame(index=df.index), copy_col=False)
    for column_name in ['a', 'b']:
        label = "test_frame_uncopied.{}".format(column_name)

        def func(col=label):
            return col
        for table_name in ['test_copied_columns', 'test_uncopied_columns']:
            orcha.add_column(table_name, column_name, func)

    for name in ['test_frame_uncopied', 'test_func_uncopied',
                 'test_funcd_uncopied', 'test_funcd_uncopied2',
                 'test_funcd_uncopied3', 'test_cache_uncopied',
                 'test_cached_uncopied', 'test_uncopied_columns',
                 'test_frame_copied', 'test_func_copied',
                 'test_funcd_copied', 'test_funcd_copied2',
                 'test_funcd_copied3', 'test_cache_copied',
                 'test_cached_copied', 'test_copied_columns']:
        table = orcha.get_table(name)
        table2 = orcha.get_table(name)

        # to_frame will always return a copy.
        pdt.assert_frame_equal(table.to_frame(), df)
        assert table.to_frame() is not df
        pdt.assert_frame_equal(table.to_frame(), table.to_frame())
        assert table.to_frame() is not table.to_frame()
        pdt.assert_series_equal(table.to_frame()['a'], df['a'])
        assert table.to_frame()['a'] is not df['a']
        pdt.assert_series_equal(table.to_frame()['a'],
                                table.to_frame()['a'])
        assert table.to_frame()['a'] is not table.to_frame()['a']

        if 'uncopied' in name:
            pdt.assert_series_equal(table['a'], df['a'])
            assert table['a'] is df['a']
            pdt.assert_series_equal(table['a'], table2['a'])
            assert table['a'] is table2['a']
        else:
            pdt.assert_series_equal(table['a'], df['a'])
            assert table['a'] is not df['a']
            pdt.assert_series_equal(table['a'], table2['a'])
            assert table['a'] is not table2['a']


def test_columns_for_table():
    orcha.add_column(
        'table1', 'col10', pd.Series([1, 2, 3], index=['a', 'b', 'c']))
    orcha.add_column(
        'table2', 'col20', pd.Series([10, 11, 12], index=['x', 'y', 'z']))

    @orcha.column('table1')
    def col11():
        return pd.Series([4, 5, 6], index=['a', 'b', 'c'])

    @orcha.column('table2', 'col21')
    def asdf():
        return pd.Series([13, 14, 15], index=['x', 'y', 'z'])

    t1_col_names = orcha._list_columns_for_table('table1')
    assert set(t1_col_names) == {'col10', 'col11'}

    t2_col_names = orcha._list_columns_for_table('table2')
    assert set(t2_col_names) == {'col20', 'col21'}

    t1_cols = orcha._columns_for_table('table1')
    assert 'col10' in t1_cols and 'col11' in t1_cols

    t2_cols = orcha._columns_for_table('table2')
    assert 'col20' in t2_cols and 'col21' in t2_cols


def test_columns_and_tables(df):
    orcha.add_table('test_frame', df)

    @orcha.table()
    def test_func(test_frame):
        return test_frame.to_frame() / 2

    orcha.add_column('test_frame', 'c', pd.Series([7, 8, 9], index=df.index))

    @orcha.column('test_func', 'd')
    def asdf(test_func):
        return test_func.to_frame(columns=['b'])['b'] * 2

    @orcha.column('test_func')
    def e(column='test_func.d'):
        return column + 1

    test_frame = orcha.get_table('test_frame')
    assert set(test_frame.columns) == set(['a', 'b', 'c'])
    assert_frames_equal(
        test_frame.to_frame(),
        pd.DataFrame(
            {'a': [1, 2, 3],
             'b': [4, 5, 6],
             'c': [7, 8, 9]},
            index=['x', 'y', 'z']))
    assert_frames_equal(
        test_frame.to_frame(columns=['a', 'c']),
        pd.DataFrame(
            {'a': [1, 2, 3],
             'c': [7, 8, 9]},
            index=['x', 'y', 'z']))

    test_func_df = orcha._TABLES['test_func']
    assert set(test_func_df.columns) == set(['d', 'e'])
    assert_frames_equal(
        test_func_df.to_frame(),
        pd.DataFrame(
            {'a': [0.5, 1, 1.5],
             'b': [2, 2.5, 3],
             'c': [3.5, 4, 4.5],
             'd': [4., 5., 6.],
             'e': [5., 6., 7.]},
            index=['x', 'y', 'z']))
    assert_frames_equal(
        test_func_df.to_frame(columns=['b', 'd']),
        pd.DataFrame(
            {'b': [2, 2.5, 3],
             'd': [4., 5., 6.]},
            index=['x', 'y', 'z']))
    assert set(test_func_df.columns) == set(['a', 'b', 'c', 'd', 'e'])

    assert set(orcha.list_columns()) == {
        ('test_frame', 'c'), ('test_func', 'd'), ('test_func', 'e')}


def test_column_cache(df):
    orcha.add_injectable('x', 2)
    series = pd.Series([1, 2, 3], index=['x', 'y', 'z'])
    key = ('table', 'col')

    @orcha.table()
    def table():
        return df

    @orcha.column(*key, cache=True)
    def column(variable='x'):
        return series * variable

    def c():
        return orcha._COLUMNS[key]

    pdt.assert_series_equal(c()(), series * 2)
    orcha.add_injectable('x', 3)
    pdt.assert_series_equal(c()(), series * 2)
    c().clear_cached()
    pdt.assert_series_equal(c()(), series * 3)
    orcha.add_injectable('x', 4)
    pdt.assert_series_equal(c()(), series * 3)
    orcha.clear_cache()
    pdt.assert_series_equal(c()(), series * 4)
    orcha.add_injectable('x', 5)
    pdt.assert_series_equal(c()(), series * 4)
    orcha.get_table('table').clear_cached()
    pdt.assert_series_equal(c()(), series * 5)
    orcha.add_injectable('x', 6)
    pdt.assert_series_equal(c()(), series * 5)
    orcha.add_column(*key, column=column, cache=True)
    pdt.assert_series_equal(c()(), series * 6)


def test_column_cache_disabled(df):
    orcha.add_injectable('x', 2)
    series = pd.Series([1, 2, 3], index=['x', 'y', 'z'])
    key = ('table', 'col')

    @orcha.table()
    def table():
        return df

    @orcha.column(*key, cache=True)
    def column(x):
        return series * x

    def c():
        return orcha._COLUMNS[key]

    orcha.disable_cache()

    pdt.assert_series_equal(c()(), series * 2)
    orcha.add_injectable('x', 3)
    pdt.assert_series_equal(c()(), series * 3)

    orcha.enable_cache()

    orcha.add_injectable('x', 4)
    pdt.assert_series_equal(c()(), series * 3)


def test_update_col(df):
    wrapped = orcha.add_table('table', df)

    wrapped.update_col('b', pd.Series([7, 8, 9], index=df.index))
    pdt.assert_series_equal(wrapped['b'], pd.Series([7, 8, 9], index=df.index))

    wrapped.update_col_from_series('a', pd.Series([]))
    pdt.assert_series_equal(wrapped['a'], df['a'])

    wrapped.update_col_from_series('a', pd.Series([99], index=['y']))
    pdt.assert_series_equal(
        wrapped['a'], pd.Series([1, 99, 3], index=df.index))


class _FakeTable(object):
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns


@pytest.fixture
def fta():
    return _FakeTable('a', ['aa', 'ab', 'ac'])


@pytest.fixture
def ftb():
    return _FakeTable('b', ['bx', 'by', 'bz'])


def test_column_map_raises(fta, ftb):
    with pytest.raises(RuntimeError):
        orcha.column_map([fta, ftb], ['aa', 'by', 'bz', 'cw'])


def test_column_map_none(fta, ftb):
    assert orcha.column_map([fta, ftb], None) == {'a': None, 'b': None}


def test_column_map(fta, ftb):
    assert orcha.column_map([fta, ftb], ['aa', 'by', 'bz']) == \
        {'a': ['aa'], 'b': ['by', 'bz']}
    assert orcha.column_map([fta, ftb], ['by', 'bz']) == \
        {'a': [], 'b': ['by', 'bz']}


def test_models(df):
    orcha.add_table('test_table', df)

    df2 = df / 2
    orcha.add_table('test_table2', df2)

    @orcha.model()
    def test_model(test_table, test_column='test_table2.b'):
        tt = test_table.to_frame()
        test_table['a'] = tt['a'] + tt['b']
        pdt.assert_series_equal(test_column, df2['b'])

    with pytest.raises(KeyError):
        orcha.get_model('asdf')

    model = orcha.get_model('test_model')
    assert model._tables_used() == set(['test_table', 'test_table2'])
    model()

    table = orcha.get_table('test_table')
    pdt.assert_frame_equal(
        table.to_frame(),
        pd.DataFrame(
            {'a': [5, 7, 9],
             'b': [4, 5, 6]},
            index=['x', 'y', 'z']))

    assert orcha.list_models() == ['test_model']


def test_model_run(df):
    orcha.add_table('test_table', df)

    @orcha.table()
    def table_func(test_table):
        tt = test_table.to_frame()
        tt['c'] = [7, 8, 9]
        return tt

    @orcha.column('table_func')
    def new_col(test_table, table_func):
        tt = test_table.to_frame()
        tf = table_func.to_frame(columns=['c'])
        return tt['a'] + tt['b'] + tf['c']

    @orcha.model()
    def test_model1(year, test_table, table_func):
        tf = table_func.to_frame(columns=['new_col'])
        test_table[year] = tf['new_col'] + year

    @orcha.model('test_model2')
    def asdf(table='test_table'):
        tt = table.to_frame()
        table['a'] = tt['a'] ** 2

    orcha.run(models=['test_model1', 'test_model2'], years=[2000, 3000])

    test_table = orcha.get_table('test_table')
    assert_frames_equal(
        test_table.to_frame(),
        pd.DataFrame(
            {'a': [1, 16, 81],
             'b': [4, 5, 6],
             2000: [2012, 2015, 2018],
             3000: [3012, 3017, 3024]},
            index=['x', 'y', 'z']))

    m = orcha.get_model('test_model1')
    assert set(m._tables_used()) == {'test_table', 'table_func'}


def test_get_broadcasts():
    orcha.broadcast('a', 'b')
    orcha.broadcast('b', 'c')
    orcha.broadcast('z', 'b')
    orcha.broadcast('f', 'g')

    with pytest.raises(ValueError):
        orcha._get_broadcasts(['a', 'b', 'g'])

    assert set(orcha._get_broadcasts(['a', 'b', 'c', 'z']).keys()) == \
        {('a', 'b'), ('b', 'c'), ('z', 'b')}
    assert set(orcha._get_broadcasts(['a', 'b', 'z']).keys()) == \
        {('a', 'b'), ('z', 'b')}
    assert set(orcha._get_broadcasts(['a', 'b', 'c']).keys()) == \
        {('a', 'b'), ('b', 'c')}

    assert set(orcha.list_broadcasts()) == \
        {('a', 'b'), ('b', 'c'), ('z', 'b'), ('f', 'g')}


def test_collect_variables(df):
    orcha.add_table('df', df)

    @orcha.table()
    def df_func():
        return df

    @orcha.column('df')
    def zzz():
        return df['a'] / 2

    orcha.add_injectable('answer', 42)

    @orcha.injectable()
    def injected():
        return 'injected'

    @orcha.table('source table', cache=True)
    def source():
        return df

    with pytest.raises(KeyError):
        orcha._collect_variables(['asdf'])

    with pytest.raises(KeyError):
        orcha._collect_variables(names=['df'], expressions=['asdf'])

    names = ['df', 'df_func', 'answer', 'injected', 'source_label', 'df_a']
    expressions = ['source table', 'df.a']
    things = orcha._collect_variables(names, expressions)

    assert set(things.keys()) == set(names)
    assert isinstance(things['source_label'], orcha.DataFrameWrapper)
    pdt.assert_frame_equal(things['source_label'].to_frame(), df)
    assert isinstance(things['df_a'], pd.Series)
    pdt.assert_series_equal(things['df_a'], df['a'])


def test_collect_variables_expression_only(df):
    @orcha.table()
    def table():
        return df

    vars = orcha._collect_variables(['a'], ['table.a'])
    pdt.assert_series_equal(vars['a'], df.a)


def test_injectables():
    orcha.add_injectable('answer', 42)

    @orcha.injectable()
    def func1(answer):
        return answer * 2

    @orcha.injectable('func2', autocall=False)
    def asdf(variable='x'):
        return variable / 2

    @orcha.injectable()
    def func3(func2):
        return func2(4)

    @orcha.injectable()
    def func4(func='func1'):
        return func / 2

    assert orcha._INJECTABLES['answer'] == 42
    assert orcha._INJECTABLES['func1']() == 42 * 2
    assert orcha._INJECTABLES['func2'](4) == 2
    assert orcha._INJECTABLES['func3']() == 2
    assert orcha._INJECTABLES['func4']() == 42

    assert orcha.get_injectable('answer') == 42
    assert orcha.get_injectable('func1') == 42 * 2
    assert orcha.get_injectable('func2')(4) == 2
    assert orcha.get_injectable('func3') == 2
    assert orcha.get_injectable('func4') == 42

    with pytest.raises(KeyError):
        orcha.get_injectable('asdf')

    assert set(orcha.list_injectables()) == \
        {'answer', 'func1', 'func2', 'func3', 'func4'}


def test_injectables_combined(df):
    @orcha.injectable()
    def column():
        return pd.Series(['a', 'b', 'c'], index=df.index)

    @orcha.table()
    def table():
        return df

    @orcha.model()
    def model(table, column):
        df = table.to_frame()
        df['new'] = column
        orcha.add_table('table', df)

    orcha.run(models=['model'])

    table_wr = orcha.get_table('table').to_frame()

    pdt.assert_frame_equal(table_wr[['a', 'b']], df)
    pdt.assert_series_equal(table_wr['new'], column())


def test_injectables_cache():
    x = 2

    @orcha.injectable(autocall=True, cache=True)
    def inj():
        return x * x

    def i():
        return orcha._INJECTABLES['inj']

    assert i()() == 4
    x = 3
    assert i()() == 4
    i().clear_cached()
    assert i()() == 9
    x = 4
    assert i()() == 9
    orcha.clear_cache()
    assert i()() == 16
    x = 5
    assert i()() == 16
    orcha.add_injectable('inj', inj, autocall=True, cache=True)
    assert i()() == 25


def test_injectables_cache_disabled():
    x = 2

    @orcha.injectable(autocall=True, cache=True)
    def inj():
        return x * x

    def i():
        return orcha._INJECTABLES['inj']

    orcha.disable_cache()

    assert i()() == 4
    x = 3
    assert i()() == 9

    orcha.enable_cache()

    assert i()() == 9
    x = 4
    assert i()() == 9

    orcha.disable_cache()
    assert i()() == 16


def test_memoized_injectable():
    outside = 'x'

    @orcha.injectable(autocall=False, memoize=True)
    def x(s):
        return outside + s

    assert 'x' in orcha._MEMOIZED

    def getx():
        return orcha.get_injectable('x')

    assert hasattr(getx(), 'cache')
    assert hasattr(getx(), 'clear_cached')

    assert getx()('y') == 'xy'
    outside = 'z'
    assert getx()('y') == 'xy'

    getx().clear_cached()

    assert getx()('y') == 'zy'


def test_memoized_injectable_cache_off():
    outside = 'x'

    @orcha.injectable(autocall=False, memoize=True)
    def x(s):
        return outside + s

    def getx():
        return orcha.get_injectable('x')('y')

    orcha.disable_cache()

    assert getx() == 'xy'
    outside = 'z'
    assert getx() == 'zy'

    orcha.enable_cache()
    outside = 'a'

    assert getx() == 'zy'

    orcha.disable_cache()

    assert getx() == 'ay'


def test_clear_cache_all(df):
    @orcha.table(cache=True)
    def table():
        return df

    @orcha.column('table', cache=True)
    def z(table):
        return df.a

    @orcha.injectable(cache=True)
    def x():
        return 'x'

    @orcha.injectable(autocall=False, memoize=True)
    def y(s):
        return s + 'y'

    orcha.eval_variable('table.z')
    orcha.eval_variable('x')
    orcha.get_injectable('y')('x')

    assert orcha._TABLE_CACHE.keys() == ['table']
    assert orcha._COLUMN_CACHE.keys() == [('table', 'z')]
    assert orcha._INJECTABLE_CACHE.keys() == ['x']
    assert orcha._MEMOIZED['y'].value.cache == {(('x',), None): 'xy'}

    orcha.clear_cache()

    assert orcha._TABLE_CACHE == {}
    assert orcha._COLUMN_CACHE == {}
    assert orcha._INJECTABLE_CACHE == {}
    assert orcha._MEMOIZED['y'].value.cache == {}


def test_clear_cache_scopes(df):
    @orcha.table(cache=True, cache_scope='forever')
    def table():
        return df

    @orcha.column('table', cache=True, cache_scope='iteration')
    def z(table):
        return df.a

    @orcha.injectable(cache=True, cache_scope='step')
    def x():
        return 'x'

    @orcha.injectable(autocall=False, memoize=True, cache_scope='iteration')
    def y(s):
        return s + 'y'

    orcha.eval_variable('table.z')
    orcha.eval_variable('x')
    orcha.get_injectable('y')('x')

    assert orcha._TABLE_CACHE.keys() == ['table']
    assert orcha._COLUMN_CACHE.keys() == [('table', 'z')]
    assert orcha._INJECTABLE_CACHE.keys() == ['x']
    assert orcha._MEMOIZED['y'].value.cache == {(('x',), None): 'xy'}

    orcha.clear_cache(scope='step')

    assert orcha._TABLE_CACHE.keys() == ['table']
    assert orcha._COLUMN_CACHE.keys() == [('table', 'z')]
    assert orcha._INJECTABLE_CACHE == {}
    assert orcha._MEMOIZED['y'].value.cache == {(('x',), None): 'xy'}

    orcha.clear_cache(scope='iteration')

    assert orcha._TABLE_CACHE.keys() == ['table']
    assert orcha._COLUMN_CACHE == {}
    assert orcha._INJECTABLE_CACHE == {}
    assert orcha._MEMOIZED['y'].value.cache == {}

    orcha.clear_cache(scope='forever')

    assert orcha._TABLE_CACHE == {}
    assert orcha._COLUMN_CACHE == {}
    assert orcha._INJECTABLE_CACHE == {}
    assert orcha._MEMOIZED['y'].value.cache == {}


def test_cache_scope(df):
    orcha.add_injectable('x', 11)
    orcha.add_injectable('y', 22)
    orcha.add_injectable('z', 33)
    orcha.add_injectable('iterations', 1)

    @orcha.injectable(cache=True, cache_scope='forever')
    def a(x):
        return x

    @orcha.injectable(cache=True, cache_scope='iteration')
    def b(y):
        return y

    @orcha.injectable(cache=True, cache_scope='step')
    def c(z):
        return z

    @orcha.model()
    def m1(year, a, b, c):
        orcha.add_injectable('x', year + a)
        orcha.add_injectable('y', year + b)
        orcha.add_injectable('z', year + c)

        assert a == 11

    @orcha.model()
    def m2(year, a, b, c, iterations):
        assert a == 11
        if year == 1000:
            assert b == 22
            assert c == 1033
        elif year == 2000:
            assert b == 1022
            assert c == 3033

        orcha.add_injectable('iterations', iterations + 1)

    orcha.run(['m1', 'm2'], years=[1000, 2000])


def test_table_func_local_cols(df):
    @orcha.table()
    def table():
        return df
    orcha.add_column(
        'table', 'new', pd.Series(['a', 'b', 'c'], index=df.index))

    assert orcha.get_table('table').local_columns == ['a', 'b']


def test_is_table(df):
    orcha.add_table('table', df)
    assert orcha._is_table('table') is True
    assert orcha._is_table('asdf') is False


@pytest.fixture
def store_name(request):
    fname = tempfile.NamedTemporaryFile(suffix='.h5').name

    def fin():
        if os.path.isfile(fname):
            os.remove(fname)
    request.addfinalizer(fin)

    return fname


def test_write_tables(df, store_name):
    orcha.add_table('table', df)

    @orcha.model()
    def model(table):
        pass

    orcha.write_tables(store_name, ['model'], None)

    with pd.get_store(store_name, mode='r') as store:
        assert 'table' in store
        pdt.assert_frame_equal(store['table'], df)

    orcha.write_tables(store_name, ['model'], 1969)

    with pd.get_store(store_name, mode='r') as store:
        assert '1969/table' in store
        pdt.assert_frame_equal(store['1969/table'], df)


def test_run_and_write_tables(df, store_name):
    orcha.add_table('table', df)

    def year_key(y):
        return '{}'.format(y)

    def series_year(y):
        return pd.Series([y] * 3, index=df.index)

    @orcha.model()
    def model(year, table):
        table[year_key(year)] = series_year(year)

    orcha.run(['model'], years=range(11), data_out=store_name, out_interval=3)

    with pd.get_store(store_name, mode='r') as store:
        for year in range(3, 11, 3):
            key = '{}/table'.format(year)
            assert key in store

            for x in range(year):
                pdt.assert_series_equal(
                    store[key][year_key(x)], series_year(x))

        assert 'base/table' in store

        for x in range(11):
            pdt.assert_series_equal(
                store['final/table'][year_key(x)], series_year(x))


def test_get_table(df):
    orcha.add_table('frame', df)

    @orcha.table()
    def table():
        return df

    @orcha.table(cache=True)
    def source():
        return df

    fr = orcha.get_table('frame')
    ta = orcha.get_table('table')
    so = orcha.get_table('source')

    with pytest.raises(KeyError):
        orcha.get_table('asdf')

    assert isinstance(fr, orcha.DataFrameWrapper)
    assert isinstance(ta, orcha.DataFrameWrapper)
    assert isinstance(so, orcha.DataFrameWrapper)

    pdt.assert_frame_equal(fr.to_frame(), df)
    pdt.assert_frame_equal(ta.to_frame(), df)
    pdt.assert_frame_equal(so.to_frame(), df)


def test_cache_disabled_cm():
    x = 3

    @orcha.injectable(cache=True)
    def xi():
        return x

    assert orcha.get_injectable('xi') == 3
    x = 5
    assert orcha.get_injectable('xi') == 3

    with orcha.cache_disabled():
        assert orcha.get_injectable('xi') == 5

    # cache still gets updated even when cacheing is off
    assert orcha.get_injectable('xi') == 5


def test_injectables_cm():
    orcha.add_injectable('a', 'a')
    orcha.add_injectable('b', 'b')
    orcha.add_injectable('c', 'c')

    with orcha.injectables():
        assert orcha._INJECTABLES == {
            'a': 'a', 'b': 'b', 'c': 'c'
        }

    with orcha.injectables(c='d', x='x', y='y', z='z'):
        assert orcha._INJECTABLES == {
            'a': 'a', 'b': 'b', 'c': 'd',
            'x': 'x', 'y': 'y', 'z': 'z'
        }

    assert orcha._INJECTABLES == {
        'a': 'a', 'b': 'b', 'c': 'c'
    }


def test_is_expression():
    assert orcha.is_expression('name') is False
    assert orcha.is_expression('table.column') is True


def test_eval_variable(df):
    orcha.add_injectable('x', 3)
    assert orcha.eval_variable('x') == 3

    @orcha.injectable()
    def func(x):
        return 'xyz' * x
    assert orcha.eval_variable('func') == 'xyzxyzxyz'
    assert orcha.eval_variable('func', x=2) == 'xyzxyz'

    @orcha.table()
    def table(x):
        return df * x
    pdt.assert_series_equal(orcha.eval_variable('table.a'), df.a * 3)


def test_eval_model(df):
    orcha.add_injectable('x', 3)

    @orcha.model()
    def model(x):
        return df * x

    pdt.assert_frame_equal(orcha.eval_model('model'), df * 3)
    pdt.assert_frame_equal(orcha.eval_model('model', x=5), df * 5)


def test_always_dataframewrapper(df):
    @orcha.table()
    def table():
        return df / 2

    @orcha.table()
    def table2(table):
        assert isinstance(table, orcha.DataFrameWrapper)
        return table.to_frame() / 2

    result = orcha.eval_variable('table2')
    pdt.assert_frame_equal(result.to_frame(), df / 4)
