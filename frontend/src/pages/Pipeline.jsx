import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, FileText, DollarSign, Calendar, Edit, Users, X } from 'lucide-react'
import { getProjects, createProject, updateProject, updateProjectTeam, getProject, getEmployees, removeTeamMember, checkEmployeeAllocation } from '../services/api'

const Pipeline = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [showUpdateModal, setShowUpdateModal] = useState(false)
  const [showTeamModal, setShowTeamModal] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
  const [teamMembers, setTeamMembers] = useState([])
  const [availableEmployees, setAvailableEmployees] = useState([])
  const [validationErrors, setValidationErrors] = useState({}) // { index: { message: string, isValidating: boolean } }
  const [formData, setFormData] = useState({
    client_name: '',
    project_name: '',
    description: '',
    budget_cap: '',
    start_date: '',
    end_date: '',
    status: 'PIPELINE',
    probability: 50,
    tech_stack: '',
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await getProjects()
      setProjects(data.projects || [])
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await createProject(formData)
      alert('Project created successfully!')
      setShowForm(false)
      setFormData({
        client_name: '',
        project_name: '',
        description: '',
        budget_cap: '',
        start_date: '',
        end_date: '',
        status: 'PIPELINE',
        probability: 50,
        tech_stack: '',
      })
      loadProjects()
    } catch (error) {
      console.error('Failed to create project:', error)
      alert('Failed to create project: ' + error.message)
    }
  }

  const handleUpdateProject = async (e) => {
    e.preventDefault()
    try {
      await updateProject(selectedProject.id, formData)
      alert('Project updated successfully!')
      setShowUpdateModal(false)
      setSelectedProject(null)
      loadProjects()
    } catch (error) {
      console.error('Failed to update project:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error'
      alert('Failed to update project: ' + errorMessage)
    }
  }

  const openUpdateModal = async (project) => {
    setSelectedProject(project)
    setFormData({
      client_name: project.client_name,
      project_name: project.project_name,
      description: project.description,
      budget_cap: project.budget_cap,
      start_date: project.start_date || '',
      end_date: project.end_date || '',
      status: project.status,
      probability: project.probability || 50,
      tech_stack: project.tech_stack || '',
    })
    setShowUpdateModal(true)
  }

  const openTeamModal = async (project) => {
    setSelectedProject(project)
    try {
      // Load project details with team
      const projectData = await getProject(project.id)
      setTeamMembers(projectData.team || [])
      
      // Load available employees
      const employeesData = await getEmployees()
      setAvailableEmployees(employeesData.employees || [])
      
      setShowTeamModal(true)
    } catch (error) {
      console.error('Failed to load project team:', error)
      alert('Failed to load project team: ' + error.message)
    }
  }

  const handleTeamUpdate = async () => {
    try {
      // Validate all team members before submission
      const errors = {}
      let hasErrors = false

      // Validate all members
      for (let i = 0; i < teamMembers.length; i++) {
        const member = teamMembers[i]
        if (!member.employee_id) {
          continue // Skip if employee not selected yet
        }

        const allocationPercentage = parseInt(member.allocation_percentage) || 100
        const startDate = member.start_date || new Date().toISOString().split('T')[0]
        const endDate = member.end_date || null

        // Validate range
        if (allocationPercentage < 0 || allocationPercentage > 100) {
          errors[i] = { message: 'Allocation percentage must be between 0 and 100%', isValidating: false }
          hasErrors = true
          continue
        }

        // Check with backend
        try {
          const checkResult = await checkEmployeeAllocation(member.employee_id, {
            allocation_percentage: allocationPercentage,
            start_date: startDate,
            end_date: endDate,
            exclude_allocation_id: member.id || null
          })

          if (!checkResult.is_valid) {
            errors[i] = { message: checkResult.error_message || `Total allocation would be ${checkResult.would_be_total}%. Maximum allowed is 100%.`, isValidating: false }
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
        billable_percentage: parseInt(member.billable_percentage) || 100,
        billing_rate: member.billing_rate || null
      }))
      
      await updateProjectTeam(selectedProject.id, allocations)
      alert('Project team updated successfully!')
      setShowTeamModal(false)
      setSelectedProject(null)
      setValidationErrors({})
      loadProjects()
    } catch (error) {
      console.error('Failed to update team:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error'
      alert('Failed to update team: ' + errorMessage)
    }
  }

  const handleRemoveTeamMember = async (allocationId) => {
    if (!confirm('Are you sure you want to remove this team member?')) return
    
    try {
      await removeTeamMember(selectedProject.id, allocationId)
      setTeamMembers(teamMembers.filter(m => m.id !== allocationId))
      loadProjects()
    } catch (error) {
      console.error('Failed to remove team member:', error)
      alert('Failed to remove team member: ' + error.message)
    }
  }

  const handleAddTeamMember = () => {
    setTeamMembers([...teamMembers, {
      employee_id: '',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      allocation_percentage: 100,
      billable_percentage: 100,
      billing_rate: null
    }])
  }

  const handleTeamMemberChange = (index, field, value) => {
    const updated = [...teamMembers]
    updated[index][field] = value
    setTeamMembers(updated)
    
    // Clear validation error for this field when user changes it
    if (field === 'allocation_percentage' || field === 'start_date' || field === 'end_date' || field === 'employee_id') {
      const newErrors = { ...validationErrors }
      delete newErrors[index]
      setValidationErrors(newErrors)
    }
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
      const allocationPercentage = parseInt(member.allocation_percentage) || 100
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

  if (loading) {
    return <div className="text-center py-12">Loading pipeline...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary">Projects</h1>
          <p className="text-muted-foreground mt-2">Manage active projects and pipeline</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Create Project / Lead</span>
        </button>
      </div>

      {/* Create Project Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Create Project / Lead</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.project_name}
                  onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Description / Scope * (Critical for Vectorization)
              </label>
              <textarea
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 h-32"
                placeholder="Describe the project requirements, tech stack, and scope..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget Cap *
                </label>
                <input
                  type="number"
                  required
                  value={formData.budget_cap}
                  onChange={(e) => setFormData({ ...formData, budget_cap: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Probability (0-100%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={formData.probability}
                  onChange={(e) => setFormData({ ...formData, probability: parseInt(e.target.value) })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="PIPELINE">Pipeline</option>
                  <option value="ACTIVE">Active</option>
                  <option value="CLOSED">Closed</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tech Stack (comma-separated)
              </label>
              <input
                type="text"
                value={formData.tech_stack}
                onChange={(e) => setFormData({ ...formData, tech_stack: e.target.value })}
                placeholder="e.g., React, Python, AWS"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                className="bg-primary text-white px-6 py-2 rounded-md hover:bg-primary-dark"
              >
                Create Project
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="border border-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Projects List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div key={project.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{project.client_name}</h3>
                <Link
                  to={`/projects/${project.id}`}
                  className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  {project.project_name}
                </Link>
              </div>
              <span className={`px-2 py-1 text-xs rounded ${
                project.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                project.status === 'PIPELINE' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {project.status}
              </span>
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-3">{project.description}</p>

            <div className="space-y-2">
              <div className="flex items-center text-sm text-gray-600">
                <DollarSign className="w-4 h-4 mr-2" />
                Budget: ${project.budget_cap?.toLocaleString()}
                {project.budget_consumed !== undefined && (
                  <span className="ml-2 text-gray-500">
                    (Consumed: ${project.budget_consumed?.toLocaleString()})
                  </span>
                )}
              </div>
              {project.probability > 0 && (
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">Probability:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full"
                      style={{ width: `${project.probability}%` }}
                    />
                  </div>
                  <span className="ml-2">{project.probability}%</span>
                </div>
              )}
              {project.tech_stack && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {project.tech_stack.split(',').map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                    >
                      {tech.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between">
              <Link
                to={`/projects/${project.id}`}
                className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
              >
                <FileText className="w-4 h-4 mr-1" />
                View Details
              </Link>
              <div className="flex space-x-2">
                <button
                  onClick={() => openUpdateModal(project)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
                  title="Update Project"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => openTeamModal(project)}
                  className="text-green-600 hover:text-green-800 text-sm font-medium flex items-center"
                  title="Manage Team"
                >
                  <Users className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No projects in pipeline. Create your first project to get started.
        </div>
      )}

      {/* Update Project Modal */}
      {showUpdateModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Update Project</h2>
              <button
                onClick={() => {
                  setShowUpdateModal(false)
                  setSelectedProject(null)
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleUpdateProject} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Client Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.client_name}
                    onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.project_name}
                    onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description *
                </label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 h-32"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Budget Cap *
                  </label>
                  <input
                    type="number"
                    required
                    value={formData.budget_cap}
                    onChange={(e) => setFormData({ ...formData, budget_cap: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Probability (0-100%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.probability}
                    onChange={(e) => setFormData({ ...formData, probability: parseInt(e.target.value) })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="PIPELINE">Pipeline</option>
                    <option value="ACTIVE">Active</option>
                    <option value="CLOSED">Closed</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tech Stack (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.tech_stack}
                  onChange={(e) => setFormData({ ...formData, tech_stack: e.target.value })}
                  placeholder="e.g., React, Python, AWS"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="bg-primary text-white px-6 py-2 rounded-md hover:bg-primary-dark"
                >
                  Update Project
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowUpdateModal(false)
                    setSelectedProject(null)
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
      {showTeamModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-5xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Manage Team - {selectedProject.project_name}
              </h2>
              <button
                onClick={() => {
                  setShowTeamModal(false)
                  setSelectedProject(null)
                  setTeamMembers([])
                  setValidationErrors({})
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

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
                      Allocation %
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Billable %
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Billing Rate
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {teamMembers.map((member, index) => {
                    const employee = availableEmployees.find(e => e.id === member.employee_id)
                    return (
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
                          <input
                            type="date"
                            value={member.start_date || ''}
                            onChange={(e) => handleTeamMemberChange(index, 'start_date', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                          />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <input
                            type="date"
                            value={member.end_date || ''}
                            onChange={(e) => handleTeamMemberChange(index, 'end_date', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                          />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div>
                            <input
                              type="number"
                              min="0"
                              max="100"
                              value={member.allocation_percentage || 100}
                              onChange={(e) => handleTeamMemberChange(index, 'allocation_percentage', e.target.value)}
                              onBlur={() => validateTeamMember(index)}
                              className={`w-full border rounded-md px-2 py-1 text-sm w-20 ${
                                validationErrors[index] 
                                  ? 'border-red-500 bg-red-50' 
                                  : 'border-gray-300'
                              }`}
                            />
                            {validationErrors[index] && (
                              <div className="mt-1 text-xs text-red-600 max-w-48">
                                {validationErrors[index].isValidating ? (
                                  <span className="text-blue-600">Validating...</span>
                                ) : (
                                  <span>{validationErrors[index].message}</span>
                                )}
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
                        <td className="px-4 py-3 whitespace-nowrap text-sm font-medium">
                          {member.id && (
                            <button
                              onClick={() => handleRemoveTeamMember(member.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Remove
                            </button>
                          )}
                        </td>
                      </tr>
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
                className={`px-6 py-2 rounded-md ${
                  Object.keys(validationErrors).length > 0
                    ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    : 'bg-primary text-white hover:bg-primary-dark'
                }`}
              >
                Save Changes
                {Object.keys(validationErrors).length > 0 && (
                  <span className="ml-2 text-xs">({Object.keys(validationErrors).length} error{Object.keys(validationErrors).length > 1 ? 's' : ''})</span>
                )}
              </button>
              <button
                onClick={() => {
                  setShowTeamModal(false)
                  setSelectedProject(null)
                  setTeamMembers([])
                  setValidationErrors({})
                }}
                className="border border-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Pipeline
