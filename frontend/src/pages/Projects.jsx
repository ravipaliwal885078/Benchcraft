import React from "react";
import RFPUploader from "../components/RFPUploader";
import PageHeader from "../components/PageHeader";

const Projects = () => {
  return (
    <div className="p-8">
      <PageHeader
        title="Project Management"
        subtitle="Upload RFP/SOW documents to onboard new projects."
      />
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-primary mb-2">Upload RFP</h2>
        <RFPUploader />
      </div>
    </div>
  );
};

export default Projects;
