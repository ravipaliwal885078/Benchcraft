import { useState, useEffect } from 'react'
import { createEmployee, updateEmployee } from '../services/api'
import { X, Save, User, Mail, MapPin, DollarSign, Calendar } from 'lucide-react'

const EmployeeModal = ({ isOpen, onClose, employee, onSuccess }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role_level: 'JR',
    ctc_monthly: '',
    currency: 'USD',
    base_location: '',
    visa_status: '',
    remote_pref: false,
    status: 'BENCH',
    joined_date: new Date().toISOString().split('T')[0],
    bio_summary: '',
    skills: []
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (employee) {
      setFormData({
        first_name: employee.first_name || '',
        last_name: employee.last_name || '',
        email: employee.email || '',
        role_level: employee.role_level || 'JR',
        ctc_monthly: employee.ctc_monthly || '',
        currency: employee.currency || 'USD',
        base_location: employee.base_location || '',
        visa_status: employee.visa_status || '',
        remote_pref: employee.remote_pref || false,
        status: employee.status || 'BENCH',
        joined_date: employee.joined_date || new Date().toISOString().split('T')[0],
        bio_summary: employee.bio_summary || '',
        skills: employee.skills || []
      })
    } else {
      // Reset form for new employee
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        role_level: 'JR',
        ctc_monthly: '',
        currency: 'USD',
        base_location: '',
        visa_status: '',
        remote_pref: false,
        status: 'BENCH',
        joined_date: new Date().toISOString().split('T')[0],
        bio_summary: '',
        skills: []
      })
    }
    setErrors({})
  }, [employee, isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})

    try {
      const submitData = {
        ...formData,
        ctc_monthly: parseFloat(formData.ctc_monthly) || 0
      }

      if (employee) {
        await updateEmployee(employee.id, submitData)
      } else {
        await createEmployee(submitData)
      }

      onSuccess()
      onClose()
    } catch (error) {
      console.error('Failed to save employee:', error)
      if (error.response?.data?.error) {
        setErrors({ general: error.response.data.error })
      } else {
        setErrors({ general: 'Failed to save employee. Please try again.' })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-primary">
            {employee ? 'Edit Employee' : 'Add Employee'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {errors.general && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{errors.general}</p>
            </div>
          )}

          {/* Personal Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="w-5 h-5 mr-2" />
              Personal Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
                  <Mail className="w-4 h-4 mr-1" />
                  Email *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Professional Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="w-5 h-5 mr-2" />
              Professional Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role Level *
                </label>
                <select
                  name="role_level"
                  value={formData.role_level}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="JR">Junior</option>
                  <option value="MID">Mid</option>
                  <option value="SR">Senior</option>
                  <option value="LEAD">Lead</option>
                  <option value="PRINCIPAL">Principal</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status *
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="BENCH">Bench</option>
                  <option value="ALLOCATED">Allocated</option>
                  <option value="NOTICE_PERIOD">Notice Period</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly CTC *
                </label>
                <input
                  type="number"
                  name="ctc_monthly"
                  value={formData.ctc_monthly}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Currency
                </label>
                <select
                  name="currency"
                  value={formData.currency}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  Base Location
                </label>
                <input
                  type="text"
                  name="base_location"
                  value={formData.base_location}
                  onChange={handleChange}
                  placeholder="e.g., New York, NY"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Additional Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Visa Status
                </label>
                <input
                  type="text"
                  name="visa_status"
                  value={formData.visa_status}
                  onChange={handleChange}
                  placeholder="e.g., H1B, Green Card"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Joined Date
                </label>
                <input
                  type="date"
                  name="joined_date"
                  value={formData.joined_date}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div className="md:col-span-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="remote_pref"
                    checked={formData.remote_pref}
                    onChange={handleChange}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Open to remote work</span>
                </label>
              </div>
            </div>
          </div>

          {/* Bio Summary */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bio Summary
            </label>
            <textarea
              name="bio_summary"
              value={formData.bio_summary}
              onChange={handleChange}
              rows={4}
              placeholder="Brief professional summary and key strengths..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
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
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              {loading ? 'Saving...' : (employee ? 'Update Employee' : 'Create Employee')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EmployeeModal