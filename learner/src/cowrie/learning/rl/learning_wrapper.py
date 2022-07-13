from cowrie.learning.rl.learning_algorithm import CentralAlgorithm
from cowrie.learning.rl.environment import LearningEnv
from twisted.python import log
from cowrie.core.config import CowrieConfig


class LearningAlgHandler:
    central_alg = None

    def init_central_alg(self):
        alg_name = CowrieConfig.get('learning', 'alg_name')
        learning_rate = CowrieConfig.getfloat('learning', 'learning_rate')
        discount = CowrieConfig.getfloat('learning', 'discount')
        epsilon = CowrieConfig.getfloat('learning', 'epsilon')
        evaluation = CowrieConfig.getboolean('learning', 'evaluation')

        self.central_alg = CentralAlgorithm(alg=alg_name, learning_rate=learning_rate, discount=discount,
                                             epsilon=epsilon, evaluation=evaluation)

        log.msg(eventid='cannypot.manager', format="Central algorithm initialized")

    def get_learning_env(self):
        env = LearningEnv()
        env.init_learning_alg(self.central_alg.getAlgInstance())
        return env

    def episode_finished(self, job):
        self.central_alg.insertJobInQueue(job)
