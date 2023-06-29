import ipywidgets as widg
import matplotlib.pyplot as plt
from IPython.display import display, Javascript
from hublib import ui
from pathlib import Path
import files


class DataSelector(widg.VBox):
    """
    Widget handling the selection of data for the project; allows for selecting
      from sample data (packaged with project), existing (previously uploaded),
      and upload data (upload your own)
    """
    OPTIONS = ['Sample', 'Personal']

    def __init__(self, **kwargs):
        self.data = None
        self.data_path: Path = None

        # uploaded/selected data
        label_instr = widg.Label(value='Select data source:')
        btn_sample = widg.Button(description=self.OPTIONS[0])
        btn_own = widg.Button(description=self.OPTIONS[1])
        box_options = widg.HBox((label_instr, btn_sample, btn_own))

        sel_file = widg.Select(
            options=[],
            description='Select files:',
        )
        sel_file.layout.display = 'none' # hide selector upon init

        btn_up = widg.FileUpload(
            desc='Upload',
            accept='.p,.csv',
            multiple=True,
            dir=files.DIR_SESS_DATA,
        )
        btn_submit = widg.Button(description='Select')
        btn_submit.disabled = True # disable upon init
        box_pick = widg.HBox((btn_submit, btn_up))
        box_pick.layout.display = 'none' # hide upon init

        label_files = widg.Label()
        label_files.layout.visibility = 'hidden'

        def source_sample(b):
            """Sample data dir selected as source"""
            sel_file.layout.display = 'block'
            btn_up.layout.visibility = 'hidden'
            box_pick.layout.display = 'block'
            label_files.layout.visibility = 'visible'

            samples = [
                str(files.get_path_relative_to(p, files.DIR_PROJECT))
                for p in Path(files.DIR_SAMPLE_DATA).iterdir()
                if p.suffix in files.FORMAT_DATA
            ]
            sel_file.options = samples

        def source_own(b):
            """Personal data dir selected as source"""
            sel_file.layout.display = 'block'
            btn_up.layout.visibility = 'visible'
            box_pick.layout.display = 'block'
            label_files.layout.visibility = 'visible'

            personal = [
                str(files.get_path_relative_to(p, files.DIR_PROJECT))
                for p in Path(files.DIR_SESS_DATA).iterdir()
                if p.suffix in files.FORMAT_DATA
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
                self.data_path = files.DIR_PROJECT / v
            else:
                btn_submit.disabled = True

        sel_file.observe(select, names='value')

        def submit(b):
            """Read data in @self.data_path"""
            self.data = files.load_data(self.data_path)
            label_files.value = f'Loaded data from: {self.data_path.name} ' \
                                f'| Access using "data" attribute of DataSelector.'

        btn_submit.on_click(submit)

        def upload(change):
            v = change['new']

            if (v is not None) and (len(v) > 0):
                for name, meta in v.items():
                    files.dump_array(name, meta['content'], bytes=True)
                    btn_own.click() # reload list of existing files

        btn_up.observe(upload, names='value')

        super().__init__(
            [box_options, sel_file, box_pick, label_files],
            **kwargs
        )


class BtnImgDownload(widg.HBox):
    """Button to download images"""
    def __init__(self):
        txt_filename = widg.Text(
            value='',
            placeholder='enter file name',
        )
        drop_file_format = widg.Dropdown(
            options=files.FORMAT_IMG_OUT,
            value=files.FORMAT_IMG_OUT[0]
        )
        btn_down = widg.Button(
            description='Download',
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


class FormConfigIO(ui.Form):
    """
    Extension of hublib.ui.Form which appends submit and download buttons,
      as well as an Output widget that can print optional (test) messages
    """
    def __init__(self,
                 wlist,
                 update_func,
                 submit_text: str = "Submit",
                 download=True,
                 test=False,
                 test_msg: str = None,
                 **kwargs):
        """
        :param wlist:
        :param update_func:
        :param submit_text:
        :param download: should a download button be displayed to save output?
        :param test:
        :param test_msg:
        :param kwargs:
        """
        btn_submit = widg.Button(description=submit_text)
        btn_down = BtnImgDownload()
        if download:
            btn_down.disable() # nothing to download yet; disable
        else:
            btn_down.hide() # @download == False
        box_btns = widg.HBox([btn_submit, btn_down])
        out_test = widg.Output()

        # @update_func output
        output = None

        @out_test.capture(clear_output=True, wait=True)
        def update(b):
            """Call the @update_func passed above"""
            if test:
                # print test output
                with out_test:
                    print('Updated parameters:\n')
                    for widget in wlist:
                        # only read new input from NumValue and its children
                        if isinstance(widget, ui.numvalue.NumValue):
                             print(f'{widget.name} {widget.value}')

                    # print any additional message if passed
                    if test_msg is not None: print(test_msg)

            nonlocal output
            output = update_func()

            # if @update_func returns some results, enable downloading
            if output is None:
                btn_down.disable()
            else:
                btn_down.enable()

        def save(b):
            nonlocal output
            btn_down.download(output)

        btn_submit.on_click(update)
        btn_down.on_click(save)

        wlist.extend([box_btns, out_test])
        super().__init__(wlist, **kwargs)


if __name__ == '__main__':
    f1 = plt.figure(figsize=(12, 7))
    d = DataSelector()
    _, btn_sample, btn_own = d.children[0].children
    btn_own.click()

    btn_submit, btn_up = d.children[2].children
    btn_submit.click()
