import { useEffect, useState } from 'react'
import { getComprehensiveDashboard } from '../services/api'
import ChatAgent from '../components/ChatAgent'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ComposedChart, Area, AreaChart
} from 'recharts'

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [timeFilter, setTimeFilter] = useState('6M')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getComprehensiveDashboard()
      setDashboardData(data)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to load dashboard data'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`
    }
    return `$${amount}`
  }

  const getPriorityBadgeClass = (tier) => {
    switch (tier) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800'
      case 'HIGH':
        return 'bg-orange-100 text-orange-800'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800'
      case 'LOW':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const COLORS = {
    blue: '#4299e1',
    green: '#48bb78',
    red: '#f56565',
    orange: '#ed8936',
    purple: '#9f7aea',
    teal: '#38b2ac',
    yellow: '#ecc94b',
    dark: '#2d3748'
  }

  const chartColors = [
    COLORS.blue, COLORS.green, COLORS.orange, COLORS.purple, COLORS.teal, COLORS.yellow
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !dashboardData) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-2xl mx-auto">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading Dashboard</h2>
          <p className="text-red-600 mb-4">{error || 'Failed to load dashboard data'}</p>
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const { kpis, trends, priority_queue, insights } = dashboardData

  // Filter priority queue by search term
  const filteredQueue = priority_queue.filter(emp =>
    emp.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.primary_domain.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gray-50 p-5">
      <div className="max-w-[1800px] mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-1">🎯 Resource Management Dashboard</h1>
            <p className="text-gray-600 text-sm">Real-time insights powered by AI • Last updated: {new Date(dashboardData.last_updated).toLocaleTimeString()}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="bg-gray-50 px-5 py-2 rounded-lg text-gray-700 text-sm font-medium border border-gray-200">
              📅 {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </div>
            <button
              onClick={loadDashboardData}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold text-sm hover:bg-blue-700 transition shadow-md hover:shadow-lg"
            >
              ↻ Refresh Data
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-5">
          <div className="bg-white rounded-2xl shadow-sm border-l-4 border-l-red-500 p-6 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Bench Resources</div>
              </div>
              <div className="w-11 h-11 bg-red-50 rounded-xl flex items-center justify-center text-2xl">👥</div>
            </div>
            <div className="text-4xl font-bold text-gray-900 mb-2">{kpis.bench_resources}</div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-red-600 font-semibold">↓ 25%</span>
              <span className="text-gray-500">vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border-l-4 border-l-green-500 p-6 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Utilization Rate</div>
              </div>
              <div className="w-11 h-11 bg-green-50 rounded-xl flex items-center justify-center text-2xl">📊</div>
            </div>
            <div className="text-4xl font-bold text-gray-900 mb-2">{kpis.utilization_rate}%</div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-600 font-semibold">↑ 8%</span>
              <span className="text-gray-500">vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border-l-4 border-l-blue-500 p-6 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Monthly Bench Burn</div>
              </div>
              <div className="w-11 h-11 bg-blue-50 rounded-xl flex items-center justify-center text-2xl">💸</div>
            </div>
            <div className="text-4xl font-bold text-gray-900 mb-2">{formatCurrency(kpis.monthly_bench_burn)}</div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-red-600 font-semibold">↓ 31%</span>
              <span className="text-gray-500">vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border-l-4 border-l-orange-500 p-6 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Cost Savings (YTD)</div>
              </div>
              <div className="w-11 h-11 bg-orange-50 rounded-xl flex items-center justify-center text-2xl">💰</div>
            </div>
            <div className="text-4xl font-bold text-gray-900 mb-2">{formatCurrency(kpis.ytd_savings)}</div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-600 font-semibold">↑ 45%</span>
              <span className="text-gray-500">vs last year</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border-l-4 border-l-purple-500 p-6 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Notice Period (At Risk)</div>
              </div>
              <div className="w-11 h-11 bg-purple-50 rounded-xl flex items-center justify-center text-2xl">⚠️</div>
            </div>
            <div className="text-4xl font-bold text-gray-900 mb-2">{kpis.notice_period_at_risk}</div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-600 font-semibold">→ 0%</span>
              <span className="text-gray-500">vs last month</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border-l-4 border-l-yellow-500 p-6 hover:shadow-md transition">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Avg Time to Allocate</div>
              </div>
              <div className="w-11 h-11 bg-yellow-50 rounded-xl flex items-center justify-center text-2xl">⏱️</div>
            </div>
            <div className="text-4xl font-bold text-gray-900 mb-2">{kpis.avg_time_to_allocate}d</div>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-red-600 font-semibold">↓ 62%</span>
              <span className="text-gray-500">vs last month</span>
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bench Trend Chart */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-5 pb-4 border-b border-gray-200">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Bench Trend & Utilization Forecast</h3>
                <p className="text-sm text-gray-500 mt-1">Historical data with AI-powered 90-day prediction</p>
              </div>
              <div className="flex gap-2">
                {['6M', '1Y', 'ALL'].map(filter => (
                  <button
                    key={filter}
                    onClick={() => setTimeFilter(filter)}
                    className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${
                      timeFilter === filter
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={trends.bench_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" stroke="#718096" />
                <YAxis yAxisId="left" stroke="#718096" label={{ value: 'Bench Count', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" stroke="#718096" label={{ value: 'Utilization %', angle: 90, position: 'insideRight' }} />
                <Tooltip />
                <Legend />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="bench_count"
                  fill={COLORS.red}
                  fillOpacity={0.1}
                  stroke={COLORS.red}
                  strokeWidth={3}
                  name="Bench Count"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="utilization"
                  stroke={COLORS.green}
                  strokeWidth={3}
                  name="Utilization %"
                />
                {trends.bench_trend.some(d => d.forecast) && (
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="bench_count"
                    stroke={COLORS.purple}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Forecast (90d)"
                    data={trends.bench_trend.filter(d => d.forecast)}
                  />
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Utilization by Role */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-5 pb-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Utilization by Role Level</h3>
              <p className="text-sm text-gray-500 mt-1">Current allocation status</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends.utilization_by_role}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="role" stroke="#718096" />
                <YAxis stroke="#718096" label={{ value: 'Percentage', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="allocated" stackId="a" fill={COLORS.green} radius={[4, 4, 0, 0]} name="Allocated" />
                <Bar dataKey="bench" stackId="a" fill={COLORS.red} radius={[0, 0, 4, 4]} name="Bench" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Revenue by Domain */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-5 pb-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Revenue by Domain</h3>
              <p className="text-sm text-gray-500 mt-1">Monthly billing breakdown ($K)</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={trends.revenue_by_domain}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ domain, revenue }) => `${domain}: $${revenue}K`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="revenue"
                >
                  {trends.revenue_by_domain.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Skill Gaps */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-5 pb-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Top Skill Gaps</h3>
              <p className="text-sm text-gray-500 mt-1">Pipeline demand vs current supply</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends.skill_gaps}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="skill" stroke="#718096" />
                <YAxis stroke="#718096" label={{ value: 'Number of Resources', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="demand" fill={COLORS.blue} radius={[4, 4, 0, 0]} name="Pipeline Demand" />
                <Bar dataKey="supply" fill={COLORS.green} radius={[4, 4, 0, 0]} name="Current Supply" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Gross Margin */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-5 pb-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Gross Margin by Project Type</h3>
              <p className="text-sm text-gray-500 mt-1">Profitability comparison</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends.gross_margin} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" domain={[0, 100]} stroke="#718096" label={{ value: 'Margin Percentage', position: 'insideBottom', offset: -5 }} />
                <YAxis dataKey="type" type="category" stroke="#718096" width={100} />
                <Tooltip />
                <Bar dataKey="margin" fill={COLORS.blue} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Cost Savings */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="mb-5 pb-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Cost Savings Impact Analysis</h3>
              <p className="text-sm text-gray-500 mt-1">Contribution by AI feature (YTD)</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends.cost_savings}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="category" stroke="#718096" />
                <YAxis stroke="#718096" label={{ value: 'Savings ($K)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Bar dataKey="savings" fill={COLORS.blue} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority Allocation Queue */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-5 pb-4 border-b border-gray-200">
            <div>
              <h3 className="text-lg font-bold text-gray-900">Priority Allocation Queue</h3>
              <p className="text-sm text-gray-500 mt-1">AI-ranked by billing rate, bench days, and domain demand</p>
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="🔍 Search employees..."
              className="px-4 py-2 border border-gray-200 rounded-lg w-64 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Priority</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Employee</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Role</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Primary Domain</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Billing Rate</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Bench Days</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Bench Cost</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Matched Projects</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredQueue.map((emp) => (
                  <tr key={emp.employee_id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getPriorityBadgeClass(emp.priority_tier)}`}>
                        {emp.priority_tier}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="font-semibold text-gray-900">{emp.employee_name}</div>
                    </td>
                    <td className="px-4 py-4 text-gray-700">{emp.role}</td>
                    <td className="px-4 py-4 text-gray-700">{emp.primary_domain}</td>
                    <td className="px-4 py-4">
                      <span className="font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded text-sm">
                        ${emp.billing_rate}/hr
                      </span>
                    </td>
                    <td className="px-4 py-4 text-gray-700">{emp.bench_days} days</td>
                    <td className="px-4 py-4 font-semibold text-red-600">${emp.bench_cost.toLocaleString()}</td>
                    <td className="px-4 py-4 text-gray-700">{emp.matched_projects} matches</td>
                    <td className="px-4 py-4">
                      <button className="px-4 py-1.5 bg-white text-blue-600 border border-blue-600 rounded-lg text-xs font-semibold hover:bg-blue-600 hover:text-white transition">
                        View Matches
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredQueue.length === 0 && (
              <div className="text-center py-8 text-gray-500">No employees found matching your search.</div>
            )}
          </div>
        </div>

        {/* Insights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {insights.map((insight, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-sm border-l-4 border-l-blue-500 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-xl">
                  {insight.icon}
                </div>
                <h4 className="text-base font-bold text-gray-900">{insight.title}</h4>
              </div>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">{insight.body}</p>
              <div className="pt-4 border-t border-gray-200 flex justify-between items-center">
                <div className="text-2xl font-bold text-blue-600">{insight.value}</div>
                <span className="text-gray-500 text-xs">{insight.value_label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Chat Agent */}
        <ChatAgent />
      </div>
    </div>
  )
}

export default Dashboard
