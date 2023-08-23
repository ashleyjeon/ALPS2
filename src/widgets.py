import ipywidgets as pwidg
import matplotlib.pyplot as plt
from numpy import ndarray
from pandas import DataFrame
from IPython.display import display, Javascript, clear_output
# TODO 8/15: try to migrate away from hublib; unnecessary
from hublib import ui
from pathlib import Path
from typing import List, Callable
from enum import Enum

import files
import plotting


class DataDisplay(pwidg.VBox):
    """
    Widget connecting .DataSelector and .FormConfigIO
    """
    class FuncType(Enum):
        GCV = 0
        REML = 1
        TWO_STAGE = 2
        MMF = 3

    def __init__(self, func_type: FuncType, fig: plt.Figure, **kwargs):
        """
        :param func_type:
        :param fig:
        """
        sel_data = DataSelector()
        display(sel_data)

        def observe_data(data):
            self.configure(func_type, fig, data)

        sel_data.m_observe(observe_data)

        children = (sel_data,)
        super().__init__(children, **kwargs)

    def configure(self, func_type, fig, data):
        """Initialize FormConfigIO with updated @data"""
        if func_type == self.FuncType.GCV:
            form_data = plotting.conf_gcv(fig, data)
        elif func_type == self.FuncType.REML:
            form_data = plotting.conf_reml(fig, data)
        elif func_type == self.FuncType.TWO_STAGE:
            form_data = plotting.conf_two_stage(fig, data)
        elif func_type == self.FuncType.MMF:
            form_data = plotting.conf_mmf(fig, data)
        else:
            form_data = plotting.conf_gcv(fig, data)

        clear_output()

        self.children = (self.children[0], form_data)
        display(self)


class DataSelector(pwidg.VBox):
    """
    Widget handling the selection of data for the project; allows for selecting
      from sample data (packaged with project), existing (previously uploaded),
      and upload data (upload your own)
    """
    OPTIONS = ['Sample', 'Personal']

    def __init__(self, **kwargs):
        self._data = None # getter/setter below
        self._data_path: Path = None
        self._callbacks = []

        # uploaded/selected data
        label_instr = pwidg.Label(value='Select data source:')
        btn_sample = pwidg.Button(description=self.OPTIONS[0])
        btn_own = pwidg.Button(description=self.OPTIONS[1])
        box_options = pwidg.HBox((label_instr, btn_sample, btn_own))

        sel_file = pwidg.Select(
            options=[],
            description='Select files:',
        )
        sel_file.layout.display = 'none' # hide selector upon init

        btn_up = pwidg.FileUpload(
            desc='Upload',
            accept='.p,.csv',
            multiple=True,
            dir=files.DIR_SESS_DATA,
        )
        btn_submit = pwidg.Button(description='Select')
        btn_submit.disabled = True # disable upon init
        box_pick = pwidg.HBox((btn_submit, btn_up))
        box_pick.layout.display = 'none' # hide upon init

        out_selected = pwidg.Output()
        out_selected.layout.visibility = 'hidden'

        def source_sample(b):
            """Sample data dir selected as source"""
            sel_file.layout.display = 'block'
            btn_up.layout.visibility = 'hidden'
            box_pick.layout.display = 'block'
            out_selected.layout.visibility = 'visible'

            samples = [
                str(files.get_path_relative_to(p, files.DIR_PROJECT))
                for p in Path(files.DIR_SAMPLE_DATA).iterdir()
                if p.suffix in files.FORMAT_DATA_IN
            ]
            sel_file.options = samples

        def source_own(b):
            """Personal data dir selected as source"""
            sel_file.layout.display = 'block'
            btn_up.layout.visibility = 'visible'
            box_pick.layout.display = 'block'
            out_selected.layout.visibility = 'visible'

            personal = [
                str(files.get_path_relative_to(p, files.DIR_PROJECT))
                for p in Path(files.DIR_SESS_TDATA).iterdir()
                if p.suffix in files.FORMAT_DATA_IN
            ]
            sel_file.options = personal

        btn_sample.on_click(source_sample)
        btn_own.on_click(source_own)

        def select(change):
            """File selected from selector"""
            v = change['new']

            if (v is not None) and (len(v) > 0):
                btn_submit.disabled = False
                # save data path from project root
                self._data_path = files.DIR_PROJECT / v
            else:
                btn_submit.disabled = True

        sel_file.observe(select, names='value')

        def submit(b):
            """Read data in @self.data_path"""
            self.data = files.load_data(self._data_path)
            out_selected.clear_output(wait=True)

            with out_selected:
                print(f'Loaded data from: {self._data_path.name}\n'
                      f'First 5 elements:')

                if isinstance(self.data, DataFrame):
                    display(self.data.head(5))
                elif isinstance(self.data, ndarray):
                    display(self.data[:5, :])

        btn_submit.on_click(submit)

        def upload(change):
            v = change['new']

            if (v is not None) and (len(v) > 0):
                for name, meta in v.items():
                    # files.dump_data() requires a dictionary
                    d = {name: meta['content']}
                    files.dump_data(files.DIR_SESS_TDATA / name, d, bytes=True)
                    btn_own.click() # reload list of existing files

        btn_up.observe(upload, names='value')

        super().__init__(
            [box_options, sel_file, box_pick, out_selected],
            **kwargs
        )

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, val):
        """Call observing functions"""
        self._data = val
        for cb in self._callbacks:
            cb(self._data)

    def m_observe(self, callback):
        self._callbacks.append(callback)


