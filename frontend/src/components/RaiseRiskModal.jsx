import { useState, useEffect } from 'react'
import { X, Save, AlertTriangle } from 'lucide-react'
import { raiseEmployeeRisk, getEmployees } from '../services/api'

const RaiseRiskModal = ({ isOpen, onClose, employee, onSuccess }) => {
  const [formData, setFormData] = useState({
    project_id: '',
    risk_type: 'NOTICE_PERIOD',
    severity: 'MEDIUM',
    description: '',
    mitigation_plan: '',
    mitigation_owner_emp_id: '',
    target_resolution_date: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [employees, setEmployees] = useState([])
  const [projects, setProjects] = useState([])

  useEffect(() => {
    if (isOpen) {
      // Load employees for mitigation owner dropdown
      loadEmployees()
      // Load projects if needed
      // For now, we'll leave projects empty or load from employee's current allocation
      if (employee?.current_allocation?.project_id) {
        setFormData(prev => ({
          ...prev,
          project_id: employee.current_allocation.project_id.toString()
        }))
      }
    }
  }, [isOpen, employee])

  const loadEmployees = async () => {
    try {
      const data = await getEmployees({})
      setEmployees(data.employees || [])
    } catch (err) {
      console.error('Failed to load employees:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const submitData = {
        ...formData,
        project_id: formData.project_id ? parseInt(formData.project_id) : null,
        mitigation_owner_emp_id: formData.mitigation_owner_emp_id ? parseInt(formData.mitigation_owner_emp_id) : null,
        target_resolution_date: formData.target_resolution_date || null
      }
      
      await raiseEmployeeRisk(employee.id, submitData)
      onSuccess()
      onClose()
      // Reset form
      setFormData({
        project_id: '',
        risk_type: 'NOTICE_PERIOD',
        severity: 'MEDIUM',
        description: '',
        mitigation_plan: '',
        mitigation_owner_emp_id: '',
        target_resolution_date: ''
      })
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to raise risk')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'LOW': return 'text-green-600 bg-green-50'
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50'
      case 'HIGH': return 'text-orange-600 bg-orange-50'
      case 'CRITICAL': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-primary flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-red-500" />
            Raise Risk - {employee?.first_name} {employee?.last_name}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risk Type *
              </label>
              <select
                name="risk_type"
                value={formData.risk_type}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="NOTICE_PERIOD">Notice Period</option>
                <option value="CRITICAL_ROLE">Critical Role</option>
                <option value="SINGLE_POINT_FAILURE">Single Point of Failure</option>
                <option value="SKILL_GAP">Skill Gap</option>
                <option value="PERFORMANCE">Performance Issue</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Severity *
              </label>
              <select
                name="severity"
                value={formData.severity}
                onChange={handleChange}
                required
                className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${getSeverityColor(formData.severity)}`}
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description *
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows={4}
              placeholder="Describe the risk in detail..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mitigation Plan (Optional)
            </label>
            <textarea
              name="mitigation_plan"
              value={formData.mitigation_plan}
              onChange={handleChange}
              rows={3}
              placeholder="Describe the plan to mitigate this risk..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mitigation Owner (Optional)
              </label>
              <select
                name="mitigation_owner_emp_id"
                value={formData.mitigation_owner_emp_id}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="">Select owner...</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>
                    {emp.first_name} {emp.last_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Resolution Date (Optional)
              </label>
              <input
                type="date"
                name="target_resolution_date"
                value={formData.target_resolution_date}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {employee?.current_allocation && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                <strong>Current Project:</strong> {employee.current_allocation.project_name} 
                {employee.current_allocation.client_name && ` (${employee.current_allocation.client_name})`}
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              {loading ? 'Raising...' : 'Raise Risk'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RaiseRiskModal
