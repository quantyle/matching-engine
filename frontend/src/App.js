import { useState } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {

  const [counter, setCounter] = useState(0);

  const increment = () => {
    setCounter(counter + 1);
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a className="App-link">
          {counter}
        </a>
        <button onClick={increment}>
          increment  
        </button> 
      </header>
    </div>
  );
}

export default App;
