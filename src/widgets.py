import ipywidgets as widg
from IPython.display import display
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


class BtnUpload(widg.HBox):
    def __init__(self, disabled=False, **kwargs):
        dropdown_file = widg.Dropdown(
            options=files.VALID_DATATYPES,
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

        super().__init__((box_selector, btn_upload, output))

        self.observe(self._finish_upload)

    @staticmethod
    def _finish_upload(widget, name):
        """Reset the FileUpload widget to accept more uploads"""
        print('Successfully uploaded:')
        for n in name:
            print('\t', n)

        widget.reset()


class ConfigForm(ui.Form):
    def __init__(self,
                 wlist,
                 update_func,
                 submit_text: str = "Submit",
                 test = False,
                 test_msg: str = None,
                 download = False,
                 **kwargs):
        """
        Appends an ipywidgets.Output widget to capture any stdout for testing
          purposes, as well as a button for submitting form parameters
        :param wlist:
        :param test:
        :param submit_text:
        :param kwargs:
        """
        btn_submit = widg.Button(description=submit_text)
        out_test = widg.Output()

        @out_test.capture(clear_output=True, wait=True)
        def update(b):
            """Call the @update_func passed above"""
            if test:
                with out_test:
                    print('Updated parameters:\n')
                    for widget in wlist:
                        # Only read new input from NumValue and its children
                        if isinstance(widget, ui.numvalue.NumValue):
                             print(f'{widget.name} {widget.value}')

                    # Print any additional message if passed
                    if test_msg is not None: print(test_msg)

            update_func()

        btn_submit.on_click(update)

        wlist.extend([btn_submit, out_test])
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


# class DownloadToggle(ui.Download):
#     def __int__(self, filename, disable = False, **kwargs):
#         super.__init__(filename, **kwargs)


