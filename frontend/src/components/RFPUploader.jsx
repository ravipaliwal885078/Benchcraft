import React, { useState } from "react";

const RFPUploader = ({ onParsed }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [project, setProject] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setProject(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/v1/rfp/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setProject(data.project);
        if (onParsed) onParsed(data.project);
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
        {loading ? "Uploading..." : "Upload RFP"}
      </button>
      {error && <div className="text-destructive">{error}</div>}
      {project && (
        <div className="bg-muted p-4 rounded">
          <h3 className="font-bold mb-2">Extracted Project Data</h3>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(project, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default RFPUploader;
