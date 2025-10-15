import { useEffect, useMemo, useState } from 'react';
import './App.css';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [message, setMessage] = useState('Loading backend message…');

  const apiBaseUrl = useMemo(() => {
    const envUrl = import.meta.env.VITE_API_BASE_URL?.trim();
    return envUrl && envUrl.length > 0 ? envUrl.replace(/\/$/, '') : DEFAULT_API_BASE_URL;
  }, []);

  useEffect(() => {
    fetch(`${apiBaseUrl}/api/hello`)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as { message: string };
        setMessage(data.message);
      })
      .catch(() => {
        setMessage('Backend unavailable. Is it running?');
      });
  }, [apiBaseUrl]);

  return (
    <main className="app">
      <h1>Hello from React</h1>
      <p>{message}</p>
    </main>
  );
}

export default App;
