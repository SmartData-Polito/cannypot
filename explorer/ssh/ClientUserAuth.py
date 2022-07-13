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
        return keys.Key.fromFile('/root/.ssh/id_rsa.pub')

    def getPrivateKey(self):
        return defer.succeed(keys.Key.fromFile('/root/.ssh/id_rsa'))