class ResultsDownloader(pwidg.HBox):
    """
    Abstract widget object for downloading some data with a field for specifying filename and a
      dropdown filetype selection
    """
    def __init__(self,
                 placeholder_filename: str,
                 download_formats: List,
                 download_name: str):
        txt_filename = pwidg.Text(
            value='',
            placeholder=placeholder_filename,
        )
        drop_file_format = pwidg.Dropdown(
            options=download_formats,
            value=download_formats[0]
        )
        btn_down = pwidg.Button(
            description=download_name,
            icon='download',
            disabled=True
        )

        def toggle(change):
            """Disable download button if no filename specified"""
            if change['name'] == 'value':
                if len(change['new']) > 0:
                    btn_down.disabled = False
                else:
                    btn_down.disabled = True

        txt_filename.observe(toggle)

        super().__init__((txt_filename, drop_file_format, btn_down))

    def on_click(self, func):
        btn_down = self.children[2]
        btn_down.on_click(func)

    def download(self, **kwargs):
        """Function that downloads respective data"""
        raise NotImplementedError('Abstract method; must override!')

    def disable(self):
        """
        Disable everything but the download button -- that gets controlled by
          the filename field
        """
        # TODO 6/27: could see this not working as intended if order of the
        #   children is changed
        for c in self.children[:-1]:
            c.disabled = True

    def enable(self):
        """
        Enable everything but the download button -- that gets controlled by
          the filename field
        """
        # TODO 6/27: could see this not working as intended if order of the
        #   children is changed
        for c in self.children[:-1]:
            c.disabled = False

    def hide(self):
        """Hide the widget"""
        if self.layout.display == 'block':
            self.layout.display = 'none'

    def show(self):
        """Show the widget"""
        if self.layout.display == 'none':
            self.layout.display = 'block'


class PlotDownloader(ResultsDownloader):
    """Button to download plots"""
    def __init__(self):
        super().__init__(
            placeholder_filename='enter plot filename',
            download_formats=files.FORMAT_IMG_OUT,
            download_name='Plot'
        )

    def download(self, fig: plt.Figure):
        """Download image to browser"""
        txt_filename = self.children[0]
        drop_file_format = self.children[1]

        filename = f'{txt_filename.value}.{drop_file_format.value}'
        path = files.upload_plt_plot(fig, filename)
        # need to make path relative to '.' for javascript windows
        path = files.get_path_relative_to(path, files.DIR_SRC).as_posix()

        # trigger a browser popup that will download the image to browser
        js = Javascript(
            f"window.open('{path}', 'Download', '_blank')"
        )
        display(js)


