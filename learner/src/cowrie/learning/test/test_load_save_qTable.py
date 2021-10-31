from learner.src.cowrie.learning.rl.learning_algorithm import CentralAlgorithm

alg = CentralAlgorithm('Q-Learning', 0.1, 0.9, 0.5, 0.2, 50)
alg.saveLearningState('q_table')
alg.loadLearningState('q_table')
print(alg.command_dict.outputs)
