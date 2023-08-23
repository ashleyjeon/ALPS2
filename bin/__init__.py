import atexit
import files


@atexit.register
def hello_world():
    with open(files.DIR_SESS_TDATA / 'goodbye.txt', 'w') as f:
        f.write('Goodbye, world!!!')


atexit.register(files.clear_temp)