import { useState, useEffect } from 'react'
import { X, ChevronRight, ChevronLeft, Check } from 'lucide-react'
import { createProject, getEmployees, suggestTeam } from '../services/api'

const ROLE_OPTIONS = [
  'Architect',
  'Project Manager',
  'Senior Developer',
  'Developer',
  'Business Analyst',
  'QA Engineer',
  'Tech Lead',
  'Designer'
]

const ROLE_DEFAULTS = {
  'Architect': { utilization: 25, maxUtilization: 50 },
  'Project Manager': { utilization: 20, maxUtilization: 99 },
  'Senior Developer': { utilization: 100, maxUtilization: 100 },
  'Developer': { utilization: 100, maxUtilization: 100 },
  'Business Analyst': { utilization: 50, maxUtilization: 100 },
  'QA Engineer': { utilization: 50, maxUtilization: 99 },
  'Tech Lead': { utilization: 75, maxUtilization: 100 },
  'Designer': { utilization: 75, maxUtilization: 100 }
}

const INDUSTRY_DOMAINS = ['FinTech', 'Healthcare', 'Retail', 'Manufacturing', 'Telecom', 'Education', 'Other']
const PROJECT_TYPES = ['Fixed_Price', 'T&M', 'Retainer']
const CURRENCIES = ['INR', 'USD', 'EUR']
const STATUS_OPTIONS = ['PIPELINE', 'ACTIVE', 'ON_HOLD', 'CLOSED', 'CANCELLED']

