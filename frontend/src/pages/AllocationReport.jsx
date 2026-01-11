import { useEffect, useState } from 'react'
import { getAllocationReport } from '../services/api'
import Pagination from '../components/Pagination'

const AllocationReport = () => {
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [forecastDays, setForecastDays] = useState(30)
  const [includeBench, setIncludeBench] = useState(true)
  const [filterStatus, setFilterStatus] = useState('all')
  const [sortBy, setSortBy] = useState('priority')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10 // Grid/Table format

  useEffect(() => {
    loadReport()
  }, [forecastDays, includeBench])

  const loadReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getAllocationReport(forecastDays, includeBench)
      setReportData(data)
    } catch (error) {
      console.error('Failed to load allocation report:', error)
      console.error('Error response:', error.response?.data)
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Failed to load allocation report'
      const errorType = error.response?.data?.error_type || ''
      setError(`${errorMessage}${errorType ? ` (${errorType})` : ''}`)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount, currency = 'USD') => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount)
  }

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'ALLOCATED':
        return 'bg-green-100 text-green-800'
      case 'BENCH':
        return 'bg-yellow-100 text-yellow-800'
      case 'NOTICE_PERIOD':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityBadgeColor = (tier) => {
    switch (tier) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800'
      case 'HIGH':
        return 'bg-orange-100 text-orange-800'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800'
      case 'LOW':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getMarginColor = (margin) => {
    if (margin >= 50) return 'text-green-600 font-semibold'
    if (margin >= 30) return 'text-yellow-600'
    return 'text-red-600'
  }

  const filteredEmployees = reportData?.employees?.filter(emp => {
    if (filterStatus === 'all') return true
    if (filterStatus === 'available') return emp.availability.will_be_available_in_forecast
    if (filterStatus === 'allocated') return emp.current_project.project_name
    if (filterStatus === 'bench') return emp.status === 'BENCH'
    return true
  }) || []

  const sortedEmployees = [...filteredEmployees].sort((a, b) => {
    if (sortBy === 'priority') {
      const scoreA = a.priority.priority_score || 0
      const scoreB = b.priority.priority_score || 0
      return scoreB - scoreA
    }
    if (sortBy === 'margin') {
      const marginA = a.financials.gross_margin_percentage || 0
      const marginB = b.financials.gross_margin_percentage || 0
      return marginB - marginA
    }
    if (sortBy === 'profit') {
      const profitA = a.financials.gross_profit_per_hour || 0
      const profitB = b.financials.gross_profit_per_hour || 0
      return profitB - profitA
    }
    if (sortBy === 'rate') {
      const rateA = a.financials.current_hourly_rate || 0
      const rateB = b.financials.current_hourly_rate || 0
      return rateB - rateA
    }
    return 0
  })

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="mt-2 text-gray-600">Loading allocation report...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-2xl mx-auto">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Report</h2>
          <p className="text-red-600 mb-4">{error}</p>
          {error.includes('table') || error.includes('Table') || error.includes('database') ? (
            <div className="mt-4">
              <p className="text-sm text-gray-700 mb-2">The database tables may need to be initialized.</p>
              <button
                onClick={async () => {
                  try {
                    const response = await fetch('/api/v1/hr/init-db', { method: 'POST' })
                    const data = await response.json()
                    if (response.ok) {
                      alert('Database initialized successfully! Please refresh the page.')
                      loadReport()
                    } else {
                      alert(`Error: ${data.error || 'Failed to initialize database'}`)
                    }
                  } catch (err) {
                    alert(`Error: ${err.message}`)
                  }
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Initialize Database Tables
              </button>
            </div>
          ) : (
            <button
              onClick={loadReport}
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    )
  }

  if (!reportData) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="mt-2 text-gray-600">Loading allocation report...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Project Allocation Manager Report</h1>
          <p className="text-gray-600 mt-2">
            Employee profitability and availability insights for proactive planning
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Report Date: {new Date(reportData.report_date).toLocaleDateString()}</p>
          <p className="text-sm text-gray-500">Forecast Period: {reportData.forecast_days} days</p>
          <button
            onClick={loadReport}
            className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
          >
            Refresh Report
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Employees</p>
          <p className="text-2xl font-bold text-gray-900">{reportData.total_employees}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Currently Allocated</p>
          <p className="text-2xl font-bold text-green-600">{reportData.summary.total_allocated}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Available in Forecast</p>
          <p className="text-2xl font-bold text-blue-600">{reportData.summary.total_available_in_forecast}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Avg Gross Margin</p>
          <p className="text-2xl font-bold text-indigo-600">{reportData.summary.avg_gross_margin}%</p>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Forecast Days</label>
            <input
              type="number"
              min="7"
              max="90"
              value={forecastDays}
              onChange={(e) => setForecastDays(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Employees</option>
              <option value="allocated">Allocated</option>
              <option value="bench">On Bench</option>
              <option value="available">Available in Forecast</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="priority">Priority Score</option>
              <option value="margin">Gross Margin</option>
              <option value="profit">Gross Profit/Hour</option>
              <option value="rate">Hourly Rate</option>
            </select>
          </div>
          <div className="flex items-end">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeBench}
                onChange={(e) => setIncludeBench(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Include Bench Employees</span>
            </label>
          </div>
        </div>
      </div>

      {/* Employee Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Employee
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Project
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Allocation %
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Alignment Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hourly Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Gross Margin
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Monthly Profit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Availability
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedEmployees.map((employee) => (
                <tr key={employee.employee_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {employee.employee_name || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-500">{employee.email || 'N/A'}</div>
                      <div className="flex items-center gap-2 mt-1">
                        {employee.role_level && (
                          <span className="inline-flex px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700">
                            {employee.role_level}
                          </span>
                        )}
                        {employee.status && (
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeColor(employee.status)}`}>
                            {employee.status}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {employee.current_project?.project_name ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {employee.current_project.project_name}
                        </div>
                        {employee.current_project.client_name && (
                          <div className="text-sm text-gray-500">
                            {employee.current_project.client_name}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">Not allocated</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.current_project?.allocation_percentage || employee.current_project?.utilization_percentage ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {employee.current_project.allocation_percentage || employee.current_project.utilization_percentage || 100}%
                        </div>
                        {employee.current_project.billable_percentage && (
                          <div className="text-xs text-gray-500">
                            Billable: {employee.current_project.billable_percentage}%
                          </div>
                        )}
                        {(employee.current_project.allocation_percentage || employee.current_project.utilization_percentage || 100) !== (employee.current_project.billable_percentage || 100) && (
                          <div className="text-xs text-orange-600 mt-1">⚠️ Partial</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.current_project?.allocation_percentage || employee.current_project?.utilization_percentage ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {employee.current_project.allocation_percentage || employee.current_project.utilization_percentage || 100}%
                        </div>
                        {employee.current_project.billable_percentage && (
                          <div className="text-xs text-gray-500">
                            Billable: {employee.current_project.billable_percentage}%
                          </div>
                        )}
                        {(employee.current_project.allocation_percentage || employee.current_project.utilization_percentage || 100) !== (employee.current_project.billable_percentage || 100) && (
                          <div className="text-xs text-orange-600 mt-1">⚠️ Partial</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.current_project?.start_date ? (
                      <div>
                        <div className="text-sm text-gray-900">
                          {new Date(employee.current_project.start_date).toLocaleDateString()}
                        </div>
                        {employee.current_project.end_date ? (
                          <>
                            <div className="text-sm text-gray-500">
                              to {new Date(employee.current_project.end_date).toLocaleDateString()}
                            </div>
                            {employee.current_project.alignment_period_days && (
                              <div className="text-xs text-gray-400">
                                {employee.current_project.alignment_period_days} days
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-sm text-gray-500">Ongoing</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.financials?.current_hourly_rate ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {formatCurrency(employee.financials.current_hourly_rate, employee.currency || 'USD')}
                        </div>
                        {employee.financials.hourly_cost && (
                          <div className="text-xs text-gray-500">
                            Cost: {formatCurrency(employee.financials.hourly_cost, employee.currency || 'USD')}
                          </div>
                        )}
                        {employee.financials.rate_card_type && (
                          <div className="text-xs text-gray-400">
                            {employee.financials.rate_card_type}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">No rate card</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.financials?.gross_margin_percentage !== null && employee.financials?.gross_margin_percentage !== undefined ? (
                      <div>
                        <div className={`text-sm font-medium ${getMarginColor(employee.financials.gross_margin_percentage)}`}>
                          {employee.financials.gross_margin_percentage.toFixed(1)}%
                        </div>
                        {employee.financials.gross_profit_per_hour && (
                          <div className="text-xs text-gray-500">
                            {formatCurrency(employee.financials.gross_profit_per_hour, employee.currency || 'USD')}/hr
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.financials?.estimated_monthly_profit ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {formatCurrency(employee.financials.estimated_monthly_profit, employee.currency || 'USD')}
                        </div>
                        {employee.financials.estimated_monthly_revenue && (
                          <div className="text-xs text-gray-500">
                            Rev: {formatCurrency(employee.financials.estimated_monthly_revenue, employee.currency || 'USD')}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {employee.priority?.priority_score !== null && employee.priority?.priority_score !== undefined ? (
                      <div>
                        {employee.priority.priority_tier && (
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityBadgeColor(employee.priority.priority_tier)}`}>
                            {employee.priority.priority_tier}
                          </span>
                        )}
                        <div className="text-xs text-gray-500 mt-1">
                          Score: {employee.priority.priority_score?.toFixed(1) || 'N/A'}
                        </div>
                        {employee.priority.max_domain_rate_value && (
                          <div className="text-xs text-gray-400">
                            Max: {formatCurrency(employee.priority.max_domain_rate_value, employee.currency || 'USD')}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">Not calculated</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      {employee.availability?.next_available_date ? (
                        <div>
                          <div className="text-sm text-gray-900">
                            {new Date(employee.availability.next_available_date).toLocaleDateString()}
                          </div>
                          {employee.availability.will_be_available_in_forecast && (
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 mt-1">
                              Available
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">N/A</span>
                      )}
                      {employee.upcoming_allocations && employee.upcoming_allocations.length > 0 && (
                        <div className="text-xs text-gray-500 mt-1">
                          {employee.upcoming_allocations.length} upcoming
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {sortedEmployees.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No employees found matching the selected filters.
          </div>
        )}
      </div>
    </div>
  )
}

export default AllocationReport
