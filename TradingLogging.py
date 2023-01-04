import sys
import logging
import logging.config
# ================== Logger ================================

def Logger(file_name):
    formatter = logging.Formatter(fmt='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                    datefmt='%Y/%m/%d %H:%M:%S') # %I:%M:%S %p AM|PM format
    logging.basicConfig(filename = '%s.log' %(file_name),format= '%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                    datefmt='%Y/%m/%d %H:%M:%S', filemode = 'a', level = logging.INFO)
    LOG = logging.getLogger()
    LOG.setLevel(logging.DEBUG)
    # LOG = logging.getLogger().addHandler(logging.StreamHandler())

    # console printer
    screen_handler = logging.StreamHandler(stream=sys.stdout) #stream=sys.stdout is similar to normal print
    screen_handler.setFormatter(formatter)
    logging.getLogger().addHandler(screen_handler)

    LOG.info("Logger object created successfully..")
    return LOG
    # =======================================================


# #MUTHUKUMAR_LOGGING_CHECK.py #>>>>>>>>>>> file name
# # calling **Logger** function
# file_name = 'muthu'
# LOG =Logger(file_name)
# LOG.info("yes   hfghghg ghgfh".format())
# LOG.critical("CRIC".format())
# LOG.error("ERR".format())
# LOG.warning("WARN".format())
# LOG.debug("debug".format())
# LOG.info("qwerty".format())
# LOG.info("asdfghjkl".format())
# LOG.info("zxcvbnm".format())
# # closing file
# LOG.handlers.clear()