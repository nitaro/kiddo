#!/usr/bin/python 3

import sys; sys.path.append("..")
import logging
import logging.handlers
import os
import platform
import random
import unittest
import kiddo

logging.basicConfig(level=10)


class Test_Kiddo(unittest.TestCase):
    """ Tests Kiddo class. """


    def test__interpreter(self):
        """ Tests the log interpreter. """

        # create Kiddo instance.
        kid = kiddo.Kiddo(name=sys._getframe().f_code.co_name)

        # open data file; assume no errors yet exist.
        lines_file = open("sample_lines.txt")
        errors = []
        
        # test the interpreter against each line of @lines_file.
        i = 0
        for line in lines_file.read().split("\n"):

            # skip blank lines.
            if line == "":
                continue
            else:
                logging.info("Interpreting line: {}".format(line))
    
            # interpret the line's logging level and get the expected level.
            line = kid.log_interpreter(line)
            level, expected_level = line[0], line[1].split("LOGGING." )[-1].lower()
            
            # log results.
            if level != expected_level:
                logging.warning("Line '{}' wasn't interpreted correctly.".format(i))
                logging.error("Not equal: {}/{}".format(level, expected_level))
                errors.append(i)
            else:
                logging.info("Line interpreted as: LOGGING.{}".format(level.upper()))

            i += 1        
        
        lines_file.close()

        logging.info("Making sure that no interpreting errors occurred.")
        self.assertEqual(errors, [])


    def test__long_output(self):
        """ Tests that last line in long output was logged. """

        # creat Kiddo instance and add memory logger for its child process.
        kid = kiddo.Kiddo(name=sys._getframe().f_code.co_name)
        mem_logger = logging.handlers.MemoryHandler(1000)
        kid.child_logger.level = 10
        kid.child_logger.addHandler(mem_logger)

        # determine value of stdout line.
        final_line = random.randrange(500,1500)
        logging.info("STDOUT will output: {}".format(final_line))

        # run app.
        app_file = os.path.join(os.path.dirname(__file__), "echo_max_line.py")
        py_prefix = "py -3" if platform.system() == "Windows" else "python3"
        cmd = "{} {} {}".format(py_prefix, app_file, final_line)
        logging.info("Running: {}".format(cmd))
        kid.run(cmd)

        # get value of last log message in @mem_logger.
        log_val = int(mem_logger.__dict__["buffer"][-1].msg)
        logging.info("Log value was: {}".format(log_val))

        logging.info("Making sure log value equals STDOUT value.")
        self.assertEqual(log_val, final_line)


    def test__error(self):
        """ Tests that errors are captured. """

        # creat Kiddo instance.
        kid = kiddo.Kiddo(name=sys._getframe().f_code.co_name)

        # run app.
        app_file = os.path.join(os.path.dirname(__file__), "echo_error_code.py")
        py_prefix = "py -3" if platform.system() == "Windows" else "python3"
        cmd = "{} {}".format(py_prefix, app_file)
        logging.info("Running: {}".format(cmd))
        
        # get return code, stderr.
        ret_code, ret_err = kid.run(cmd)
        logging.info("Return code: {}".format(ret_code))
        logging.info("STDERR: {}".format(ret_err))

        logging.info("Making return code is 1 and that STDERR is not empty.")
        result_bool = ret_code == 1 * (len(ret_err) > 0) 
        self.assertTrue(result_bool)


if __name__ == "__main__":
    pass