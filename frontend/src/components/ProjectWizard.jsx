import { useState, useEffect } from 'react'
import { X, ChevronRight, ChevronLeft, Check } from 'lucide-react'
import { createProject, getEmployees, suggestTeam } from '../services/api'
import Step1ProjectDetails from './ProjectWizardSteps/Step1ProjectDetails'
import Step2TeamStructure from './ProjectWizardSteps/Step2TeamStructure'
import Step3TeamAllotment from './ProjectWizardSteps/Step3TeamAllotment'
import Step4Review from './ProjectWizardSteps/Step4Review'

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
  const [teamAllotment, setTeamAllotment] = useState([]) // [{ role_name, employee_id, allocation_percentage, internal_allocation_percentage, billable_percentage, billing_rate, start_date, end_date }]
  const [allotmentErrors, setAllotmentErrors] = useState({})
  const [aiSuggestions, setAiSuggestions] = useState(null) // { suggestions, insights, benefits }
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  
  useEffect(() => {
    if (isOpen) {
      loadEmployees()
    }
  }, [isOpen])
  
  useEffect(() => {
    // Generate empty team allotment rows based on team structure (no AI auto-population)
    if (currentStep === 3 && teamStructure.length > 0) {
      // Only generate if teamAllotment is empty
      if (teamAllotment.length === 0) {
        const allotmentRows = []
        teamStructure.forEach(structure => {
          for (let i = 0; i < structure.required_count; i++) {
            allotmentRows.push({
              role_name: structure.role_name,
              employee_id: '',
              allocation_percentage: structure.utilization_percentage,
              internal_allocation_percentage: structure.utilization_percentage,
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
    
    // Clear AI suggestions when leaving step 3
    if (currentStep !== 3) {
      setAiSuggestions(null)
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
              internal_allocation_percentage: sug.internal_allocation_percentage || sug.allocation_percentage,
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
              internal_allocation_percentage: structure.utilization_percentage,
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
      console.error('Error details:', error.response?.data || error.message)
      // Show user-friendly error message
      if (error.response?.data?.error) {
        alert(`Failed to generate AI suggestions: ${error.response.data.error}`)
      } else {
        alert('Failed to generate AI suggestions. Please check the console for details.')
      }
      // Fallback to empty rows
      const allotmentRows = []
      teamStructure.forEach(structure => {
        for (let i = 0; i < structure.required_count; i++) {
          allotmentRows.push({
            role_name: structure.role_name,
            employee_id: '',
            allocation_percentage: structure.utilization_percentage,
            internal_allocation_percentage: structure.utilization_percentage,
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
    setAiSuggestions(null)
    setLoadingSuggestions(false)
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
    setStep1Errors(errors)
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
          internal_allocation_percentage: parseInt(a.internal_allocation_percentage !== undefined ? a.internal_allocation_percentage : a.allocation_percentage),
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
              aiSuggestions={aiSuggestions}
              loadingSuggestions={loadingSuggestions}
              onGenerateSuggestions={generateAISuggestions}
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


export default ProjectWizard
