import marimo

__generated_with = "0.11.13"
app = marimo.App()


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %load_ext autoreload
    # '%autoreload 2' command supported automatically in marimo
    # '%matplotlib inline' command supported automatically in marimo

    # update import path
    import os, sys
    sys.path.insert(1, os.path.join(sys.path[0], '..', 'src'))

    import io
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import train_test_split

    # import keras modules
    import keras
    from keras.models import Sequential
    from keras.layers import Dense, Dropout
    from keras import optimizers
    from keras import losses
    return (
        Dense,
        Dropout,
        Sequential,
        io,
        keras,
        losses,
        mean_absolute_error,
        np,
        optimizers,
        os,
        pd,
        plt,
        sys,
        train_test_split,
    )


@app.cell
def _(os, pd):
    # read csv
    data = pd.read_csv(os.path.join('..', 'data', 'datasets', 'log_steering.csv'), index_col=0)

    # make datetime index (could also be done directly in read_csv)
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    data = data.dropna()
    print (data.shape)
    data.head()
    return (data,)


@app.cell
def _(data):
    # show the boat approaching the target course
    data['target_angle'][:2000].plot()
    data['boat_angle'][:2000].plot()
    return


@app.cell
def _(Sequential, data, mean_absolute_error, train_test_split):
    # select features and target
    y = data['rudder_angle']

    ### CHOOSE FEATURES TO USE ###
    x = data[[...]]

    # split test/train sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.10, random_state=42)

    # create model
    model = Sequential([
        ### ADD YOUR LAYERS HERE ###
    ])

    ### CHOOSE LOSS FUNCTION AND OPTIMIZER ###
    model.compile(loss='...', optimizer='...')

    # show summary of the model
    model.summary()

    # fit model to training data
    model.fit(x_train, y_train, validation_split=0.2, epochs=20)

    # show performance
    pred_y = model.predict(x_test)
    print (mean_absolute_error(pred_y, y_test))
    return model, pred_y, x, x_test, x_train, y, y_test, y_train


@app.cell
def _(model, os):
    # save model to file
    model.save(os.path.join('..', 'src', 'strategies', 'my_ml_strategy', 'my-keras-model.h5'))
    return


if __name__ == "__main__":
    app.run()
