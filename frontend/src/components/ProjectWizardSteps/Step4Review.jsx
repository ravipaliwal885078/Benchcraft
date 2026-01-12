const Step4Review = ({ projectDetails, teamStructure, teamAllotment, employees }) => {
  const getEmployeeName = (employeeId) => {
    const emp = employees.find(e => e.id === parseInt(employeeId))
    return emp ? `${emp.first_name} ${emp.last_name}` : 'N/A'
  }
  
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Project Details</h3>
      
      {/* Project Details Summary */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Project Details</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-600">Client:</span> <span className="font-medium">{projectDetails.client_name}</span></div>
          <div><span className="text-gray-600">Project:</span> <span className="font-medium">{projectDetails.project_name}</span></div>
          <div><span className="text-gray-600">Industry:</span> <span className="font-medium">{projectDetails.industry_domain}</span></div>
          <div><span className="text-gray-600">Type:</span> <span className="font-medium">{projectDetails.project_type}</span></div>
          <div><span className="text-gray-600">Status:</span> <span className="font-medium">{projectDetails.status}</span></div>
          {projectDetails.status === 'PIPELINE' && (
            <div><span className="text-gray-600">Probability:</span> <span className="font-medium">{projectDetails.probability}%</span></div>
          )}
          <div><span className="text-gray-600">Budget:</span> <span className="font-medium">{projectDetails.billing_currency} {projectDetails.budget_cap}</span></div>
          <div><span className="text-gray-600">Start Date:</span> <span className="font-medium">{projectDetails.start_date}</span></div>
          {projectDetails.end_date && (
            <div><span className="text-gray-600">End Date:</span> <span className="font-medium">{projectDetails.end_date}</span></div>
          )}
        </div>
        {projectDetails.tech_stack.length > 0 && (
          <div className="mt-4">
            <span className="text-gray-600 text-sm">Tech Stack:</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {projectDetails.tech_stack.map((tech, i) => (
                <span key={i} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Team Structure Summary */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Team Structure</h4>
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left">Role</th>
              <th className="px-4 py-2 text-left">Count</th>
              <th className="px-4 py-2 text-left">Utilization</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {teamStructure.map((item, i) => (
              <tr key={i}>
                <td className="px-4 py-2">{item.role_name}</td>
                <td className="px-4 py-2">{item.required_count}</td>
                <td className="px-4 py-2">{item.utilization_percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Team Allotment Summary */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Team Allotment</h4>
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left">Role</th>
              <th className="px-4 py-2 text-left">Resource</th>
              <th className="px-4 py-2 text-left">Allocation % (Client)</th>
              <th className="px-4 py-2 text-left">Internal Allocation %</th>
              <th className="px-4 py-2 text-left">Billable %</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {teamAllotment.map((item, i) => (
              <tr key={i}>
                <td className="px-4 py-2">{item.role_name}</td>
                <td className="px-4 py-2">{getEmployeeName(item.employee_id)}</td>
                <td className="px-4 py-2">{item.allocation_percentage}%</td>
                <td className="px-4 py-2">{item.internal_allocation_percentage !== undefined ? item.internal_allocation_percentage : item.allocation_percentage}%</td>
                <td className="px-4 py-2">{item.billable_percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Step4Review
