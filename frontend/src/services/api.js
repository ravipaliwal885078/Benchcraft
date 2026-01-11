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

export const createProjectFeedback = async (projectId, feedbackData) => {
  const response = await api.post(`/projects/${projectId}/feedback`, feedbackData)
  return response.data
}

export const createEmployeeFeedback = async (employeeId, feedbackData) => {
  const response = await api.post(`/employees/${employeeId}/feedback`, feedbackData)
  return response.data
}

export default api
