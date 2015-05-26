import imp
import os
import re
from functools import wraps
from operator import methodcaller

import orca
from flask import Flask, abort, jsonify, request
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

_GROUPBY_AGG_MAP = {
    'sum': methodcaller('sum'),
    'mean': methodcaller('mean'),
    'median': methodcaller('median'),
    'std': methodcaller('std'),
    'size': methodcaller('size')
}


def import_file(filename):
    """
    Import a file that will trigger the population of Orca.

    Parameters
    ----------
    filename : str

    """
    pathname, filename = os.path.split(filename)
    modname = re.match(
        r'(?P<modname>\w+)\.py', filename).group('modname')
    file, path, desc = imp.find_module(modname, [pathname])

    try:
        imp.load_module(modname, file, path, desc)
    finally:
        file.close()


def check_is_table(func):
    """
    Decorator that will check whether the "table_name" keyword argument
    to the wrapped function matches a registered Orca table.

    """
    @wraps(func)
    def wrapper(**kwargs):
        if not orca.is_table(kwargs['table_name']):
            abort(404)
        return func(**kwargs)
    return wrapper


def check_is_column(func):
    """
    Decorator that will check whether the "table_name" and "col_name"
    keyword arguments to the wrapped function match a registered Orca
    table and column.

    """
    @wraps(func)
    def wrapper(**kwargs):
        table_name = kwargs['table_name']
        col_name = kwargs['col_name']
        if not orca.is_table(table_name):
            abort(404)
        if col_name not in orca.get_table(table_name).columns:
            abort(404)

        return func(**kwargs)
    return wrapper


def check_is_injectable(func):
    """
    Decorator that will check whether the "inj_name" keyword argument to
    the wrapped function matches a registered Orca injectable.

    """
    @wraps(func)
    def wrapper(**kwargs):
        name = kwargs['inj_name']
        if not orca.is_injectable(name):
            abort(404)
        return func(**kwargs)
    return wrapper


@app.route('/schema')
def schema():
    """
    All tables, columns, steps, injectables and broadcasts registered with
    Orca. Includes local columns on tables.

    """
    tables = orca.list_tables()
    cols = {t: orca.get_table(t).columns for t in tables}
    steps = orca.list_steps()
    injectables = orca.list_injectables()
    broadcasts = orca.list_broadcasts()

    return jsonify(
        tables=tables, columns=cols, steps=steps, injectables=injectables,
        broadcasts=broadcasts)


@app.route('/tables')
def list_tables():
    tables = orca.list_tables()
    return jsonify(tables=tables)


@app.route('/tables/<table_name>/preview')
@check_is_table
def table_preview(table_name):
    """
    Returns the first five rows of a table as JSON. Inlcudes all columns.
    Uses Pandas' "split" JSON format.

    """
    preview = orca.get_table(table_name).to_frame().head()
    return (
        preview.to_json(orient='split', date_format='iso'),
        200,
        {'Content-Type': 'application/json'})


@app.route('/tables/<table_name>/describe')
@check_is_table
def table_describe(table_name):
    """
    Return summary statistics of a table as JSON. Includes all columns.
    Uses Pandas' "split" JSON format.

    """
    desc = orca.get_table(table_name).to_frame().describe()
    return (
        desc.to_json(orient='split', date_format='iso'),
        200,
        {'Content-Type': 'application/json'})


@app.route('/tables/<table_name>/definition')
@check_is_table
def table_definition(table_name):
    """
    Get the source of a table function.

    If a table is registered DataFrame and not a function then all that is
    returned is {'type': 'dataframe'}.

    If the table is a registered function then the JSON returned has keys
    "type", "filename", "lineno", "text", and "html". "text" is the raw
    text of the function, "html" has been marked up by Pygments.

    """
    if orca.table_type(table_name) == 'dataframe':
        return jsonify(type='dataframe')

    filename, lineno, source = \
        orca.get_raw_table(table_name).func_source_data()

    html = highlight(source, PythonLexer(), HtmlFormatter())

    return jsonify(
        type='function', filename=filename, lineno=lineno, text=source,
        html=html)


@app.route('/tables/<table_name>/csv')
@check_is_table
def table_csv(table_name):
    """
    Returns a table as text/csv using Pandas default csv output.

    """
    csv = orca.get_table(table_name).to_frame().to_csv()
    return csv, 200, {'Content-Type': 'text/csv'}


