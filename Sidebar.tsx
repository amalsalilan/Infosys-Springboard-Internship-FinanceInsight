// Sidebar.tsx



import { Button } from "@/components/ui/button";
import { BarChart3, Tag, Languages } from "lucide-react";
import { cn } from "@/lib/utils";
import React, { useEffect, useState } from "react";

interface SidebarProps {
  onAnalysisSelect: (type: string) => void;
  selectedAnalysis: string;
}

const Sidebar = ({ onAnalysisSelect, selectedAnalysis }: SidebarProps) => {
  const analysisTypes = [
    { id: 'sentiment', label: 'Sentiment Analysis', icon: BarChart3 },
    { id: 'ner', label: 'Named Entity Recognition', icon: Tag },
    { id: 'langextract', label: 'Language Extract', icon: Languages },
  ];

  // -----------------------------
  // Model Settings state (NEW)
  // -----------------------------
  const NER_API = process.env.NEXT_PUBLIC_NER_API || "http://localhost:8002";
  const SENT_API = process.env.NEXT_PUBLIC_SENT_API || "http://localhost:8001";

  const [settingsOpen, setSettingsOpen] = useState(false);

  // NER
  const [nerAvailable, setNerAvailable] = useState<string[]>([]);
  const [nerActive, setNerActive] = useState<string | null>(null);
  const [nerUploadFile, setNerUploadFile] = useState<File | null>(null);
  const [nerUploading, setNerUploading] = useState(false);
  const [nerError, setNerError] = useState<string>("");

  // Sentiment
  const [sentAvailable, setSentAvailable] = useState<string[]>([]);
  const [sentActive, setSentActive] = useState<string | null>(null);
  const [sentUploadFile, setSentUploadFile] = useState<File | null>(null);
  const [sentUploading, setSentUploading] = useState(false);
  const [sentError, setSentError] = useState<string>("");
  const [sentHfRepo, setSentHfRepo] = useState<string>("");

  // HF repo for NER too (optional)
  const [nerHfRepo, setNerHfRepo] = useState<string>("");

  // Built-ins (always show in dropdowns)
  const NER_BUILTINS = ["dslim/bert-base-NER", "dbmdz/bert-large-cased-finetuned-conll03-english"];
  const SENT_BUILTINS = ["ProsusAI/finbert", "yiyanghkust/finbert-tone"];

  const authHeaders = () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const refreshNerModels = async () => {
    try {
      setNerError("");
      const res = await fetch(`${NER_API}/models`, { headers: { ...authHeaders() } });
      if (!res.ok) throw new Error(`NER GET /models -> ${res.status}`);
      const data = await res.json();
      const info = data?.ner || {};
      const available = Array.from(new Set([...(info.available || []), ...NER_BUILTINS])).sort();
      setNerAvailable(available);
      setNerActive(info.active || null);
    } catch (e: any) {
      setNerError("NER service not reachable.");
    }
  };

  const refreshSentModels = async () => {
    try {
      setSentError("");
      const res = await fetch(`${SENT_API}/models`, { headers: { ...authHeaders() } });
      if (!res.ok) throw new Error(`SENT GET /models -> ${res.status}`);
      const data = await res.json();
      // sentiment service returns { bert: { available, active, torch_available }, spacy: {...} }
      const info = data?.bert || {};
      const available = Array.from(new Set([...(info.available || []), ...SENT_BUILTINS])).sort();
      setSentAvailable(available);
      setSentActive(info.active || null);
    } catch (e: any) {
      setSentError("Sentiment service not reachable.");
    }
  };

  useEffect(() => {
    refreshNerModels();
    refreshSentModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activateNer = async (name: string) => {
    try {
      const res = await fetch(`${NER_API}/models/activate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ name }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || "NER activation failed");
      }
      await refreshNerModels();
    } catch (e: any) {
      alert(`NER activation error: ${e.message || e}`);
    }
  };

  const activateSent = async (name: string) => {
    try {
      const res = await fetch(`${SENT_API}/models/activate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ name }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || "Sentiment activation failed");
      }
      await refreshSentModels();
    } catch (e: any) {
      alert(`Sentiment activation error: ${e.message || e}`);
    }
  };

  const uploadNerZip = async () => {
    if (!nerUploadFile) return;
    setNerUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", nerUploadFile);
      // Some NER services may not expose an upload endpoint; catch the error gracefully.
      const res = await fetch(`${NER_API}/models/upload`, {
        method: "POST",
        headers: { ...authHeaders() },
        body: fd,
      });
      if (!res.ok) throw new Error(`NER upload not available (${res.status})`);
      const data = await res.json();
      await refreshNerModels();
      if (data?.name) await activateNer(data.name);
      setNerUploadFile(null);
    } catch (e: any) {
      alert(`NER upload failed or endpoint unavailable: ${e.message || e}`);
    } finally {
      setNerUploading(false);
    }
  };

  const uploadSentZip = async () => {
    if (!sentUploadFile) return;
    setSentUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", sentUploadFile);
      // Matches the backend we used earlier
      const res = await fetch(`${SENT_API}/models/bert/upload`, {
        method: "POST",
        headers: { ...authHeaders() },
        body: fd,
      });
      if (!res.ok) throw new Error(`Sentiment upload not available (${res.status})`);
      const data = await res.json();
      await refreshSentModels();
      if (data?.name) await activateSent(data.name);
      setSentUploadFile(null);
    } catch (e: any) {
      alert(`Sentiment upload failed or endpoint unavailable: ${e.message || e}`);
    } finally {
      setSentUploading(false);
    }
  };

  const addNerFromHf = async () => {
    const repo = (nerHfRepo || "").trim();
    if (!repo) return;
    try {
      const res = await fetch(`${NER_API}/models/from_hf`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ repo }),
      });
      if (!res.ok) throw new Error(`NER HF add failed (${res.status})`);
      const data = await res.json();
      await refreshNerModels();
      if (data?.name) await activateNer(data.name);
      setNerHfRepo("");
    } catch (e: any) {
      alert(`NER HF add failed: ${e.message || e}`);
    }
  };

  const addSentFromHf = async () => {
    const repo = (sentHfRepo || "").trim();
    if (!repo) return;
    try {
      const res = await fetch(`${SENT_API}/models/from_hf`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({ repo }),
      });
      if (!res.ok) throw new Error(`Sentiment HF add failed (${res.status})`);
      const data = await res.json();
      await refreshSentModels();
      if (data?.name) await activateSent(data.name);
      setSentHfRepo("");
    } catch (e: any) {
      alert(`Sentiment HF add failed: ${e.message || e}`);
    }
  };

  return (
    <aside className="w-64 bg-[hsl(var(--sidebar))] p-3 flex flex-col gap-1 border-r border-border">
      {analysisTypes.map((type) => {
        const Icon = type.icon;
        const isActive = selectedAnalysis === type.id;

        return (
          <Button
            key={type.id}
            variant="ghost"
            className={cn(
              "justify-start text-sm h-10 gap-3 transition-all duration-200 border-l-4 border-transparent",
              isActive && "bg-accent font-semibold border-l-primary shadow-sm",
              !isActive && "text-sidebar-foreground hover:bg-accent/50 hover:border-l-accent"
            )}
            onClick={() => onAnalysisSelect(type.id)}
          >
            <Icon className={cn("h-4 w-4", isActive && "text-primary")} />
            {type.label}
          </Button>
        );
      })}

      {/* Spacer pushes settings to end */}
      <div className="flex-1" />

      {/* Model Settings (NEW) */}
      <div className="mt-2 border-t border-border pt-2">
        <button
          type="button"
          onClick={() => setSettingsOpen((v) => !v)}
          className="w-full flex items-center justify-between text-sm font-semibold px-2 py-2 rounded hover:bg-accent/50 transition"
        >
          <span>Model Settings</span>
          <span className={cn("transition-transform", settingsOpen ? "rotate-180" : "rotate-0")}>▾</span>
        </button>

        {settingsOpen && (
          <div className="mt-2 space-y-4 px-1">
            {/* NER model */}
            <div className="space-y-2">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">NER model</div>
              {nerError && <div className="text-xs text-red-500">{nerError}</div>}
              <select
                className="w-full h-9 rounded border border-border bg-background px-2 text-sm"
                value={nerActive || ""}
                onChange={(e) => activateNer(e.target.value || "")}
              >
                <option value="">Server default</option>
                {Array.from(new Set([...(nerAvailable || []), ...NER_BUILTINS])).sort().map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
              <div className="text-xs text-muted-foreground">
                {nerActive ? `Active: ${nerActive}` : "Using server default"}
              </div>

              {/* Upload zip (stacked, always visible) */}
              <div className="space-y-2">
                <input
                  type="file"
                  accept=".zip,.tar,.tar.gz"
                  onChange={(e) => setNerUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-sm"
                />
                <Button
                  variant="secondary"
                  className="w-full h-9"
                  disabled={nerUploading || !nerUploadFile}
                  onClick={uploadNerZip}
                >
                  {nerUploading ? "Uploading..." : "Upload zip"}
                </Button>
              </div>

              {/* Add from HF */}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Hugging Face repo (e.g., dbmdz/bert-large...)"
                  value={nerHfRepo}
                  onChange={(e) => setNerHfRepo(e.target.value)}
                  className="flex-1 h-9 rounded border border-border bg-background px-2 text-sm"
                />
                <Button
                  variant="secondary"
                  className="h-9"
                  disabled={!nerHfRepo.trim()}
                  onClick={addNerFromHf}
                >
                  Add from HF
                </Button>
              </div>
            </div>

            {/* Sentiment model */}
            <div className="space-y-2">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Sentiment model</div>
              {sentError && <div className="text-xs text-red-500">{sentError}</div>}
              <select
                className="w-full h-9 rounded border border-border bg-background px-2 text-sm"
                value={sentActive || ""}
                onChange={(e) => activateSent(e.target.value || "")}
              >
                <option value="">Server default</option>
                {Array.from(new Set([...(sentAvailable || []), ...SENT_BUILTINS])).sort().map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
              <div className="text-xs text-muted-foreground">
                {sentActive ? `Active: ${sentActive}` : "Using server default"}
              </div>

              {/* Upload zip (stacked, always visible) */}
              <div className="space-y-2">
                <input
                  type="file"
                  accept=".zip,.tar,.tar.gz"
                  onChange={(e) => setSentUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-sm"
                />
                <Button
                  variant="secondary"
                  className="w-full h-9"
                  disabled={sentUploading || !sentUploadFile}
                  onClick={uploadSentZip}
                >
                  {sentUploading ? "Uploading..." : "Upload zip"}
                </Button>
              </div>

              {/* Add from HF */}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Hugging Face repo (e.g., ProsusAI/finbert)"
                  value={sentHfRepo}
                  onChange={(e) => setSentHfRepo(e.target.value)}
                  className="flex-1 h-9 rounded border border-border bg-background px-2 text-sm"
                />
                <Button
                  variant="secondary"
                  className="h-9"
                  disabled={!sentHfRepo.trim()}
                  onClick={addSentFromHf}
                >
                  Add from HF
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;