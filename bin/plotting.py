from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import functions as func
from . import widgets as mwidg


def conf_gcv(fig: plt.Figure, data):
    """
    Form of widgets to configure the input parameters to GCV
    :param fig: matplotlib figure in which to plot output
    :param data: array of data
    :param test: (bool) show test output?
    :return:
    """
    params_base = mwidg.ParamsForm(
        4, 2, 200
    )
    params_plot = mwidg.ParamsPlot(
        'GCV-fitted ALPS', 'Time', 'Thickness Change(m)'
    )

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        gcv = func.fit_gcv(
            data=data,
            p=params_base.p_value,
            q=params_base.q_value,
            num=params_base.num_value
        )

        fig.clear()
        ax = fig.subplots()

        plot(ax,
             points=[('Data', data), ],
             lines=[('Mean Prediction', gcv.xpred, gcv.ypred), ],
             fill=[
                 ('95% t-interval',
                  gcv.xpred,
                  gcv.ypred.flatten() - gcv.std_t,
                  gcv.ypred.flatten() + gcv.std_t),
             ],
             title=params_plot.title,
             x_label=params_plot.label_x,
             y_label=params_plot.label_y
             )

        out_data = {'gcv': gcv}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = mwidg.FormConfigIO(
        [params_base, params_plot,],
        update_func=update_plot,
        submit_text='Plot'
    )

    return form


def conf_reml(fig: plt.Figure, data):
    """
    Setup widgets to accept parameter inputs for REML fitting
    :param fig:
    :param data:
    :param test:
    :return:
    """
    params_base = mwidg.ParamsFormVar(
        5, 2, 200, 0.1, 0.1
    )
    params_plot = mwidg.ParamsPlot(
        'REML-fitted ALPS', 'Time', 'Thickness Change(m)'
    )

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        reml = func.fit_reml(
            data=data,
            p=params_base.p_value,
            q=params_base.q_value,
            num=params_base.num_value,
            par=(params_base.lam_value, params_base.error_value)
        )

        fig.clear()
        ax = fig.subplots()

        plot(ax,
             points=[('Data', data), ],
             lines=[('Mean Prediction', reml.xpred, reml.ypred), ],
             fill=[
                 ('95% t-interval',
                  reml.xpred,
                  reml.ypred.flatten() - reml.std_t,
                  reml.ypred.flatten() + reml.std_t),
             ],
             title=params_plot.title,
             x_label=params_plot.label_x,
             y_label=params_plot.label_y
             )

        out_data = {'reml': reml}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = mwidg.FormConfigIO(
        [params_base, params_plot,],
        update_func=update_plot,
        submit_text='Plot'
    )

    return form


def conf_two_stage(fig: plt.Figure, data):
    """
    Fitting and plotting using two-stage strategy
    :param fig:
    :param data:
    :param test:
    :return:
    """
    params_base = mwidg.ParamsFormScale(
        4, 2, 300, 3.0, 1.2
    )
    params_plot1 = mwidg.ParamsPlot(
        'One-step', 'Time', 'Thickness Change(m)',
        'Plot 1 labels'
    )
    params_plot2 = mwidg.ParamsPlot(
        'Two-step', 'Time', 'Thickness Change(m)',
        'Plot 2 labels'
    )

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        clean, out = func.Outlier(
            data, params_base.scale1_value, params_base.scale2_value
        )

        # GCV fit of original data
        gcv_o = func.fit_gcv(
            data=data,
            p=params_base.p_value,
            q=params_base.q_value,
            num=params_base.num_value
        )
        # GCV fit of clean data
        gcv_c = func.fit_gcv(
            data=clean,
            p=params_base.p_value,
            q=params_base.q_value,
            num=params_base.num_value
        )

        fig.clear()
        ax1, ax2 = fig.subplots(1, 2)

        plot(ax1,
             points=[('Data', data), ],
             lines=[('With full data', gcv_o.xpred, gcv_o.ypred), ],
             fill=[
                 ('95% t-interval',
                  gcv_o.xpred,
                  gcv_o.ypred.flatten() - gcv_o.std_t,
                  gcv_o.ypred.flatten() + gcv_o.std_t),
             ],
             title=params_plot1.title,
             x_label=params_plot1.label_x,
             y_label=params_plot1.label_y
             )

        plot(ax2,
             points=[
                 ('Normal data', clean),
                 ('Outlier detected', out)
             ],
             lines=[
                 ('With full data', gcv_o.xpred, gcv_o.ypred),
                 ('Without outliers', gcv_c.xpred, gcv_c.ypred),
             ],
             fill=[
                 ('95% t-interval',
                  gcv_c.xpred,
                  gcv_c.ypred.flatten() - gcv_c.std_t,
                  gcv_c.ypred.flatten() + gcv_c.std_t),
             ],
             title=params_plot2.title,
             x_label=params_plot2.label_x,
             y_label=params_plot2.label_y
             )

        out_data = {'original_gcv': gcv_o, 'clean_gcv': gcv_c}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = mwidg.FormConfigIO(
        [params_base, params_plot1, params_plot2],
        update_func=update_plot,
        submit_text='Plot'
    )

    return form


