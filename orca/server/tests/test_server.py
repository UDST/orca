import json

import orca
import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from .. import server


@pytest.fixture
def tapp():
    server.app.config['TESTING'] = True
    return server.app.test_client()


@pytest.fixture(scope='module')
def dfa():
    return pd.DataFrame(
        {'a': [100, 200, 300, 200, 100]},
        index=['v', 'w', 'x', 'y', 'z'])


@pytest.fixture(scope='module')
def dfb():
    return pd.DataFrame(
        {'b': [70, 80, 90],
         'a_id': ['w', 'v', 'z']},
        index=['a', 'b', 'b'])


@pytest.fixture(scope='module')
def dfa_col(dfa):
    return pd.Series([2, 4, 6, 8, 10], index=dfa.index)


@pytest.fixture(scope='module')
def dfb_col(dfb):
    return pd.Series([10, 20, 30], index=dfb.index)


@pytest.fixture(scope='module')
def dfa_factor():
    return 0.5


@pytest.fixture(scope='module')
def dfb_factor():
    return 2


@pytest.fixture(scope='module', autouse=True)
def setup_orca(dfa, dfb, dfa_col, dfb_col, dfa_factor, dfb_factor):
    orca.add_injectable('a_factor', dfa_factor)

    @orca.injectable()
    def b_factor():
        return dfb_factor

    orca.add_table('dfa', dfa)

    @orca.table('dfb')
    def dfb_table():
        return dfb

    orca.add_column('dfa', 'acol', dfa_col)
    orca.add_column('dfb', 'bcol', dfb_col)

    @orca.column('dfa')
    def extra_acol(a_factor):
        return dfa_col * a_factor

    @orca.column('dfb')
    def extra_bcol(b_factor):
        return dfb_col * b_factor

    orca.broadcast('dfb', 'dfa', cast_on='a_id', onto_index=True)

    @orca.step()
    def test_step(dfa, dfb):
        pass


def test_schema(tapp):
    rv = tapp.get('/schema')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert set(data['tables']) == {'dfa', 'dfb'}
    assert set(data['columns']['dfa']) == {'extra_acol', 'acol', 'a'}
    assert set(data['columns']['dfb']) == {'bcol', 'extra_bcol', 'a_id', 'b'}
    assert data['steps'] == ['test_step']
    assert set(data['injectables']) == {'a_factor', 'b_factor'}
    assert data['broadcasts'] == [['dfb', 'dfa']]


def test_list_tables(tapp):
    rv = tapp.get('/tables')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert set(data['tables']) == {'dfa', 'dfb'}


def test_table_info(tapp):
    rv = tapp.get('/tables/dfa/info')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')

    assert 'extra_acol' in data


def test_table_preview(tapp):
    rv = tapp.get('/tables/dfa/preview')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')

    assert data == orca.get_table('dfa').to_frame().to_json(orient='split')


def test_table_preview_404(tapp):
    rv = tapp.get('/tables/not_a_table/preview')
    assert rv.status_code == 404


def test_table_describe(tapp):
    rv = tapp.get('/tables/dfa/describe')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')

    assert data == (orca.get_table('dfa')
                        .to_frame()
                        .describe()
                        .to_json(orient='split'))


