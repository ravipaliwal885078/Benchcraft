import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProject, createProjectFeedback, getEmployees, updateProjectTeam, checkEmployeeAllocation, removeTeamMember } from '../services/api'
import {
  Building, Calendar, DollarSign, Users, TrendingUp,
  Star, MessageSquare, Target, Clock, Briefcase, X, Plus, Edit
} from 'lucide-react'
import ManageTeamModal from '../components/ManageTeamModal'

const ProjectView = () => {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Helper function to get today's date in YYYY-MM-DD format (timezone-safe)
  const getTodayDate = () => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const [availableEmployees, setAvailableEmployees] = useState([])
  const [feedbackForm, setFeedbackForm] = useState({
    employee_id: '',
    rating: 5,
    feedback: '',
    tags: ''
  })
  const [showUpdateMemberModal, setShowUpdateMemberModal] = useState(false)
  const [selectedMember, setSelectedMember] = useState(null)
  const [memberForm, setMemberForm] = useState({
    start_date: '',
    end_date: '',
    allocation_percentage: 100,
    internal_allocation_percentage: 100,
    billable_percentage: 100,
    billing_rate: ''
  })
  const [memberValidationError, setMemberValidationError] = useState(null)
  const [showTeamModal, setShowTeamModal] = useState(false)
  const [showPastAllocations, setShowPastAllocations] = useState(false)

  useEffect(() => {
    loadProject()
    loadEmployees()
  }, [id])


  const loadEmployees = async () => {
    try {
      const data = await getEmployees()
      setAvailableEmployees(data.employees || [])
    } catch (error) {
      console.error('Failed to load employees:', error)
    }
  }

  const loadProject = async () => {
    try {
      const data = await getProject(id)
      setProject(data)
    } catch (error) {
      console.error('Failed to load project:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault()
    try {
      await createProjectFeedback(id, feedbackForm)
      alert('Feedback submitted successfully!')
      setShowFeedbackModal(false)
      setFeedbackForm({
        employee_id: '',
        rating: 5,
        feedback: '',
        tags: ''
      })
      loadProject() // Reload to show new feedback
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      alert('Failed to submit feedback: ' + (error.response?.data?.error || error.message))
    }
  }

  const openUpdateMemberModal = (member) => {
    setSelectedMember(member)
    setMemberForm({
      start_date: member.start_date || '',
      end_date: member.end_date || '',
      allocation_percentage: member.allocation_percentage || member.utilization || 100,
      internal_allocation_percentage: member.internal_allocation_percentage || member.allocation_percentage || member.utilization || 100,
      billable_percentage: member.billable_percentage || 100,
      billing_rate: member.billing_rate || ''
    })
    setMemberValidationError(null)
    setShowUpdateMemberModal(true)
  }

  const validateMemberAllocation = async () => {
    if (!selectedMember) return true

    const today = getTodayDate()
    const allocationPercentage = parseInt(memberForm.allocation_percentage) || 0
    const startDate = memberForm.start_date || today
    const endDate = memberForm.end_date || null

    // Validate end date (must be >= start date)
    if (endDate && endDate < startDate) {
      setMemberValidationError('End date cannot be before start date.')
      return false
    }

    // Validate range
    if (allocationPercentage < 0 || allocationPercentage > 100) {
      setMemberValidationError('Allocation percentage must be between 0 and 100%')
      return false
    }

    // If allocation percentage is 0%, skip backend validation (0% is always valid)
    if (allocationPercentage === 0) {
      setMemberValidationError(null)
      return true
    }

    // Use internal_allocation_percentage for validation
    const internalAllocationPercentage = parseInt(memberForm.internal_allocation_percentage) || allocationPercentage
    try {
      const checkResult = await checkEmployeeAllocation(selectedMember.employee_id, {
        internal_allocation_percentage: internalAllocationPercentage,
        start_date: startDate,
        end_date: endDate,
        exclude_allocation_id: selectedMember.id
      })

      if (!checkResult.is_valid) {
        setMemberValidationError(checkResult.error_message || `Total allocation would be ${checkResult.would_be_total}%. Maximum allowed is 100%.`)
        return false
      }

      setMemberValidationError(null)
      return true
    } catch (checkError) {
      const errorMsg = checkError.response?.data?.error || checkError.message || 'Validation check failed'
      setMemberValidationError(errorMsg)
      return false
    }
  }

  const handleMemberUpdate = async (e) => {
    e.preventDefault()
    
    // Validate before submission
    const isValid = await validateMemberAllocation()
    if (!isValid) {
      return
    }

    try {
      const allocations = [{
        employee_id: selectedMember.employee_id,
        allocation_id: selectedMember.id,
        start_date: memberForm.start_date,
        end_date: memberForm.end_date || null,
        allocation_percentage: parseInt(memberForm.allocation_percentage) || 100,
        internal_allocation_percentage: parseInt(memberForm.internal_allocation_percentage) || parseInt(memberForm.allocation_percentage) || 100,
        billable_percentage: parseInt(memberForm.billable_percentage) || 100,
        billing_rate: memberForm.billing_rate ? parseFloat(memberForm.billing_rate) : null
      }]

      await updateProjectTeam(id, allocations)
      alert('Team member updated successfully!')
      setShowUpdateMemberModal(false)
      setSelectedMember(null)
      loadProject() // Reload to show updated data
    } catch (error) {
      console.error('Failed to update team member:', error)
      alert('Failed to update team member: ' + (error.response?.data?.error || error.message))
    }
  }

  const openTeamModal = () => {
    setShowTeamModal(true)
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
        is_trainee: member.is_trainee || false,
        mentoring_primary_emp_id: member.is_trainee ? (member.mentoring_primary_emp_id || null) : null
      }))
      
      await updateProjectTeam(id, allocations)
      alert('Project team updated successfully!')
      setShowTeamModal(false)
      setValidationErrors({})
      loadProject() // Reload to show updated data
    } catch (error) {
      console.error('Failed to update team:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error'
      alert('Failed to update team: ' + errorMessage)
    }
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
    if (field === 'allocation_percentage' && updated[index].employee_id && updated[index].start_date) {
      setTimeout(() => {
        validateTeamMemberAllocation(index, updated[index])
      }, 100)
    }
    
    // Clear validation error for this field when user changes it (but not if we're validating)
    if (field === 'allocation_percentage' || field === 'start_date' || field === 'end_date' || field === 'employee_id') {
      const newErrors = { ...validationErrors }
      // Only clear if we're not currently validating (which will set new errors)
      if (newErrors[index] && !newErrors[index].isValidating) {
        // Don't clear immediately - let validation run first
        // The validation function will update errors appropriately
      }
    }
  }

  const validateTeamMemberDates = async (index, member) => {
    const errors = { ...validationErrors }
    
    // Validate end date
    if (member.end_date && member.start_date) {
      if (member.end_date < member.start_date) {
        errors[index] = {
          message: 'End date cannot be before start date.',
          isValidating: false
        }
        setValidationErrors(errors)
        return
      }
    }
    
    // If employee is selected and dates are valid, check for allocation overlaps
    if (member.employee_id && member.start_date) {
      await validateTeamMemberAllocation(index, member)
      return
    }
    
    // Clear errors if validation passes
    if (errors[index]) {
      delete errors[index]
      setValidationErrors(errors)
    }
  }

  const validateTeamMemberAllocation = async (index, member) => {
    if (!member.employee_id || !member.start_date) {
      return // Skip if employee or start date not selected
    }

    // Use internal_allocation_percentage for validation (primary field)
    const internalAllocationPercentage = parseInt(member.internal_allocation_percentage !== undefined ? member.internal_allocation_percentage : member.allocation_percentage) || 0
    
    // If internal allocation percentage is 0%, it doesn't count towards total allocation
    // (0% means not allocated, so it's always valid - clear any existing errors)
    if (internalAllocationPercentage === 0) {
      setValidationErrors(prev => {
        const newErrors = { ...prev }
        // Only clear allocation-related errors, keep date validation errors
        if (newErrors[index] && (
          newErrors[index].message.includes('allocated') ||
          newErrors[index].message.includes('exceed') ||
          newErrors[index].message.includes('Total allocation') ||
          newErrors[index].message.includes('internal allocation')
        )) {
          delete newErrors[index]
        }
        return newErrors
      })
      return
    }

    // Set validating state
    setValidationErrors(prev => ({
      ...prev,
      [index]: { message: 'Checking availability...', isValidating: true }
    }))

    try {
      const startDate = member.start_date
      const endDate = member.end_date || null

      // Check with backend for overlapping allocations using internal_allocation_percentage
      const checkResult = await checkEmployeeAllocation(member.employee_id, {
        internal_allocation_percentage: internalAllocationPercentage,
        start_date: startDate,
        end_date: endDate,
        exclude_allocation_id: member.id || null
      })

      if (!checkResult.is_valid) {
        // Check if the issue is due to 100% internal allocation overlap
        if (checkResult.would_be_total > 100) {
          const errorMsg = checkResult.error_message || 
            `Resource is already ${checkResult.current_total}% internally allocated in this date range. Adding ${internalAllocationPercentage}% would exceed 100%.`
          
          setValidationErrors(prev => ({
            ...prev,
            [index]: { 
              message: errorMsg,
              isValidating: false 
            }
          }))
        } else {
          setValidationErrors(prev => ({
            ...prev,
            [index]: { 
              message: checkResult.error_message || 'Allocation validation failed',
              isValidating: false 
            }
          }))
        }
      } else {
        // Clear validation error if valid
        setValidationErrors(prev => {
          const newErrors = { ...prev }
          // Only clear if the error was about allocation, not date validation
          if (newErrors[index] && !newErrors[index].message.includes('date')) {
            delete newErrors[index]
          }
          return newErrors
        })
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || 'Validation check failed'
      setValidationErrors(prev => ({
        ...prev,
        [index]: { 
          message: errorMsg,
          isValidating: false 
        }
      }))
    }
  }

  const handleRemoveNewTeamMember = (index) => {
    const updated = teamMembers.filter((_, i) => i !== index)
    setTeamMembers(updated)
    
    // Clear validation errors for removed member
    const newErrors = { ...validationErrors }
    delete newErrors[index]
    // Shift errors for members after the removed one
    const shiftedErrors = {}
    Object.keys(newErrors).forEach(key => {
      const keyNum = parseInt(key)
      if (keyNum < index) {
        shiftedErrors[keyNum] = newErrors[key]
      } else if (keyNum > index) {
        shiftedErrors[keyNum - 1] = newErrors[key]
      }
    })
    setValidationErrors(shiftedErrors)
  }

  const validateTeamMember = async (index) => {
    const member = teamMembers[index]
    if (!member.employee_id) {
      return // Skip validation if employee not selected
    }

    // Set validating state
    setValidationErrors(prev => ({
      ...prev,
      [index]: { message: 'Validating...', isValidating: true }
    }))

    try {
      const allocationPercentage = parseInt(member.allocation_percentage) || 0
      const startDate = member.start_date || new Date().toISOString().split('T')[0]
      const endDate = member.end_date || null

      // Validate range first
      if (allocationPercentage < 0 || allocationPercentage > 100) {
        setValidationErrors(prev => ({
          ...prev,
          [index]: { message: 'Allocation percentage must be between 0 and 100%', isValidating: false }
        }))
        return
      }

      // If allocation percentage is 0%, skip backend validation (0% is always valid)
      if (allocationPercentage === 0) {
        setValidationErrors(prev => {
          const newErrors = { ...prev }
          // Only clear allocation-related errors, keep date validation errors
          if (newErrors[index] && (
            newErrors[index].message.includes('allocated') ||
            newErrors[index].message.includes('exceed') ||
            newErrors[index].message.includes('Total allocation')
          )) {
            delete newErrors[index]
          }
          return newErrors
        })
        return
      }

      // Check with backend
      const checkResult = await checkEmployeeAllocation(member.employee_id, {
        allocation_percentage: allocationPercentage,
        start_date: startDate,
        end_date: endDate,
        exclude_allocation_id: member.id || null
      })

      if (!checkResult.is_valid) {
        setValidationErrors(prev => ({
          ...prev,
          [index]: { message: checkResult.error_message || `Total allocation would be ${checkResult.would_be_total}%. Maximum allowed is 100%.`, isValidating: false }
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

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-success/10 text-success'
      case 'pipeline': return 'bg-info/10 text-info'
      case 'closed': return 'bg-muted text-muted-foreground'
      default: return 'bg-muted text-muted-foreground'
    }
  }

  const getRoleColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'principal': return 'bg-purple-600'
      case 'lead': return 'bg-info'
      case 'sr': return 'bg-primary'
      case 'mid': return 'bg-accent'
      case 'jr': return 'bg-success'
      default: return 'bg-muted-foreground'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD'
    return new Date(dateString).toLocaleDateString()
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">Loading project details...</div>
  }

  if (!project) {
    return <div className="text-center py-12 text-destructive">Project not found</div>
  }

  const proj = project.project
  const team = project.team
  const feedbacks = project.feedbacks
  const metrics = project.metrics

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-background rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 rounded-full bg-accent flex items-center justify-center">
              <Building className="w-8 h-8 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {proj.project_name}
              </h1>
              <p className="text-gray-600 flex items-center mt-1">
                <Building className="w-4 h-4 mr-2" />
                {proj.client_name}
              </p>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(proj.status)}`}>
                  {proj.status}
                </span>
                {proj.probability > 0 && (
                  <span className="text-sm text-gray-600">
                    {proj.probability}% probability
                  </span>
                )}
              </div>
            </div>
          </div>
          <Link
            to="/pipeline"
            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
          >
            ← Back to Projects
          </Link>
        </div>
      </div>

      {/* Project Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Team Size</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.total_team_members}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <DollarSign className="w-8 h-8 text-green-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Budget Used</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(metrics.budget_utilized)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-purple-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Avg Utilization</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.avg_utilization}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <Target className="w-8 h-8 text-orange-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Budget Remaining</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(metrics.budget_remaining)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Project Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Client:</span>
              <span className="font-medium">{proj.client_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Project:</span>
              <span className="font-medium">{proj.project_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(proj.status)}`}>
                {proj.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Budget Cap:</span>
              <span className="font-medium">{formatCurrency(proj.budget_cap)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Start Date:</span>
              <span className="font-medium">{formatDate(proj.start_date)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">End Date:</span>
              <span className="font-medium">{formatDate(proj.end_date)}</span>
            </div>
            {proj.probability > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Probability:</span>
                <span className="font-medium">{proj.probability}%</span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tech Stack & Description</h3>
          {proj.tech_stack && (
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">Technologies:</p>
              <div className="flex flex-wrap gap-2">
                {proj.tech_stack.split(',').map((tech, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {tech.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div>
            <p className="text-sm text-gray-600 mb-2">Description:</p>
            <p className="text-gray-700 leading-relaxed">{proj.description}</p>
          </div>
        </div>
      </div>

      {/* Team Members */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Users className="w-5 h-5 mr-2" />
            Team Members ({team.length})
          </h3>
          <div className="flex items-center space-x-3">
            {(() => {
              // Filter active and past allocations
              const today = getTodayDate()
              const activeTeam = team.filter(m => {
                // Active: no end_date (ongoing) OR end_date is in the future (end_date > today)
                return !m.end_date || m.end_date > today
              })
              const pastTeam = team.filter(m => {
                // Past: has end_date AND end_date is today or in the past (end_date <= today)
                return m.end_date && m.end_date <= today
              })
              
              return (
                <>
                  {pastTeam.length > 0 && (
                    <button
                      onClick={() => setShowPastAllocations(!showPastAllocations)}
                      className="text-indigo-600 hover:text-indigo-800 text-sm font-medium underline flex items-center space-x-1 transition-colors"
                    >
                      <Clock className="w-4 h-4" />
                      <span>{showPastAllocations ? 'Active Team' : 'Past Team'}</span>
                    </button>
                  )}
                  <button
                    onClick={openTeamModal}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center space-x-2 text-sm"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Manage Team</span>
                  </button>
                </>
              )
            })()}
          </div>
        </div>
        {(() => {
          // Filter active and past allocations
          const today = getTodayDate()
          const activeTeam = team.filter(m => {
            // Active: no end_date (ongoing) OR end_date is in the future (end_date > today)
            return !m.end_date || m.end_date > today
          })
          const pastTeam = team.filter(m => {
            // Past: has end_date AND end_date is today or in the past (end_date <= today)
            return m.end_date && m.end_date <= today
          })
          const displayTeam = showPastAllocations ? pastTeam : activeTeam
          
          if (displayTeam.length === 0) {
            if (showPastAllocations) {
              return <p className="text-gray-600 text-center py-8">No past allocations found.</p>
            }
            return <p className="text-gray-600 text-center py-8">No team members allocated yet.</p>
          }
          
          return (
            <>
              {!showPastAllocations && activeTeam.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                  {activeTeam.map((member) => (
                    <div key={member.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Link
                          to={`/employees/${member.employee_id}`}
                          className="font-medium text-indigo-600 hover:text-indigo-800"
                        >
                          {member.first_name} {member.last_name}
                        </Link>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(member.role_level)}`}>
                          {member.role_level}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>📅 {formatDate(member.start_date)} - {formatDate(member.end_date)}</p>
                        {member.billing_rate && <p>💰 ${member.billing_rate}/hr</p>}
                        <div className="flex items-center space-x-3 mt-1">
                          <span className="text-blue-600">
                            📊 Allocation: {member.allocation_percentage || member.utilization || 100}%
                          </span>
                          <span className="text-purple-600">
                            💰 Billable: {member.billable_percentage || 100}%
                          </span>
                        </div>
                        {(member.allocation_percentage || member.utilization || 100) !== (member.billable_percentage || 100) && (
                          <p className="text-orange-600 text-xs mt-1">⚠️ Partial billing scenario</p>
                        )}
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <button
                          onClick={() => openUpdateMemberModal(member)}
                          className="w-full bg-indigo-600 text-white px-3 py-2 rounded-md hover:bg-indigo-700 flex items-center justify-center space-x-2 text-sm"
                        >
                          <Edit className="w-4 h-4" />
                          <span>Update</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {showPastAllocations && pastTeam.length > 0 && (
                <div className="space-y-4">
                  <div className="border-l-4 border-gray-400 pl-4 py-2 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600 font-medium">
                      Past Allocations ({pastTeam.length})
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {pastTeam.map((member) => (
                      <div key={member.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50 opacity-75">
                        <div className="flex items-center justify-between mb-2">
                          <Link
                            to={`/employees/${member.employee_id}`}
                            className="font-medium text-indigo-600 hover:text-indigo-800"
                          >
                            {member.first_name} {member.last_name}
                          </Link>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(member.role_level)}`}>
                            {member.role_level}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>📅 {formatDate(member.start_date)} - {formatDate(member.end_date)}</p>
                          {member.billing_rate && <p>💰 ${member.billing_rate}/hr</p>}
                          <div className="flex items-center space-x-3 mt-1">
                            <span className="text-blue-600">
                              📊 Allocation: {member.allocation_percentage || member.utilization || 100}%
                            </span>
                            <span className="text-purple-600">
                              💰 Billable: {member.billable_percentage || 100}%
                            </span>
                          </div>
                          {(member.allocation_percentage || member.utilization || 100) !== (member.billable_percentage || 100) && (
                            <p className="text-orange-600 text-xs mt-1">⚠️ Partial billing scenario</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )
        })()}
      </div>

      {/* Performance Feedback */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <MessageSquare className="w-5 h-5 mr-2" />
            Performance Feedback ({feedbacks.length})
          </h3>
          <button
            onClick={() => setShowFeedbackModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center space-x-2 text-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Feedback</span>
          </button>
        </div>
        {feedbacks.length > 0 ? (
          <div className="space-y-4">
            {feedbacks.map((feedback) => (
              <div key={feedback.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{feedback.employee_name}</span>
                  <div className="flex items-center">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`w-4 h-4 ${
                          star <= feedback.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                        }`}
                      />
                    ))}
                    <span className="ml-2 text-sm font-medium">{feedback.rating}/5</span>
                  </div>
                </div>
                <p className="text-gray-700 mb-2">{feedback.feedback}</p>
                {feedback.tags && (
                  <div className="flex flex-wrap gap-2">
                    {feedback.tags.split(',').map((tag, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600 text-center py-8">No feedback available for this project.</p>
        )}
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Performance Feedback - Project</h2>
              <button
                onClick={() => {
                  setShowFeedbackModal(false)
                  setFeedbackForm({
                    employee_id: '',
                    rating: 5,
                    feedback: '',
                    tags: ''
                  })
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleFeedbackSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team Member *
                </label>
                <select
                  required
                  value={feedbackForm.employee_id}
                  onChange={(e) => setFeedbackForm({ ...feedbackForm, employee_id: parseInt(e.target.value) })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Select Team Member</option>
                  {team.map((member) => (
                    <option key={member.employee_id} value={member.employee_id}>
                      {member.first_name} {member.last_name} ({member.role_level})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rating (1-5) *
                </label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setFeedbackForm({ ...feedbackForm, rating: star })}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`w-8 h-8 ${
                          star <= feedbackForm.rating
                            ? 'text-yellow-400 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                  <span className="ml-2 text-sm text-gray-600">{feedbackForm.rating}/5</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Feedback *
                </label>
                <textarea
                  required
                  value={feedbackForm.feedback}
                  onChange={(e) => setFeedbackForm({ ...feedbackForm, feedback: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 h-32"
                  placeholder="Enter your feedback..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={feedbackForm.tags}
                  onChange={(e) => setFeedbackForm({ ...feedbackForm, tags: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="e.g., Delivery, Innovation, Communication"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700"
                >
                  Submit Feedback
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowFeedbackModal(false)
                    setFeedbackForm({
                      employee_id: '',
                      rating: 5,
                      feedback: '',
                      tags: ''
                    })
                  }}
                  className="border border-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Update Team Member Modal */}
      {showUpdateMemberModal && selectedMember && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Update Team Member - {selectedMember.first_name} {selectedMember.last_name}
              </h2>
              <button
                onClick={() => {
                  setShowUpdateMemberModal(false)
                  setSelectedMember(null)
                  setMemberValidationError(null)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleMemberUpdate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={memberForm.start_date}
                    onChange={(e) => {
                      setMemberForm({ ...memberForm, start_date: e.target.value })
                      setMemberValidationError(null)
                    }}
                    onBlur={validateMemberAllocation}
                    className="w-full border rounded-md px-3 py-2 border-gray-300"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={memberForm.end_date}
                    min={memberForm.start_date || getTodayDate()}
                    onChange={(e) => {
                      setMemberForm({ ...memberForm, end_date: e.target.value })
                      setMemberValidationError(null)
                    }}
                    onBlur={validateMemberAllocation}
                    className={`w-full border rounded-md px-3 py-2 ${
                      memberValidationError && memberValidationError.includes('End date')
                        ? 'border-red-500 bg-red-50'
                        : 'border-gray-300'
                    }`}
                  />
                  {memberValidationError && memberValidationError.includes('End date') && (
                    <div className="mt-1 text-xs text-red-600">
                      {memberValidationError}
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Allocation % (Client) *
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    required
                    value={memberForm.allocation_percentage}
                    onChange={(e) => {
                      setMemberForm({ ...memberForm, allocation_percentage: e.target.value })
                      setMemberValidationError(null)
                    }}
                    onBlur={validateMemberAllocation}
                    className={`w-full border rounded-md px-3 py-2 ${
                      memberValidationError ? 'border-red-500 bg-red-50' : 'border-gray-300'
                    }`}
                    title="Allocation percentage reported to client"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Internal Allocation % *
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    required
                    value={memberForm.internal_allocation_percentage}
                    onChange={(e) => setMemberForm({ ...memberForm, internal_allocation_percentage: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    title="Actual internal allocation percentage (for cost calculation)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Billable % *
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    required
                    value={memberForm.billable_percentage}
                    onChange={(e) => setMemberForm({ ...memberForm, billable_percentage: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Billing Rate
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={memberForm.billing_rate}
                  onChange={(e) => setMemberForm({ ...memberForm, billing_rate: e.target.value })}
                  placeholder="0.00"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              {memberValidationError && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-600">{memberValidationError}</p>
                </div>
              )}

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  disabled={!!memberValidationError}
                  className={`px-6 py-2 rounded-md ${
                    memberValidationError
                      ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                      : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  }`}
                >
                  Update Team Member
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowUpdateMemberModal(false)
                    setSelectedMember(null)
                    setMemberValidationError(null)
                  }}
                  className="border border-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manage Team Modal */}
      <ManageTeamModal
        projectId={id}
        projectName={project?.project_name || 'Project'}
        isOpen={showTeamModal}
        onClose={() => setShowTeamModal(false)}
        onSuccess={loadProject}
      />
    </div>
  )
}

export default ProjectView