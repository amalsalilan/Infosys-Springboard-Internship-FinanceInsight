import React, { useState, useRef, useEffect } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { useNavigate } from "react-router-dom";
import "./FinanceNERTool.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// Use worker from pdfjs-dist (recommended)
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.js",
  import.meta.url
).toString();

// Clean SVG logo
const FinanceLogo = ({ className = "", size = 32 }) => (
  <svg className={className} width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="Finance Insight logo">
    <defs>
      <linearGradient id="fiGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#2563eb" />
        <stop offset="100%" stopColor="#60a5fa" />
      </linearGradient>
    </defs>
    <rect x="2" y="2" width="60" height="60" rx="14" fill="url(#fiGrad)" />
    <path d="M12 42 L26 32 L36 38 L50 22" stroke="#ffffff" strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="12" cy="42" r="3" fill="#ffffff" />
    <circle cx="26" cy="32" r="3" fill="#ffffff" />
    <circle cx="36" cy="38" r="3" fill="#ffffff" />
    <circle cx="50" cy="22" r="3" fill="#ffffff" />
  </svg>
);

const FinanceNERTool = () => {
  const [customEntity, setCustomEntity] = useState("");
  const [entityList, setEntityList] = useState([
    "ORG", "LOC", "PERSON", "STOCK_PRICE", "REVENUE", "EARNINGS",
    "FINANCIAL_RATIO", "FINANCIAL_DATE", "MARKET_EVENT",
  ]);
  const [selectedEntities, setSelectedEntities] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [file, setFile] = useState(null);
  const [fileURL, setFileURL] = useState(null);
  const [fileMessage, setFileMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [examples, setExamples] = useState("");
  const [loading, setLoading] = useState(false);

  // LangExtract visualization
  const [vizHtml, setVizHtml] = useState(null);
  const [vizUrl, setVizUrl] = useState(null);
  const [jsonlPath, setJsonlPath] = useState(null);

  // spaCy: displaCy visualization
  const [spacyHtml, setSpacyHtml] = useState(null);
  const [spacyUrl, setSpacyUrl] = useState(null);

  // Predictive panel (BERT/FinBERT)
  const [showPredictive, setShowPredictive] = useState(true);

  // Sentiment dashboard state
  const [sentimentOn, setSentimentOn] = useState({ positive: true, negative: true, neutral: true });
  const [minConfPN, setMinConfPN] = useState(0.5);   // pos/neg threshold
  const [minConfNeu, setMinConfNeu] = useState(0.58); // neutral threshold

  // Advanced dashboard
  const [advOpen, setAdvOpen] = useState(true);
  const [showHighlights, setShowHighlights] = useState(true);
  const [highlightAlpha, setHighlightAlpha] = useState(1); // 0.1..1
  const [pdfZoom, setPdfZoom] = useState(1);               // 0.75..1.75
  const [gotoPage, setGotoPage] = useState(1);

  const navigate = useNavigate();
  const viewerRef = useRef(null);

  const getCurrentUser = () => {
    const token = localStorage.getItem("token");
    if (!token) return null;
    try {
      const tokenData = JSON.parse(atob(token.split(".")[1]));
      return tokenData.sub;
    } catch {
      return null;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const currentUser = getCurrentUser();

  // Color palette
  const colors = {
    PERSON: "#a3e635", ORG: "#60a5fa", LOC: "#fca5a5", STOCK_PRICE: "#facc15",
    REVENUE: "#34d399", EARNINGS: "#fb923c", FINANCIAL_RATIO: "#c084fc",
    FINANCIAL_DATE: "#38bdf8", MARKET_EVENT: "#f472b6", MISC: "#eab308",
    PERFORMANCE_METRIC: "#9b59b6",
    POSITIVE: "#22c55e", NEGATIVE: "#ef4444", NEUTRAL: "#3b82f6", MIXED: "#f59e0b",
    DEFAULT: "rgba(255, 255, 0, 0.4)",
  };

  const sentimentPriority = { NEUTRAL: 1, POSITIVE: 2, NEGATIVE: 3, MIXED: 2 };
  const labelOpacity = (lbl) => {
    const L = getCleanLabel(lbl);
    if (L === "NEUTRAL") return 0.28;
    if (L === "POSITIVE") return 0.30;
    if (L === "NEGATIVE") return 0.33;
    return 0.26;
  };

  const handleEntityChange = (entity) => {
    setSelectedEntities((prev) =>
      prev.includes(entity) ? prev.filter((e) => e !== entity) : [...prev, entity]
    );
  };

  const handleAddEntity = () => {
    if (customEntity && !entityList.includes(customEntity)) {
      setEntityList([...entityList, customEntity.toUpperCase().replace(/\s/g, "_")]);
      setCustomEntity("");
    }
  };

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files?.[0];
    if (fileURL) URL.revokeObjectURL(fileURL);
    if (!uploadedFile) {
      setFile(null); setFileURL(null); setFileMessage(""); setResponse(null); setNumPages(null);
      setVizHtml(null); setVizUrl(null); setJsonlPath(null);
      setSpacyHtml(null); setSpacyUrl(null);
      return;
    }
    setFile(uploadedFile);
    const url = URL.createObjectURL(uploadedFile);
    setFileURL(url);
    setFileMessage(`File uploaded: ${uploadedFile.name}`);
    setResponse(null);
    setNumPages(null);
    setVizHtml(null); setVizUrl(null); setJsonlPath(null);
    setSpacyHtml(null); setSpacyUrl(null);
  };

  const handleSubmit = async () => {
    if (!file) { alert("Please upload a file first!"); return; }
    if (!selectedModel) { alert("Please select a model!"); return; }

    const modelMap = { LangExtract: "langextract", "spaCy Model": "spacy", "BERT/FinBERT": "bert" };
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_choice", modelMap[selectedModel] || "bert");

    if (selectedModel === "spaCy Model") {
      formData.append("entity_types", selectedEntities.length ? JSON.stringify(selectedEntities) : "all");
    } else {
      formData.append("entity_types", "all");
    }

    if (selectedModel === "LangExtract") {
      formData.append("prompt", prompt || "");
      formData.append("examples", examples || "");
    }

    setLoading(true);
    setResponse(null);
    setVizHtml(null); setVizUrl(null); setJsonlPath(null);
    setSpacyHtml(null); setSpacyUrl(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) { alert("Please log in to use this feature."); navigate("/login"); return; }

      const res = await fetch("http://localhost:8000/process/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        if (res.status === 401) { alert("Session expired. Please log in again."); localStorage.removeItem("token"); navigate("/login"); return; }
        const text = await res.text();
        console.error("Error:", res.status, text);
        alert(`Server error (${res.status}). Check logs.`);
        return;
      }

      const data = await res.json();
      setResponse(data);

      if (selectedModel === "LangExtract") {
        if (data.visualization_html) setVizHtml(data.visualization_html);
        else if (data.visualization_html_base64) { try { setVizHtml(atob(data.visualization_html_base64)); } catch {} }
        if (data.visualization_url) setVizUrl(data.visualization_url);
        if (data.jsonl_path) setJsonlPath(data.jsonl_path);
      }
      if (selectedModel === "spaCy Model") {
        if (data.spacy_visualization_html) setSpacyHtml(data.spacy_visualization_html);
        if (data.spacy_visualization_url) setSpacyUrl(data.spacy_visualization_url);
      }
    } catch (err) {
      console.error("Upload error:", err);
      alert("Error connecting to backend.");
    } finally {
      setLoading(false);
    }
  };

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setGotoPage(1);
  };

  // Normalize labels + sentiment variants
  const getCleanLabel = (label) => {
    if (!label) return "MISC";
    let v = String(label);
    if (v.startsWith("B-") || v.startsWith("I-")) v = v.substring(2);
    const upper = v.toUpperCase().trim();
    const map = {
      POS: "POSITIVE", POSITIVE: "POSITIVE",
      NEG: "NEGATIVE", NEGATIVE: "NEGATIVE",
      NEU: "NEUTRAL", NEUTRAL: "NEUTRAL",
      LABEL_0: "NEGATIVE", LABEL_1: "NEUTRAL", LABEL_2: "POSITIVE",
      SENT_POS: "POSITIVE", SENT_NEG: "NEGATIVE", SENT_NEU: "NEUTRAL",
    };
    return map[upper] || upper;
  };

  // Snap to a grid so rectangles look tidier
  const snap = (val, step = 0.5) => {
    const n = parseFloat(val);
    if (Number.isNaN(n)) return 0;
    return Math.max(0, Math.min(100, Math.round(n / step) * step));
  };

  // Smooth scroll inside viewer
  const scrollToPage = (page) => {
    const p = Math.max(1, Math.min(page || 1, numPages || 1));
    const node = viewerRef.current?.querySelector(`#page_${p}`);
    if (node) node.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  // Filter highlights by dashboard settings and showHighlights
  const filterBySentiments = (arr) => {
    if (!showHighlights) return [];
    const allow = {
      POSITIVE: sentimentOn.positive,
      NEGATIVE: sentimentOn.negative,
      NEUTRAL: sentimentOn.neutral,
    };
    return (arr || []).filter((h) => {
      const L = getCleanLabel(h.label);
      if (!allow[L]) return false;
      const s = typeof h.score === "number" ? h.score : 1;
      if (L === "NEUTRAL") return s >= minConfNeu;
      if (L === "POSITIVE" || L === "NEGATIVE") return s >= minConfPN;
      return true;
    });
  };

  const PageWithHighlights = ({ pageNumber, highlights }) => {
    const pageHighlights = filterBySentiments(highlights)
      .filter((h) => h.page === pageNumber)
      .map((h) => ({
        ...h,
        _label: getCleanLabel(h.label),
        _priority: sentimentPriority[getCleanLabel(h.label)] || 0,
      }))
      .sort((a, b) => (a._priority || 0) - (b._priority || 0));

    const baseWidth = Math.round(820 * pdfZoom);

    return (
      <div id={`page_${pageNumber}`} className="pdf-page-container">
        <Page pageNumber={pageNumber} width={baseWidth} renderTextLayer renderAnnotationLayer />
        {pageHighlights.map((h, i) => {
          const displayLabel = h._label;
          const bg = colors[displayLabel] || colors.DEFAULT;

          const safeTop = snap(h.top);
          const safeLeft = snap(h.left);
          const safeWidth = snap(h.width);
          const safeHeight = snap(h.height);
          const wAdj = Math.max(0, Math.min(100 - safeLeft, safeWidth + 0.4));

          return (
            <span
              key={i}
              className="highlight-overlay"
              style={{
                top: `${safeTop}%`,
                left: `${safeLeft}%`,
                width: `${wAdj}%`,
                height: `${safeHeight}%`,
                backgroundColor: bg,
                opacity: Math.max(0.05, Math.min(1, labelOpacity(displayLabel) * highlightAlpha)),
                border: `1px solid ${bg}`,
                zIndex: 5 + (h._priority || 0),
              }}
              title={`${displayLabel}${h.score ? ` (${(h.score * 100).toFixed(1)}%)` : ""}${h.word ? `: ${h.word}` : ""}`}
            />
          );
        })}
      </div>
    );
  };

  const getHighlights = () => {
    if (!response) return [];
    if (response.pdf_highlights?.length) return response.pdf_highlights;
    if (response.sentiment_highlights?.length) return response.sentiment_highlights;
    return [];
  };

  const renderPDFViewer = () => {
    if (!file && !fileURL) return null;
    const highlights = getHighlights();
    return (
      <div className="pdf-viewer card" ref={viewerRef}>
        <Document
          file={file || fileURL}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={(err) => console.error("PDF onLoadError:", err)}
          onSourceError={(err) => console.error("PDF onSourceError:", err)}
          loading="Loading PDF..."
          error="Failed to load PDF file."
        >
          {Array.from(new Array(numPages || 0), (el, index) => (
            <PageWithHighlights key={`page_${index + 1}`} pageNumber={index + 1} highlights={highlights} />
          ))}
        </Document>
      </div>
    );
  };

  // LangExtract visualization (unchanged)
  const renderLangExtractVisualization = () => {
    const showViz = selectedModel === "LangExtract" && (vizHtml || vizUrl);
    if (!showViz) return null;
    return (
      <div className="card">
        <h3 className="card-title">Interactive Visualization</h3>
        {vizUrl ? (
          <iframe className="viz-frame" src={vizUrl} title="LangExtract Visualization" />
        ) : (
          <iframe className="viz-frame" srcDoc={vizHtml} title="LangExtract Visualization" />
        )}
        <div className="actions-row">
          {vizHtml && (
            <>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const blob = new Blob([vizHtml], { type: "text/html" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "visualization.html";
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                ⬇️ Download HTML
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const blob = new Blob([vizHtml], { type: "text/html" });
                  const url = URL.createObjectURL(blob);
                  window.open(url, "_blank", "noopener,noreferrer");
                }}
              >
                🧭 Open in new tab
              </button>
            </>
          )}
          {vizUrl && (
            <a className="btn" href={vizUrl} target="_blank" rel="noreferrer">
              🧭 Open visualization
            </a>
          )}
          {jsonlPath && <span className="muted">JSONL: {jsonlPath}</span>}
        </div>
      </div>
    );
  };

  // spaCy visualization (unchanged)
  const renderSpacyVisualization = () => {
    const show = selectedModel === "spaCy Model" && (spacyHtml || spacyUrl);
    if (!show) return null;
    return (
      <div className="card">
        <h3 className="card-title">spaCy Entities Visualization</h3>
        {spacyUrl ? (
          <iframe className="viz-frame" src={spacyUrl} title="spaCy displaCy" />
        ) : (
          <iframe className="viz-frame" srcDoc={spacyHtml} title="spaCy displaCy" />
        )}
        {spacyHtml && (
          <div className="actions-row">
            <button
              type="button"
              className="btn"
              onClick={() => {
                const blob = new Blob([spacyHtml], { type: "text/html" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "spacy_visualization.html";
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              ⬇️ Download HTML
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => {
                const blob = new Blob([spacyHtml], { type: "text/html" });
                const url = URL.createObjectURL(blob);
                window.open(url, "_blank", "noopener,noreferrer");
              }}
            >
              🧭 Open in new tab
            </button>
          </div>
        )}
      </div>
    );
  };

  // Sentiment legend + Predictive Analysis (model-driven only)
  const renderSentimentInsights = () => {
    if (selectedModel !== "BERT/FinBERT") return null;

    const summary = response?.sentiment_summary || {};
    const counts = response?.sentiment_counts || summary.counts || {};
    const overall = response?.overall_sentiment
      ? getCleanLabel(response.overall_sentiment)
      : (summary.overall_label ? getCleanLabel(summary.overall_label) : null);
    const avgConf = typeof summary.average_confidence === "number" ? summary.average_confidence : null;
    const predictive = (response?.predictive_analysis && String(response.predictive_analysis).trim())
      ? response.predictive_analysis
      : "Predictive analysis not available from the model.";

    return (
      <div className="card">
        <div className="legend-row">
          <span className="legend-title">Sentiment Legend:</span>
          <span className="legend-dot" style={{ background: colors.POSITIVE }} /> Positive
          <span className="legend-dot" style={{ background: colors.NEGATIVE }} /> Negative
          <span className="legend-dot" style={{ background: colors.NEUTRAL }} /> Neutral
          <span className="spacer" />
          {(typeof counts.positive === "number" ||
            typeof counts.negative === "number" ||
            typeof counts.neutral === "number" ||
            overall ||
            typeof avgConf === "number") && (
            <span className="legend-stats">
              {typeof counts.positive === "number" && <span style={{ color: colors.POSITIVE }}>+{counts.positive}</span>}
              {typeof counts.negative === "number" && <span style={{ color: colors.NEGATIVE }}>-{counts.negative}</span>}
              {typeof counts.neutral === "number" && <span style={{ color: colors.NEUTRAL }}>{counts.neutral} neutral</span>}
              {overall && (
                <span style={{ fontWeight: 600 }}>
                  Overall: <span style={{ color: colors[overall] || "#111827" }}>{overall}</span>
                </span>
              )}
              {typeof avgConf === "number" && <span className="muted">Avg conf: {avgConf.toFixed(2)}</span>}
            </span>
          )}
        </div>

        <div className="card">
          <div className="predictive-header">
            <span className="card-title">Predictive Analysis</span>
            <button type="button" className="btn primary" onClick={() => setShowPredictive((v) => !v)}>
              {showPredictive ? "Hide" : "Show"}
            </button>
          </div>
          {showPredictive && <div className="predictive-body">{predictive}</div>}
        </div>
      </div>
    );
  };

  // =========================
  // Model Settings (NEW)
  // =========================
  const API_BASE = "http://localhost:8000";

  const [modelSettingsOpen, setModelSettingsOpen] = useState(false);
  const [modelsMeta, setModelsMeta] = useState({
    spacy: { available: [], active: null },
    bert: { available: [], active: null },
  });
  const [spacyUploadFile, setSpacyUploadFile] = useState(null);
  const [bertUploadFile, setBertUploadFile] = useState(null);
  const [bertHfRepo, setBertHfRepo] = useState("");
  const [uploadingSpacy, setUploadingSpacy] = useState(false);
  const [uploadingBert, setUploadingBert] = useState(false);
  const [modelsError, setModelsError] = useState("");

  // Always show these options in dropdowns
  const SPACY_BUILTINS = ["en_core_web_sm", "en_core_web_lg"];
  const BERT_BUILTINS = ["ProsusAI/finbert", "yiyanghkust/finbert-tone"];

  const refreshModels = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      setModelsError("");
      const res = await fetch(`${API_BASE}/models`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`GET /models -> ${res.status}`);
      const data = await res.json();
      setModelsMeta({
        spacy: {
          available: data?.spacy?.available || [],
          active: data?.spacy?.active || null,
        },
        bert: {
          available: data?.bert?.available || [],
          active: data?.bert?.active || null,
        },
      });
    } catch (err) {
      console.error("Failed to fetch models:", err);
      setModelsError("Model catalog not reachable. You can still upload.");
    }
  };

  useEffect(() => {
    refreshModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activateModel = async (type, name) => {
    const token = localStorage.getItem("token");
    if (!token) { alert("Please log in."); navigate("/login"); return; }
    try {
      const res = await fetch(`${API_BASE}/models/activate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ type, name: name || null }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(`Activate failed: ${res.status} ${t}`);
      }
      await refreshModels();
    } catch (err) {
      console.error(err);
      alert("Failed to set active model. Check server.");
    }
  };

  const uploadSpacyModel = async () => {
    if (!spacyUploadFile) return;
    const token = localStorage.getItem("token");
    if (!token) { alert("Please log in."); navigate("/login"); return; }
    setUploadingSpacy(true);
    try {
      const fd = new FormData();
      fd.append("file", spacyUploadFile);
      const res = await fetch(`${API_BASE}/models/spacy/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(`spaCy upload failed: ${res.status} ${t}`);
      }
      const data = await res.json(); // expect { name: "your_spacy_model_name" }
      await refreshModels();
      if (data?.name) await activateModel("spacy", data.name);
      setSpacyUploadFile(null);
    } catch (err) {
      console.error(err);
      alert("spaCy model upload failed.");
    } finally {
      setUploadingSpacy(false);
    }
  };

  const uploadBertZip = async () => {
    if (!bertUploadFile) return;
    const token = localStorage.getItem("token");
    if (!token) { alert("Please log in."); navigate("/login"); return; }
    setUploadingBert(true);
    try {
      const fd = new FormData();
      fd.append("file", bertUploadFile);
      const res = await fetch(`${API_BASE}/models/bert/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(`BERT upload failed: ${res.status} ${t}`);
      }
      const data = await res.json(); // expect { name: "your_bert_model_name" }
      await refreshModels();
      if (data?.name) await activateModel("bert", data.name);
      setBertUploadFile(null);
    } catch (err) {
      console.error(err);
      alert("BERT/FinBERT model upload failed.");
    } finally {
      setUploadingBert(false);
    }
  };

  const addBertFromHf = async () => {
    const repo = (bertHfRepo || "").trim();
    if (!repo) return;
    const token = localStorage.getItem("token");
    if (!token) { alert("Please log in."); navigate("/login"); return; }
    setUploadingBert(true);
    try {
      const res = await fetch(`${API_BASE}/models/bert/from_hf`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ repo }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(`HF repo add failed: ${res.status} ${t}`);
      }
      const data = await res.json(); // expect { name: "registered_repo_name" }
      await refreshModels();
      if (data?.name) await activateModel("bert", data.name);
      setBertHfRepo("");
    } catch (err) {
      console.error(err);
      alert("Adding BERT/FinBERT from Hugging Face failed.");
    } finally {
      setUploadingBert(false);
    }
  };

  // Merge server-provided lists with built-ins
  const spacyOptions = Array.from(new Set([...(modelsMeta.spacy.available || []), ...SPACY_BUILTINS]))
.filter((n) => n !== "en_core_web_trf")
.sort();
  const bertOptions  = Array.from(new Set([...(modelsMeta.bert.available || []),  ...BERT_BUILTINS])).sort();

  return (
    <div className="app-shell">
      {/* Top bar */}
      <header className="topbar">
        <div className="brand">
          <FinanceLogo className="app-logo" />
          <h1 className="app-title">Finance Insight NER Tool</h1>
        </div>
        <div className="user-area">
          <span className="muted">Welcome, {currentUser}!</span>
          <div className="user-icon">👤</div>
          <button className="btn danger" onClick={handleLogout}>🚪 Sign out</button>
        </div>
      </header>

      <div className="layout">
        {/* Left: Dashboard with Advanced at bottom */}
        <aside className="sidebar-left">
          <div className="card sticky">
            <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14 }}>
              <h3 className="card-title">Dashboard</h3>

              <div className="subtle">Sentiments</div>
              <div className="sentiment-toggles">
                <label className="toggle">
                  <input type="checkbox" checked={sentimentOn.positive}
                    onChange={(e) => setSentimentOn((s) => ({ ...s, positive: e.target.checked }))} />
                  <span className="toggle-dot" style={{ background: colors.POSITIVE }} />
                  Positive
                </label>
                <label className="toggle">
                  <input type="checkbox" checked={sentimentOn.negative}
                    onChange={(e) => setSentimentOn((s) => ({ ...s, negative: e.target.checked }))} />
                  <span className="toggle-dot" style={{ background: colors.NEGATIVE }} />
                  Negative
                </label>
                <label className="toggle">
                  <input type="checkbox" checked={sentimentOn.neutral}
                    onChange={(e) => setSentimentOn((s) => ({ ...s, neutral: e.target.checked }))} />
                  <span className="toggle-dot" style={{ background: colors.NEUTRAL }} />
                  Neutral
                </label>
              </div>

              <div className="subtle" style={{ marginTop: 12 }}>Confidence thresholds</div>
              <div className="slider-row">
                <label>Pos/Neg ({minConfPN.toFixed(2)})</label>
                <input type="range" min={0} max={1} step={0.01}
                  value={minConfPN} onChange={(e) => setMinConfPN(parseFloat(e.target.value))} />
              </div>
              <div className="slider-row">
                <label>Neutral ({minConfNeu.toFixed(2)})</label>
                <input type="range" min={0} max={1} step={0.01}
                  value={minConfNeu} onChange={(e) => setMinConfNeu(parseFloat(e.target.value))} />
              </div>

              <div className="actions-row">
                <button className="btn" type="button" onClick={() => {
                  setSentimentOn({ positive: true, negative: true, neutral: true });
                  setMinConfPN(0.5); setMinConfNeu(0.58);
                  setShowHighlights(true); setHighlightAlpha(1); setPdfZoom(1);
                  setGotoPage(1); if (numPages) scrollToPage(1);
                }}>
                  Reset
                </button>
              </div>

              <div className="legend-inline">
                <span className="legend-dot" style={{ background: colors.POSITIVE }} /> Positive
                <span className="legend-dot" style={{ background: colors.NEGATIVE }} /> Negative
                <span className="legend-dot" style={{ background: colors.NEUTRAL }} /> Neutral
              </div>

              {/* Spacer to push Advanced to the bottom */}
              <div style={{ flex: 1 }} />

              {/* Advanced group */}
              <div style={{ borderTop: "1px dashed #e5e7eb", paddingTop: 12 }}>
                <div
                  style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}
                  onClick={() => setAdvOpen((v) => !v)}
                >
                  <span className="card-title">Advanced</span>
                  <span style={{ transform: advOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform .2s" }}>▾</span>
                </div>
                {advOpen && (
                  <div style={{ display: "grid", gap: 10, marginTop: 8 }}>
                    <label className="toggle">
                      <input type="checkbox" checked={showHighlights} onChange={(e) => setShowHighlights(e.target.checked)} />
                      <span className="toggle-dot" style={{ background: "#2563eb" }} />
                      Show highlights
                    </label>

                    <div className="slider-row">
                      <label>Highlight opacity ({highlightAlpha.toFixed(2)})</label>
                      <input type="range" min={0.1} max={1} step={0.01}
                        value={highlightAlpha} onChange={(e) => setHighlightAlpha(parseFloat(e.target.value))} />
                    </div>

                    <div className="slider-row">
                      <label>PDF zoom ({Math.round(pdfZoom * 100)}%)</label>
                      <input type="range" min={0.75} max={1.75} step={0.01}
                        value={pdfZoom} onChange={(e) => setPdfZoom(parseFloat(e.target.value))} />
                    </div>

                    <div className="slider-row">
                      <label>Page</label>
                      <input
                        type="range"
                        min={1}
                        max={numPages || 1}
                        step={1}
                        value={Math.min(gotoPage, numPages || 1)}
                        onChange={(e) => {
                          const p = parseInt(e.target.value, 10);
                          setGotoPage(p);
                          scrollToPage(p);
                        }}
                        disabled={!numPages}
                      />
                    </div>

                    <div className="actions-row">
                      <button className="btn" type="button"
                        onClick={() => {
                          const p = Math.max(1, (gotoPage || 1) - 1);
                          setGotoPage(p); scrollToPage(p);
                        }}
                        disabled={!numPages || gotoPage <= 1}
                      >
                        ◀ Previous
                      </button>
                      <button className="btn" type="button"
                        onClick={() => {
                          const p = Math.min(numPages || 1, (gotoPage || 1) + 1);
                          setGotoPage(p); scrollToPage(p);
                        }}
                        disabled={!numPages || gotoPage >= (numPages || 1)}
                      >
                        Next ▶
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </aside>

        {/* Middle: dynamic controls + PDF viewer + visualizations */}
        <main className="content">
          <div className="card">
            <div className="flex-between">
              <h3 className="card-title">Processing</h3>
              <button className="btn primary" onClick={handleSubmit} disabled={loading}>
                {loading ? "Processing..." : "Submit"}
              </button>
            </div>

            {/* Model-specific controls */}
            {selectedModel === "LangExtract" && (
              <div className="model-panel">
                <div className="subtle">LangExtract Prompt</div>
                <textarea
                  className="text-input"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter extraction prompt (e.g., 'Extract company names and their latest revenues')..."
                  rows={4}
                />
                <div className="subtle" style={{ marginTop: 8 }}>Examples (JSON)</div>
                <textarea
                  className="text-input"
                  value={examples}
                  onChange={(e) => setExamples(e.target.value)}
                  placeholder='Examples (JSON or custom format your backend expects).'
                  rows={4}
                />
              </div>
            )}

            {selectedModel === "spaCy Model" && (
              <div className="model-panel">
                <div className="subtle">spaCy Entity Types</div>
                <div className="chip-grid">
                  {entityList.map((entity) => (
                    <label key={entity} className="chip">
                      <input
                        type="checkbox"
                        value={entity}
                        checked={selectedEntities.includes(entity)}
                        onChange={() => handleEntityChange(entity)}
                      />
                      <span>{entity}</span>
                    </label>
                  ))}
                </div>
                <div className="add-row">
                  <input
                    type="text"
                    className="text-input"
                    placeholder="Add custom entity..."
                    value={customEntity}
                    onChange={(e) => setCustomEntity(e.target.value)}
                  />
                  <button type="button" className="btn" onClick={handleAddEntity}>
                    Add
                  </button>
                </div>
              </div>
            )}

            {selectedModel === "BERT/FinBERT" && (
              <div className="model-panel hint">
                Using FinBERT for sentence-level sentiment. Highlights will appear on the PDF, and Predictive Analysis will be shown below.
              </div>
            )}

            <div className="subtle" style={{ marginTop: 10 }}>Upload Financial Document (PDF)</div>
            <input type="file" accept="application/pdf" onChange={handleFileUpload} />
            {fileMessage && <p className="muted" style={{ marginTop: 6 }}>{fileMessage}</p>}
          </div>

          {/* Output region */}
          <div className="card">
            <h3 className="card-title">{response ? "Processed Document" : "Uploaded Document Preview"}</h3>
            {loading && <div className="loading-spinner">Processing document...</div>}
            {renderPDFViewer()}
          </div>

          {renderLangExtractVisualization()}
          {renderSpacyVisualization()}
          {renderSentimentInsights()}
        </main>

        {/* Right: Model selection with bottom tip */}
        <aside className="sidebar-right">
          <div className="card sticky">
            <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14 }}>
              <h3 className="card-title">Model Selection</h3>
              <div className="radio-grid">
                {["LangExtract", "spaCy Model", "BERT/FinBERT"].map((m) => (
                  <label key={m} className={`radio-tile ${selectedModel === m ? "active" : ""}`}>
                    <input
                      type="radio"
                      name="model"
                      value={m}
                      checked={selectedModel === m}
                      onChange={() => setSelectedModel(m)}
                    />
                    <div className="radio-title">{m}</div>
                    <div className="radio-desc">
                      {m === "LangExtract" && "Promptable, few-shot extraction with interactive HTML viewer."}
                      {m === "spaCy Model" && "Rule + NER visualization (displaCy) with finance regex merge."}
                      {m === "BERT/FinBERT" && "Sentence-level sentiment overlays + predictive analysis."}
                    </div>
                  </label>
                ))}
              </div>

              {/* Spacer to push Model Settings and tip to the bottom */}
              <div style={{ flex: 1 }} />

              {/* Model Settings (NEW) */}
              <div className="card" style={{ marginTop: 8 }}>
                <div
                  className="flex-between"
                  style={{ cursor: "pointer" }}
                  onClick={() => setModelSettingsOpen((v) => !v)}
                >
                  <span className="card-title">Model Settings</span>
                  <span
                    style={{
                      transform: modelSettingsOpen ? "rotate(180deg)" : "rotate(0deg)",
                      transition: "transform .2s",
                    }}
                  >
                    ▾
                  </span>
                </div>

                {modelSettingsOpen && (
                  <div style={{ display: "grid", gap: 12 }}>
                    {modelsError && (
                      <div className="muted" style={{ color: "#ef4444" }}>
                        {modelsError}
                      </div>
                    )}

                    {/* spaCy model section */}
                    <div className="subtle">spaCy model</div>
                    <div className="select-row" style={{ display: "grid", gap: 8 }}>
                      <select
                        className="text-input"
                        value={modelsMeta.spacy.active || ""}
                        onChange={(e) => activateModel("spacy", e.target.value || null)}
                      >
                        <option value="">Server default</option>
                        {spacyOptions.map((name) => (
                          <option key={name} value={name}>{name}</option>
                        ))}
                      </select>
                      <span className="muted">
                        {modelsMeta.spacy.active ? `Active: ${modelsMeta.spacy.active}` : "Using server default"}
                      </span>
                    </div>

                    {/* Always-visible upload button (stacked) */}
                    <div style={{ display: "grid", gap: 8 }}>
                      <input
                        type="file"
                        accept=".tar,.gz,.tar.gz,.zip"
                        onChange={(e) => setSpacyUploadFile(e.target.files?.[0] || null)}
                        style={{ width: "100%" }}
                      />
                      <button
                        type="button"
                        className="btn"
                        onClick={uploadSpacyModel}
                        disabled={uploadingSpacy || !spacyUploadFile}
                        style={{ width: "100%" }}
                      >
                        {uploadingSpacy ? "Uploading..." : "Upload zip"}
                      </button>
                    </div>

                    {/* BERT/FinBERT model section */}
                    <div className="subtle" style={{ marginTop: 6 }}>BERT/FinBERT model</div>
                    <div className="select-row" style={{ display: "grid", gap: 8 }}>
                      <select
                        className="text-input"
                        value={modelsMeta.bert.active || ""}
                        onChange={(e) => activateModel("bert", e.target.value || null)}
                      >
                        <option value="">Server default</option>
                        {bertOptions.map((name) => (
                          <option key={name} value={name}>{name}</option>
                        ))}
                      </select>
                      <span className="muted">
                        {modelsMeta.bert.active ? `Active: ${modelsMeta.bert.active}` : "Using server default"}
                      </span>
                    </div>

                    {/* Always-visible upload button (stacked) */}
                    <div style={{ display: "grid", gap: 8 }}>
                      <input
                        type="file"
                        accept=".zip,.tar,.tar.gz"
                        onChange={(e) => setBertUploadFile(e.target.files?.[0] || null)}
                        style={{ width: "100%" }}
                      />
                      <button
                        type="button"
                        className="btn"
                        onClick={uploadBertZip}
                        disabled={uploadingBert || !bertUploadFile}
                        style={{ width: "100%" }}
                      >
                        {uploadingBert ? "Uploading..." : "Upload zip"}
                      </button>
                    </div>

                    <div className="add-row">
                      <input
                        type="text"
                        className="text-input"
                        placeholder="or Hugging Face repo (e.g., prosusai/finbert)"
                        value={bertHfRepo}
                        onChange={(e) => setBertHfRepo(e.target.value)}
                      />
                      <button
                        type="button"
                        className="btn"
                        onClick={addBertFromHf}
                        disabled={uploadingBert || !bertHfRepo.trim()}
                      >
                        {uploadingBert ? "Processing..." : "Add from HF"}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* tip pinned to bottom */}
              <div className="tip muted">
                Tip: Choose a model on the right, set options in the middle, then click Submit.
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default FinanceNERTool;