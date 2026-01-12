import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchTalent = async (query, minProficiency = 1, maxBudget = null) => {
  const response = await api.post('/search', {
    query,
    min_proficiency: minProficiency,
    max_budget: maxBudget,
  })
  return response.data
}

export const allocateResource = async (empUuid, projectId, startDate, endDate = null, billingRate = null) => {
  const response = await api.post('/employees/allocate', {
    emp_uuid: empUuid,
    project_id: projectId,
    start_date: startDate,
    end_date: endDate,
    billing_rate: billingRate,
  })
  return response.data
}

export const getProjects = async () => {
  const response = await api.get('/projects')
  return response.data
}

export const getProject = async (projectId) => {
  const response = await api.get(`/projects/${projectId}`)
  return response.data
}

export const createProject = async (projectData) => {
  const response = await api.post('/projects', projectData)
  return response.data
}

export const updateProject = async (projectId, projectData) => {
  const response = await api.put(`/projects/${projectId}`, projectData)
  return response.data
}

export const updateProjectTeam = async (projectId, allocations) => {
  const response = await api.post(`/projects/${projectId}/team`, { allocations })
  return response.data
}

export const removeTeamMember = async (projectId, allocationId) => {
  const response = await api.delete(`/projects/${projectId}/team/${allocationId}`)
  return response.data
}

export const checkEmployeeAllocation = async (employeeId, allocationData) => {
  const response = await api.post(`/employees/${employeeId}/allocation-check`, allocationData)
  return response.data
}

export const getKPI = async () => {
  const response = await api.get('/kpi')
  return response.data
}

export const getForecast = async () => {
  const response = await api.get('/forecast')
  return response.data
}

// Employee Management APIs
export const getEmployees = async (filters = {}) => {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value)
  })
  const response = await api.get(`/employees/?${params}`)
  return response.data
}

export const getEmployee = async (empId) => {
  const response = await api.get(`/employees/${empId}`)
  return response.data
}

export const createEmployee = async (employeeData) => {
  const response = await api.post('/employees/', employeeData)
  return response.data
}

export const updateEmployee = async (empId, employeeData) => {
  const response = await api.put(`/employees/${empId}`, employeeData)
  return response.data
}

export const deleteEmployee = async (empId) => {
  const response = await api.delete(`/employees/${empId}`)
  return response.data
}

export const getEmployeeAvailability = async (empId) => {
  const response = await api.get(`/employees/${empId}/availability`)
  return response.data
}

export const addEmployeeSkill = async (empId, skillData) => {
  const response = await api.post(`/employees/${empId}/skills`, skillData)
  return response.data
}

export const removeEmployeeSkill = async (empId, skillId) => {
  const response = await api.delete(`/employees/${empId}/skills/${skillId}`)
  return response.data
}

export const raiseEmployeeRisk = async (empId, riskData) => {
  const response = await api.post(`/employees/${empId}/risks`, riskData)
  return response.data
}

// HR Report APIs
export const getAllocationReport = async (forecastDays = 30, includeBench = true) => {
  const params = new URLSearchParams()
  params.append('forecast_days', forecastDays)
  params.append('include_bench', includeBench)
  const response = await api.get(`/hr/allocation-report?${params}`)
  return response.data
}

// Allocation Reports APIs (New)
export const generateAllocationReport = async (reportType = 'internal', level = 'overall', projectId = null, startDate = null, endDate = null) => {
  const params = new URLSearchParams()
  params.append('report_type', reportType)
  params.append('level', level)
  if (projectId) params.append('project_id', projectId)
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  const response = await api.get(`/allocation-reports/generate?${params}`)
  return response.data
}

export const exportAllocationReportExcel = async (reportType = 'internal', level = 'overall', projectId = null, startDate = null, endDate = null) => {
  const params = new URLSearchParams()
  params.append('report_type', reportType)
  params.append('level', level)
  if (projectId) params.append('project_id', projectId)
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  
  const response = await api.get(`/allocation-reports/export-excel?${params}`, {
    responseType: 'blob'
  })
  
  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  const filename = `allocation_report_${reportType}_${level}${projectId ? `_${projectId}` : ''}_${new Date().toISOString().split('T')[0]}.xlsx`
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
  
  return { success: true }
}