@app.route('/tables/<table_name>/groupbyagg')
@check_is_table
def table_groupbyagg(table_name):
    """
    Perform a groupby on a table and return an aggregation on a single column.

    This depends on some request parameters in the URL.
    "column" and "agg" must always be present, and one of "by" or "level"
    must be present. "column" is the table column on which aggregation will
    be performed, "agg" is the aggregation that will be performed, and
    "by"/"level" define how to group the data.

    Supported "agg" parameters are: mean, median, std, sum, and size.

    """
    table = orca.get_table(table_name)

    # column to aggregate
    column = request.args.get('column', None)
    if not column or column not in table.columns:
        abort(400)

    # column or index level to group by
    by = request.args.get('by', None)
    level = request.args.get('level', None)
    if (not by and not level) or (by and level):
        abort(400)

    # aggregation type
    agg = request.args.get('agg', None)
    if not agg or agg not in _GROUPBY_AGG_MAP:
        abort(400)

    column = table.get_column(column)

    # level can either be an integer level number or a string level name.
    # try converting to integer, but if that doesn't work
    # we go ahead with the string.
    if level:
        try:
            level = int(level)
        except ValueError:
            pass
        gby = column.groupby(level=level)
    else:
        by = table.get_column(by)
        gby = column.groupby(by)

    result = _GROUPBY_AGG_MAP[agg](gby)

    return (
        result.to_json(orient='split', date_format='iso'),
        200,
        {'Content-Type': 'application/json'})


@app.route('/tables/<table_name>/columns')
@check_is_table
def list_table_columns(table_name):
    return jsonify(columns=orca.get_table(table_name).columns)


@app.route('/tables/<table_name>/columns/<col_name>/definition')
@check_is_column
def column_definition(table_name, col_name):
    col_type = orca.get_table(table_name).column_type(col_name)

    if col_type != 'function':
        return jsonify(type=col_type)

    filename, lineno, source = \
        orca.get_raw_column(table_name, col_name).func_source_data()

    html = highlight(source, PythonLexer(), HtmlFormatter())

    return jsonify(
        type='function', filename=filename, lineno=lineno, text=source,
        html=html)


@app.route('/tables/<table_name>/columns/<col_name>/describe')
@check_is_column
def column_describe(table_name, col_name):
    col_desc = orca.get_table(table_name).get_column(col_name).describe()
    return (
        col_desc.to_json(orient='split'),
        200,
        {'Content-Type': 'application/json'})


@app.route('/tables/<table_name>/columns/<col_name>/csv')
@check_is_column
def column_csv(table_name, col_name):
    csv = orca.get_table(table_name).get_column(col_name).to_csv(path=None)
    return csv, 200, {'Content-Type': 'text/csv'}


@app.route('/injectables')
def list_injectables():
    return jsonify(injectables=orca.list_injectables())


@app.route('/injectables/<inj_name>/repr')
@check_is_injectable
def injectable_repr(inj_name):
    i = orca.get_injectable(inj_name)
    return jsonify(type=str(type(i)), repr=repr(i))


@app.route('/injectables/<inj_name>/definition')
@check_is_injectable
def injectable_definition(inj_name):
    inj_type = orca.injectable_type(inj_name)

    if inj_type == 'variable':
        return jsonify(type='variable')
    else:
        filename, lineno, source = \
            orca.get_injectable_func_source_data(inj_name)
        html = highlight(source, PythonLexer(), HtmlFormatter())
        return jsonify(
            type='function', filename=filename, lineno=lineno, text=source,
            html=html)


@app.route('/broadcasts')
def list_broadcasts():
    casts = [{'cast': b[0], 'onto': b[1]} for b in orca.list_broadcasts()]
    return jsonify(broadcasts=casts)


@app.route('/broadcasts/<cast_name>/<onto_name>/definition')
def broadcast_definition(cast_name, onto_name):
    if not orca.is_broadcast(cast_name, onto_name):
        abort(404)

    b = orca.get_broadcast(cast_name, onto_name)

    return jsonify(
        cast=b.cast, onto=b.onto, cast_on=b.cast_on, onto_on=b.onto_on,
        cast_index=b.cast_index, onto_index=b.onto_index)


@app.route('/steps')
def list_steps():
    return jsonify(steps=orca.list_steps())


@app.route('/steps/<step_name>/definition')
def step_definition(step_name):
    if not orca.is_step(step_name):
        abort(404)

    filename, lineno, source = \
        orca.get_step(step_name).func_source_data()
    html = highlight(source, PythonLexer(), HtmlFormatter())
    return jsonify(filename=filename, lineno=lineno, text=source, html=html)


if __name__ == '__main__':
    filename = 'precipout.py'
    import_file(filename)
    app.run(debug=True)
