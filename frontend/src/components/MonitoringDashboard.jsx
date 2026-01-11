import React, { useEffect, useState } from "react";

const MonitoringDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/monitor/dashboard");
      const data = await res.json();
      if (res.ok) {
        setMetrics(data);
      } else {
        setError(data.error || "Failed to load metrics");
      }
    } catch (err) {
      setError("Network error");
    }
    setLoading(false);
  };

  return (
    <div className="bg-background p-6 rounded shadow mt-8">
      <h2 className="text-lg font-semibold text-primary mb-4">Continuous Monitoring & Feedback</h2>
      {loading && <div>Loading...</div>}
      {error && <div className="text-destructive mb-2">{error}</div>}
      {metrics && (
        <div>
          <ul className="list-disc ml-6 mb-4">
            <li>Bench Burn Cost: <span className="font-mono">${metrics.bench_burn_cost}</span></li>
            <li>Avg. Time to Allocation: <span className="font-mono">{metrics.avg_time_to_allocation} days</span></li>
            <li>Utilization Rate: <span className="font-mono">{(metrics.utilization_rate * 100).toFixed(1)}%</span></li>
            <li>Training ROI: <span className="font-mono">{metrics.training_roi}</span></li>
            <li>Attrition Rate: <span className="font-mono">{(metrics.attrition_rate * 100).toFixed(1)}%</span></li>
          </ul>
          <div className="mb-2 font-semibold">Feedback Summary:</div>
          <ul className="list-disc ml-6">
            <li>Positive: {metrics.feedback_summary.positive}</li>
            <li>Neutral: {metrics.feedback_summary.neutral}</li>
            <li>Negative: {metrics.feedback_summary.negative}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default MonitoringDashboard;