def test_table_definition_frame(tapp):
    rv = tapp.get('/tables/dfa/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'type': 'dataframe'}


def test_table_definition_func(tapp):
    rv = tapp.get('/tables/dfb/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data['type'] == 'function'
    assert data['filename'].endswith('test_server.py')
    assert isinstance(data['lineno'], int)
    assert data['text'] == (
        "    @orca.table('dfb')\n"
        "    def dfb_table():\n"
        "        return dfb\n")
    assert 'dfb_table' in data['html']


def test_table_csv(tapp):
    rv = tapp.get('/tables/dfb/csv')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')

    assert rv.mimetype == 'text/csv'
    assert data == orca.get_table('dfb').to_frame().to_csv()


def test_list_table_columns(tapp):
    rv = tapp.get('/tables/dfb/columns')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert set(data['columns']) == {'a_id', 'b', 'bcol', 'extra_bcol'}


def test_column_definition_local(tapp):
    rv = tapp.get('/tables/dfa/columns/a/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'type': 'local'}


def test_column_definition_series(tapp):
    rv = tapp.get('/tables/dfa/columns/acol/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'type': 'series'}


def test_column_definition_func(tapp):
    rv = tapp.get('/tables/dfa/columns/extra_acol/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data['type'] == 'function'
    assert data['filename'].endswith('test_server.py')
    assert isinstance(data['lineno'], int)
    assert data['text'] == (
        "    @orca.column('dfa')\n"
        "    def extra_acol(a_factor):\n"
        "        return dfa_col * a_factor\n")
    assert 'extra_acol' in data['html']


def test_column_describe(tapp):
    rv = tapp.get('/tables/dfa/columns/extra_acol/describe')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')

    assert data == (orca.get_table('dfa')
                        .extra_acol.describe()
                        .to_json(orient='split'))


def test_column_csv(tapp, dfa):
    rv = tapp.get('/tables/dfa/columns/a/csv')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')
    assert data == dfa.a.to_csv(path_or_buf=None)


def test_no_column_404(tapp):
    rv = tapp.get('/tables/dfa/columns/not-a-column/csv')
    assert rv.status_code == 404


def test_list_injectables(tapp):
    rv = tapp.get('/injectables')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert set(data['injectables']) == {'a_factor', 'b_factor'}


def test_injectable_repr(tapp, dfb_factor):
    rv = tapp.get('/injectables/b_factor/repr')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'type': str(type(42)), 'repr': '2'}


def test_no_injectable_404(tapp):
    rv = tapp.get('/injectables/nope/repr')
    assert rv.status_code == 404


def test_injectable_definition_var(tapp):
    rv = tapp.get('/injectables/a_factor/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'type': 'variable'}


def test_injectable_definition_func(tapp):
    rv = tapp.get('/injectables/b_factor/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data['type'] == 'function'
    assert data['filename'].endswith('test_server.py')
    assert isinstance(data['lineno'], int)
    assert data['text'] == (
        "    @orca.injectable()\n"
        "    def b_factor():\n"
        "        return dfb_factor\n")
    assert 'b_factor' in data['html']


def test_list_broadcasts(tapp):
    rv = tapp.get('/broadcasts')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'broadcasts': [{'cast': 'dfb', 'onto': 'dfa'}]}


def test_broadcast_definition(tapp):
    rv = tapp.get('/broadcasts/dfb/dfa/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {
        'cast': 'dfb',
        'onto': 'dfa',
        'cast_on': 'a_id',
        'onto_on': None,
        'cast_index': False,
        'onto_index': True}


def test_no_broadcast_404(tapp):
    rv = tapp.get('/broadcasts/table1/table2/definition')
    assert rv.status_code == 404


def test_list_steps(tapp):
    rv = tapp.get('/steps')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data == {'steps': ['test_step']}


def test_no_step_404(tapp):
    rv = tapp.get('/steps/not_a_step/definition')
    assert rv.status_code == 404


def test_step_definition(tapp):
    rv = tapp.get('/steps/test_step/definition')
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))

    assert data['filename'].endswith('test_server.py')
    assert isinstance(data['lineno'], int)
    assert data['text'] == (
        "    @orca.step()\n"
        "    def test_step(dfa, dfb):\n"
        "        pass\n")
    assert 'test_step' in data['html']


def test_table_groupbyagg_errors(tapp):
    # non-existant column
    rv = tapp.get('/tables/dfa/groupbyagg?column=notacolumn')
    assert rv.status_code == 400

    # both by and level missing
    rv = tapp.get('/tables/dfa/groupbyagg?column=a')
    assert rv.status_code == 400

    # bad or missing agg type
    rv = tapp.get('/tables/dfa/groupbyagg?column=a&level=0&agg=notanagg')
    assert rv.status_code == 400


def test_table_groupbyagg_by_size(tapp):
    rv = tapp.get('/tables/dfa/groupbyagg?by=a&column=a&agg=size')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')
    test = pd.read_json(data, orient='split', typ='series')

    pdt.assert_series_equal(
        test,
        pd.Series([2, 2, 1], index=[100, 200, 300]),
        check_names=False)


def test_table_groupbyagg_level_mean(tapp):
    rv = tapp.get('/tables/dfb/groupbyagg?level=0&column=b&agg=mean')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')
    test = pd.read_json(data, orient='split', typ='series')

    pdt.assert_series_equal(
        test,
        pd.Series([70, 85], index=['a', 'b'], name='b'))


def test_table_groupbyagg_level_median(tapp):
    rv = tapp.get('/tables/dfb/groupbyagg?level=0&column=b&agg=median')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')
    test = pd.read_json(data, orient='split', typ='series')

    pdt.assert_series_equal(
        test,
        pd.Series([70, 85], index=['a', 'b'], name='b'))


def test_table_groupbyagg_level_sum(tapp):
    rv = tapp.get('/tables/dfb/groupbyagg?level=0&column=b&agg=sum')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')
    test = pd.read_json(data, orient='split', typ='series')

    pdt.assert_series_equal(
        test,
        pd.Series([70, 170], index=['a', 'b'], name='b'))


def test_table_groupbyagg_level_std(tapp):
    rv = tapp.get('/tables/dfb/groupbyagg?level=0&column=b&agg=std')
    assert rv.status_code == 200

    data = rv.data.decode('utf-8')
    test = pd.read_json(data, orient='split', typ='series')

    pdt.assert_series_equal(
        test,
        pd.Series(
            [np.nan, pd.Series([80, 90]).std()],
            index=['a', 'b'], name='b'))
