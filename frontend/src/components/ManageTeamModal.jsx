import { useState, useEffect } from 'react'
import { X, Plus } from 'lucide-react'
import { getProject, getEmployees, updateProjectTeam, checkEmployeeAllocation } from '../services/api'

// Helper function to get today's date in YYYY-MM-DD format (timezone-safe)
const getTodayDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const ManageTeamModal = ({ projectId, projectName, isOpen, onClose, onSuccess }) => {
  const [teamMembers, setTeamMembers] = useState([])
  const [availableEmployees, setAvailableEmployees] = useState([])
  const [validationErrors, setValidationErrors] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadTeamData()
    }
  }, [isOpen, projectId])

  const loadTeamData = async () => {
    try {
      setLoading(true)
      // Load project details with team
      const projectData = await getProject(projectId)
      const allTeamMembers = projectData.team || []
      
      // Filter out past resources (end_date < today)
      const today = getTodayDate()
      const activeTeamMembers = allTeamMembers.filter(member => {
        // Keep members with no end_date (ongoing) or end_date > today (future only)
        // Exclude members with end_date <= today (past or ending today)
        return !member.end_date || member.end_date > today
      })
      
      setTeamMembers(activeTeamMembers)
      
      // Load available employees
      const employeesData = await getEmployees()
      setAvailableEmployees(employeesData.employees || [])
    } catch (error) {
      console.error('Failed to load project team:', error)
      alert('Failed to load project team: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleTeamUpdate = async () => {
    try {
      // Validate all team members before submission
      const errors = {}
      let hasErrors = false

      // Validate all members
      const today = getTodayDate()
      for (let i = 0; i < teamMembers.length; i++) {
        const member = teamMembers[i]
        if (!member.employee_id) {
          errors[i] = { message: 'Please select an employee', isValidating: false }
          hasErrors = true
          continue
        }

        // Use internal_allocation_percentage for validation (primary field)
        const internalAllocationPercentage = parseInt(member.internal_allocation_percentage !== undefined ? member.internal_allocation_percentage : member.allocation_percentage) || 0
        const startDate = member.start_date || getTodayDate()
        const endDate = member.end_date || null

        // Validate end date (must be >= start date)
        if (endDate && endDate < startDate) {
          errors[i] = { message: 'End date cannot be before start date', isValidating: false }
          hasErrors = true
          continue
        }

        // Validate range for internal allocation percentage
        if (internalAllocationPercentage < 0 || internalAllocationPercentage > 100) {
          errors[i] = { message: 'Internal allocation percentage must be between 0 and 100%', isValidating: false }
          hasErrors = true
          continue
        }

        // If internal allocation percentage is 0%, skip backend validation (0% is always valid)
        if (internalAllocationPercentage === 0) {
          continue // Skip backend check for 0% internal allocation
        }

        // Check with backend using internal_allocation_percentage
        try {
          const checkResult = await checkEmployeeAllocation(member.employee_id, {
            internal_allocation_percentage: internalAllocationPercentage,
            start_date: startDate,
            end_date: endDate,
            exclude_allocation_id: member.id || null
          })

          if (!checkResult.is_valid) {
            errors[i] = { message: checkResult.error_message || `Total internal allocation would be ${checkResult.would_be_total}%. Maximum allowed is 100%.`, isValidating: false }
            hasErrors = true
          }
        } catch (checkError) {
          const errorMsg = checkError.response?.data?.error || checkError.message || 'Validation check failed'
          errors[i] = { message: errorMsg, isValidating: false }
          hasErrors = true
        }
      }

      // Update validation errors state
      setValidationErrors(errors)

      // If validation errors found, prevent submission
      if (hasErrors) {
        return
      }

      // All validations passed, proceed with update
      const allocations = teamMembers.map(member => ({
        employee_id: member.employee_id,
        allocation_id: member.id || null,
        start_date: member.start_date || new Date().toISOString().split('T')[0],
        end_date: member.end_date || null,
        allocation_percentage: parseInt(member.allocation_percentage) || 100,
        internal_allocation_percentage: parseInt(member.internal_allocation_percentage) || parseInt(member.allocation_percentage) || 100,
        billable_percentage: parseInt(member.billable_percentage) || 100,
        billing_rate: member.billing_rate || null,
        is_trainee: member.is_trainee === true ? true : false,  // Explicitly set to false if not true
        mentoring_primary_emp_id: member.is_trainee === true ? (member.mentoring_primary_emp_id || null) : null
      }))
      
      await updateProjectTeam(projectId, allocations)
      alert('Project team updated successfully!')
      handleClose()
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      console.error('Failed to update team:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error'
      alert('Failed to update team: ' + errorMessage)
    }
  }

  const handleClose = () => {
    setTeamMembers([])
    setValidationErrors({})
    onClose()
  }

  const handleRemoveTeamMember = (allocationId) => {
    if (!confirm('Are you sure you want to remove this team member? The allocation will end today and be saved when you click "Save Changes".')) return
    
    // Set end_date to today instead of deleting
    // This preserves the allocation history
    const today = getTodayDate()
    
    const memberIndex = teamMembers.findIndex(m => m.id === allocationId)
    const updatedMembers = teamMembers.map(member => {
      if (member.id === allocationId) {
        return {
          ...member,
          end_date: today
        }
      }
      return member
    })
    
    setTeamMembers(updatedMembers)
    
    // Clear validation errors for this member since we're ending the allocation
    if (memberIndex !== -1) {
      const newErrors = { ...validationErrors }
      delete newErrors[memberIndex]
      setValidationErrors(newErrors)
    }
  }

  const handleRemoveNewTeamMember = (index) => {
    setTeamMembers(teamMembers.filter((_, i) => i !== index))
    const newErrors = { ...validationErrors }
    delete newErrors[index]
    // Reindex errors for remaining members
    const reindexedErrors = {}
    Object.keys(newErrors).forEach(key => {
      const keyNum = parseInt(key)
      if (keyNum > index) {
        reindexedErrors[keyNum - 1] = newErrors[key]
      } else if (keyNum < index) {
        reindexedErrors[keyNum] = newErrors[key]
      }
    })
    setValidationErrors(reindexedErrors)
  }

  const handleAddTeamMember = () => {
    setTeamMembers([...teamMembers, {
      employee_id: '',
      start_date: getTodayDate(),
      end_date: '',
      allocation_percentage: 100,
      internal_allocation_percentage: 100,
      billable_percentage: 100,
      billing_rate: null,
      is_trainee: false,
      mentoring_primary_emp_id: null
    }])
  }

  const handleTeamMemberChange = (index, field, value) => {
    const updated = [...teamMembers]
    updated[index][field] = value
    setTeamMembers(updated)
    
    // Validate dates and allocation overlaps when changed
    if (field === 'start_date' || field === 'end_date' || field === 'employee_id') {
      // Delay validation slightly to allow state to update
      setTimeout(() => {
        validateTeamMemberDates(index, updated[index])
      }, 100)
    }
    
    // Validate allocation when allocation percentage changes
    if (field === 'allocation_percentage' || field === 'internal_allocation_percentage') {
      if (updated[index].employee_id && updated[index].start_date) {
        setTimeout(() => {
          validateTeamMemberAllocation(index, updated[index])
        }, 100)
      }
    }
    
    // Clear validation error for this field when user changes it
    if (field === 'allocation_percentage' || field === 'start_date' || field === 'end_date' || field === 'employee_id' || field === 'internal_allocation_percentage') {
      const newErrors = { ...validationErrors }
      if (newErrors[index] && !newErrors[index].isValidating) {
        // Don't clear immediately - let validation run first
      }
    }
    
    // When is_trainee is unchecked, clear mentoring_primary_emp_id
    if (field === 'is_trainee' && !value) {
      updated[index].mentoring_primary_emp_id = null
      setTeamMembers(updated)
    }
  }

  const validateTeamMemberDates = async (index, member) => {
    const errors = { ...validationErrors }
    
    // Validate end date
    if (member.end_date && member.start_date) {
      if (member.end_date < member.start_date) {
        errors[index] = { message: 'End date cannot be before start date', isValidating: false }
        setValidationErrors(errors)
        return
      }
    }
    
    // Clear date errors if valid
    if (errors[index] && errors[index].message.includes('End date')) {
      delete errors[index]
      setValidationErrors(errors)
    }
  }

  const validateTeamMemberAllocation = async (index, member) => {
    if (!member.employee_id) {
      return // Skip validation if employee not selected
    }

    // Set validating state
    setValidationErrors(prev => ({
      ...prev,
      [index]: { message: 'Validating...', isValidating: true }
    }))

    try {
      // Use internal_allocation_percentage for validation (primary field)
      const internalAllocationPercentage = parseInt(member.internal_allocation_percentage !== undefined ? member.internal_allocation_percentage : member.allocation_percentage) || 0
      const startDate = member.start_date || getTodayDate()
      const endDate = member.end_date || null

      // Validate range first
      if (internalAllocationPercentage < 0 || internalAllocationPercentage > 100) {
        setValidationErrors(prev => ({
          ...prev,
          [index]: { message: 'Internal allocation percentage must be between 0 and 100%', isValidating: false }
        }))
        return
      }

      // If 0%, it's always valid
      if (internalAllocationPercentage === 0) {
        const newErrors = { ...validationErrors }
        delete newErrors[index]
        setValidationErrors(newErrors)
        return
      }

      // Check with backend using internal_allocation_percentage
      const checkResult = await checkEmployeeAllocation(member.employee_id, {
        internal_allocation_percentage: internalAllocationPercentage,
        start_date: startDate,
        end_date: endDate,
        exclude_allocation_id: member.id || null
      })

      if (!checkResult.is_valid) {
        setValidationErrors(prev => ({
          ...prev,
          [index]: { message: checkResult.error_message || `Total internal allocation would be ${checkResult.would_be_total}%. Maximum allowed is 100%.`, isValidating: false }
        }))
      } else {
        // Clear error if valid
        const newErrors = { ...validationErrors }
        delete newErrors[index]
        setValidationErrors(newErrors)
      }
    } catch (checkError) {
      console.error('Failed to check allocation:', checkError)
      const errorMsg = checkError.response?.data?.error || checkError.message || 'Validation check failed'
      setValidationErrors(prev => ({
        ...prev,
        [index]: { message: errorMsg, isValidating: false }
      }))
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-5xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Manage Team - {projectName}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">Loading team data...</div>
        ) : (
          <>
            <div className="mb-4">
              <button
                onClick={handleAddTeamMember}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add Team Member</span>
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Employee
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Start Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      End Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Allocation % (Client)
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Internal Allocation %
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Billable %
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Billing Rate
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Is Shadow
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Shadow For
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {teamMembers.map((member, index) => {
                    const employee = availableEmployees.find(e => e.id === member.employee_id)
                    const hasError = validationErrors[index] && !validationErrors[index].isValidating
                    const errorMessage = validationErrors[index]?.message || ''
                    const isStartDateError = errorMessage.includes('Start date')
                    const isEndDateError = errorMessage.includes('End date')
                    const isAllocationError = hasError && !isStartDateError && !isEndDateError
                    
                    return (
                      <>
                        <tr key={member.id || index}>
                          <td className="px-4 py-3 whitespace-nowrap">
                            {member.id ? (
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {member.first_name} {member.last_name}
                                </div>
                                <div className="text-sm text-gray-500">{member.role_level}</div>
                              </div>
                            ) : (
                              <select
                                value={member.employee_id}
                                onChange={(e) => handleTeamMemberChange(index, 'employee_id', parseInt(e.target.value))}
                                className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                              >
                                <option value="">Select Employee</option>
                                {availableEmployees.map(emp => (
                                  <option key={emp.id} value={emp.id}>
                                    {emp.first_name} {emp.last_name} ({emp.role_level})
                                  </option>
                                ))}
                              </select>
                            )}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex flex-col">
                              <input
                                type="date"
                                value={member.start_date || ''}
                                onChange={(e) => handleTeamMemberChange(index, 'start_date', e.target.value)}
                                onBlur={() => validateTeamMemberDates(index, member)}
                                className="w-full border rounded-md px-2 py-1 text-sm border-gray-300"
                              />
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex flex-col">
                              <input
                                type="date"
                                value={member.end_date || ''}
                                min={member.start_date || getTodayDate()}
                                onChange={(e) => handleTeamMemberChange(index, 'end_date', e.target.value)}
                                onBlur={() => validateTeamMemberDates(index, member)}
                                className={`w-full border rounded-md px-2 py-1 text-sm ${
                                  validationErrors[index] && validationErrors[index].message.includes('End date')
                                    ? 'border-red-500 bg-red-50'
                                    : (() => {
                                        const today = getTodayDate()
                                        return member.end_date === today && member.id ? 'border-orange-500 bg-orange-50' : 'border-gray-300'
                                      })()
                                }`}
                              />
                              {validationErrors[index] && validationErrors[index].message.includes('End date') && !validationErrors[index].isValidating && (
                                <div className="mt-1 text-xs text-red-600 whitespace-normal break-words max-w-48">
                                  {validationErrors[index].message}
                                </div>
                              )}
                              {(() => {
                                const today = getTodayDate()
                                if (member.end_date === today && member.id) {
                                  return (
                                    <div className="mt-1 text-xs text-orange-600">
                                      Will be removed when saved
                                    </div>
                                  )
                                }
                                return null
                              })()}
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex flex-col">
                              <input
                                type="number"
                                min="0"
                                max="100"
                                value={member.allocation_percentage || 100}
                                onChange={(e) => handleTeamMemberChange(index, 'allocation_percentage', e.target.value)}
                                onBlur={() => validateTeamMemberAllocation(index, member)}
                                className={`w-full border rounded-md px-2 py-1 text-sm w-20 ${
                                  validationErrors[index] && (
                                    validationErrors[index].message.includes('Allocation percentage') ||
                                    (validationErrors[index].message.includes('allocated') ||
                                     validationErrors[index].message.includes('exceed') ||
                                     validationErrors[index].message.includes('Total allocation'))
                                  ) && !validationErrors[index].isValidating
                                    ? 'border-red-500 bg-red-50' 
                                    : 'border-gray-300'
                                }`}
                                title="Allocation percentage reported to client"
                              />
                              {validationErrors[index] && validationErrors[index].message.includes('Allocation percentage') && !validationErrors[index].isValidating && (
                                <div className="mt-1 text-xs text-red-600 whitespace-normal break-words max-w-48">
                                  {validationErrors[index].message}
                                </div>
                              )}
                              {validationErrors[index] && validationErrors[index].isValidating && (
                                <div className="mt-1 text-xs text-blue-600">
                                  {validationErrors[index].message}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex flex-col">
                              <input
                                type="number"
                                min="0"
                                max="100"
                                value={member.internal_allocation_percentage !== undefined ? member.internal_allocation_percentage : (member.allocation_percentage || 100)}
                                onChange={(e) => handleTeamMemberChange(index, 'internal_allocation_percentage', e.target.value)}
                                onBlur={() => validateTeamMemberAllocation(index, member)}
                                className={`w-full border rounded-md px-2 py-1 text-sm w-20 ${
                                  validationErrors[index] && (
                                    validationErrors[index].message.includes('allocated') ||
                                    validationErrors[index].message.includes('exceed') ||
                                    validationErrors[index].message.includes('Total internal allocation') ||
                                    validationErrors[index].message.includes('internal allocation')
                                  ) && !validationErrors[index].isValidating
                                    ? 'border-red-500 bg-red-50' 
                                    : 'border-gray-300'
                                }`}
                                title="Actual internal allocation percentage (for cost calculation)"
                              />
                              {validationErrors[index] && (
                                validationErrors[index].message.includes('allocated') ||
                                validationErrors[index].message.includes('exceed') ||
                                validationErrors[index].message.includes('Total internal allocation') ||
                                validationErrors[index].message.includes('internal allocation')
                              ) && !validationErrors[index].isValidating && (
                                <div className="mt-1 text-xs text-red-600 whitespace-normal break-words max-w-48">
                                  {validationErrors[index].message}
                                </div>
                              )}
                              {validationErrors[index] && validationErrors[index].isValidating && (
                                <div className="mt-1 text-xs text-blue-600">
                                  {validationErrors[index].message}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={member.billable_percentage || 100}
                              onChange={(e) => handleTeamMemberChange(index, 'billable_percentage', e.target.value)}
                              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm w-20"
                            />
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <input
                              type="number"
                              step="0.01"
                              value={member.billing_rate || ''}
                              onChange={(e) => handleTeamMemberChange(index, 'billing_rate', e.target.value ? parseFloat(e.target.value) : null)}
                              placeholder="0.00"
                              className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm w-24"
                            />
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <input
                              type="checkbox"
                              checked={member.is_trainee || false}
                              onChange={(e) => {
                                handleTeamMemberChange(index, 'is_trainee', e.target.checked)
                                if (!e.target.checked) {
                                  handleTeamMemberChange(index, 'mentoring_primary_emp_id', null)
                                }
                              }}
                              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                              title="Check if this is a shadow/trainee resource"
                            />
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            {member.is_trainee ? (
                              <select
                                value={member.mentoring_primary_emp_id || ''}
                                onChange={(e) => handleTeamMemberChange(index, 'mentoring_primary_emp_id', e.target.value ? parseInt(e.target.value) : null)}
                                className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                              >
                                <option value="">Select Mentor</option>
                                {availableEmployees
                                  .filter(emp => emp.id !== member.employee_id && teamMembers.some(m => m.employee_id === emp.id && !m.is_trainee))
                                  .map(emp => (
                                    <option key={emp.id} value={emp.id}>
                                      {emp.first_name} {emp.last_name}
                                    </option>
                                  ))}
                              </select>
                            ) : (
                              <span className="text-gray-400 text-xs">N/A</span>
                            )}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm font-medium">
                            {member.id ? (
                              <>
                                {(() => {
                                  const today = getTodayDate()
                                  const isMarkedForRemoval = member.end_date === today
                                  return isMarkedForRemoval ? (
                                    <span className="text-orange-600 text-xs italic">Ending today</span>
                                  ) : (
                                    <button
                                      onClick={() => handleRemoveTeamMember(member.id)}
                                      className="text-red-600 hover:text-red-900"
                                    >
                                      Remove
                                    </button>
                                  )
                                })()}
                              </>
                            ) : (
                              <button
                                onClick={() => handleRemoveNewTeamMember(index)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Remove
                              </button>
                            )}
                          </td>
                        </tr>
                        {isAllocationError && (
                          <tr key={`error-${member.id || index}`} className="bg-red-50">
                            <td colSpan="10" className="px-4 py-2 border-t border-red-200">
                              <div className="text-xs text-red-600 whitespace-normal break-words">
                                {errorMessage}
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {teamMembers.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No team members. Click "Add Team Member" to get started.
              </div>
            )}

            <div className="flex space-x-3 pt-4 mt-4 border-t border-gray-200">
              <button
                onClick={handleTeamUpdate}
                disabled={Object.keys(validationErrors).length > 0}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  Object.keys(validationErrors).length > 0
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                }`}
              >
                Save Changes
              </button>
              <button
                onClick={handleClose}
                className="px-4 py-2 rounded-md text-sm font-medium bg-gray-200 text-gray-700 hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default ManageTeamModal
