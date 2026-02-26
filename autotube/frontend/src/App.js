import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const STEPS = [
  { key: 'researching', label: 'Researching', icon: '🔍' },
  { key: 'scripting', label: 'Writing Script', icon: '✍️' },
  { key: 'voicing', label: 'Voiceover', icon: '🎙️' },
  { key: 'creating_video', label: 'Creating Video', icon: '🎬' },
  { key: 'ready', label: 'Ready', icon: '✅' },
];

export default function App() {
  const [page, setPage] = useState('home'); // home | generating | review | upload | done
  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState('informative');
  const [duration, setDuration] = useState(60);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [ytTitle, setYtTitle] = useState('');
  const [ytDesc, setYtDesc] = useState('');
  const [ytTags, setYtTags] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [showScript, setShowScript] = useState(false);
  const [error, setError] = useState('');
  const pollRef = useRef(null);

  const startPolling = (id) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status/${id}`);
        const data = await res.json();
        setJobStatus(data);
        if (data.status === 'ready') {
          clearInterval(pollRef.current);
          setPage('review');
        } else if (data.status === 'error') {
          clearInterval(pollRef.current);
          setError(data.error || 'Something went wrong');
        } else if (data.status === 'uploaded') {
          clearInterval(pollRef.current);
          setPage('done');
        }
      } catch (e) {
        // silent retry
      }
    }, 2000);
  };

  useEffect(() => () => clearInterval(pollRef.current), []);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setError('');
    setPage('generating');
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, style, duration })
      });
      const data = await res.json();
      setJobId(data.job_id);
      setJobStatus({ status: 'queued', step: 'Starting...', progress: 0, topic });
      startPolling(data.job_id);
    } catch (e) {
      setError('Failed to connect to backend. Is it running?');
      setPage('home');
    }
  };

  const handleApprove = async () => {
    await fetch(`${API_BASE}/api/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, approved: true })
    });
    setPage('upload');
  };

  const handleReject = async () => {
    await fetch(`${API_BASE}/api/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, approved: false, feedback })
    });
    // Regenerate
    setFeedback('');
    setPage('generating');
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: jobStatus?.topic || topic, style, duration })
    });
    const data = await res.json();
    setJobId(data.job_id);
    setJobStatus({ status: 'queued', step: 'Regenerating...', progress: 0, topic });
    startPolling(data.job_id);
  };

  const handleUpload = async () => {
    if (!accessToken.trim()) { setError('Please paste your YouTube access token'); return; }
    setError('');
    setPage('generating');
    setJobStatus({ status: 'uploading', step: 'Uploading to YouTube...', progress: 90, topic });
    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          access_token: accessToken,
          youtube_title: ytTitle || topic,
          youtube_description: ytDesc,
          youtube_tags: ytTags.split(',').map(t => t.trim()).filter(Boolean)
        })
      });
      await res.json();
      startPolling(jobId);
    } catch (e) {
      setError('Upload failed: ' + e.message);
      setPage('upload');
    }
  };

  const currentStepIdx = STEPS.findIndex(s => s.key === jobStatus?.status);

  return (
    <div className="app">
      <div className="noise" />
      <div className="grid-lines" />

      {/* Header */}
      <header className="header">
        <div className="logo" onClick={() => { setPage('home'); clearInterval(pollRef.current); }}>
          <span className="logo-icon">▶</span>
          <span className="logo-text">AutoTube</span>
          <span className="logo-badge">AI</span>
        </div>
        <div className="header-sub">Free AI Video Agent</div>
      </header>

      {/* HOME PAGE */}
      {page === 'home' && (
        <main className="home">
          <div className="hero">
            <div className="hero-eyebrow">Powered by Groq + Pexels + Edge TTS</div>
            <h1 className="hero-title">
              Turn any topic into<br />
              <span className="gradient-text">a YouTube video</span><br />
              in minutes
            </h1>
            <p className="hero-sub">Research → Script → Voiceover → Video → Upload. All automated. All free.</p>
          </div>

          <div className="input-card">
            <div className="input-section">
              <label className="input-label">What's your video about?</label>
              <input
                className="topic-input"
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleGenerate()}
                placeholder="e.g. How Black Holes Are Formed"
                autoFocus
              />
            </div>

            <div className="options-row">
              <div className="option-group">
                <label className="option-label">Style</label>
                <div className="pill-group">
                  {['informative', 'story', 'tutorial'].map(s => (
                    <button key={s} className={`pill ${style === s ? 'pill-active' : ''}`} onClick={() => setStyle(s)}>
                      {s === 'informative' ? '📖 Informative' : s === 'story' ? '🎭 Story' : '🛠️ Tutorial'}
                    </button>
                  ))}
                </div>
              </div>

              <div className="option-group">
                <label className="option-label">Duration: <strong>{duration}s</strong></label>
                <input
                  type="range" min="30" max="180" step="15"
                  value={duration}
                  onChange={e => setDuration(Number(e.target.value))}
                  className="slider"
                />
                <div className="slider-labels"><span>30s</span><span>3min</span></div>
              </div>
            </div>

            {error && <div className="error-box">⚠️ {error}</div>}

            <button className="generate-btn" onClick={handleGenerate} disabled={!topic.trim()}>
              <span>Generate Video</span>
              <span className="btn-arrow">→</span>
            </button>
          </div>

          <div className="flow-steps">
            {['🔍 Research', '✍️ Script', '🎙️ Voice', '🎬 Video', '📤 Upload'].map((step, i) => (
              <React.Fragment key={step}>
                <div className="flow-step">{step}</div>
                {i < 4 && <div className="flow-arrow">›</div>}
              </React.Fragment>
            ))}
          </div>
        </main>
      )}

      {/* GENERATING PAGE */}
      {page === 'generating' && (
        <main className="generating">
          <div className="gen-card">
            <div className="gen-topic">"{jobStatus?.topic || topic}"</div>
            <h2 className="gen-title">Your video is being created</h2>

            <div className="progress-track">
              <div className="progress-bar" style={{ width: `${jobStatus?.progress || 0}%` }} />
            </div>
            <div className="progress-label">{jobStatus?.step || 'Starting...'} — {jobStatus?.progress || 0}%</div>

            <div className="steps-list">
              {STEPS.map((s, i) => {
                const done = currentStepIdx > i;
                const active = currentStepIdx === i;
                return (
                  <div key={s.key} className={`step-item ${done ? 'step-done' : active ? 'step-active' : 'step-pending'}`}>
                    <span className="step-icon">{done ? '✓' : s.icon}</span>
                    <span className="step-label">{s.label}</span>
                    {active && <span className="step-spinner" />}
                  </div>
                );
              })}
            </div>
          </div>
        </main>
      )}

      {/* REVIEW PAGE */}
      {page === 'review' && jobStatus && (
        <main className="review">
          <div className="review-header">
            <h2>Review Your Video</h2>
            <p>Watch the preview below. Approve to proceed to upload, or request changes.</p>
          </div>

          <div className="review-grid">
            <div className="video-panel">
              <video
                className="video-preview"
                src={`${API_BASE}${jobStatus.video_url}`}
                controls
                autoPlay={false}
              />
            </div>

            <div className="review-panel">
              <div className="review-meta">
                <div className="meta-item"><span className="meta-key">Topic</span><span className="meta-val">{jobStatus.topic}</span></div>
                <div className="meta-item"><span className="meta-key">Style</span><span className="meta-val">{style}</span></div>
                <div className="meta-item"><span className="meta-key">Duration</span><span className="meta-val">~{duration}s</span></div>
              </div>

              <button className="script-toggle" onClick={() => setShowScript(!showScript)}>
                {showScript ? '▲ Hide Script' : '▼ View Script'}
              </button>

              {showScript && (
                <div className="script-box">
                  <pre className="script-text">{jobStatus.script}</pre>
                </div>
              )}

              <div className="review-actions">
                <button className="approve-btn" onClick={handleApprove}>
                  ✅ Approve & Continue to Upload
                </button>

                <div className="reject-section">
                  <textarea
                    className="feedback-input"
                    value={feedback}
                    onChange={e => setFeedback(e.target.value)}
                    placeholder="Optional: Tell AI what to change (e.g. 'Make it more dramatic')"
                    rows={3}
                  />
                  <button className="reject-btn" onClick={handleReject}>
                    🔄 Regenerate Video
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      )}

      {/* UPLOAD PAGE */}
      {page === 'upload' && (
        <main className="upload-page">
          <div className="upload-card">
            <h2>Upload to YouTube</h2>
            <p className="upload-sub">Paste your YouTube OAuth access token to upload. <a href="https://developers.google.com/oauthplayground" target="_blank" rel="noreferrer" className="link">Get token here ↗</a></p>

            <div className="field">
              <label>Video Title</label>
              <input className="yt-input" value={ytTitle} onChange={e => setYtTitle(e.target.value)} placeholder={topic} />
            </div>
            <div className="field">
              <label>Description</label>
              <textarea className="yt-input" value={ytDesc} onChange={e => setYtDesc(e.target.value)} rows={4} placeholder="Video description..." />
            </div>
            <div className="field">
              <label>Tags (comma separated)</label>
              <input className="yt-input" value={ytTags} onChange={e => setYtTags(e.target.value)} placeholder="ai, technology, tutorial" />
            </div>
            <div className="field">
              <label>YouTube OAuth Access Token <span className="required">*</span></label>
              <input className="yt-input token-input" value={accessToken} onChange={e => setAccessToken(e.target.value)} placeholder="ya29.a0..." type="password" />
            </div>

            {error && <div className="error-box">⚠️ {error}</div>}

            <div className="upload-actions">
              <button className="upload-btn" onClick={handleUpload}>
                📤 Upload to YouTube
              </button>
              <button className="skip-btn" onClick={() => setPage('done')}>
                Skip — Download Only
              </button>
            </div>
          </div>
        </main>
      )}

      {/* DONE PAGE */}
      {page === 'done' && (
        <main className="done-page">
          <div className="done-card">
            <div className="done-icon">🎉</div>
            <h2>Video Complete!</h2>
            {jobStatus?.youtube_url ? (
              <>
                <p>Your video has been uploaded to YouTube.</p>
                <a href={jobStatus.youtube_url} target="_blank" rel="noreferrer" className="yt-link">
                  View on YouTube ↗
                </a>
              </>
            ) : (
              <p>Your video is ready. You can download it below.</p>
            )}
            <div className="done-actions">
              <a className="download-btn" href={`${API_BASE}${jobStatus?.video_url}`} download>
                ⬇️ Download Video
              </a>
              <button className="new-btn" onClick={() => { setPage('home'); setTopic(''); setJobId(null); setJobStatus(null); }}>
                + Create Another
              </button>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
