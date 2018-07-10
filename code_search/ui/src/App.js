import React, { Component } from 'react';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { MuiThemeProvider } from '@material-ui/core/styles';
import SearchIcon from '@material-ui/icons/Search';

import blueTheme from './theme';
import logo from './logo.svg';
import './App.css';
import CodeSample from './CodeSample';

class App extends Component {
  render() {
    return (
      <MuiThemeProvider theme={blueTheme}>
        <div className="App">
          <header className="App-header">
            <img src={logo} className="App-logo" alt="logo" />
            <h1 className="App-title">Code Search Demo</h1>
          </header>
            <div className="Search-Wrapper">
              <TextField
                id="Search-Bar"
                placeholder="Enter Search Query Here"
                InputProps={{
                  disableUnderline: true,
                }}
              />
            </div>
            <div className="Search-Wrapper">
              <Button
                variant="contained"
                color="primary"
                id="Search-Button"
              >
                <SearchIcon/>Search Code
              </Button>
            </div>
            <div className="Search-Results">
              <h2 className="Search-Results-Title">Search Results</h2>
              {/** TODO: for illustrative purposes only  **/}
              <CodeSample
                nwo="activatedgeek/torchrl"
                path="torchrl/agents/random_gym_agent.py"
                lineno={19}
                function_string={`
def act(self, obs):
  return [[self.action_space.sample()] for _ in range(len(obs))]
                `}
              />
              <hr />
              <CodeSample
                nwo="activatedgeek/torchrl"
                path="torchrl/policies/epsilon_greedy.py"
                lineno={4}
                function_string={`
distribution = np.ones((len(choices), action_size),
                       dtype=np.float32) * eps / action_size
distribution[np.arange(len(choices)), choices] += 1.0 - eps
actions = np.array([
    np.random.choice(np.arange(action_size), p=dist)
    for dist in distribution
])
return np.expand_dims(actions, axis=1)
                `}
              />
            </div>
        </div>
      </MuiThemeProvider>
    );
  }
}

export default App;
