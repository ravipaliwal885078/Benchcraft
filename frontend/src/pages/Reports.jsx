import { useEffect, useState } from 'react'
import {
  getResourceCriticalProjects,
  getProjectsAtRisk,
  getLowROIProjects,
  getHighROIProjects,
  getEmployeesAtRisk,
  getHiringNeeds,
  getUpskillingOpportunities,
  getLowROIEmployees,
  getStarEmployees,
  getEmployeeProfitEfficiency,
  getConsolidatedRisks,
  getFinanciallyUnderperformingProjects,
  getLowGrossProfitEmployees
} from '../services/api'
import {
  AlertTriangle, TrendingDown, TrendingUp, Users, Briefcase,
  DollarSign, Target, Award, AlertCircle, BarChart3, PieChart
} from 'lucide-react'
import PageHeader from '../components/PageHeader'

const Reports = () => {
  const [activeTab, setActiveTab] = useState('projects')
  const [loading, setLoading] = useState(false)
  
  // Project Intelligence Data
  const [resourceCritical, setResourceCritical] = useState(null)
  const [projectsAtRisk, setProjectsAtRisk] = useState(null)
  const [lowROIProjects, setLowROIProjects] = useState(null)
  const [highROIProjects, setHighROIProjects] = useState(null)
  const [highROIReportType, setHighROIReportType] = useState('highest_roi')
  
  // Employee Intelligence Data
  const [employeesAtRisk, setEmployeesAtRisk] = useState(null)
  const [hiringNeeds, setHiringNeeds] = useState(null)
  const [upskillingOpportunities, setUpskillingOpportunities] = useState(null)
  const [lowROIEmployees, setLowROIEmployees] = useState(null)
  const [starEmployees, setStarEmployees] = useState(null)
  const [starReportType, setStarReportType] = useState('highest_ratio')
  const [profitEfficiency, setProfitEfficiency] = useState(null)
  
  // Risk & Financial Data
  const [consolidatedRisks, setConsolidatedRisks] = useState(null)
  const [underperformingProjects, setUnderperformingProjects] = useState(null)
  const [lowGrossProfitEmployees, setLowGrossProfitEmployees] = useState(null)

  useEffect(() => {
    loadData()
  }, [activeTab, highROIReportType, starReportType])

  const loadData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'projects') {
        const [critical, atRisk, lowROI, highROI] = await Promise.all([
          getResourceCriticalProjects(),
          getProjectsAtRisk(),
          getLowROIProjects(),
          getHighROIProjects(highROIReportType)
        ])
        setResourceCritical(critical)
        setProjectsAtRisk(atRisk)
        setLowROIProjects(lowROI)
        setHighROIProjects(highROI)
      } else if (activeTab === 'employees') {
        const [atRisk, hiring, upskilling, lowROI, stars, efficiency] = await Promise.all([
          getEmployeesAtRisk(),
          getHiringNeeds(),
          getUpskillingOpportunities(),
          getLowROIEmployees(),
          getStarEmployees(starReportType),
          getEmployeeProfitEfficiency()
        ])
        setEmployeesAtRisk(atRisk)
        setHiringNeeds(hiring)
        setUpskillingOpportunities(upskilling)
        setLowROIEmployees(lowROI)
        setStarEmployees(stars)
        setProfitEfficiency(efficiency)
      } else if (activeTab === 'risks') {
        const [risks, underperforming, lowGP] = await Promise.all([
          getConsolidatedRisks(),
          getFinanciallyUnderperformingProjects(),
          getLowGrossProfitEmployees()
        ])
        setConsolidatedRisks(risks)
        setUnderperformingProjects(underperforming)
        setLowGrossProfitEmployees(lowGP)
      }
    } catch (error) {
      console.error('Failed to load reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'CRITICAL':
      case 'RED':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'HIGH':
      case 'AMBER':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'LOW':
      case 'GREEN':
        return 'bg-green-100 text-green-800 border-green-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const renderProjectsTab = () => (
    <div className="space-y-6">
      {/* Story 1.1: Resource Critical Projects */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
            Resource-Critical Projects
          </h2>
        </div>
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : resourceCritical?.critical_projects?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Remaining Days</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Remaining Allocation %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {resourceCritical.critical_projects.map((project) => (
                  <tr key={project.project_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{project.project_name}</div>
                      <div className="text-sm text-gray-500">{project.client_name}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{project.remaining_duration_days} days</td>
                    <td className="px-4 py-3 text-sm">{project.remaining_allocation_pct}%</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getRiskColor(project.risk_indicator)}`}>
                        {project.risk_indicator}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No resource-critical projects found</div>
        )}
      </div>

      {/* Story 1.2: Projects at Risk */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
          Projects at Risk
        </h2>
        {projectsAtRisk?.at_risk_projects?.length > 0 ? (
          <div className="space-y-4">
            {projectsAtRisk.at_risk_projects.map((project) => (
              <div key={project.project_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-medium text-gray-900">{project.project_name}</h3>
                    <p className="text-sm text-gray-500">{project.client_name}</p>
                  </div>
                  <span className={`px-3 py-1 text-sm font-semibold rounded ${getRiskColor(project.severity)}`}>
                    {project.severity}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                  <div>
                    <span className="text-gray-500">Project Risks:</span>
                    <span className="ml-2 font-medium">{project.project_risk_count}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Risky Employees:</span>
                    <span className="ml-2 font-medium">{project.risky_employee_count}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <span className="ml-2 font-medium">{project.status}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No projects at risk</div>
        )}
      </div>

      {/* Story 1.3: Low ROI Projects */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <TrendingDown className="w-5 h-5 mr-2 text-red-600" />
          Low ROI Projects
        </h2>
        {lowROIProjects?.low_roi_projects?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ROI %</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {lowROIProjects.low_roi_projects.map((project) => (
                  <tr key={project.project_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{project.project_name}</div>
                      <div className="text-sm text-gray-500">{project.client_name}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(project.revenue)}</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(project.cost)}</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(project.profit)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        project.roi_percentage < 0 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {project.roi_percentage.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No low ROI projects found</div>
        )}
      </div>

      {/* Story 1.4: High ROI / Star Projects */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            High ROI / Star Projects
          </h2>
          <select
            value={highROIReportType}
            onChange={(e) => setHighROIReportType(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm"
          >
            <option value="highest_roi">Highest ROI</option>
            <option value="most_efficient">Most Efficient</option>
            <option value="most_stable">Most Stable</option>
          </select>
        </div>
        {highROIProjects?.high_roi_projects?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ROI %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Team Size</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {highROIProjects.high_roi_projects.map((project) => (
                  <tr key={project.project_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{project.project_name}</div>
                      <div className="text-sm text-gray-500">{project.client_name}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                        {project.roi_percentage.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(project.profit)}</td>
                    <td className="px-4 py-3 text-sm">{project.team_size}</td>
                    <td className="px-4 py-3">
                      {project.is_star_performer && (
                        <span className="px-2 py-1 text-xs font-semibold rounded bg-yellow-100 text-yellow-800 flex items-center w-fit">
                          <Award className="w-3 h-3 mr-1" />
                          Star Performer
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No high ROI projects found</div>
        )}
      </div>
    </div>
  )

  const renderEmployeesTab = () => (
    <div className="space-y-6">
      {/* Story 2.1: Employees at Risk */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <Users className="w-5 h-5 mr-2 text-orange-600" />
          Employees at Risk or Under-Utilized
        </h2>
        {employeesAtRisk?.at_risk_employees?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Reasons</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {employeesAtRisk.at_risk_employees.map((emp) => (
                  <tr key={emp.employee_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{emp.employee_name}</div>
                      <div className="text-sm text-gray-500">{emp.email}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{emp.internal_allocation_percentage}%</td>
                    <td className="px-4 py-3 text-sm">{emp.status}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {emp.risk_reasons.map((reason) => (
                          <span key={reason} className="px-2 py-1 text-xs rounded bg-orange-100 text-orange-800">
                            {reason}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No employees at risk</div>
        )}
      </div>

      {/* Story 2.2: Hiring Needs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <Target className="w-5 h-5 mr-2 text-blue-600" />
          Hiring Needs for Pipeline Projects
        </h2>
        {hiringNeeds?.hiring_needs?.length > 0 ? (
          <div className="space-y-3">
            {hiringNeeds.hiring_needs.map((need, idx) => (
              <div key={idx} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{need.skill}</h3>
                    <p className="text-sm text-gray-500">{need.project_name}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm">
                      <span className="text-gray-500">Required:</span>
                      <span className="ml-2 font-medium">{need.required_count}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-500">Available:</span>
                      <span className="ml-2 font-medium">{need.available_count}</span>
                    </div>
                    <div className="text-sm font-semibold text-red-600">
                      Need: {need.needed_count}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No hiring needs identified</div>
        )}
      </div>

      {/* Story 2.3: Upskilling Opportunities */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <Award className="w-5 h-5 mr-2 text-purple-600" />
          Employees Suitable for Upskilling
        </h2>
        {upskillingOpportunities?.upskilling_opportunities?.length > 0 ? (
          <div className="space-y-3">
            {upskillingOpportunities.upskilling_opportunities.map((opp, idx) => (
              <div key={idx} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-medium text-gray-900">{opp.employee_name}</h3>
                    <p className="text-sm text-gray-500">Current Allocation: {opp.current_allocation_pct}%</p>
                  </div>
                  <span className="px-2 py-1 text-xs font-semibold rounded bg-purple-100 text-purple-800">
                    Trainable
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                  <div>
                    <span className="text-gray-500">Current Skills:</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {opp.current_skills.slice(0, 3).map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">Target Skill:</span>
                    <span className="ml-2 font-medium">{opp.target_skill}</span>
                    <div className="mt-1">
                      <span className="text-gray-500">Project:</span>
                      <span className="ml-2 font-medium">{opp.project_name}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No upskilling opportunities found</div>
        )}
      </div>

      {/* Story 2.4: Low ROI Employees */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <TrendingDown className="w-5 h-5 mr-2 text-red-600" />
          Low ROI Employees
        </h2>
        {lowROIEmployees?.low_roi_employees?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit/Allocation</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Projects</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {lowROIEmployees.low_roi_employees.map((emp) => (
                  <tr key={emp.employee_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{emp.employee_name}</div>
                      <div className="text-sm text-gray-500">{emp.email}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{emp.internal_allocation_percentage}%</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(emp.total_profit)}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-red-100 text-red-800">
                        {emp.profit_to_allocation_ratio.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{emp.projects.length} projects</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No low ROI employees found</div>
        )}
      </div>

      {/* Story 2.5: Star Employees */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Award className="w-5 h-5 mr-2 text-yellow-600" />
            Star Employees
          </h2>
          <select
            value={starReportType}
            onChange={(e) => setStarReportType(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm"
          >
            <option value="highest_ratio">Highest Profit-to-Allocation</option>
            <option value="best_utilization">Best Utilization</option>
            <option value="consistent">Consistent Performers</option>
          </select>
        </div>
        {starEmployees?.star_employees?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit/Allocation</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {starEmployees.star_employees.map((emp) => (
                  <tr key={emp.employee_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{emp.employee_name}</div>
                      <div className="text-sm text-gray-500">{emp.email}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{emp.internal_allocation_percentage}%</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(emp.total_profit)}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                        {emp.profit_to_allocation_ratio.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {emp.is_star_performer && (
                        <span className="px-2 py-1 text-xs font-semibold rounded bg-yellow-100 text-yellow-800 flex items-center w-fit">
                          <Award className="w-3 h-3 mr-1" />
                          Star Performer
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No star employees found</div>
        )}
      </div>

      {/* Story 2.6: Profit Efficiency */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" />
          Employee Profit Efficiency Analysis
        </h2>
        {profitEfficiency?.efficiency_data?.length > 0 ? (
          <div className="space-y-4">
            {profitEfficiency.efficiency_data.slice(0, 10).map((emp) => (
              <div key={emp.employee_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-gray-900">{emp.employee_name}</h3>
                    <p className="text-sm text-gray-500">Total Allocation: {emp.total_internal_allocation_pct}%</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold">{formatCurrency(emp.total_profit)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getRiskColor(emp.efficiency_level)}`}>
                      {emp.efficiency_level}
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  Profit-to-Allocation Ratio: {emp.profit_to_allocation_ratio.toFixed(1)}
                </div>
                {emp.recommendations?.length > 0 && (
                  <div className="mt-2 pt-2 border-t">
                    <p className="text-xs font-medium text-gray-700 mb-1">Recommendations:</p>
                    {emp.recommendations.map((rec, i) => (
                      <p key={i} className="text-xs text-gray-600">{rec.message}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No efficiency data available</div>
        )}
      </div>
    </div>
  )

  const renderRisksTab = () => (
    <div className="space-y-6">
      {/* Story 3.1: Consolidated Risks */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
          Consolidated Risk View
        </h2>
        {consolidatedRisks ? (
          <div className="space-y-4">
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-600">{consolidatedRisks.summary?.critical || 0}</div>
                <div className="text-sm text-red-700">Critical</div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">{consolidatedRisks.summary?.high || 0}</div>
                <div className="text-sm text-orange-700">High</div>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">{consolidatedRisks.summary?.medium || 0}</div>
                <div className="text-sm text-yellow-700">Medium</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{consolidatedRisks.summary?.low || 0}</div>
                <div className="text-sm text-green-700">Low</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Project Risks</h3>
                <div className="space-y-2">
                  {consolidatedRisks.project_risks?.slice(0, 5).map((risk) => (
                    <div key={risk.risk_id} className="border rounded p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">{risk.project_name}</span>
                        <span className={`px-2 py-1 text-xs rounded ${getRiskColor(risk.severity)}`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600">{risk.risk_type}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Employee Risks</h3>
                <div className="space-y-2">
                  {consolidatedRisks.employee_risks?.slice(0, 5).map((risk) => (
                    <div key={risk.risk_id} className="border rounded p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">{risk.employee_name}</span>
                        <span className={`px-2 py-1 text-xs rounded ${getRiskColor(risk.severity)}`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600">{risk.risk_type}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No risks found</div>
        )}
      </div>

      {/* Story 3.2: Financially Underperforming Projects */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <DollarSign className="w-5 h-5 mr-2 text-red-600" />
          Financially Underperforming Projects
        </h2>
        {underperformingProjects?.underperforming_projects?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Margin %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Budget Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {underperformingProjects.underperforming_projects.map((project) => (
                  <tr key={project.project_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{project.project_name}</div>
                      <div className="text-sm text-gray-500">{project.client_name}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(project.revenue)}</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(project.cost)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        project.margin_percentage < 0 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {project.margin_percentage.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {formatCurrency(project.budget_consumed)} / {formatCurrency(project.budget_cap)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No underperforming projects found</div>
        )}
      </div>

      {/* Story 3.3: Low Gross Profit Employees */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
          <TrendingDown className="w-5 h-5 mr-2 text-red-600" />
          Employees with Low Gross Profit Contribution
        </h2>
        {lowGrossProfitEmployees?.low_gross_profit_employees?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gross Profit</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Allocation-Adjusted GP</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {lowGrossProfitEmployees.low_gross_profit_employees.map((emp) => (
                  <tr key={emp.employee_id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{emp.employee_name}</div>
                      <div className="text-sm text-gray-500">{emp.email}</div>
                    </td>
                    <td className="px-4 py-3 text-sm">{emp.internal_allocation_percentage}%</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(emp.gross_profit)}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-red-100 text-red-800">
                        {emp.allocation_adjusted_gross_profit.toFixed(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">No low gross profit employees found</div>
        )}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports & Analytics"
        subtitle="Actionable insights across Projects, Employees, and Risks"
        variant="simple"
      />

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('projects')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'projects'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Briefcase className="w-4 h-4 inline mr-2" />
              Project Intelligence
            </button>
            <button
              onClick={() => setActiveTab('employees')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'employees'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Users className="w-4 h-4 inline mr-2" />
              Employee Intelligence
            </button>
            <button
              onClick={() => setActiveTab('risks')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'risks'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <AlertCircle className="w-4 h-4 inline mr-2" />
              Risk & Financial Health
            </button>
          </nav>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <p className="mt-2 text-gray-600">Loading reports...</p>
            </div>
          ) : (
            <>
              {activeTab === 'projects' && renderProjectsTab()}
              {activeTab === 'employees' && renderEmployeesTab()}
              {activeTab === 'risks' && renderRisksTab()}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Reports
