import { useState } from "react";
import TopicInput from "./components/TopicInput";
import ResearchPanel from "./components/ResearchPanel";
import ScriptEditor from "./components/ScriptEditor";
import VoiceSelector from "./components/VoiceSelector";
import VideoPreview from "./components/VideoPreview";
import UploadPanel from "./components/UploadPanel";
import StepIndicator from "./components/StepIndicator";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [step, setStep] = useState(0);
  const [topic, setTopic] = useState("");
  const [researchData, setResearchData] = useState(null);
  const [script, setScript] = useState(null);
  const [voiceData, setVoiceData] = useState(null);
  const [videoData, setVideoData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");

  const steps = ["Topic", "Research", "Script", "Voice", "Video", "Upload"];

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">▶</span>
          <span className="logo-text">AutoTube</span>
          <span className="logo-badge">AI</span>
        </div>
        <p className="tagline">From idea to YouTube — fully automated</p>
      </header>

      <StepIndicator steps={steps} currentStep={step} />

      <main className="app-main">
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner" />
            <p className="loading-msg">{loadingMsg}</p>
          </div>
        )}

        {step === 0 && (
          <TopicInput
            onSubmit={async (t, opts) => {
              setTopic(t);
              setLoading(true);
              setLoadingMsg("🔍 Researching your topic across the web...");
              try {
                const res = await fetch(`${API_BASE}/api/research/`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ topic: t, depth: opts.depth })
                });
                const data = await res.json();
                setResearchData(data.data);
                setStep(1);
              } catch (e) {
                alert("Research failed: " + e.message);
              } finally {
                setLoading(false);
              }
            }}
          />
        )}

        {step === 1 && researchData && (
          <ResearchPanel
            topic={topic}
            data={researchData}
            onApprove={async (opts) => {
              setLoading(true);
              setLoadingMsg("✍️ Writing your YouTube script with AI...");
              try {
                const res = await fetch(`${API_BASE}/api/script/generate`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    topic,
                    research_data: researchData,
                    duration: opts.duration,
                    style: opts.style
                  })
                });
                const data = await res.json();
                setScript(data.data);
                setStep(2);
              } catch (e) {
                alert("Script generation failed: " + e.message);
              } finally {
                setLoading(false);
              }
            }}
            onRedo={() => setStep(0)}
          />
        )}

        {step === 2 && script && (
          <ScriptEditor
            script={script}
            onApprove={() => setStep(3)}
            onEdit={async (feedback) => {
              setLoading(true);
              setLoadingMsg("✏️ Updating script based on your feedback...");
              try {
                const res = await fetch(`${API_BASE}/api/script/edit`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ script: JSON.stringify(script), feedback })
                });
                const data = await res.json();
                setScript(data.data);
              } catch (e) {
                alert("Edit failed: " + e.message);
              } finally {
                setLoading(false);
              }
            }}
            onBack={() => setStep(1)}
          />
        )}

        {step === 3 && script && (
          <VoiceSelector
            script={script}
            onGenerate={async (voice, speed) => {
              setLoading(true);
              setLoadingMsg("🎙️ Generating voiceover with Microsoft Edge TTS...");
              try {
                const res = await fetch(`${API_BASE}/api/voice/generate`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ script, voice, speed })
                });
                const data = await res.json();
                setVoiceData(data.data);
                setStep(4);
              } catch (e) {
                alert("Voice generation failed: " + e.message);
              } finally {
                setLoading(false);
              }
            }}
            apiBase={API_BASE}
            onBack={() => setStep(2)}
          />
        )}

        {step === 4 && script && voiceData && (
          <VideoPreview
            topic={topic}
            script={script}
            voiceData={voiceData}
            apiBase={API_BASE}
            onApprove={(vd) => { setVideoData(vd); setStep(5); }}
            onBack={() => setStep(3)}
            onGenerateVideo={async (resolution) => {
              setLoading(true);
              setLoadingMsg("🎬 Creating video with Pexels stock footage... (2-5 mins)");
              try {
                const res = await fetch(`${API_BASE}/api/video/generate`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ topic, script, audio_file: voiceData, resolution })
                });
                const data = await res.json();
                return data.data;
              } catch (e) {
                alert("Video generation failed: " + e.message);
                return null;
              } finally {
                setLoading(false);
              }
            }}
          />
        )}

        {step === 5 && videoData && script && (
          <UploadPanel
            videoData={videoData}
            script={script}
            apiBase={API_BASE}
            onSuccess={(url) => {
              alert(`🎉 Video uploaded! Watch at: ${url}`);
              window.open(url, "_blank");
            }}
            onBack={() => setStep(4)}
          />
        )}
      </main>
    </div>
  );
}