def conf_mmf(fig: plt.Figure, data: np.ndarray):
    """Fitting and plotting using two-stage strategy"""
    params_base = mwidg.ParamsFormVar(
        4, 3, 200, 0.1, 0.1
    )
    params_plot1 = mwidg.ParamsPlot(
        'REML', 'Time', 'Thickness Change(m)',
        'Plot 1 labels'
    )
    params_plot2 = mwidg.ParamsPlot(
        'Split Frequency', 'Time', 'Thickness Change(m)',
        'Plot 2 labels'
    )

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        fig.clear()
        ax1, ax2 = fig.subplots(1, 2)

        # Fit the REML model
        reml = func.fit_reml(
            data=data,
            p=params_base.p_value,
            q=params_base.q_value,
            num=params_base.num_value,
            par=(params_base.lam_value, params_base.error_value)
        )

        plot(ax1,
             points=[('Data', data), ],
             lines=[('Mean Prediction', reml.xpred, reml.ypred), ],
             fill=[
                 ('95% t-interval',
                  reml.xpred,
                  reml.ypred.flatten() - reml.std_t,
                  reml.ypred.flatten() + reml.std_t),
             ],
             title=params_plot1.title,
             x_label=params_plot1.label_x,
             y_label=params_plot1.label_y
             )

        f_low, f_high = func.Inference_effects(
            params_base.q_value, data, reml.Cpred, reml.C, reml.lam, reml.D
        )
        plot(ax2,
             points=[('Data', data), ],
             lines=[
                 ('Low freq. signal', reml.xpred, f_low),
                 ('High freq. signal', reml.xpred, f_high),
             ],
             title=params_plot2.title,
             x_label=params_plot2.label_x,
             y_label=params_plot2.label_y
             )
        # TODO 6/25: verify y=0 should be constant
        ax2.axhline(
            y=0, color='k', linestyle=':',label='0 thickness change', lw=3
        )
        ax2.legend()

        out_data = {'reml': reml, 'freq_low': f_low, 'freq_high': f_high}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = mwidg.FormConfigIO(
        [params_base, params_plot1, params_plot2],
        update_func=update_plot,
        submit_text='Plot'
    )

    return form


def plot(
        ax: plt.Axes,
        points: List[Tuple[str, np.ndarray]],
        lines: List[Tuple[Union[str, None], np.ndarray, np.ndarray]],
        fill: List[Tuple[str, np.ndarray, np.ndarray, np.ndarray]] = None,
        title: str = None,
        x_label: str = None,
        y_label: str = None):
    """
    Standardized method of plotting fitted ALPS models
    :param ax: matplotlib Axes
    :param points: scatter plot data;
      list of tuples (label, data points)
    :param lines: line data;
      list of tuples (label, x data, y data)
    :param fill: area on the plot to fill with color;
      list of tuples (label, x data, lower bound, upper bound)
    :param title: plot title
    :param x_label: x-axis label
    :param y_label: y-axis label
    :return:
    """
    # for d in y:
    #     ax.plot(x[0], d[0], linewidth=4, label='Mean Prediction')
    for label, x, y in lines:
        ax.plot(x, y, linewidth=4, label=label if label is not None else '')

    for label, d in points:
        if d.shape[0] == 0:
            ax.scatter([], [], label=label, s=100) # random color
            continue

        # ax.scatter(d[1][:, 0], d[1][:, 1], label=d[0], color='r', s=100)
        ax.scatter(d[:, 0], d[:, 1], label=label, s=100) # random color

    if fill is not None:
        for label, x, lb, ub in fill:
            ax.fill_between(
                x, lb, ub,
                alpha=0.2, color='k', label=label if label is not None else ''
            )

    ax.set_title(title if title is not None else '', size=25)
    ax.tick_params(axis='x', labelsize=19, labelrotation=30)
    ax.tick_params(axis='y', labelsize=19)
    ax.set_xlabel(x_label, size=25)
    ax.set_ylabel(y_label, size=25)

    ax.legend(fontsize=18)
    ax.grid(True)


if __name__ == '__main__':
    d = mwidg.DataSelector()
    _, btn_sample, _ = d.children[0].children
    btn_sample.click()

    btn_submit, _ = d.children[2].children
    btn_submit.click()

    f1 = plt.figure(figsize=(12, 7))
    form = conf_gcv(f1, d.data)

    params = form.children[0]
    params.num_value

    # btn_plot = form.children[3].children[0]
    # btn_plot.click()

