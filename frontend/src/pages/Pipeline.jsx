import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, FileText, DollarSign, Calendar, Edit, Users, X } from 'lucide-react'
import { getProjects, createProject, updateProject } from '../services/api'
import ProjectWizard from '../components/ProjectWizard'
import ManageTeamModal from '../components/ManageTeamModal'
import PageHeader from '../components/PageHeader'

const Pipeline = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showWizard, setShowWizard] = useState(false)
  const [showUpdateModal, setShowUpdateModal] = useState(false)
  const [showTeamModal, setShowTeamModal] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
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

  const openTeamModal = (project) => {
    setSelectedProject(project)
    setShowTeamModal(true)
  }


  if (loading) {
    return <div className="text-center py-12">Loading pipeline...</div>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Projects"
        subtitle="Manage active projects and pipeline"
        actions={
          <button
            onClick={() => setShowWizard(true)}
            className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Create Project</span>
          </button>
        }
      />

      {/* Project Wizard Modal */}
      <ProjectWizard
        isOpen={showWizard}
        onClose={() => setShowWizard(false)}
        onSuccess={(project) => {
          loadProjects()
        }}
      />

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
      <ManageTeamModal
        projectId={selectedProject?.id}
        projectName={selectedProject?.project_name || 'Project'}
        isOpen={showTeamModal && selectedProject !== null}
        onClose={() => {
          setShowTeamModal(false)
          setSelectedProject(null)
        }}
        onSuccess={loadProjects}
      />
    </div>
  )
}

export default Pipeline
