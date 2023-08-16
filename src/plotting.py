import matplotlib.pyplot as plt
from hublib import ui
import numpy as np
from typing import List, Tuple, Union
from IPython.display import display, clear_output
import functions as func
import widgets


def conf_gcv(fig: plt.Figure, data, test=False):
    """
    Form of widgets to configure the input parameters to GCV
    :param fig: matplotlib figure in which to plot output
    :param data: array of data
    :param test: (bool) show test output?
    :return:
    """
    # validate input data
    valid = func.validate_data(data)

    # degree of bases
    p = ui.Integer(name='Degree of bases:', value=5)
    # order of penalty
    q = ui.Integer(name='Order of penalty:', value=2)
    # number of observations(?)
    num = ui.Integer(name='Number of observations:', value=200)

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        gcv = func.fit_gcv(
            data=valid,
            p=p.value,
            q=q.value,
            num=num.value
        )
        xpred, ypred, std_t = gcv['xpred'], gcv['ypred'], gcv['std_t']

        fig.clear()
        ax = fig.subplots()

        plot(ax,
             points=[('Data', valid), ],
             lines=[('Mean Prediction', xpred, ypred), ],
             fill=[
                 ('95% t-interval',
                  xpred,
                  ypred.flatten() - std_t,
                  ypred.flatten() + std_t),
             ],
             title='GCV fitted ALPS',
             x_label='Time',
             y_label='Thickness Change (m)'
             )

        display(fig)
        clear_output(wait=True)

        out_data = {'gcv': gcv}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = widgets.FormConfigIO(
        [p, q, num],
        update_func=update_plot,
        submit_text='Plot',
        test=test
    )

    return form


def conf_reml(fig: plt.Figure, data, test=False):
    """
    Setup widgets to accept parameter inputs for REML fitting
    :param fig:
    :param data:
    :param test:
    :return:
    """
    # validate input data
    valid = func.validate_data(data)

    # degree of bases
    p = ui.Integer(name='Degree of bases:', value=5)
    # order of penalty
    q = ui.Integer(name='Order of penalty:', value=2)
    # number of observations(TODO 6/21: verify)
    num = ui.Integer(name='Number of observations:', value=200)
    lambda_var = ui.Number(name='Lambda variance:', value=0.1)
    error_var = ui.Number(name='Error variance:', value=0.1)

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        reml = func.fit_reml(
            data=valid,
            p=p.value,
            q=q.value,
            num=num.value,
            par=(lambda_var.value, error_var.value)
        )

        xpred, ypred, std_t = reml['xpred'], reml['ypred'], reml['std_t']

        fig.clear()
        ax = fig.subplots()

        plot(ax,
             points=[('Data', valid), ],
             lines=[('Mean Prediction', xpred, ypred), ],
             fill=[
                 ('95% t-interval',
                  xpred,
                  ypred.flatten()-std_t,
                  ypred.flatten()+std_t),
             ],
             title='REML fitted ALPS',
             x_label='Time',
             y_label='Thickness Change (m)'
             )

        display(fig)
        clear_output(wait=True)

        out_data = {'reml': reml}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = widgets.FormConfigIO(
        [p, q, num, lambda_var, error_var],
        update_func=update_plot,
        submit_text='Plot',
        test=test
    )

    return form


