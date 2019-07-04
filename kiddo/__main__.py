#!/usr/bin/python 3

""" This module contains the Kiddo class as well as its default log-interpreter function.

Todo:
    * You should probably do some type checking for user parameters.
"""

# import modules.
import logging
import platform
import subprocess


def DEFAULT_LOG_INTERPRETER(line, **kwargs):
    """ Determines the logging level for a given @line. If @line starts with a valid logging level
    followed by a colon, e.g. "info: Hi", "iNfO: Hi", or "INFO: Hi", the message will be interpreted
    as a logging.INFO message of "Hi".
    
    Args:
        - line (str): The stdout line to be interpreted.
    
    Returns:
        tuple: The return value.
        The first item is a valid lowercase logging level: "info", "error", etc. The second item is 
        the message value to log.
    """

    # determine logging level based on the line prefix.
    level = line[:line.find(":")].lower()

    # default to None if @level is not a valid logging level.
    if level not in ["debug", "info", "warning", "error", "critical"]:
        level, message = "info", line
    else:
        message = line.split(":", 1)[1].strip()
    
    return (level, message)


class Kiddo():
    """ A class for running command line scripts and logging the output.

    On Windows, it also prevents a new console window from opening.
    
    Example:
        >>> kid = Kiddo("hiKiddo")
        >>> kidding = kid.run("myscript.bat")
        >>> # stdout from @kidding will be routed to a Python logger, @kid.child_logger.
        >>> return_code, stderr = kidding
        >>> return_code # 0
        >>> stderr # []
    """


    def __init__(self, name, log_interpreter=None, hide_console=True, charset="utf-8", 
        **kwargs):
        """ Sets instance attributes. 

        Args:
            - name (str): The name for the instance. This value will also be the name of 
            @self.child_logger.
            - log_interpreter (function): Interprets the logging level for a each line in
            @self.child_process.stdout. This takes two arguments: a line of text and **kwargs. It
            must return a tuple: a valid lowercase logging level ("debug", "info", "warning",
            "error", "critical") and the message to log. If None, the default log interpreter is 
            used.
            - hide_console: Use True to prevent a new console from appearing (Windows).
            - charset (str): The encoding with which to convert each line of 
            @self.child_process.stdout.

        Attributes:
            - child_process (subprocess.Popen): The child process launched by @self.run(). This is
            initially None.
            - logger (logging.Logger): The class instance's logger.
            - child_logger (logging.Logger): The logger to which @self.child_process stdout is 
            routed. This logger's records contain an additional field, "stdout", that contains the
            original value for each line of @self.child_process.stdout.
            - kwargs: Any optional keyword/value pairs to pass to @self.log_interpreter() or the
            underlying subprocess.Popen() method.

        Raises:
            - ValueError: If @name equals the __name__ attribute of this module.
        """

        # set user attributes.
        if name == __name__:
            raise ValueError("Illegal value for @name: {}".format(__name__))
        else:
            self.name = name
        self.log_interpreter = (log_interpreter if log_interpreter is not None else 
            DEFAULT_LOG_INTERPRETER)
        self.hide_console = hide_console
        self.charset = charset
        self.kwargs = kwargs

        # set other atributes.
        self.child_process = None

        # create loggers.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.child_logger = logging.getLogger(self.name)
        self.child_logger.addHandler(logging.NullHandler())   

 
    def _log_child_process_line(self, line):
        """ Calls @self.child_logger to log a @line of text outputted by @self.child_process.stdout.
        The @line is passed through @self.log_interpreter().
        
        Args:
            - line (str): The text outputted by the child process.
        
        Returns:
            None
        """

        try:
            level, message = self.log_interpreter(line, **self.kwargs)
            getattr(self.child_logger, level)(message, extra={"stdout":line})
        except Exception as err:
            self.logger.warning("Can't log subprocess line: {}".format(line))
            self.logger.error(err)

        return


    def run(self, arg_list, **kwargs):
        """ Runs @arg_list via subprocess.Popen() and sets that call as @self.child_process.

        Args:
            - arg_list (list): When joined with a space, each item in this list forms the command to
            run. Example: "arg_list=['python3', '/myScripts/foo.py'])". If @arg_list is a string, it
            will be split before being passed to subprocess.Popen().
            - **kwargs: Additional keyword values to pass along to subprocess.Popen() except for
            forbidden arguments: "args", "stdout", "stderr", "startup_info", "text", 
            "universal_newlines".

        Returns:
            tuple: The return value.
            The first item is the return code for @self.child_process. The second item is a list of
            each line from @self.child_process.stderr.

        Raises:
            - ValueError: If **kwargs contains a forbidden argument.
        """
        
        # if needed, split @arg_list.
        if isinstance(arg_list, str):
            arg_list = arg_list.split()
            self.logger.debug("Split @arg_list string to a list: {}".format(arg_list))
            
        # make sure forbidden args are not in @kwargs.
        for forbidden in ["args", "stdout", "stderr", "startup_info", "text", "universal_newlines"]:
            if forbidden in kwargs:
                msg = "@kwargs contaings forbidden argument: {}".format(forbidden)
                self.logger.error(msg)
                raise ValueError(msg)
        
        # create the command to run.
        self.logger.debug("Running command: {}".format(" ".join(arg_list)))
    
        # if needed, hide the Windows console per: https://stackoverflow.com/a/1016651
        # see also: https://docs.python.org/3/library/subprocess.html#windows-popen-helpers
        startup_info = None
        if (self.hide_console and platform.system() == "Windows"):
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # run child process based on: https://stackoverflow.com/a/803396.
        try:
            self.child_process = subprocess.Popen(args=arg_list, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, startupinfo=startup_info, universal_newlines=True, **kwargs)
        except Exception as err:
            self.logger.warning("Couldn't run command.")
            self.logger.error(err)
            raise
        
        # log each line of stdout.
        while self.child_process.poll() is None:
        
            for line in self.child_process.stdout:
                line = line.encode().decode(self.charset, errors="i")
                line = line.strip()
                self._log_child_process_line(line)

        # create items for return tuple.
        retcode = self.child_process.returncode
        reterr = [l.strip() for l in self.child_process.stderr.readlines()]
        
        # report on results.
        if retcode != 0 or len(reterr) != 0:
            self.logger.warning("Running the command appears to have failed.")
            self.logger.debug("@self.child_process.stderr: {}".format(reterr))
        self.logger.info("Command returned code: {}".format(retcode))

        return (retcode, reterr)


if __name__ == "__main__":
    pass
