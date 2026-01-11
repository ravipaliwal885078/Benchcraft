import { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { getEmployees, deleteEmployee } from '../services/api'
import EmployeeModal from '../components/EmployeeModal'
import AddSkillsModal from '../components/AddSkillsModal'
import RaiseRiskModal from '../components/RaiseRiskModal'
import { Users, Plus, Search, Filter, Edit, Trash2, Eye, Award, AlertTriangle, Briefcase, DollarSign, Calendar } from 'lucide-react'

const EmployeeList = () => {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 9 // Cards format
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showSkillsModal, setShowSkillsModal] = useState(false)
  const [showRiskModal, setShowRiskModal] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState(null)
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const hasLoadedRef = useRef(false)
  const searchInputRef = useRef(null)

  // Debounce search term to avoid too many API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm)
    }, 300) // 300ms delay

    return () => clearTimeout(timer)
  }, [searchTerm])

  // Initial load on mount
  useEffect(() => {
    loadEmployees(true)
    hasLoadedRef.current = true
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Load employees when filters change (after initial load)
  useEffect(() => {
    if (hasLoadedRef.current) {
      loadEmployees(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearchTerm, statusFilter, roleFilter])

  const loadEmployees = async (showLoading = false) => {
    if (showLoading) {
      setLoading(true)
    }
    try {
      const filters = {}
      if (debouncedSearchTerm) filters.search = debouncedSearchTerm
      if (statusFilter) filters.status = statusFilter
      if (roleFilter) filters.role_level = roleFilter

      const data = await getEmployees(filters)
      setEmployees(data.employees || [])
    } catch (error) {
      console.error('Failed to load employees:', error)
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  const handleEdit = (employee) => {
    setEditingEmployee(employee)
    setShowAddModal(true)
  }

  const handleAddSkills = (employee) => {
    setSelectedEmployee(employee)
    setShowSkillsModal(true)
  }

  const handleRaiseRisk = (employee) => {
    setSelectedEmployee(employee)
    setShowRiskModal(true)
  }

  const handleDelete = async (empId) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) {
      return
    }
    try {
      await deleteEmployee(empId)
      loadEmployees()
    } catch (error) {
      console.error('Failed to delete employee:', error)
      alert('Failed to delete employee. Please try again.')
    }
  }

  const handleModalClose = () => {
    setShowAddModal(false)
    setShowSkillsModal(false)
    setShowRiskModal(false)
    setEditingEmployee(null)
    setSelectedEmployee(null)
  }

  const handleModalSuccess = () => {
    loadEmployees() // Refresh the list
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'allocated': return 'bg-green-100 text-green-800'
      case 'bench': return 'bg-yellow-100 text-yellow-800'
      case 'notice_period': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRoleColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'principal': return 'bg-purple-100 text-purple-800'
      case 'lead': return 'bg-blue-100 text-blue-800'
      case 'sr': return 'bg-indigo-100 text-indigo-800'
      case 'mid': return 'bg-teal-100 text-teal-800'
      case 'jr': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getProficiencyColor = (proficiency) => {
    if (proficiency >= 4) return 'text-green-600'
    if (proficiency >= 3) return 'text-yellow-600'
    return 'text-gray-600'
  }

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">Loading employees...</div>
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-primary flex items-center">
            <Users className="w-8 h-8 mr-3 text-primary" />
            Employee Management
          </h1>
          <p className="text-muted-foreground mt-2">Comprehensive employee directory and management</p>
        </div>
        <button
          onClick={() => {
            setEditingEmployee(null)
            setShowAddModal(true)
          }}
          className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-dark flex items-center shadow-md"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Employee
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search employees..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value="BENCH">Bench</option>
            <option value="ALLOCATED">Allocated</option>
            <option value="NOTICE_PERIOD">Notice Period</option>
          </select>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">All Roles</option>
            <option value="JR">Junior</option>
            <option value="MID">Mid</option>
            <option value="SR">Senior</option>
            <option value="LEAD">Lead</option>
            <option value="PRINCIPAL">Principal</option>
          </select>
          <div className="text-sm text-muted-foreground flex items-center">
            <Filter className="w-4 h-4 mr-2" />
            {employees.length} employees found
          </div>
        </div>
      </div>

      {/* Employee Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {employees.map((employee) => (
          <div key={employee.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-primary">
                  {employee.first_name} {employee.last_name}
                </h3>
                <p className="text-sm text-gray-500">{employee.email}</p>
                {employee.base_location && (
                  <p className="text-xs text-gray-400 mt-1">{employee.base_location}</p>
                )}
              </div>
              <div className="flex space-x-1">
                <Link
                  to={`/employees/${employee.id}`}
                  className="text-blue-600 hover:text-blue-800 p-1.5 rounded hover:bg-blue-50"
                  title="View Details"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleEdit(employee)}
                  className="text-gray-600 hover:text-primary p-1.5 rounded hover:bg-gray-50"
                  title="Edit Employee"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleAddSkills(employee)}
                  className="text-green-600 hover:text-green-800 p-1.5 rounded hover:bg-green-50"
                  title="Add Skills"
                >
                  <Award className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleRaiseRisk(employee)}
                  className="text-red-600 hover:text-red-800 p-1.5 rounded hover:bg-red-50"
                  title="Raise Risk"
                >
                  <AlertTriangle className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Status and Role */}
            <div className="flex gap-2 mb-4">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(employee.role_level)}`}>
                {employee.role_level}
              </span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(employee.status)}`}>
                {employee.status?.replace('_', ' ')}
              </span>
            </div>

            {/* Project Allocation */}
            {employee.current_allocation ? (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center mb-2">
                  <Briefcase className="w-4 h-4 mr-2 text-blue-600" />
                  <span className="text-sm font-semibold text-blue-900">Current Project</span>
                </div>
                <p className="text-sm font-medium text-gray-900">{employee.current_allocation.project_name}</p>
                {employee.current_allocation.client_name && (
                  <p className="text-xs text-gray-600">{employee.current_allocation.client_name}</p>
                )}
                <div className="flex items-center mt-2 text-xs text-gray-600">
                  <Calendar className="w-3 h-3 mr-1" />
                  <span>
                    {employee.current_allocation.start_date && 
                      new Date(employee.current_allocation.start_date).toLocaleDateString()}
                    {employee.current_allocation.end_date && 
                      ` - ${new Date(employee.current_allocation.end_date).toLocaleDateString()}`}
                  </span>
                </div>
                {(employee.current_allocation.allocation_percentage || employee.current_allocation.utilization) && (
                  <div className="text-xs text-gray-600 mt-1 space-y-1">
                    <p>
                      Allocation: {employee.current_allocation.allocation_percentage || employee.current_allocation.utilization || 100}%
                    </p>
                    {employee.current_allocation.billable_percentage && (
                      <p>
                        Billable: {employee.current_allocation.billable_percentage}%
                      </p>
                    )}
                    {(employee.current_allocation.allocation_percentage || employee.current_allocation.utilization || 100) !== (employee.current_allocation.billable_percentage || 100) && (
                      <p className="text-orange-600">⚠️ Partial billing</p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-600">No current allocation</p>
              </div>
            )}

            {/* Skills */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-700 flex items-center">
                  <Award className="w-4 h-4 mr-1" />
                  Skills ({employee.skills?.length || 0})
                </span>
              </div>
              {employee.skills && employee.skills.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {employee.skills.slice(0, 5).map((skill) => (
                    <span
                      key={skill.id}
                      className={`text-xs px-2 py-1 rounded bg-gray-100 ${getProficiencyColor(skill.proficiency)}`}
                      title={`Proficiency: ${skill.proficiency}/5`}
                    >
                      {skill.skill_name} ({skill.proficiency})
                    </span>
                  ))}
                  {employee.skills.length > 5 && (
                    <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-600">
                      +{employee.skills.length - 5} more
                    </span>
                  )}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No skills added</p>
              )}
            </div>

            {/* Financial Info */}
            <div className="pt-4 border-t border-gray-200 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Monthly CTC:</span>
                <span className="text-sm font-semibold text-gray-900">
                  {employee.currency || 'USD'} {employee.ctc_monthly?.toLocaleString()}
                </span>
              </div>
              {employee.current_hourly_rate && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 flex items-center">
                    <DollarSign className="w-3 h-3 mr-1" />
                    Hourly Rate:
                  </span>
                  <span className="text-sm font-semibold text-green-600">
                    {employee.currency || 'USD'} {employee.current_hourly_rate.toFixed(2)}/hr
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {employees.length === 0 && !loading && (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-primary mb-2">No employees found</h3>
          <p className="text-muted-foreground">Try adjusting your search filters or add a new employee.</p>
        </div>
      )}

      {/* Modals */}
      <EmployeeModal
        isOpen={showAddModal}
        onClose={handleModalClose}
        employee={editingEmployee}
        onSuccess={handleModalSuccess}
      />
      <AddSkillsModal
        isOpen={showSkillsModal}
        onClose={handleModalClose}
        employee={selectedEmployee}
        onSuccess={handleModalSuccess}
      />
      <RaiseRiskModal
        isOpen={showRiskModal}
        onClose={handleModalClose}
        employee={selectedEmployee}
        onSuccess={handleModalSuccess}
      />
    </div>
  )
}

export default EmployeeList
