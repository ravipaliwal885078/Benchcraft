import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProject } from '../services/api'
import {
  Building, Calendar, DollarSign, Users, TrendingUp,
  Star, MessageSquare, Target, Clock, Briefcase
} from 'lucide-react'

const ProjectView = () => {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProject()
  }, [id])

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
            ← Back to Pipeline
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
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2" />
          Team Members ({team.length})
        </h3>
        {team.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {team.map((member) => (
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
                  <p>⚡ {member.utilization}% utilization</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600 text-center py-8">No team members allocated yet.</p>
        )}
      </div>

      {/* Performance Feedback */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <MessageSquare className="w-5 h-5 mr-2" />
          Performance Feedback ({feedbacks.length})
        </h3>
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
    </div>
  )
}

export default ProjectView