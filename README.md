# Introduction
**Kiddo** makes it easy to run child scripts.

## Example
	>>> import logging
	>>> logging.basicConfig(level=logging.INFO)
	>>> import kiddo
	>>> kid = kiddo.Kiddo("hiKiddo")
	>>> kidding = kid.run("py -3 tests/echo_max_line.py 123")
	INFO:hiKiddo:123
	INFO:kiddo.__main__:Command returned code: 0
	>>> return_code, stderr = kidding
	>>> return_code
	0
	>>> stderr
	[]

## Logging
**Kiddo** logs `STDOUT` to a Kiddo instance's `child_logger` object.

By default, logging levels are determined by the starting string (case insensitive) of a line of `STDOUT`. For example, the line `debug: Hello world!` results in a record with a `msg` value of "Hello world!" at the `logging.DEBUG` level.

The same holds true for lines that start with other valid logging levels: "info", "warning", "error", "critical". All other lines are logged at the `logging.INFO` level.

You can override the default logging interpreter by passing in a custom `log_interpreter` function:

	def custom_interpreter(line, **kw):
	  """ Logs everything at the logging.INFO level; 
	      makes the record's @msg value lowercase. """
	  return ("info", line.lower())
		
	kid = kiddo.Kiddo("customKiddo", log_interpreter=custom_interpreter)

For more information, do `help(kiddo.Kiddo)`.