const ProjectWizard = ({ isOpen, onClose, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState(1)
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(false)
  
  // Step 1: Project Details
  const [projectDetails, setProjectDetails] = useState({
    client_name: '',
    project_name: '',
    industry_domain: '',
    project_type: '',
    start_date: '',
    end_date: '',
    status: 'PIPELINE',
    probability: 0,
    budget_cap: '',
    billing_currency: 'USD',
    tech_stack: [],
    description: ''
  })
  
  // Step 1: Errors
  const [step1Errors, setStep1Errors] = useState({})
  
  // Step 2: Team Structure
  const [teamStructure, setTeamStructure] = useState([
    { role_name: '', required_count: 1, utilization_percentage: 100 }
  ])
  const [structureErrors, setStructureErrors] = useState({})
  
  // Step 3: Team Allotment
  const [teamAllotment, setTeamAllotment] = useState([]) // [{ role_name, employee_id, allocation_percentage, billable_percentage, billing_rate, start_date, end_date }]
  const [allotmentErrors, setAllotmentErrors] = useState({})
  const [aiSuggestions, setAiSuggestions] = useState(null) // { suggestions, insights, benefits }
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  
  useEffect(() => {
    if (isOpen) {
      loadEmployees()
    }
  }, [isOpen])
  
  useEffect(() => {
    // Generate team allotment rows based on team structure
    if (currentStep === 3 && teamStructure.length > 0) {
      // Only regenerate if teamAllotment is empty or structure changed significantly
      const hasValidStructure = teamStructure.every(s => s.role_name)
      const totalRequired = teamStructure.reduce((sum, s) => sum + (s.required_count || 0), 0)
      
      // If we have valid structure and no existing allotment, generate AI suggestions
      if (hasValidStructure && totalRequired > 0 && teamAllotment.length === 0) {
        generateAISuggestions()
      } else if (teamAllotment.length === 0) {
        // Fallback: generate empty rows
        const allotmentRows = []
        teamStructure.forEach(structure => {
          for (let i = 0; i < structure.required_count; i++) {
            allotmentRows.push({
              role_name: structure.role_name,
              employee_id: '',
              allocation_percentage: structure.utilization_percentage,
              billable_percentage: 100,
              billing_rate: '',
              start_date: projectDetails.start_date || '',
              end_date: projectDetails.end_date || ''
            })
          }
        })
        setTeamAllotment(allotmentRows)
      }
    }
  }, [currentStep])
  
  const generateAISuggestions = async () => {
    // Validate we have required data
    if (!projectDetails.start_date || teamStructure.length === 0) {
      return
    }
    
    const hasValidStructure = teamStructure.every(s => s.role_name && s.required_count > 0)
    if (!hasValidStructure) {
      return
    }
    
    setLoadingSuggestions(true)
    try {
      // Prepare project details for AI
      const projectDetailsForAI = {
        project_name: projectDetails.project_name || 'New Project',
        description: projectDetails.description || '',
        tech_stack: Array.isArray(projectDetails.tech_stack) 
          ? projectDetails.tech_stack.join(', ') 
          : projectDetails.tech_stack || '',
        industry_domain: projectDetails.industry_domain || ''
      }
      
      // Prepare role requirements
      const roleReqs = teamStructure
        .filter(s => s.role_name && s.required_count > 0)
        .map(s => ({
          role_name: s.role_name,
          required_count: parseInt(s.required_count),
          utilization_percentage: parseInt(s.utilization_percentage)
        }))
      
      const response = await suggestTeam(
        projectDetailsForAI,
        roleReqs,
        projectDetails.start_date,
        projectDetails.end_date || null
      )
      
      setAiSuggestions({
        insights: response.insights || '',
        benefits: response.benefits || ''
      })
      
      // Map AI suggestions to allotment rows
      const allotmentRows = []
      const suggestionsByRole = {}
      
      // Group suggestions by role
      response.suggestions.forEach(sug => {
        if (!suggestionsByRole[sug.role_name]) {
          suggestionsByRole[sug.role_name] = []
        }
        suggestionsByRole[sug.role_name].push(sug)
      })
      
      // Create rows based on role requirements
      teamStructure.forEach(structure => {
        const roleSugs = suggestionsByRole[structure.role_name] || []
        const requiredCount = parseInt(structure.required_count)
        
        for (let i = 0; i < requiredCount; i++) {
          if (i < roleSugs.length) {
            // Use AI suggestion
            const sug = roleSugs[i]
            allotmentRows.push({
              role_name: structure.role_name,
              employee_id: sug.employee_id.toString(),
              allocation_percentage: sug.allocation_percentage,
              billable_percentage: sug.billable_percentage || 100,
              billing_rate: sug.billing_rate || '',
              start_date: projectDetails.start_date || '',
              end_date: projectDetails.end_date || ''
            })
          } else {
            // Empty row if not enough suggestions
            allotmentRows.push({
              role_name: structure.role_name,
              employee_id: '',
              allocation_percentage: structure.utilization_percentage,
              billable_percentage: 100,
              billing_rate: '',
              start_date: projectDetails.start_date || '',
              end_date: projectDetails.end_date || ''
            })
          }
        }
      })
      
      setTeamAllotment(allotmentRows)
      
    } catch (error) {
      console.error('Failed to generate AI suggestions:', error)
      // Fallback to empty rows
      const allotmentRows = []
      teamStructure.forEach(structure => {
        for (let i = 0; i < structure.required_count; i++) {
          allotmentRows.push({
            role_name: structure.role_name,
            employee_id: '',
            allocation_percentage: structure.utilization_percentage,
            billable_percentage: 100,
            billing_rate: '',
            start_date: projectDetails.start_date || '',
            end_date: projectDetails.end_date || ''
          })
        }
      })
      setTeamAllotment(allotmentRows)
    } finally {
      setLoadingSuggestions(false)
    }
  }
  
  const loadEmployees = async () => {
    try {
      const data = await getEmployees()
      setEmployees(data.employees || [])
    } catch (error) {
      console.error('Failed to load employees:', error)
    }
  }
  
  const handleClose = () => {
    if (window.confirm('Are you sure you want to cancel? All entered data will be lost.')) {
      resetForm()
      onClose()
    }
  }
  
  const resetForm = () => {
    setCurrentStep(1)
    setProjectDetails({
      client_name: '',
      project_name: '',
      industry_domain: '',
      project_type: '',
      start_date: '',
      end_date: '',
      status: 'PIPELINE',
      probability: 0,
      budget_cap: '',
      billing_currency: 'USD',
      tech_stack: [],
      description: ''
    })
    setTeamStructure([{ role_name: '', required_count: 1, utilization_percentage: 100 }])
    setTeamAllotment([])
    setStructureErrors({})
    setAllotmentErrors({})
  }
  
  const validateStep1 = () => {
    const errors = {}
    if (!projectDetails.client_name.trim()) errors.client_name = 'Client Name is required'
    if (!projectDetails.project_name.trim()) errors.project_name = 'Project Name is required'
    if (!projectDetails.industry_domain) errors.industry_domain = 'Industry Domain is required'
    if (!projectDetails.project_type) errors.project_type = 'Project Type is required'
    if (!projectDetails.start_date) errors.start_date = 'Start Date is required'
    if (projectDetails.end_date && projectDetails.end_date < projectDetails.start_date) {
      errors.end_date = 'End Date cannot be before Start Date'
    }
    if (!projectDetails.status) errors.status = 'Status is required'
    if (projectDetails.status === 'PIPELINE' && (projectDetails.probability < 0 || projectDetails.probability > 100)) {
      errors.probability = 'Probability must be between 0 and 100'
    }
    if (!projectDetails.budget_cap || parseFloat(projectDetails.budget_cap) < 0) {
      errors.budget_cap = 'Budget Cap is required and must be >= 0'
    }
    if (!projectDetails.billing_currency) errors.billing_currency = 'Billing Currency is required'
    if (!projectDetails.description.trim() || projectDetails.description.length < 10) {
      errors.description = 'Description is required (minimum 10 characters)'
    }
    return Object.keys(errors).length === 0
  }
  
  const validateStep2 = () => {
    const errors = {}
    const roleNames = []
    
    teamStructure.forEach((structure, index) => {
      if (!structure.role_name) {
        errors[`${index}_role`] = 'Role is required'
      } else {
        // Check for duplicate roles
        if (roleNames.includes(structure.role_name)) {
          errors[`${index}_role`] = 'This role is already added'
        } else {
          roleNames.push(structure.role_name)
        }
      }
      
      if (!structure.required_count || structure.required_count < 1) {
        errors[`${index}_count`] = 'Required Count must be at least 1'
      }
      
      const roleDefaults = ROLE_DEFAULTS[structure.role_name]
      if (roleDefaults) {
        if (structure.utilization_percentage < 0 || structure.utilization_percentage > 100) {
          errors[`${index}_utilization`] = 'Utilization must be between 0 and 100%'
        } else if (structure.utilization_percentage > roleDefaults.maxUtilization) {
          errors[`${index}_utilization`] = `${structure.role_name} utilization cannot exceed ${roleDefaults.maxUtilization}%`
        }
      } else if (structure.utilization_percentage < 0 || structure.utilization_percentage > 100) {
        errors[`${index}_utilization`] = 'Utilization must be between 0 and 100%'
      }
    })
    
    setStructureErrors(errors)
    return Object.keys(errors).length === 0
  }
  
  const validateStep3 = () => {
    const errors = {}
    
    teamAllotment.forEach((allotment, index) => {
      if (!allotment.employee_id) {
        errors[`${index}_employee`] = 'Resource selection is required'
      }
      if (!allotment.start_date) {
        errors[`${index}_start_date`] = 'Start Date is required'
      }
      if (allotment.end_date && allotment.end_date < allotment.start_date) {
        errors[`${index}_end_date`] = 'End Date cannot be before Start Date'
      }
    })
    
    setAllotmentErrors(errors)
    return Object.keys(errors).length === 0
  }
  
  const handleNext = () => {
    let isValid = false
    
    if (currentStep === 1) {
      isValid = validateStep1()
    } else if (currentStep === 2) {
      isValid = validateStep2()
    } else if (currentStep === 3) {
      isValid = validateStep3()
    }
    
    if (isValid) {
      setCurrentStep(currentStep + 1)
    }
  }
  
  const handleBack = () => {
    setCurrentStep(currentStep - 1)
  }
  
  const handleSubmit = async () => {
    if (!validateStep3()) return
    
    setLoading(true)
    try {
      const payload = {
        ...projectDetails,
        budget_cap: parseFloat(projectDetails.budget_cap),
        tech_stack: Array.isArray(projectDetails.tech_stack) 
          ? projectDetails.tech_stack.join(', ') 
          : projectDetails.tech_stack,
        role_requirements: teamStructure.map(s => ({
          role_name: s.role_name,
          required_count: parseInt(s.required_count),
          utilization_percentage: parseInt(s.utilization_percentage)
        })),
        allocations: teamAllotment.map(a => ({
          employee_id: parseInt(a.employee_id),
          allocation_percentage: parseInt(a.allocation_percentage),
          billable_percentage: parseInt(a.billable_percentage),
          billing_rate: a.billing_rate ? parseFloat(a.billing_rate) : null,
          start_date: a.start_date,
          end_date: a.end_date || null
        }))
      }
      
      const response = await createProject(payload)
      alert(`Project created successfully!\nProject Code: ${response.project.project_code}`)
      resetForm()
      onSuccess(response.project)
      onClose()
    } catch (error) {
      console.error('Failed to create project:', error)
      alert('Failed to create project: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
    }
  }
  
  const handleTechStackAdd = (tech) => {
    if (tech && !projectDetails.tech_stack.includes(tech)) {
      setProjectDetails({
        ...projectDetails,
        tech_stack: [...projectDetails.tech_stack, tech]
      })
    }
  }
  
  const handleTechStackRemove = (tech) => {
    setProjectDetails({
      ...projectDetails,
      tech_stack: projectDetails.tech_stack.filter(t => t !== tech)
    })
  }
  
  const handleAddRole = () => {
    setTeamStructure([...teamStructure, { role_name: '', required_count: 1, utilization_percentage: 100 }])
  }
  
  const handleRemoveRole = (index) => {
    if (teamStructure.length > 1) {
      const newStructure = teamStructure.filter((_, i) => i !== index)
      setTeamStructure(newStructure)
      // Clear errors for removed index
      const newErrors = { ...structureErrors }
      Object.keys(newErrors).forEach(key => {
        if (key.startsWith(`${index}_`)) {
          delete newErrors[key]
        }
      })
      setStructureErrors(newErrors)
    }
  }
  
  const handleRoleChange = (index, field, value) => {
    const updated = [...teamStructure]
    updated[index][field] = value
    
    // Auto-fill utilization based on role
    if (field === 'role_name' && value) {
      const defaults = ROLE_DEFAULTS[value]
      if (defaults) {
        updated[index].utilization_percentage = defaults.utilization
      }
    }
    
    setTeamStructure(updated)
    
    // Clear errors for this field
    const newErrors = { ...structureErrors }
    delete newErrors[`${index}_${field}`]
    setStructureErrors(newErrors)
  }
  
  const handleAllotmentChange = (index, field, value) => {
    const updated = [...teamAllotment]
    updated[index][field] = value
    setTeamAllotment(updated)
    
    // Clear errors for this field
    const newErrors = { ...allotmentErrors }
    delete newErrors[`${index}_${field}`]
    setAllotmentErrors(newErrors)
  }
  
  const getEmployeesForRole = (roleName) => {
    // Filter employees based on role - for now, return all employees
    // In future, you can add role mapping logic here
    return employees
  }
  
  if (!isOpen) return null
  
  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={(e) => e.target === e.currentTarget && handleClose()}
    >
      {/* Backdrop with blur */}
      <div className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm" />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-2xl w-full max-w-[1100px] max-h-[90vh] mx-4 overflow-hidden flex flex-col animate-in fade-in-0 zoom-in-95 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
          <div>
            <h2 className="text-2xl font-bold">Create Project</h2>
            <p className="text-indigo-100 text-sm mt-1">Step {currentStep} of 4</p>
          </div>
          <button
            onClick={handleClose}
            className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        {/* Stepper */}
        <div className="px-6 py-4 border-b bg-gray-50">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    currentStep >= step
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}>
                    {currentStep > step ? (
                      <Check className="w-6 h-6" />
                    ) : (
                      step
                    )}
                  </div>
                  <span className={`ml-2 text-sm font-medium ${
                    currentStep >= step ? 'text-indigo-600' : 'text-gray-500'
                  }`}>
                    {step === 1 && 'Project Details'}
                    {step === 2 && 'Team Structure'}
                    {step === 3 && 'Team Allotment'}
                    {step === 4 && 'Review'}
                  </span>
                </div>
                {step < 4 && (
                  <ChevronRight className="w-5 h-5 text-gray-400 mx-2" />
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {currentStep === 1 && (
            <Step1ProjectDetails
              data={projectDetails}
              onChange={setProjectDetails}
              errors={step1Errors}
            />
          )}
          {currentStep === 2 && (
            <Step2TeamStructure
              structure={teamStructure}
              onChange={setTeamStructure}
              onAdd={handleAddRole}
              onRemove={handleRemoveRole}
              onRoleChange={handleRoleChange}
              errors={structureErrors}
            />
          )}
          {currentStep === 3 && (
            <Step3TeamAllotment
              allotment={teamAllotment}
              employees={employees}
              onChange={setTeamAllotment}
              onAllotmentChange={handleAllotmentChange}
              getEmployeesForRole={getEmployeesForRole}
              errors={allotmentErrors}
            />
          )}
          {currentStep === 4 && (
            <Step4Review
              projectDetails={projectDetails}
              teamStructure={teamStructure}
              teamAllotment={teamAllotment}
              employees={employees}
            />
          )}
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <button
            onClick={handleClose}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <div className="flex space-x-3">
            {currentStep > 1 && (
              <button
                onClick={handleBack}
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 transition-colors flex items-center"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Back
              </button>
            )}
            {currentStep < 4 ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors flex items-center"
              >
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create Project'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Step 1: Project Details
const Step1ProjectDetails = ({ data, onChange, errors }) => {
  const [techInput, setTechInput] = useState('')
  
  const handleChange = (field, value) => {
    onChange({ ...data, [field]: value })
  }
  
  return (
    <div className="space-y-6">
      {/* Basic Info */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Basic Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Client Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={data.client_name}
              onChange={(e) => handleChange('client_name', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 ${errors.client_name ? 'border-red-500' : 'border-gray-300'}`}
              required
            />
            {errors.client_name && <p className="text-red-500 text-xs mt-1">{errors.client_name}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={data.project_name}
              onChange={(e) => handleChange('project_name', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 ${errors.project_name ? 'border-red-500' : 'border-gray-300'}`}
              required
            />
            {errors.project_name && <p className="text-red-500 text-xs mt-1">{errors.project_name}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry Domain <span className="text-red-500">*</span>
            </label>
            <select
              value={data.industry_domain}
              onChange={(e) => handleChange('industry_domain', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 ${errors.industry_domain ? 'border-red-500' : 'border-gray-300'}`}
              required
            >
              <option value="">Select Domain</option>
              {INDUSTRY_DOMAINS.map(domain => (
                <option key={domain} value={domain}>{domain}</option>
              ))}
            </select>
            {errors.industry_domain && <p className="text-red-500 text-xs mt-1">{errors.industry_domain}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project Type <span className="text-red-500">*</span>
            </label>
            <div className="flex space-x-4 mt-2">
              {PROJECT_TYPES.map(type => (
                <label key={type} className="flex items-center">
                  <input
                    type="radio"
                    name="project_type"
                    value={type}
                    checked={data.project_type === type}
                    onChange={(e) => handleChange('project_type', e.target.value)}
                    className="mr-2"
                  />
                  <span className="text-sm">{type}</span>
                </label>
              ))}
            </div>
            {errors.project_type && <p className="text-red-500 text-xs mt-1">{errors.project_type}</p>}
          </div>
        </div>
      </div>
      
      {/* Timeline & Status */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Timeline & Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={data.start_date}
              onChange={(e) => handleChange('start_date', e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className={`w-full border rounded-md px-3 py-2 ${errors.start_date ? 'border-red-500' : 'border-gray-300'}`}
              required
            />
            {errors.start_date && <p className="text-red-500 text-xs mt-1">{errors.start_date}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={data.end_date}
              onChange={(e) => handleChange('end_date', e.target.value)}
              min={data.start_date || new Date().toISOString().split('T')[0]}
              className={`w-full border rounded-md px-3 py-2 ${errors.end_date ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.end_date && <p className="text-red-500 text-xs mt-1">{errors.end_date}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              value={data.status}
              onChange={(e) => handleChange('status', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 ${errors.status ? 'border-red-500' : 'border-gray-300'}`}
              required
            >
              {STATUS_OPTIONS.map(status => (
                <option key={status} value={status}>{status.replace('_', ' ')}</option>
              ))}
            </select>
            {errors.status && <p className="text-red-500 text-xs mt-1">{errors.status}</p>}
          </div>
          {data.status === 'PIPELINE' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Probability <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={data.probability}
                  onChange={(e) => handleChange('probability', parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-sm font-medium w-16 text-right">{data.probability}%</span>
              </div>
              {errors.probability && <p className="text-red-500 text-xs mt-1">{errors.probability}</p>}
            </div>
          )}
        </div>
      </div>
      
      {/* Budget */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Budget</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Budget Cap <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={data.budget_cap}
              onChange={(e) => handleChange('budget_cap', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 ${errors.budget_cap ? 'border-red-500' : 'border-gray-300'}`}
              required
            />
            {errors.budget_cap && <p className="text-red-500 text-xs mt-1">{errors.budget_cap}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Billing Currency <span className="text-red-500">*</span>
            </label>
            <select
              value={data.billing_currency}
              onChange={(e) => handleChange('billing_currency', e.target.value)}
              className={`w-full border rounded-md px-3 py-2 ${errors.billing_currency ? 'border-red-500' : 'border-gray-300'}`}
              required
            >
              {CURRENCIES.map(currency => (
                <option key={currency} value={currency}>{currency}</option>
              ))}
            </select>
            {errors.billing_currency && <p className="text-red-500 text-xs mt-1">{errors.billing_currency}</p>}
          </div>
        </div>
      </div>
      
      {/* Technology */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Technology Stack</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {data.tech_stack.map((tech, index) => (
            <span
              key={index}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-indigo-100 text-indigo-800"
            >
              {tech}
              <button
                onClick={() => {
                  const newStack = data.tech_stack.filter((_, i) => i !== index)
                  handleChange('tech_stack', newStack)
                }}
                className="ml-2 text-indigo-600 hover:text-indigo-800"
              >
                <X className="w-4 h-4" />
              </button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={techInput}
            onChange={(e) => setTechInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                if (techInput.trim()) {
                  handleChange('tech_stack', [...data.tech_stack, techInput.trim()])
                  setTechInput('')
                }
              }
            }}
            placeholder="Add technology (press Enter)"
            className="flex-1 border border-gray-300 rounded-md px-3 py-2"
          />
          <button
            onClick={() => {
              if (techInput.trim()) {
                handleChange('tech_stack', [...data.tech_stack, techInput.trim()])
                setTechInput('')
              }
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Add
          </button>
        </div>
      </div>
      
      {/* Description */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Description</h3>
        <div>
          <textarea
            value={data.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={6}
            maxLength={1000}
            className={`w-full border rounded-md px-3 py-2 ${errors.description ? 'border-red-500' : 'border-gray-300'}`}
            placeholder="Enter project description..."
            required
          />
          <div className="flex justify-between mt-1">
            {errors.description && <p className="text-red-500 text-xs">{errors.description}</p>}
            <p className="text-xs text-gray-500 ml-auto">{data.description.length}/1000 characters</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Step 2: Team Structure
const Step2TeamStructure = ({ structure, onChange, onAdd, onRemove, onRoleChange, errors }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Team Structure Requirements</h3>
        <button
          onClick={onAdd}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
        >
          + Add Role
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Required Count</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Utilization (%)</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {structure.map((item, index) => (
              <tr key={index}>
                <td className="px-4 py-3">
                  <select
                    value={item.role_name}
                    onChange={(e) => onRoleChange(index, 'role_name', e.target.value)}
                    className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_role`] ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Select Role</option>
                    {ROLE_OPTIONS.map(role => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                  {errors[`${index}_role`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`${index}_role`]}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    min="1"
                    value={item.required_count}
                    onChange={(e) => onRoleChange(index, 'required_count', parseInt(e.target.value) || 1)}
                    className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_count`] ? 'border-red-500' : 'border-gray-300'}`}
                  />
                  {errors[`${index}_count`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`${index}_count`]}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={item.utilization_percentage}
                    onChange={(e) => onRoleChange(index, 'utilization_percentage', parseInt(e.target.value) || 0)}
                    className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_utilization`] ? 'border-red-500' : 'border-gray-300'}`}
                  />
                  {errors[`${index}_utilization`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`${index}_utilization`]}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  {structure.length > 1 && (
                    <button
                      onClick={() => onRemove(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Step 3: Team Allotment
const Step3TeamAllotment = ({ allotment, employees, onChange, onAllotmentChange, getEmployeesForRole, errors, aiSuggestions, loadingSuggestions }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Assign Resources to Roles</h3>
      
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
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation %</th>
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

// Step 4: Review
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
              <th className="px-4 py-2 text-left">Allocation %</th>
              <th className="px-4 py-2 text-left">Billable %</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {teamAllotment.map((item, i) => (
              <tr key={i}>
                <td className="px-4 py-2">{item.role_name}</td>
                <td className="px-4 py-2">{getEmployeeName(item.employee_id)}</td>
                <td className="px-4 py-2">{item.allocation_percentage}%</td>
                <td className="px-4 py-2">{item.billable_percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ProjectWizard
