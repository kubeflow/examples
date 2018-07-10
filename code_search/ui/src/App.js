import React, { Component } from 'react';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { MuiThemeProvider } from '@material-ui/core/styles';
import blueTheme from './theme';
import logo from './logo.svg';
import './App.css';
import SearchIcon from '@material-ui/icons/Search';

class App extends Component {
  render() {
    return (
      <MuiThemeProvider theme={blueTheme}>
        <div className="App">
          <header className="App-header">
            <img src={logo} className="App-logo" alt="logo" />
            <h1 className="App-title">Demo: Code Search</h1>
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
              <Button
                variant="contained"
                color="primary"
                id="Search-Button"
              >
                <SearchIcon/>Search Code
              </Button>
        </div>
      </MuiThemeProvider>
    );
  }
}

export default App;
