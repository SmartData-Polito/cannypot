from learner.src.cowrie.learning.rl.learning_wrapper import LearningAlgHandler

l_h = LearningAlgHandler()
l_h.init_central_alg()
env = l_h.get_learning_env()
print(env.learning_alg.q_table)
env.command_received('CommandA')
env.command_received('CommandA')
env.command_received('CommandA')
print(env.learning_alg.q_table)
job = env.connection_closed()
print(job)
