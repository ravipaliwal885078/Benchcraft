import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getConsolidatedRisks } from '../services/api'
import { AlertTriangle, User, Building, Calendar, Target, CheckCircle, XCircle, Clock, Filter } from 'lucide-react'

const RiskCardView = () => {
  const [risks, setRisks] = useState({ project_risks: [], employee_risks: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterSeverity, setFilterSeverity] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [activeTab, setActiveTab] = useState('all') // 'all', 'projects', 'employees'

  useEffect(() => {
    loadRisks()
  }, [])

  const loadRisks = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getConsolidatedRisks()
      setRisks(data)
    } catch (err) {
      console.error('Failed to load risks:', err)
      setError(err.response?.data?.error || err.message || 'Failed to load risks')
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'LOW':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'OPEN':
        return 'bg-red-50 text-red-700 border-red-200'
      case 'IN_PROGRESS':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200'
      case 'RESOLVED':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'CLOSED':
        return 'bg-gray-50 text-gray-700 border-gray-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getStatusIcon = (status) => {
    switch (status?.toUpperCase()) {
      case 'OPEN':
        return <XCircle className="w-4 h-4" />
      case 'IN_PROGRESS':
        return <Clock className="w-4 h-4" />
      case 'RESOLVED':
      case 'CLOSED':
        return <CheckCircle className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  // Filter risks
  const filterRisks = (riskList) => {
    return riskList.filter(risk => {
      if (filterSeverity !== 'all' && risk.severity?.toUpperCase() !== filterSeverity.toUpperCase()) {
        return false
      }
      if (filterType !== 'all' && risk.risk_type?.toUpperCase() !== filterType.toUpperCase()) {
        return false
      }
      if (filterStatus !== 'all' && risk.status?.toUpperCase() !== filterStatus.toUpperCase()) {
        return false
      }
      return true
    })
  }

  const allRisks = [
    ...risks.project_risks.map(r => ({ ...r, risk_category: 'project' })),
    ...risks.employee_risks.map(r => ({ ...r, risk_category: 'employee' }))
  ]

  const filteredRisks = filterRisks(allRisks)
  
  const projectRisks = filterRisks(risks.project_risks)
  const employeeRisks = filterRisks(risks.employee_risks)

  const displayRisks = activeTab === 'all' ? filteredRisks : 
                       activeTab === 'projects' ? projectRisks : 
                       employeeRisks

  // Get unique filter options
  const severityOptions = ['all', ...new Set(allRisks.map(r => r.severity?.toUpperCase()).filter(Boolean))]
  const typeOptions = ['all', ...new Set(allRisks.map(r => r.risk_type?.toUpperCase()).filter(Boolean))]
  const statusOptions = ['all', ...new Set(allRisks.map(r => r.status?.toUpperCase()).filter(Boolean))]

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="mt-2 text-gray-600">Loading risks...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-800">{error}</p>
        <button
          onClick={loadRisks}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      {risks.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical</p>
                <p className="text-2xl font-bold text-red-600">{risks.summary.critical || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High</p>
                <p className="text-2xl font-bold text-orange-600">{risks.summary.high || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Medium</p>
                <p className="text-2xl font-bold text-yellow-600">{risks.summary.medium || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-500" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Low</p>
                <p className="text-2xl font-bold text-blue-600">{risks.summary.low || 0}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-blue-500" />
            </div>
          </div>
        </div>
      )}

      {/* Filters and Tabs */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4 mb-4">
          {/* Tabs */}
          <div className="flex gap-2 border-b">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'all'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              All Risks ({filteredRisks.length})
            </button>
            <button
              onClick={() => setActiveTab('projects')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'projects'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Project Risks ({projectRisks.length})
            </button>
            <button
              onClick={() => setActiveTab('employees')}
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'employees'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Employee Risks ({employeeRisks.length})
            </button>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Filter className="w-4 h-4 inline mr-1" />
              Severity
            </label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Severities</option>
              {severityOptions.filter(s => s !== 'all').map(sev => (
                <option key={sev} value={sev}>{sev}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Risk Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Types</option>
              {typeOptions.filter(t => t !== 'all').map(type => (
                <option key={type} value={type}>{type.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Statuses</option>
              {statusOptions.filter(s => s !== 'all').map(status => (
                <option key={status} value={status}>{status.replace('_', ' ')}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Risk Cards */}
      {displayRisks.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">No risks found</p>
          <p className="text-gray-500 text-sm mt-2">Try adjusting your filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayRisks.map((risk) => (
            <div
              key={risk.risk_id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border-l-4"
              style={{
                borderLeftColor: risk.severity === 'CRITICAL' ? '#ef4444' :
                                risk.severity === 'HIGH' ? '#f97316' :
                                risk.severity === 'MEDIUM' ? '#eab308' : '#3b82f6'
              }}
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(risk.severity)}`}>
                      {risk.severity}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(risk.status)} flex items-center gap-1`}>
                      {getStatusIcon(risk.status)}
                      {risk.status?.replace('_', ' ')}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                    {risk.risk_type?.replace('_', ' ')}
                  </h3>
                </div>
                <AlertTriangle className={`w-6 h-6 ${
                  risk.severity === 'CRITICAL' ? 'text-red-500' :
                  risk.severity === 'HIGH' ? 'text-orange-500' :
                  risk.severity === 'MEDIUM' ? 'text-yellow-500' : 'text-blue-500'
                }`} />
              </div>

              {/* Description */}
              {risk.description && (
                <p className="text-sm text-gray-700 mb-4 line-clamp-3">{risk.description}</p>
              )}

              {/* Project/Employee Links */}
              <div className="space-y-2 mb-4">
                {risk.project_id && risk.project_name && (
                  <div className="flex items-center gap-2 p-2 bg-blue-50 rounded">
                    <Building className="w-4 h-4 text-blue-600" />
                    <div className="flex-1">
                      <span className="text-xs text-gray-600">Project: </span>
                      <Link
                        to={`/projects/${risk.project_id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {risk.project_name}
                      </Link>
                      {risk.client_name && (
                        <p className="text-xs text-gray-500 mt-0.5">{risk.client_name}</p>
                      )}
                    </div>
                  </div>
                )}
                {risk.employee_id && risk.employee_name && (
                  <div className="flex items-center gap-2 p-2 bg-green-50 rounded">
                    <User className="w-4 h-4 text-green-600" />
                    <div className="flex-1">
                      <span className="text-xs text-gray-600">Employee: </span>
                      <Link
                        to={`/employees/${risk.employee_id}`}
                        className="text-sm font-medium text-green-600 hover:text-green-800 hover:underline"
                      >
                        {risk.employee_name}
                      </Link>
                    </div>
                  </div>
                )}
              </div>

              {/* Mitigation Plan */}
              {risk.mitigation_plan && (
                <div className="mb-4 p-3 bg-yellow-50 rounded border border-yellow-200">
                  <div className="flex items-center gap-2 mb-1">
                    <Target className="w-4 h-4 text-yellow-700" />
                    <span className="text-xs font-semibold text-yellow-800">Mitigation Plan</span>
                  </div>
                  <p className="text-xs text-yellow-900 line-clamp-2">{risk.mitigation_plan}</p>
                </div>
              )}

              {/* Dates */}
              <div className="flex items-center gap-4 text-xs text-gray-500 pt-4 border-t">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>Identified: {formatDate(risk.identified_date)}</span>
                </div>
                {risk.target_resolution_date && (
                  <div className="flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    <span>Target: {formatDate(risk.target_resolution_date)}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RiskCardView
