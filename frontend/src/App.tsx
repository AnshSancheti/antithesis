import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('Loading backend message…');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/hello')
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as { message: string };
        setMessage(data.message);
      })
      .catch(() => {
        setMessage('Backend unavailable. Is it running on port 8000?');
      });
  }, []);

  return (
    <main className="app">
      <h1>Hello from React</h1>
      <p>{message}</p>
    </main>
  );
}

export default App;