class DataDownloader(ResultsDownloader):
    """Widget for transformed data downloading"""
    def __init__(self):
        super().__init__(
            placeholder_filename='enter output data filename',
            download_formats=files.FORMAT_DATA_OUT,
            download_name='Data'
        )

    def download(self, data: dict):
        """Download @data to host results directory and to user system"""
        txt_filename = self.children[0]
        drop_file_format = self.children[1]

        fname = f'{txt_filename.value}.{drop_file_format.value}'
        fpath = files.DIR_SESS_RESULTS / fname
        files.dump_data(fpath, data, bytes=False)

        # need to make path relative to '.' for javascript windows
        path = files.get_path_relative_to(fpath, files.DIR_SRC).as_posix()

        # trigger a browser popup that will download the image to browser
        js = Javascript(
            f"window.open('{path}', 'Download', '_blank')"
        )
        display(js)


class ParamsForm(pwidg.VBox):
    LAYOUT_BOX = pwidg.Layout(
        display='flex',
        width='100%',
    )
    LAYOUT_LABEL = pwidg.Layout(
        width='50%',
    )
    LAYOUT_TEXT = pwidg.Layout(
        width='50%',
    )

    """Box for p, q, num parameters to be used in FormConfigIO"""
    def __init__(self,
                 p_val: int,
                 q_val: int,
                 num_val: int,
                 **kwargs):
        # degree of bases
        label_p = pwidg.Label(
            value='Degree of bases:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        text_p = pwidg.BoundedIntText(
            value=p_val,
            min=2, max=5, step=1,
            # description='Degree of bases:',
            layout=self.LAYOUT_TEXT,
            # style=self.STYLE_LABEL
        )
        p = pwidg.HBox((label_p, text_p), layout=self.LAYOUT_BOX)

        # order of penalty
        label_q = pwidg.Label(
            value='Order of penalty:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        text_q = pwidg.BoundedIntText(
            value=q_val,
            min=1, max=p_val-1, step=1,
            # description='Order of penalty:',
            layout=self.LAYOUT_TEXT,
            # style=self.STYLE_LABEL
        )
        q = pwidg.HBox((label_q, text_q), layout=self.LAYOUT_BOX)

        def link_q(change):
            max = change['new']
            text_q.max = max - 1
        text_p.observe(link_q, names='value')

        # TODO 8/21: any bounds for num? Also verify the meaning of this variable
        # number of observations
        label_num = pwidg.Label(
            value='Number of observations:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        text_num = pwidg.BoundedIntText(
            value=num_val,
            min=1, max=9999, step=1, # arbitrary max
            # description='Number of observations:',
            layout=self.LAYOUT_TEXT,
            # style=self.STYLE_LABEL
        )
        num = pwidg.HBox((label_num, text_num), layout=self.LAYOUT_BOX)

        children = (p, q, num)
        super().__init__(children=children, **kwargs)

    @property
    def p_value(self):
        return self.children[0].children[1].value
    @property
    def q_value(self):
        return self.children[1].children[1].value
    @property
    def num_value(self):
        return self.children[2].children[1].value