def conf_two_stage(fig: plt.Figure, data, test=False):
    """
    Fitting and plotting using two-stage strategy
    :param fig:
    :param data:
    :param test:
    :return:
    """
    # validate input data
    valid = func.validate_data(data)

    # degree of bases
    p = ui.Integer(name='Degree of bases:', value=4)
    # order of penalty
    q = ui.Integer(name='Order of penalty:', value=2)
    # number of observations(TODO 6/21: verify)
    num = ui.Integer(name='Number of observations:', value=300)
    thresh1 = ui.Number(name='Scaling threshold 1:', value=3.0)
    thresh2 = ui.Number(name='Scaling threshold 2:', value=1.2)

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        clean, out = func.Outlier(valid, thresh1.value, thresh2.value)

        # GCV fit of original data
        gcv_o = func.fit_gcv(
            data=valid, p=p.value, q=q.value, num=num.value
        )
        # GCV fit of clean data
        gcv_c = func.fit_gcv(
            data=clean, p=p.value, q=q.value, num=num.value
        )

        fig.clear()
        ax1, ax2 = fig.subplots(1, 2)

        xpred1, ypred1, std_t1 = gcv_o['xpred'], gcv_o['ypred'], gcv_o['std_t']
        plot(ax1,
             points=[('Data', valid), ],
             lines=[('With full data', xpred1, ypred1), ],
             fill=[
                 ('95% t-interval',
                  xpred1,
                  ypred1.flatten() - std_t1,
                  ypred1.flatten() + std_t1),
             ],
             title='One-step',
             x_label='Time',
             y_label='Thickness Change (m)'
             )

        xpred2, ypred2, std_t2 = gcv_c['xpred'], gcv_c['ypred'], gcv_c['std_t']
        plot(ax2,
             points=[
                 ('Normal data', clean),
                 ('Outlier detected', out)
             ],
             lines=[
                 ('With full data', xpred1, ypred1),
                 ('Without outliers', xpred2, ypred2),
             ],
             fill=[
                 ('95% t-interval',
                  xpred2,
                  ypred2.flatten() - std_t2,
                  ypred2.flatten() + std_t2),
             ],
             title='Two-step',
             x_label='Time',
             y_label='Thickness Change (m)'
             )

        display(fig)
        # Clear cell output once another plot request is received
        clear_output(wait=True)

        out_data = {'original_gcv': gcv_o, 'clean_gcv': gcv_c}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = widgets.FormConfigIO(
        [p, q, num, thresh1, thresh2],
        update_func=update_plot,
        submit_text='Plot',
        test=test
    )

    return form


def conf_mmf(fig: plt.Figure, data: np.ndarray, test=False):
    """Fitting and plotting using two-stage strategy"""
    # validate input data
    valid = func.validate_data(data)

    # degree of bases
    p = ui.Integer(name='Degree of bases:', value=4)
    # order of penalty
    q = ui.Integer(name='Order of penalty:', value=3)
    # number of observations(TODO 6/21: verify)
    num = ui.Integer(name='Number of observations:', value=200)
    lambda_var = ui.Number(name='Lambda variance:', value=0.1)
    error_var = ui.Number(name='Error variance:', value=0.1)

    def update_plot():
        """
        Display submitted form information and anything else that can be used
          for testing purposes
        """
        fig.clear()
        ax1, ax2 = fig.subplots(1, 2)

        # Fit the REML model
        reml = func.fit_reml(
            data=valid,
            p=p.value,
            q=q.value,
            num=num.value,
            par=(lambda_var.value, error_var.value)
        )

        xpred, ypred, std_t = reml['xpred'], reml['ypred'], reml['std_t']
        plot(ax1,
             points=[('Data', valid), ],
             lines=[('Mean Prediction', xpred, ypred), ],
             fill=[
                 ('95% t-interval',
                  xpred,
                  ypred.flatten()-std_t,
                  ypred.flatten()+std_t),
             ],
             title='REML',
             x_label='Time',
             y_label='Thickness Change (m)'
             )

        C, D, lamb, Cpred = reml['C'], reml['D'], reml['lamb'], reml['Cpred']
        f_low, f_high = func.Inference_effects(
            q.value, valid, Cpred, C, lamb, D
        )
        plot(ax2,
             points=[('Data', valid), ],
             lines=[
                 ('Low freq. signal', xpred, f_low),
                 ('High freq. signal', xpred, f_high),
             ],
             title='Split Frequency',
             x_label='Time',
             y_label='Thickness Change (m)'
             )
        # TODO 6/25: verify y=0 should be constant
        ax2.axhline(
            y=0, color='k', linestyle=':',label='0 thickness change', lw=3
        )
        ax2.legend()

        display(fig)
        clear_output(wait=True)

        out_data = {'reml': reml, 'freq_low': f_low, 'freq_high': f_high}
        results = {
            'data': out_data, 'fig': fig
        }

        return results

    form = widgets.FormConfigIO(
        [p, q, num, lambda_var, error_var],
        update_func=update_plot,
        submit_text='Plot',
        test=test
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
    d = widgets.DataSelector()
    _, btn_sample, _ = d.children[0].children
    btn_sample.click()

    btn_submit, _ = d.children[2].children
    btn_submit.click()

    f1 = plt.figure(figsize=(12, 7))
    form = conf_gcv(f1, d._data)

    btn_plot = form.children[3].children[0]
    btn_plot.click()

