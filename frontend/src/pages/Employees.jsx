import React from "react";
import DocumentUploader from "../components/DocumentUploader";
import CertificateUploader from "../components/CertificateUploader";
import HRVerificationPanel from "../components/HRVerificationPanel";

const Employees = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-primary mb-4">Employee Management</h1>
      <p className="text-muted-foreground">List, onboard, and manage employees here.</p>
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-primary mb-2">
          Onboard New Employee (Upload Resume)
        </h2>
        <DocumentUploader />
      </div>
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-primary mb-2">Upload Certificate (Optional)</h2>
        <CertificateUploader />
      </div>
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-primary mb-2">HR Verification Panel</h2>
        <HRVerificationPanel />
      </div>
    </div>
  );
};

export default Employees;
