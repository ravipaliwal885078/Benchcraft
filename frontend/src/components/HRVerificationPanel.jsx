import React, { useEffect, useState } from "react";

const HRVerificationPanel = () => {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchPending();
  }, []);

  const fetchPending = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/hr/pending");
      const data = await res.json();
      setPending(data);
    } catch (err) {
      setError("Failed to load pending profiles");
    }
    setLoading(false);
  };

  const handleVerify = async (id) => {
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`/api/v1/hr/verify/${id}`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setSuccess(`Profile for ${id} activated!`);
        setPending(pending.filter((p) => p.id !== id));
      } else {
        setError(data.error || "Verification failed");
      }
    } catch (err) {
      setError("Network error");
    }
  };

  return (
    <div className="bg-background p-6 rounded shadow mt-8">
      <h2 className="text-lg font-semibold text-primary mb-4">HR Verification Panel</h2>
      {loading && <div>Loading...</div>}
      {error && <div className="text-destructive mb-2">{error}</div>}
      {success && <div className="text-success mb-2">{success}</div>}
      {pending.length === 0 && !loading && <div>No pending profiles.</div>}
      <ul className="divide-y">
        {pending.map((emp) => (
          <li key={emp.id} className="py-2 flex items-center justify-between">
            <span>{emp.first_name} {emp.last_name} ({emp.email})</span>
            <button
              className="px-3 py-1 bg-success text-white rounded"
              onClick={() => handleVerify(emp.id)}
            >
              Activate
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HRVerificationPanel;
