"""The classic Tiger problem.

This is a POMDP problem; Namely, it specifies both
the POMDP (i.e. state, action, observation space)
and the T/O/R for the agent as well as the environment.

The description of the tiger problem is as follows: (Quote from `POMDP:
Introduction to Partially Observable Markov Decision Processes
<https://cran.r-project.org/web/packages/pomdp/vignettes/POMDP.pdf>`_ by
Kamalzadeh and Hahsler )

A tiger is put with equal probability behind one
of two doors, while treasure is put behind the other one.
You are standing in front of the two closed doors and
need to decide which one to open. If you open the door
with the tiger, you will get hurt (negative reward).
But if you open the door with treasure, you receive
a positive reward. Instead of opening a door right away,
you also have the option to wait and listen for tiger noises. But
listening is neither free nor entirely accurate. You might hear the
tiger behind the left door while it is actually behind the right
door and vice versa.

States: tiger-left, tiger-right
Actions: open-left, open-right, listen
Rewards: 
    +10 for opening treasure door. -100 for opening tiger door.
    -1 for listening.
Observations: You can hear either "tiger-left", or "tiger-right".

Note that in this example, the TigerProblem is a POMDP that
also contains the agent and the environment as its fields. In
general this doesn't need to be the case. (Refer to more complicated
examples.)

"""

import pomdp_py
import random
import numpy as np
import sys

def build_states(strings):
    return {State(s) for s in strings}
def build_actions(strings):
    return {Action(s) for s in strings}
def build_observations(strings):
    return {Observation(s) for s in strings}

class State(pomdp_py.State):
    def __init__(self, name):
        if name != "tiger-left" and name != "tiger-right":
            raise ValueError("Invalid state: %s" % name)
        self.name = name
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
    def __str__(self):
        return self.name
    def __repr__(self):
        return "State(%s)" % self.name
    
class Action(pomdp_py.Action):
    def __init__(self, name):
        if name != "open-left" and name != "open-right"\
           and name != "listen":
            raise ValueError("Invalid action: %s" % name)        
        self.name = name
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        if isinstance(other, Action):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
    def __str__(self):
        return self.name
    def __repr__(self):
        return "Action(%s)" % self.name
    
class Observation(pomdp_py.Observation):
    def __init__(self, name):
        if name != "tiger-left" and name != "tiger-right":
            raise ValueError("Invalid action: %s" % name)                
        self.name = name
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        if isinstance(other, Observation):
            return self.name == other.name
        elif type(other) == str:
            return self.name == other
    def __str__(self):
        return self.name
    def __repr__(self):
        return "Observation(%s)" % self.name

# Observation model
class ObservationModel(pomdp_py.ObservationModel):
    """This problem is small enough for the probabilities to be directly given
    externally"""
    def __init__(self, probs):
        self._probs = probs

    def probability(self, observation, next_state, action, normalized=False, **kwargs):
        return self._probs[next_state][action][observation]

    def sample(self, next_state, action, normalized=False, **kwargs):
        return self.get_distribution(next_state, action).random()

    def argmax(self, next_state, action, normalized=False, **kwargs):
        """Returns the most likely observation"""
        return max(self._probs[next_state][action], key=self._probs[next_state][action].get)

    def get_distribution(self, next_state, action, **kwargs):
        """Returns the underlying distribution of the model; In this case, it's just a histogram"""
        return pomdp_py.Histogram(self._probs[next_state][action])

    def get_all_observations(self):
        return TigerProblem.OBSERVATIONS

# Transition Model
class TransitionModel(pomdp_py.TransitionModel):
    """This problem is small enough for the probabilities to be directly given
            externally"""
    def __init__(self, probs):
        self._probs = probs

    def probability(self, next_state, state, action, normalized=False, **kwargs):
        return self._probs[state][action][next_state]

    def sample(self, state, action, normalized=False, **kwargs):
        return self.get_distribution(state, action).random()

    def argmax(self, state, action, normalized=False, **kwargs):
        """Returns the most likely next state"""
        return max(self._probs[state][action], key=self._probs[state][action].get) 

    def get_distribution(self, state, action, **kwargs):
        """Returns the underlying distribution of the model"""
        return pomdp_py.Histogram(self._probs[state][action])

    def get_all_states(self):
        return TigerProblem.STATES

