import { useState } from 'react'

const INDUSTRY_DOMAINS = ['FinTech', 'Healthcare', 'Retail', 'Manufacturing', 'Telecom', 'Education', 'Other']
const PROJECT_TYPES = ['Fixed_Price', 'T&M', 'Retainer']
const CURRENCIES = ['INR', 'USD', 'EUR']
const STATUS_OPTIONS = ['PIPELINE', 'ACTIVE', 'ON_HOLD', 'CLOSED', 'CANCELLED']

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
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
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

export default Step1ProjectDetails
