from ant.core import log
import ant.core
print ant.core.__file__

SERIAL = '/dev/ttyUSB0'

# If set to True, the stick's driver will dump everything it reads/writes
# from/to the stick.
# Some demos depend on this setting being True, so unless you know what you
# are doing, leave it as is.
DEBUG = True

# Set to None to disable logging
# LOG = None
LOG = log.LogWriter()

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# ========== DO NOT CHANGE ANYTHING BELOW THIS LINE ==========
print "Using log file:", LOG.filename
print ""