# Reward Model
class RewardModel(pomdp_py.RewardModel):
    def __init__(self, scale=1):
        self._scale = scale
    def _reward_func(self, state, action):
        reward = 0
        if action == "open-left":
            if state== "tiger-right":
                reward += 10 * self._scale
            else:
                reward -= 100 * self._scale
        elif action == "open-right":
            if state== "tiger-left":
                reward += 10 * self._scale
            else:
                reward -= 100 * self._scale
        elif action == "listen":
            reward -= 1 * self._scale
        return reward

    def probability(self, reward, state, action, next_state, normalized=False, **kwargs):
        if reward == self._reward_func(state, action):
            return 1.0
        else:
            return 0.0

    def sample(self, state, action, next_state, normalized=False, **kwargs):
        # deterministic
        return self._reward_func(state, action)

    def argmax(self, state, action, next_state, normalized=False, **kwargs):
        """Returns the most likely reward"""
        return self._reward_func(state, action)

    def get_distribution(self, state, action, next_state, **kwargs):
        """Returns the underlying distribution of the model"""
        reward = self._reward_func(state, action)
        return pomdp_py.Histogram({reward:1.0})

# Policy Model
class PolicyModel(pomdp_py.RandomRollout):
    """This is an extremely dumb policy model; To keep consistent
    with the framework."""
    def probability(self, action, state, normalized=False, **kwargs):
        raise NotImplementedError  # Never used
    
    def sample(self, state, normalized=False, **kwargs):
        return self.get_all_actions().random()
    
    def argmax(self, state, normalized=False, **kwargs):
        """Returns the most likely reward"""
        raise NotImplementedError
    
    def get_all_actions(self, **kwargs):
        return TigerProblem.ACTIONS

        
class TigerProblem(pomdp_py.POMDP):

    STATES = build_states({"tiger-left", "tiger-right"})
    ACTIONS = build_actions({"open-left", "open-right", "listen"})
    OBSERVATIONS = build_observations({"tiger-left", "tiger-right"})

    def __init__(self, obs_probs, trans_probs, init_true_state, init_belief):
        """init_belief is a Distribution."""
        self._obs_probs = obs_probs
        self._trans_probs = trans_probs

        
        agent = pomdp_py.Agent(init_belief,
                               PolicyModel(),
                               TransitionModel(self._trans_probs),
                               ObservationModel(self._obs_probs),
                               RewardModel())
        env = pomdp_py.Environment(init_true_state,
                                   TransitionModel(self._trans_probs),
                                   RewardModel())
        super().__init__(agent, env, name="TigerProblem")


def test_planner(tiger_problem, planner, nsteps=3):
    """
    Runs the action-feedback loop of Tiger problem POMDP

    Args:
        tiger_problem (TigerProblem): an instance of the tiger problem.
        planner (Planner): a planner
        nsteps (int): Maximum number of steps to run this loop.
    """
    for i in range(nsteps):
        action = planner.plan(tiger_problem.agent)
        print("==== Step %d ====" % (i+1))
        print("True state: %s" % tiger_problem.env.state)
        print("Belief: %s" % str(tiger_problem.agent.cur_belief))
        print("Action: %s" % str(action))
        print("Reward: %s" % str(tiger_problem.env.reward_model.sample(tiger_problem.env.state, action, None)))

        # Let's create some simulated real observation; Update the belief
        # Creating true observation for sanity checking solver behavior.
        # In general, this observation should be sampled from agent's observation model.
        real_observation = Observation(tiger_problem.env.state.name)
        print(">> Observation: %s" % real_observation)
        tiger_problem.agent.update_history(action, real_observation)
        
        planner.update(tiger_problem.agent, action, real_observation)
        if isinstance(planner, pomdp_py.POUCT):
            print("Num sims: %d" % planner.last_num_sims)
        if isinstance(tiger_problem.agent.cur_belief, pomdp_py.Histogram):
            new_belief = pomdp_py.update_histogram_belief(tiger_problem.agent.cur_belief,
                                                          action, real_observation,
                                                          tiger_problem.agent.observation_model,
                                                          tiger_problem.agent.transition_model)
            tiger_problem.agent.set_belief(new_belief)

def build_setting(setting):
    result = {'obs_probs':{}, 'trans_probs':{}}
    for sp in setting['obs_probs']:
        result['obs_probs'][State(sp)] = {}
        for a in setting['obs_probs'][sp]:
            result['obs_probs'][State(sp)][Action(a)] =\
                {Observation(o):setting['obs_probs'][sp][a][o]
                 for o in setting['obs_probs'][sp][a]}
    for s in setting['trans_probs']:
        result['trans_probs'][State(s)] = {}
        for a in setting['trans_probs'][s]:
            result['trans_probs'][State(s)][Action(a)] =\
                {State(sp):setting['trans_probs'][s][a][sp]
                 for sp in setting['trans_probs'][s][a]}
    return result
            
