const Step3TeamAllotment = ({ allotment, employees, onChange, onAllotmentChange, getEmployeesForRole, errors, aiSuggestions, loadingSuggestions, onGenerateSuggestions }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Assign Resources to Roles</h3>
        <button
          onClick={onGenerateSuggestions}
          disabled={loadingSuggestions}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loadingSuggestions ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <span>AI Suggest Team</span>
            </>
          )}
        </button>
      </div>
      
      {/* AI Insights Section */}
      {loadingSuggestions && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <p className="text-blue-800 text-sm">AI is analyzing and suggesting optimal team members...</p>
          </div>
        </div>
      )}
      
      {aiSuggestions && !loadingSuggestions && (
        <div className="space-y-3 mb-4">
          {aiSuggestions.insights && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-indigo-900 mb-1">AI Insights</h4>
                  <p className="text-sm text-indigo-800">{aiSuggestions.insights}</p>
                </div>
              </div>
            </div>
          )}
          
          {aiSuggestions.benefits && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-green-900 mb-1">Benefits</h4>
                  <p className="text-sm text-green-800">{aiSuggestions.benefits}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation % (Client)</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Internal Allocation %</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Billable %</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Billing Rate</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Date</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">End Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {allotment.map((item, index) => {
              const availableEmployees = getEmployeesForRole(item.role_name)
              return (
                <tr key={index}>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {item.role_name}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={item.employee_id}
                      onChange={(e) => onAllotmentChange(index, 'employee_id', e.target.value)}
                      className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_employee`] ? 'border-red-500' : 'border-gray-300'}`}
                    >
                      <option value="">Select Resource</option>
                      {availableEmployees.map(emp => (
                        <option key={emp.id} value={emp.id}>
                          {emp.first_name} {emp.last_name} ({emp.role_level})
                        </option>
                      ))}
                    </select>
                    {errors[`${index}_employee`] && (
                      <p className="text-red-500 text-xs mt-1">{errors[`${index}_employee`]}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={item.allocation_percentage}
                      onChange={(e) => onAllotmentChange(index, 'allocation_percentage', parseInt(e.target.value) || 0)}
                      className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                      title="Allocation percentage reported to client"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={item.internal_allocation_percentage !== undefined ? item.internal_allocation_percentage : item.allocation_percentage}
                      onChange={(e) => onAllotmentChange(index, 'internal_allocation_percentage', parseInt(e.target.value) || 0)}
                      className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                      title="Actual internal allocation percentage (for cost calculation)"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={item.billable_percentage}
                      onChange={(e) => onAllotmentChange(index, 'billable_percentage', parseInt(e.target.value) || 100)}
                      className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={item.billing_rate}
                      onChange={(e) => onAllotmentChange(index, 'billing_rate', e.target.value)}
                      placeholder="0.00"
                      className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="date"
                      value={item.start_date}
                      onChange={(e) => onAllotmentChange(index, 'start_date', e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_start_date`] ? 'border-red-500' : 'border-gray-300'}`}
                    />
                    {errors[`${index}_start_date`] && (
                      <p className="text-red-500 text-xs mt-1">{errors[`${index}_start_date`]}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="date"
                      value={item.end_date}
                      onChange={(e) => onAllotmentChange(index, 'end_date', e.target.value)}
                      min={item.start_date || new Date().toISOString().split('T')[0]}
                      className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_end_date`] ? 'border-red-500' : 'border-gray-300'}`}
                    />
                    {errors[`${index}_end_date`] && (
                      <p className="text-red-500 text-xs mt-1">{errors[`${index}_end_date`]}</p>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Step3TeamAllotment