// Dashboard APIs
export const getComprehensiveDashboard = async () => {
  const response = await api.get('/comprehensive')
  return response.data
}

export const chatWithAgent = async (question, conversationHistory = [], useWebSearch = false) => {
  const response = await api.post('/chat', { 
    question, 
    conversation_history: conversationHistory,
    use_web_search: useWebSearch 
  })
  return response.data
}

export const suggestTeam = async (projectDetails, roleRequirements, startDate, endDate) => {
  const response = await api.post('/projects/suggest-team', {
    project_details: projectDetails,
    role_requirements: roleRequirements,
    start_date: startDate,
    end_date: endDate
  })
  return response.data
}

export const createProjectFeedback = async (projectId, feedbackData) => {
  const response = await api.post(`/projects/${projectId}/feedback`, feedbackData)
  return response.data
}

export const uploadRFP = async (formData) => {
  const response = await api.post('/rfp/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

export const createEmployeeFeedback = async (employeeId, feedbackData) => {
  const response = await api.post(`/employees/${employeeId}/feedback`, feedbackData)
  return response.data
}

// Training Recommendations API
export const getTrainingRecommendations = async () => {
  const response = await api.get('/training/recommendations')
  return response.data
}

// Reports APIs
// EPIC 1: Project Intelligence & ROI Analysis
export const getResourceCriticalProjects = async (threshold = 20) => {
  const response = await api.get(`/reports/projects/resource-critical?threshold=${threshold}`)
  return response.data
}

export const getProjectsAtRisk = async () => {
  const response = await api.get('/reports/projects/at-risk')
  return response.data
}

export const getLowROIProjects = async (threshold = 10, limit = 10) => {
  const response = await api.get(`/reports/projects/low-roi?threshold=${threshold}&limit=${limit}`)
  return response.data
}

export const getHighROIProjects = async (type = 'highest_roi', limit = 10) => {
  const response = await api.get(`/reports/projects/high-roi?type=${type}&limit=${limit}`)
  return response.data
}

// EPIC 2: Employee Intelligence & Workforce Optimization
export const getEmployeesAtRisk = async (threshold = 25) => {
  const response = await api.get(`/reports/employees/at-risk?threshold=${threshold}`)
  return response.data
}

export const getHiringNeeds = async () => {
  const response = await api.get('/reports/employees/hiring-needs')
  return response.data
}

export const getUpskillingOpportunities = async () => {
  const response = await api.get('/reports/employees/upskilling-opportunities')
  return response.data
}

export const getLowROIEmployees = async (threshold = 50, limit = 20) => {
  const response = await api.get(`/reports/employees/low-roi?threshold=${threshold}&limit=${limit}`)
  return response.data
}

export const getStarEmployees = async (type = 'highest_ratio', limit = 20) => {
  const response = await api.get(`/reports/employees/star-performers?type=${type}&limit=${limit}`)
  return response.data
}

export const getEmployeeProfitEfficiency = async (employeeId = null) => {
  const url = employeeId 
    ? `/reports/employees/profit-efficiency?employee_id=${employeeId}`
    : '/reports/employees/profit-efficiency'
  const response = await api.get(url)
  return response.data
}

// EPIC 3: Risk & Financial Performance Management
export const getConsolidatedRisks = async () => {
  const response = await api.get('/reports/risks/consolidated')
  return response.data
}

export const getFinanciallyUnderperformingProjects = async (threshold = 20) => {
  const response = await api.get(`/reports/projects/financially-underperforming?threshold=${threshold}`)
  return response.data
}

export const getLowGrossProfitEmployees = async (threshold = 50) => {
  const response = await api.get(`/reports/employees/low-gross-profit?threshold=${threshold}`)
  return response.data
}

export default api
