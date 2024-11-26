import logging
import sys

from pydfnworks.general.images import failure, success

def initialize_log_file(self, time = False):
    ''' Create Log file

    Parameters
    ---------
        self : dfnWorks object

    Returns
    --------
        None

    Notes
    -------

    '''


    # logging.getLogger(__name__)
    logging.basicConfig(level = logging.INFO, filename=self.log_filename, filemode="w"
                        , format="%(asctime)s %(levelname)s %(message)s" )
    statement = f"Initializing logfile: {self.log_filename}"
    self.print_log(statement)

def print_log(self, statement, level = 'info'):
    '''print and log statments to a file 

    Parameters
    ---------
        statement : the print/log statement

    Returns
    --------
        None

    Notes
    -------
        print statments in pydfnworks should generally be replaced with this print_log function. Use self.print_log if function is on DFN object
    '''
    # print("here")
    # logging.basicConfig(level=logging.DEBUG)
    if level == 'info':
        print(statement)
        logging.info(statement)
    elif level == 'debug':
        print(statement)
        logging.debug(statement)
    elif level == 'warning':
        print(statement)
        logging.warning(statement)
    elif level == 'error':
        logging.error(statement)
        sys.stderr.write(statement)
        sys.exit(1)
    elif level == 'critical':
        logging.critical(self.failure())
        sys.stderr.write(statement)
        sys.exit(1)
    else:
        tmp_statement = f"Unknown logging level requested: {level}. Using warning"
        print(tmp_statement)
        print(statement)
        logging.warning(tmp_statement)
        logging.warning(statement)


def local_print_log(statement, level = 'info'):
    '''print and log statments to a file

    Parameters
    ---------
    statement : the print/log statement

    Returns
    --------
    None

    Notes
    -------
    print statments in pydfnworks should generally be replaced with this print_log function. Use local_print_log if function is not in refernce to DFN object
    '''

    if level == 'info':
        print(statement)
        logging.info(statement)
    elif level == 'debug':
        print(statement)
        logging.debug(statement)
    elif level == 'warning':
        print(statement)
        logging.warning(statement)
    elif level == 'error':
        logging.error(statement)
        sys.stderr.write(statement)
        sys.exit(1)
    elif level == 'critical':
        logging.critical(statement)
        sys.stderr.write(statement)
        sys.exit(1)
    else:
        tmp_statement = f"Unknown logging level requested: {level}. Using warning"
        print(tmp_statement)
        print(statement)
        logging.warning(tmp_statement)
        logging.warning(statement)
