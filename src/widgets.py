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
    OPTIONS = ['Sample', 'Existing', 'Upload']

    def __init__(self, **kwargs):
        # uploaded/selected data
        self.data = []

        label = widg.Label(value='Select data source:')
        btn_sample = widg.Button(description=self.OPTIONS[0])
        btn_exist = widg.Button(description=self.OPTIONS[1])
        btn_up = widg.Button(description=self.OPTIONS[2])
        box_options = widg.HBox([label, btn_sample, btn_exist, btn_up])

        selector = widg.SelectMultiple(
            options=[],
            description='Select files (drag click for multiple):',
        )
        btn_upload = BtnUpload()

        def toggle(btn):
            """Display respective widget upon data source selection"""
            if btn.description == self.OPTIONS[0]: # sample
                # 'w' is 'layout' attribute of ui.FileUpload
                btn_upload.layout.visibility = 'hidden'

                f = [p.relative_to(files.DIR_PROJECT)
                     for p in Path(files.DIR_SAMPLE_DATA).iterdir()
                     if p.is_file()]
                selector.options = f
                selector.layout.visibility = 'visible'

            elif btn.description == self.OPTIONS[1]: # existing
                # 'w' is 'layout' attribute of ui.FileUpload
                btn_upload.layout.visibility = 'hidden'

                f = [p.relative_to(files.DIR_PROJECT)
                     for p in Path(files.DIR_SESS_DATA).iterdir()
                     if p.is_file()]
                selector.options = f
                selector.layout.visibility = 'visible'

            else: # upload
                selector.layout.visibility = 'hidden'
                btn_upload.layout.visibility = 'visible'

        btn_sample.on_click(toggle)
        btn_exist.on_click(toggle)
        btn_up.on_click(toggle)

        layout = widg.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
        )
        super().__init__(
            [box_options, selector, btn_upload],
            layout=layout, **kwargs
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


class BtnUpload(widg.HBox):
    def __init__(self, disabled=False, **kwargs):
        dropdown_file = widg.Dropdown(
            options=files.FORMAT_DATA,
        )

        ftype = '.p'
        desc = f'Upload {ftype}'
        btn_upload = widg.FileUpload(
            description=f'desc',
            accept='.p',
            multiple=True,
            dir=files.DIR_SESS_DATA,
            disabled=disabled
        )
        widg.link((dropdown_file, 'value'), (btn_upload, 'accept'))

        output = widg.Output()

        @output.capture(clear_output=True, wait=True)
        def finish_upload(b):
            """Reset the FileUpload widget to accept more uploads"""
            print('Successfully uploaded:')
            [print('\t', d) for d in btn_upload.value]

        btn_upload.observe(finish_upload)

        super().__init__((dropdown_file, btn_upload, output))

        self.observe(self._finish_upload)

    @staticmethod
    def _finish_upload(widget, name):
        """Reset the FileUpload widget to accept more uploads"""
        print('Successfully uploaded:')
        for n in name:
            print('\t', n)

        widget.reset()


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


def upload_files():
    dropdown_file = widg.Dropdown(
        options=['.p', '.csv', '.json', '.txt'],
        disabled=False
    )
    box_selector = widg.HBox(
        [widg.Label('Select file type to upload:'), dropdown_file]
    )
    btn_upload = widg.FileUpload(
        description='Upload files',
        accept='.p',
        multiple=True,
        dir=files.DIR_SESS_DATA
    )
    widg.link((dropdown_file, 'value'), (btn_upload, 'accept'))

    output = widg.Output()

    def upload(change):
        with output:
            print(change.items())

    btn_upload.observe(upload)

    return box_selector, btn_upload, output


# if __name__ == '__main__':
#     f1 = plt.figure(figsize=(12, 7))
#     down = BtnImgDownload(f1)
#     down.click()
