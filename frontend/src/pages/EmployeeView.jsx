import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEmployee, getEmployeeAvailability } from '../services/api'
import {
  User, MapPin, Calendar, DollarSign, Briefcase, Star,
  TrendingUp, Clock, Award, MessageSquare, Target, Users
} from 'lucide-react'

const EmployeeView = () => {
  const { id } = useParams()
  const [employee, setEmployee] = useState(null)
  const [availability, setAvailability] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadEmployeeData()
  }, [id])

  const loadEmployeeData = async () => {
    try {
      const [empData, availData] = await Promise.all([
        getEmployee(id),
        getEmployeeAvailability(id)
      ])
      setEmployee(empData)
      setAvailability(availData.availability_timeline)
    } catch (error) {
      console.error('Failed to load employee data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'allocated': return 'bg-success/10 text-success'
      case 'bench': return 'bg-warning/10 text-warning'
      case 'notice_period': return 'bg-destructive/10 text-destructive'
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

  const getProficiencyColor = (proficiency) => {
    if (proficiency >= 4) return 'bg-success'
    if (proficiency >= 3) return 'bg-warning'
    if (proficiency >= 2) return 'bg-accent'
    return 'bg-destructive'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Present'
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">Loading employee profile...</div>
  }

  if (!employee) {
    return <div className="text-center py-12 text-destructive">Employee not found</div>
  }

  const emp = employee.employee
  const currentAlloc = employee.current_allocation

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${getRoleColor(emp.role_level)}`}>
              {emp.first_name[0]}{emp.last_name[0]}
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {emp.first_name} {emp.last_name}
              </h1>
              <p className="text-gray-600 flex items-center mt-1">
                <Briefcase className="w-4 h-4 mr-2" />
                {emp.role_level} • {emp.email}
              </p>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(emp.status)}`}>
                  {emp.status?.replace('_', ' ')}
                </span>
                {emp.base_location && (
                  <span className="text-sm text-gray-600 flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    {emp.base_location}
                  </span>
                )}
                {emp.joined_date && (
                  <span className="text-sm text-gray-600 flex items-center">
                    <Calendar className="w-4 h-4 mr-1" />
                    Joined {formatDate(emp.joined_date)}
                  </span>
                )}
              </div>
            </div>
          </div>
          <Link
            to="/employees"
            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
          >
            ← Back to Employees
          </Link>
        </div>
      </div>

      {/* Current Allocation Banner */}
      {currentAlloc && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="w-5 h-5 text-green-600 mr-3" />
            <div>
              <h3 className="font-semibold text-green-800">Currently Allocated</h3>
              <p className="text-green-700">
                {currentAlloc.project_name} • Started {formatDate(currentAlloc.start_date)}
                {currentAlloc.billing_rate && ` • $${currentAlloc.billing_rate}/hr`}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {[
              { id: 'overview', label: 'Overview', icon: User },
              { id: 'skills', label: 'Skills Matrix', icon: Award },
              { id: 'timeline', label: 'Availability Timeline', icon: Clock },
              { id: 'history', label: 'Project History', icon: Briefcase },
              { id: 'feedback', label: 'Performance Feedback', icon: MessageSquare }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Full Name:</span>
                    <span className="font-medium">{emp.first_name} {emp.last_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Email:</span>
                    <span className="font-medium">{emp.email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Role Level:</span>
                    <span className="font-medium">{emp.role_level}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly CTC:</span>
                    <span className="font-medium">${emp.ctc_monthly?.toLocaleString()} {emp.currency}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Location:</span>
                    <span className="font-medium">{emp.base_location || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Visa Status:</span>
                    <span className="font-medium">{emp.visa_status || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Remote Preference:</span>
                    <span className="font-medium">{emp.remote_pref ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Bio Summary</h3>
                <p className="text-gray-700 leading-relaxed">
                  {emp.bio_summary || 'No bio summary available.'}
                </p>
              </div>
            </div>
          )}

          {/* Skills Matrix Tab */}
          {activeTab === 'skills' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills & Proficiency</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {employee.skills.map((skill) => (
                  <div key={skill.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{skill.skill_name}</h4>
                      <div className="flex items-center">
                        <div className="flex space-x-1 mr-2">
                          {[1, 2, 3, 4, 5].map((level) => (
                            <div
                              key={level}
                              className={`w-2 h-2 rounded-full ${
                                level <= skill.proficiency ? getProficiencyColor(skill.proficiency) : 'bg-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm font-medium">{skill.proficiency}/5</span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">
                      Last used: {formatDate(skill.last_used)}
                      {skill.is_verified && <span className="ml-2 text-green-600">✓ Verified</span>}
                    </div>
                  </div>
                ))}
              </div>
              {employee.skills.length === 0 && (
                <p className="text-gray-600 text-center py-8">No skills recorded for this employee.</p>
              )}
            </div>
          )}

          {/* Availability Timeline Tab */}
          {activeTab === 'timeline' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Availability Timeline</h3>
              <div className="space-y-4">
                {availability.map((period, index) => (
                  <div key={index} className="flex items-center space-x-4 bg-gray-50 rounded-lg p-4">
                    <div className={`w-4 h-4 rounded-full ${
                      period.type === 'allocated' ? 'bg-green-500' : 'bg-yellow-500'
                    }`} />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">
                          {period.type === 'allocated' ? period.project_name : 'Bench Period'}
                        </h4>
                        <span className="text-sm text-gray-600">
                          {formatDate(period.start_date)} - {formatDate(period.end_date)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {period.type === 'allocated'
                          ? `${period.client_name} • ${period.utilization}% utilization`
                          : period.reason || 'Unspecified reason'
                        }
                      </p>
                      {period.cost_incurred && (
                        <p className="text-sm text-red-600 mt-1">
                          Cost incurred: ${period.cost_incurred?.toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {availability.length === 0 && (
                <p className="text-gray-600 text-center py-8">No timeline data available.</p>
              )}
            </div>
          )}

          {/* Project History Tab */}
          {activeTab === 'history' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Allocation History</h3>
              <div className="space-y-4">
                {employee.allocations.map((alloc) => (
                  <div key={alloc.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Link
                        to={`/projects/${alloc.project_id}`}
                        className="font-medium text-indigo-600 hover:text-indigo-800"
                      >
                        {alloc.project_name}
                      </Link>
                      <span className="text-sm text-gray-600">
                        {formatDate(alloc.start_date)} - {formatDate(alloc.end_date)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{alloc.client_name}</p>
                    <div className="flex items-center space-x-4 text-sm">
                      {alloc.billing_rate && (
                        <span className="text-green-600">💰 ${alloc.billing_rate}/hr</span>
                      )}
                      <span className="text-blue-600">📊 {alloc.utilization}% utilization</span>
                    </div>
                  </div>
                ))}
              </div>
              {employee.allocations.length === 0 && (
                <p className="text-gray-600 text-center py-8">No project history available.</p>
              )}
            </div>
          )}

          {/* Performance Feedback Tab */}
          {activeTab === 'feedback' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Feedback</h3>
              <div className="space-y-4">
                {employee.feedbacks.map((feedback) => (
                  <div key={feedback.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Link
                        to={`/projects/${feedback.project_id}`}
                        className="font-medium text-indigo-600 hover:text-indigo-800"
                      >
                        {feedback.project_name}
                      </Link>
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
              {employee.feedbacks.length === 0 && (
                <p className="text-gray-600 text-center py-8">No feedback available.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default EmployeeView