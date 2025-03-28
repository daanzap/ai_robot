import marimo

__generated_with = "0.11.13"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Import libraries
        """
    )
    return


@app.cell
def _():
    # '%matplotlib inline' command supported automatically in marimo

    # importing pandas and numpy
    import pandas as pd
    import numpy as np

    import matplotlib.pyplot as plt
    import os
    from ipyfilechooser import FileChooser
    return FileChooser, np, os, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Import log file
        """
    )
    return


@app.cell
def _(FileChooser, display):
    fc = FileChooser()
    display(fc)
    return (fc,)


@app.cell
def _(fc, pd):
    # load logfile into a Pandas dataframe
    # dit stukje geven
    df = pd.read_csv(fc.selected,
                       index_col='datetime', parse_dates=True).drop(['Unnamed: 0'], axis=1)

    df.info()
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        * angle_of_attack: wind direction relative to the boat
        > * A positive angle of attack means the wind is blowing onto the right (starboard) side of the boat
        > * A negative angle of attack means the wind is blowing onto the left (port) side of the boat
        * boat_angle: compass direction in which the boat is going (North==0/360, East==90, South==180, West==270)
        * boat_heel: heeling angle in degrees (rotation around the longitudinal axis).
        * boat_speed: speed in knots (5 knots is 9.26 km per hr)
        * course_error: difference between boat_angle and target_angle
        * rudder_angle: position of the rudder relative to centerline of the boat
        * target_angle: compass direction in which you want to go
        * wind_direction: direction from where the wind is coming
        * wind_speed: wind speed in knots
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Look at a sample of the dataset
        """
    )
    return


@app.cell
def _(df):
    # Print the first 5 rows of the dataframe
    # YOUR CODE HERE
    df.head()
    return


@app.cell
def _(df):
    # Print the last 5 rows of the dataframe
    # YOUR CODE HERE
    df.tail()
    return


@app.cell
def _():
    # If you want you can look at more rows or try different slices
    # YOUR CODE HERE
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Plotting the columns
        First we will have a visual look at the data.
        """
    )
    return


@app.cell
def _(df):
    # Put the columns in a list named 'columns'
    # YOUR CODE HERE
    columns = list(df)
    return (columns,)


@app.cell
def _(columns, df, plt):
    for column in columns:
        (_, _ax) = plt.subplots(figsize=(20, 10))
        _ax.set_title(column)
        df[column].plot(ax=_ax)
        plt.grid(True)
    return (column,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Zoom in on column rudder_angle (and clip it's maximum value)
        Our AI Captain would like to control the rudder angle of the boat. Let's zoom in on this column in the dataset
        """
    )
    return


@app.cell
def _(df, plt):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    df['rudder_angle'].plot(ax=_ax)
    plt.grid(True)
    return


@app.cell
def _(df):
    # Select an interval of 1000 rows (these are 1000 datapoints) and put it in a new dataframe called 'selection'
    # YOUR CODE HERE
    selection_1k = df.iloc[0:1000]
    return (selection_1k,)


@app.cell
def _(plt, selection_1k):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    selection_1k['rudder_angle'].plot(ax=_ax)
    plt.grid(True)
    return


@app.cell
def _(df, plt):
    selection_10k = df.iloc[0:10 ** 4]
    (_, _ax) = plt.subplots(figsize=(20, 10))
    selection_10k['rudder_angle'].plot(ax=_ax)
    plt.grid(True)
    return (selection_10k,)


@app.cell
def _(df):
    # Find the maximum and minimum values for rudder_angle in the entire dataset
    # YOUR CODE HERE
    df.rudder_angle.max(), df.rudder_angle.min()
    return


@app.cell
def _(df):
    # Clip rudder_angle to [-20, 20]; i.e. set angles > 20 to 20 & angles < -20 to -20
    # YOUR CODE HERE
    df["rudder_angle"] = df["rudder_angle"].mask(df["rudder_angle"] > 20, 20)
    df["rudder_angle"] = df["rudder_angle"].mask(df["rudder_angle"] < -20, -20)
    return


@app.cell
def _(df, plt):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    df[(df.index.hour == 9) & (df.index.minute == 21)]['rudder_angle'].plot(ax=_ax)
    plt.grid(True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Boat_speed (noisy signal)
        """
    )
    return


@app.cell
def _(plt, selection_10k):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    selection_10k['boat_speed'].plot(ax=_ax)
    plt.grid(True)
    return


@app.cell
def _(plt, selection_10k):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    selection_10k['boat_speed'].rolling(20).mean().plot(ax=_ax)
    plt.grid(True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Removing outliers from wind_speed
        """
    )
    return


@app.cell
def _(plt, selection_10k):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    selection_10k['wind_speed'].plot(ax=_ax)
    plt.grid(True)
    return


@app.cell
def _(df, np):
    # The big wind_speed values are not realistic. We will define wind_speed's above 35 knots as outliers
    # Replace outliers in wind_speed with np.nan (use mask)
    # df["wind_speed"] = YOUR CODE HERE
    df["wind_speed"] = df["wind_speed"].mask(df["wind_speed"] > 35, np.nan)
    return


@app.cell
def _(df, plt):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    df.iloc[0:1000]['wind_speed'].plot(ax=_ax)
    plt.grid(True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Removing NA's
        """
    )
    return


@app.cell
def _(df):
    # Find the columns that contain NA's
    # YOUR CODE HERE
    df.isna().sum()
    return


@app.cell
def _(df):
    # Replace the NA's in each column with the last valid observation
    # Can you think of a reason why this makes more sense here then replace with mean value?
    df['boat_heel'].fillna(method='ffill', inplace=True)
    df['target_angle'].fillna(method='ffill', inplace=True)
    df['wind_speed'].fillna(method='ffill', inplace=True)
    return


@app.cell
def _(df):
    df.isna().sum().sum()
    # This should show 0
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Creating a new feature
        You can create your own features based on the existing columns.
        In sailing VMG is used a lot.
        VMG stands for Velocity Made Good and is defined as the the velocity component in the directing where you want to be going.
        Maybe this feature will help our machine learning algorithm.
        """
    )
    return


@app.cell
def _(df, np):
    df['VMG'] = df.boat_speed * np.cos(np.deg2rad(df.course_error))
    df_1 = df[['wind_speed', 'wind_direction', 'angle_of_attack', 'boat_heel', 'boat_speed', 'VMG', 'target_angle', 'boat_angle', 'course_error', 'rudder_angle']]
    return (df_1,)


@app.cell
def _(df_1, plt):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    df_1.iloc[0:1000].boat_speed.plot(ax=_ax)
    df_1.iloc[0:1000].VMG.plot(ax=_ax)
    plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Plotting correlation matrix
        """
    )
    return


@app.cell
def _(df_1):
    corr = df_1.corr()
    corr.style.background_gradient()
    return (corr,)


@app.cell
def _(df_1, plt):
    (_, _ax) = plt.subplots(figsize=(20, 10))
    df_1.iloc[0:1000].plot(ax=_ax)
    plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        Notice that the range of the values can differ quite a lot per column
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### What did you learn?
        In this notebook you have:
        * Clipped the values of rudder_angle to [-20, 20]
        * Used rolling mean to vizualize boat speed signal
        * Replaced outliers in wind_speed
        * Replaced NA's in boat_heel and target_angle
        * Added a new feature
        * Looked at the correlation matrix
        """
    )
    return


@app.cell
def _(df_1):
    df_1.to_pickle('data_clean.pkl')
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
