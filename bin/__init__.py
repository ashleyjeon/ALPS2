import atexit
import files


atexit.register(files.clear_temp)
atexit.register(files.clear_results)