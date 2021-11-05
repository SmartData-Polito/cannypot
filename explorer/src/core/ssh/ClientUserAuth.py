from twisted.conch.ssh import keys, userauth
from twisted.internet import defer


class ClientUserAuth(userauth.SSHUserAuthClient):

    preferredOrder = [b"password", b"publickey", b"keyboard-interactive"]

    def __init__(self, user, instance, password):
        userauth.SSHUserAuthClient.__init__(self, user, instance)
        self.password = password

    def getPassword(self, prompt=None):
        if self.password:
            return defer.succeed(self.password)
        else:
            return

    def getPublicKey(self):
        print("Getting public key")
        return keys.Key.fromFile('/root/.ssh/id_rsa.pub')

    def getPrivateKey(self):
        print("Getting private key")
        return defer.succeed(keys.Key.fromFile('/root/.ssh/id_rsa'))
