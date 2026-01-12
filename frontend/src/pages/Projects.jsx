import React, { useState } from "react";
import RFPUploader from "../components/RFPUploader";
import PageHeader from "../components/PageHeader";
import ProjectWizard from "../components/ProjectWizard";
import RFPImportWizard from "../components/RFPImportWizard";
import { Plus, FileUp } from "lucide-react";

const Projects = () => {
  const [showManualWizard, setShowManualWizard] = useState(false);
  const [showRFPWizard, setShowRFPWizard] = useState(false);

  const handleProjectCreated = (project) => {
    // Refresh projects list or navigate
    console.log('Project created:', project);
    window.location.reload(); // Simple refresh for now
  };

  return (
    <div className="p-8">
      <PageHeader
        title="Project Management"
        subtitle="Upload RFP/SOW documents to onboard new projects."
        actions={
          <div className="flex gap-3">
            <button
              onClick={() => setShowManualWizard(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Create Project
            </button>
            <button
              onClick={() => setShowRFPWizard(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              <FileUp className="w-5 h-5 flex-shrink-0" />
              <span className="hidden sm:inline">Create Project With RFP</span>
              <span className="sm:hidden">Import RFP</span>
            </button>
          </div>
        }
      />
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-primary mb-2">Upload RFP</h2>
        <RFPUploader />
      </div>

      {/* Manual Project Wizard */}
      <ProjectWizard
        isOpen={showManualWizard}
        onClose={() => setShowManualWizard(false)}
        onSuccess={handleProjectCreated}
      />

      {/* RFP Import Wizard */}
      <RFPImportWizard
        isOpen={showRFPWizard}
        onClose={() => setShowRFPWizard(false)}
        onSuccess={handleProjectCreated}
      />
    </div>
  );
};

export default Projects;
