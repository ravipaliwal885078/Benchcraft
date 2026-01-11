import React from "react";
import RFPUploader from "../components/RFPUploader";

const Projects = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-primary mb-4">Project Management</h1>
      <p className="text-muted-foreground">Upload RFP/SOW documents to onboard new projects.</p>
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-primary mb-2">Upload RFP</h2>
        <RFPUploader />
      </div>
    </div>
  );
};

export default Projects;
