import React, { useState } from "react";

const SkillGapAnalysis = () => {
  const [skills, setSkills] = useState("");
  const [loading, setLoading] = useState(false);
  const [gaps, setGaps] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setSkills(e.target.value);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setGaps([]);
    setRecommendations([]);
    try {
      const res = await fetch("/api/v1/training/gap-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skills }),
      });
      const data = await res.json();
      if (res.ok) {
        setGaps(data.gaps);
        setRecommendations(data.recommendations);
      } else {
        setError(data.error || "Analysis failed");
      }
    } catch (err) {
      setError("Network error");
    }
    setLoading(false);
  };

  return (
    <div className="bg-background p-6 rounded shadow mt-8">
      <h2 className="text-lg font-semibold text-primary mb-4">Skill Gap Analysis & Training</h2>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Current Skills (comma separated)"
          className="border px-2 py-1 rounded w-2/3"
          value={skills}
          onChange={handleChange}
        />
        <button
          className="px-4 py-2 bg-primary text-white rounded"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Gaps"}
        </button>
      </div>
      {error && <div className="text-destructive mb-2">{error}</div>}
      {gaps.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Skill Gaps</h3>
          <ul className="list-disc ml-6">
            {gaps.map((g, i) => (
              <li key={i}>
                {g.skill}: Required Level {g.required_level}, Current Level {g.current_level}
              </li>
            ))}
          </ul>
        </div>
      )}
      {recommendations.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Recommended Trainings</h3>
          <ul className="list-disc ml-6">
            {recommendations.map((r, i) => (
              <li key={i}>
                <a href={r.link} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
                  {r.course} ({r.provider})
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SkillGapAnalysis;
