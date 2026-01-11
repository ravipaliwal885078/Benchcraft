import React, { useState } from "react";

const NoticePeriodRisk = () => {
  const [employee, setEmployee] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setEmployee(e.target.value);
  };

  const handleCheck = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);
    try {
      const res = await fetch("/api/v1/risk/notice-status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ employee }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus(data);
      } else {
        setError(data.error || "Check failed");
      }
    } catch (err) {
      setError("Network error");
    }
    setLoading(false);
  };

  return (
    <div className="bg-background p-6 rounded shadow mt-8">
      <h2 className="text-lg font-semibold text-primary mb-4">Notice Period & Risk Management</h2>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Employee Name"
          className="border px-2 py-1 rounded w-2/3"
          value={employee}
          onChange={handleChange}
        />
        <button
          className="px-4 py-2 bg-primary text-white rounded"
          onClick={handleCheck}
          disabled={loading}
        >
          {loading ? "Checking..." : "Check Status"}
        </button>
      </div>
      {error && <div className="text-destructive mb-2">{error}</div>}
      {status && (
        <div className="bg-muted p-4 rounded">
          <h3 className="font-bold mb-2">Notice Period Status</h3>
          <ul className="list-disc ml-6">
            <li>Employee: {status.employee}</li>
            <li>Notice Period: {status.notice_period ? "Yes" : "No"}</li>
            <li>Days Remaining: {status.days_remaining}</li>
            <li>Risk Level: <span className="font-bold text-red-600">{status.risk_level}</span></li>
            <li>Project Impact: {status.project_impact}</li>
            <li>KT Status: {status.kt_status}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default NoticePeriodRisk;
