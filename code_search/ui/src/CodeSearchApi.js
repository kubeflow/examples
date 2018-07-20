const results = [
  {
    nwo: 'activatedgeek/torchrl',
    path: 'torchrl/agents/random_gym_agent.py',
    lineno: 19,
    function_string: `
def act(self, obs):
  return [[self.action_space.sample()] for _ in range(len(obs))]
    `,
  },
  {
    nwo: 'activatedgeek/torchrl',
    path: 'torchrl/policies/epsilon_greedy.py',
    lineno: 4,
    function_string: `
distribution = np.ones((len(choices), action_size),
                       dtype=np.float32) * eps / action_size
distribution[np.arange(len(choices)), choices] += 1.0 - eps
actions = np.array([
    np.random.choice(np.arange(action_size), p=dist)
    for dist in distribution
])
return np.expand_dims(actions, axis=1)
    `,
  },
];

function code_search_api(str, callback) {
  // TODO: make a real request, this is simulated
  window.setTimeout(() => {
    callback({status: 200, results: results});
  }, 2000);
}

export default code_search_api;
