import React from "react";
import RiskCardView from "../components/RiskCardView";
import PageHeader from "../components/PageHeader";

const Risk = () => {
  return (
    <div className="space-y-6 p-6">
      <PageHeader
        title="Risk & Notice Period Management"
        subtitle="Monitor and manage risks for employees and projects"
      />

      <RiskCardView />
    </div>
  );
};

export default Risk;
