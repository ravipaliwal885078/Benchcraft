import React, { useState } from "react";

const SmartMatch = () => {
  const [criteria, setCriteria] = useState({ skills: "", domain: "" });
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState([]);
  const [explanation, setExplanation] = useState("");
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setCriteria({ ...criteria, [e.target.name]: e.target.value });
  };

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setMatches([]);
    setExplanation("");
    try {
      const res = await fetch("/api/v1/search/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(criteria),
      });
      const data = await res.json();
      if (res.ok) {
        setMatches(data.matches);
        setExplanation(data.explanation);
      } else {
        setError(data.error || "Search failed");
      }
    } catch (err) {
      setError("Network error");
    }
    setLoading(false);
  };

  return (
    <div className="bg-white p-6 rounded shadow mt-8">
      <h2 className="text-lg font-semibold text-primary mb-4">Smart Matching Engine</h2>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          name="skills"
          placeholder="Required Skills (comma separated)"
          className="border px-2 py-1 rounded w-1/2"
          value={criteria.skills}
          onChange={handleChange}
        />
        <input
          type="text"
          name="domain"
          placeholder="Domain (e.g. IT, Finance)"
          className="border px-2 py-1 rounded w-1/2"
          value={criteria.domain}
          onChange={handleChange}
        />
        <button
          className="px-4 py-2 bg-primary text-white rounded"
          onClick={handleSearch}
          disabled={loading}
        >
          {loading ? "Matching..." : "Find Matches"}
        </button>
      </div>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {explanation && <div className="text-gray-600 mb-2">{explanation}</div>}
      <ul className="divide-y">
        {matches.map((m) => (
          <li key={m.anon_id} className="py-2">
            <span className="font-mono text-indigo-700">{m.anon_id}</span> | Skills: {m.skills.join(", ")} | Exp: {m.experience} | Score: {(m.score * 100).toFixed(0)}% | Proficiency: {m.proficiency}/5 | Domain: {m.domain}
          </li>
        ))}
      </ul>
      {error && <div className="text-destructive mb-2">{error}</div>}
      {explanation && <div className="text-muted-foreground mb-2">{explanation}</div>}
    </div>
  );
};

export default SmartMatch;
