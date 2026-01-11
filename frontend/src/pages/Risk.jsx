import React from "react";
import NoticePeriodRisk from "../components/NoticePeriodRisk";

const Risk = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-primary mb-4">Risk & Notice Period Management</h1>
      <p className="text-muted-foreground">Check notice period status and risk for employees and projects.</p>
      <NoticePeriodRisk />
    </div>
  );
};

export default Risk;
