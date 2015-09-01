Example
=======

The following is a very simple example of an Orca pipeline with none of the
optional features such as caching:

.. code-block:: python

    import orca
    import pandas as pd


    @orca.injectable()
    def data_file():
        return 'data.csv'


    @orca.table()
    def raw_data(data_file):
        return pd.read_csv(data_file)


    @orca.table()
    def processed(raw_data):
        # do fancy stuff
        return processed_data

    @orca.step()
    def save_data(processed, data_file):
        processed.to_csv('processed_' + data_file)

    @orca.step()
    def save_fig(processed):
        # save fancy figure

    orca.run(['save_data', 'save_fig'])

By declaring the data dependencies of your functions you can let Orca
thread them all together instead of doing it manually yourself.

The iterative capabilities of Orca are illustrated by imagining that there
are many data files to be processed::

    @orca.injectable()
    def data_file(iter_var):
        return iter_var

    # everything else the same as above

    files = glob.glob('*.csv')
    orca.run(['save_data', 'save_fig'], iter_vars=files)

A more involved example is available at
https://gist.github.com/jiffyclub/2a252333c8dcad1b99aa.