class ParamsFormVar(ParamsForm):
    def __init__(self,
                 p_val: int,
                 q_val: int,
                 num_val: int,
                 lam_val: float,
                 err_val: float,
                 **kwargs):
        super().__init__(
            p_val=p_val, q_val=q_val, num_val=num_val,
            **kwargs
        )

        lambda_label = pwidg.Label(
            value='Lambda variance:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        lambda_text = pwidg.BoundedFloatText(
            value=lam_val, min=0.0, step=0.1,
        )
        lambda_var = pwidg.HBox(
            (lambda_label, lambda_text), layout=self.LAYOUT_BOX
        )

        error_label = pwidg.Label(
            value='Error variance:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        error_text = pwidg.BoundedFloatText(
            value=err_val, min=0.0, step=0.1,
        )
        error_var = pwidg.HBox(
            (error_label, error_text), layout=self.LAYOUT_BOX
        )

        self.children = (*self.children, lambda_var, error_var)

    @property
    def lam_value(self):
        return self.children[3].children[1].value
    @property
    def error_value(self):
        return self.children[4].children[1].value


class ParamsFormScale(ParamsForm):
    def __init__(self,
                 p_val: int,
                 q_val: int,
                 num_val: int,
                 scale1_val: float,
                 scale2_val: float,
                 **kwargs):
        super().__init__(
            p_val=p_val, q_val=q_val, num_val=num_val,
            **kwargs
        )

        s1_label = pwidg.Label(
            value='Scaling threshold 1:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        s1_text = pwidg.BoundedFloatText(
            value=scale1_val, min=0.0, step=0.1,
        )
        s1 = pwidg.HBox(
            (s1_label, s1_text), layout=self.LAYOUT_BOX
        )

        s2_label = pwidg.Label(
            value='Scaling threshold 2:',
            layout=self.LAYOUT_LABEL,
            style={'description_width': 'initial'}
        )
        s2_text = pwidg.BoundedFloatText(
            value=scale2_val, min=0.0, step=0.1,
        )
        s2 = pwidg.HBox(
            (s2_label, s2_text), layout=self.LAYOUT_BOX
        )

        self.children = (*self.children, s1, s2)

    @property
    def scale1_value(self):
        return self.children[3].children[1].value
    @property
    def scale2_value(self):
        return self.children[4].children[1].value


class FormConfigIO(pwidg.VBox):
    """
    Form widget for changing parameters of a function and plotting its results
    """
    def __init__(self,
                 form_widgets: List,
                 update_func: Callable,
                 submit_text: str = "Submit",
                 download=True,
                 **kwargs):
        """
        :param form_widgets:
        :param update_func:
        :param submit_text:
        :param download: should a download button be displayed to save output?
        :param test:
        :param test_msg:
        :param kwargs:
        """
        btn_submit = pwidg.Button(description=submit_text)
        down_plot = PlotDownloader()
        down_data = DataDownloader()
        if download:
            down_plot.disable() # nothing to download yet; disable
            down_data.disable()  # nothing to download yet; disable
        else:
            down_plot.hide() # @download == False
            down_data.hide()  # @download == False
        box_down = pwidg.VBox([down_plot, down_data])
        box_btns = pwidg.HBox([btn_submit, box_down])
        out_plot = pwidg.Output()

        # @update_func output
        output = None

        def update(b):
            """Call the @update_func passed above"""
            nonlocal output
            output = update_func()

            # if @update_func returns some results, enable downloading
            if output is not None:
                down_plot.enable()
                down_data.enable()

                with out_plot:
                    out_plot.clear_output(wait=True)
                    display(output['fig'])
            else:
                down_plot.disable()
                down_data.disable()

        def save_plot(b):
            nonlocal output
            fig = output.get('fig')

            down_plot.download(fig)

        def save_data(b):
            nonlocal output

            data = output.get('data')
            down_data.download(data)

        btn_submit.on_click(update)
        down_plot.on_click(save_plot)
        down_data.on_click(save_data)

        children = (*form_widgets, box_btns, out_plot)
        super().__init__(children, **kwargs)
        display(self)


if __name__ == '__main__':
    f1 = plt.figure(figsize=(12, 7))
    d = DataSelector()
    _, btn_sample, btn_own = d.children[0].children
    btn_own.click()

    btn_submit, btn_up = d.children[2].children
    btn_submit.click()