def main():
    ## Setting 1:
    ## The values are set according to the paper.
    setting1 = {
        "obs_probs": {  # next_state -> action -> observation
            "tiger-left":{ 
                "open-left": {"tiger-left": 0.5, "tiger-right": 0.5},
                "open-right": {"tiger-left": 0.5, "tiger-right": 0.5},
                "listen": {"tiger-left": 0.85, "tiger-right": 0.15}
            },
            "tiger-right":{
                "open-left": {"tiger-left": 0.5, "tiger-right": 0.5},
                "open-right": {"tiger-left": 0.5, "tiger-right": 0.5},
                "listen": {"tiger-left": 0.15, "tiger-right": 0.85}
            }
        },
        
        "trans_probs": {  # state -> action -> next_state
            "tiger-left":{ 
                "open-left": {"tiger-left": 0.5, "tiger-right": 0.5},
                "open-right": {"tiger-left": 0.5, "tiger-right": 0.5},
                "listen": {"tiger-left": 1.0, "tiger-right": 0.0}
            },
            "tiger-right":{
                "open-left": {"tiger-left": 0.5, "tiger-right": 0.5},
                "open-right": {"tiger-left": 0.5, "tiger-right": 0.5},
                "listen": {"tiger-left": 0.0, "tiger-right": 1.0}
            }
        }
    }

    ## Setting 2:
    ## Based on my understanding of T and O; Treat the state as given.
    setting2 = {
        "obs_probs": {  # next_state -> action -> observation
            "tiger-left":{ 
                "open-left": {"tiger-left": 1.0, "tiger-right": 0.0},
                "open-right": {"tiger-left": 1.0, "tiger-right": 0.0},
                "listen": {"tiger-left": 0.85, "tiger-right": 0.15}
            },
            "tiger-right":{
                "open-left": {"tiger-left": 0.0, "tiger-right": 1.0},
                "open-right": {"tiger-left": 0.0, "tiger-right": 1.0},
                "listen": {"tiger-left": 0.15, "tiger-right": 0.85}
            }
        },
        
        "trans_probs": {  # state -> action -> next_state
            "tiger-left":{ 
                "open-left": {"tiger-left": 1.0, "tiger-right": 0.0},
                "open-right": {"tiger-left": 1.0, "tiger-right": 0.0},
                "listen": {"tiger-left": 1.0, "tiger-right": 0.0}
            },
            "tiger-right":{
                "open-left": {"tiger-left": 0.0, "tiger-right": 1.0},
                "open-right": {"tiger-left": 0.0, "tiger-right": 1.0},
                "listen": {"tiger-left": 0.0, "tiger-right": 1.0}
            }
        }
    }

    # setting1 resets the problem after the agent chooses open-left or open-right;
    # It's reasonable - when the agent opens one door and sees a tiger, it gets
    # killed; when the agent sees a treasure, it will take some of the treasure
    # and leave. Thus, the agent will have no incentive to close the door and do
    # this again. The setting2 is the case where the agent is a robot, and only
    # cares about getting higher reward.
    setting = build_setting(setting1)

    init_true_state = random.choice(list(TigerProblem.STATES))
    init_belief = pomdp_py.Histogram({State("tiger-left"): 0.5,
                                      State("tiger-right"): 0.5})
    tiger_problem = TigerProblem(setting['obs_probs'],
                                 setting['trans_probs'],
                                 init_true_state, init_belief)

    # Value iteration
    print("** Testing value iteration **")
    vi = pomdp_py.ValueIteration(horizon=2, discount_factor=0.99)
    test_planner(tiger_problem, vi, nsteps=3)

    # Reset agent belief
    tiger_problem.agent.set_belief(init_belief, prior=True)

    print("** Testing POUCT **")
    pouct = pomdp_py.POUCT(max_depth=10, discount_factor=0.95,
                           planning_time=.5, exploration_const=110,
                           rollout_policy=tiger_problem.agent.policy_model)
    test_planner(tiger_problem, pouct, nsteps=10)

    pomdp_py.visual.visualize_pouct_search_tree(tiger_problem.agent.tree,
                                                max_depth=5, anonymize=False)

    # Reset agent belief    
    tiger_problem.agent.set_belief(init_belief, prior=True)
    tiger_problem.agent.tree = None
    
    print("** Testing POMCP **")
    tiger_problem.agent.set_belief(pomdp_py.Particles.from_histogram(init_belief, num_particles=100), prior=True)
    pomcp = pomdp_py.POMCP(max_depth=10, discount_factor=0.95,
                           planning_time=.5, exploration_const=110,
                           rollout_policy=tiger_problem.agent.policy_model)
    test_planner(tiger_problem, pomcp, nsteps=10)
    
    pomdp_py.visual.visualize_pouct_search_tree(tiger_problem.agent.tree,
                                                max_depth=5, anonymize=False)

if __name__ == '__main__':
    main()
