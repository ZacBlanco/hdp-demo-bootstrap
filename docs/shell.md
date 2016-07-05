[Back to Index](README.md)

# Shell


This small submodule is built to run `bash` commands via simple python scripts. It designed to be slightly less verbose, but also take away some of the configurability of executing subprocesses via the `subprocess.Popen` function.

In doing this we can run commands by simply calling the `run` function with the desired bash command (whatever would have been typed in at the command line).

## Usage

	from shell import Shell
	
	sh = Shell()
	sh.run('pwd')
	sh.run('ls -l')
	sh.run('curl -X GET http://www.google.com')
	
## Methods

### `shell.__init__(wd='')`

This instantiates the shell. If the argument `wd` is set to anything other than an empty string, the shell will start at the specified location.

### `shell.run(command)`

This function is built to run a bash executable specified by the `command` argument.

Arguments may be added after the command, just like how they would be at the command line.

The output of the function is a 2-element array. The first element is what was printed to `std_out`. The 2nd element is the output to `std_err`

	[std_out, std_err]
	output[0] = std_out
	output[1] = std_err


**NOTE:** the `cd` (change directory) command does not work in this shell. In order to change the directory please refer to `shell.set_cwd`

### `shell.set_cwd(new_cwd)`

This function sets the working directory for the shell. Each command that is run has a new working directory set to this value. If the passed directory does not exist an `IOError` will be raised.
	

