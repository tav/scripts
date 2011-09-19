# original: https://gist.github.com/782263
# with these comments: https://gist.github.com/782312

# This all assumes you have the process running in 
# a terminal screen and you're on Linux-like system.

# First off, suspend the process and background it 
ctrl-z # suspend the process
bg # restart/continue the process in the background

# Now create files to log to. They can be called anything,
# Personally I would end the in .log. E.g. could be
# /var/logs/myprocess-stdout.log, 
# and /var/logs/myprocess-stderr.log
touch /tmp/stdout # create empty stdout log
touch /tmp/stderr # create empty stderr log

# Here's the real cleverness: Invoke the 
# GNU Debugger (gdb), a very powerful
# code debugger used most by C systems programmers.
gdb -p $! # invoke gdb and attach the process by its PID 
          # (conveniently stored in $! by our last couple commands)


# In GDB we can actually execute C code
# against the running process. That's what
# we're doing here: Calling the C system
# calls 'open' and 'dup2'. Open returns new file descriptors
# for both our files that we can write to. dup2
# aliases the fd given as a first paramter with the second parameter 
# and closes the original one: in essence redirecting
# and cleaning up in one nice call.
# 1 is the standard/default fd for stdout, 2 is stderr.
p dup2(open("/tmp/stdout", 1), 1)
p dup2(open("/tmp/stderr", 1), 2)
detach # released process from gdb control
quit # quit gdb

# Back in shell
# disown is a bashism that essentially let's you 'nohup'
# a currently running process. It means it will keep
# running after you log out (you've 'disowned' it as an
# attached/dependent child process of your terminal session)
disown
# and... we're done!
logout