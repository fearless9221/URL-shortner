import { useState } from 'react';

export default function App() {
  const [url, setUrl] = useState('');
  const [shortUrl, setShortUrl] = useState('');
  const [code, setCode] = useState('');
  const [clicks, setClicks] = useState(null);

  const shortenLink = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ long_url: url })
    });
    const data = await res.json();
    setShortUrl(data.short_url);
  };

  const checkStats = async (e) => {
    e.preventDefault();
    const res = await fetch(`http://localhost:8000/stats/${code}`);
    const data = await res.json();
    setClicks(data.total_clicks);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>1. Create Link</h2>
      <form onSubmit={shortenLink}>
        <input 
          value={url} 
          onChange={e => setUrl(e.target.value)} 
          placeholder="Enter long URL" 
          required 
        />
        <button type="submit">Shorten</button>
      </form>
      {shortUrl && <p>Short Link: <a href={shortUrl} target="_blank" rel="noreferrer">{shortUrl}</a></p>}

      <hr style={{ margin: '20px 0' }} />

      <h2>2. View Analytics</h2>
      <form onSubmit={checkStats}>
        <input 
          value={code} 
          onChange={e => setCode(e.target.value)} 
          placeholder="Enter short code" 
          required 
        />
        <button type="submit">Check Clicks</button>
      </form>
      {clicks !== null && <p>Total Clicks: {clicks}</p>}
    </div>
  );
}
