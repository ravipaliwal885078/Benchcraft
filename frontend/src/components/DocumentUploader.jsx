import React, { useState } from "react";

const DocumentUploader = ({ onParsed }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setParsed(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/v1/documents/upload/resume", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setParsed(data.parsed);
        if (onParsed) onParsed(data.parsed);
      } else {
        setError(data.error || "Upload failed");
      }
    } catch (err) {
      setError("Network error");
    }
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button
        className="px-4 py-2 bg-primary text-white rounded"
        onClick={handleUpload}
        disabled={loading || !file}
      >
        {loading ? "Uploading..." : "Upload Resume"}
      </button>
      {error && <div className="text-destructive">{error}</div>}
      {parsed && (
        <div className="bg-muted p-4 rounded">
          <h3 className="font-bold mb-2">Parsed Data</h3>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(parsed, null, 2)}</pre>
          {parsed.skills_detected && (
            <div className="mt-4">
              <h4 className="font-semibold mb-1">Detected Skills</h4>
              <ul className="list-disc ml-6">
                {parsed.skills_detected.map((s, i) => (
                  <li key={i}>
                    <span className="font-mono text-primary">{s.skill}</span> &ndash; Confidence: {(s.confidence * 100).toFixed(0)}%, Proficiency: {s.proficiency}/5
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentUploader;
