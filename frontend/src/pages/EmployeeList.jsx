import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getEmployees, deleteEmployee } from '../services/api'
import EmployeeModal from '../components/EmployeeModal'
import { Users, Plus, Search, Filter, Edit, Trash2, Eye } from 'lucide-react'

const EmployeeList = () => {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState(null)

  useEffect(() => {
    loadEmployees()
  }, [searchTerm, statusFilter, roleFilter])

  const loadEmployees = async () => {
    try {
      const filters = {}
      if (searchTerm) filters.search = searchTerm
      if (statusFilter) filters.status = statusFilter
      if (roleFilter) filters.role_level = roleFilter

      const data = await getEmployees(filters)
      setEmployees(data.employees)
    } catch (error) {
      console.error('Failed to load employees:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (employee) => {
    setEditingEmployee(employee)
    setShowAddModal(true)
  }

  const handleModalClose = () => {
    setShowAddModal(false)
    setEditingEmployee(null)
  }

  const handleModalSuccess = () => {
    loadEmployees() // Refresh the list
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'allocated': return 'bg-success/10 text-success'
      case 'bench': return 'bg-warning/10 text-warning'
      case 'notice_period': return 'bg-destructive/10 text-destructive'
      default: return 'bg-muted text-muted-foreground'
    }
  }

  const getRoleColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'principal': return 'bg-purple-100 text-purple-800'
      case 'lead': return 'bg-info/10 text-info'
      case 'sr': return 'bg-primary/10 text-primary'
      case 'mid': return 'bg-accent/10 text-accent'
      case 'jr': return 'bg-success/10 text-success'
      default: return 'bg-muted text-muted-foreground'
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">Loading employees...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-primary flex items-center">
            <Users className="w-8 h-8 mr-3 text-primary" />
            Employee Management
          </h1>
          <p className="text-muted-foreground mt-2">Comprehensive employee directory and management</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Employee
        </button>
      </div>

      {/* Filters */}
      <div className="bg-background rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search employees..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-border rounded-lg w-full focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value="BENCH">Bench</option>
            <option value="ALLOCATED">Allocated</option>
            <option value="NOTICE_PERIOD">Notice Period</option>
          </select>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
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
          <div key={employee.id} className="bg-background rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-primary">
                  {employee.first_name} {employee.last_name}
                </h3>
                <p className="text-sm text-muted-foreground">{employee.email}</p>
              </div>
              <div className="flex space-x-2">
                <Link
                  to={`/employees/${employee.id}`}
                  className="text-primary hover:text-primary/80 p-1"
                  title="View Details"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleEdit(employee)}
                  className="text-muted-foreground hover:text-primary p-1"
                  title="Edit"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(employee.id)}
                  className="text-destructive hover:text-destructive/80 p-1"
                  title="Remove"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Role:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(employee.role_level)}`}>
                  {employee.role_level}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Status:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(employee.status)}`}>
                  {employee.status?.replace('_', ' ')}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Location:</span>
                <span className="text-sm font-medium">{employee.base_location || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Skills:</span>
                <span className="text-sm font-medium">{employee.skills_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">CTC:</span>
                <span className="text-sm font-medium">${employee.ctc_monthly?.toLocaleString()}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-border">
              <Link
                to={`/employees/${employee.id}`}
                className="text-primary hover:text-primary/80 text-sm font-medium"
              >
                View 360° Profile →
              </Link>
            </div>
          </div>
        ))}
      </div>

      {employees.length === 0 && (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-primary mb-2">No employees found</h3>
          <p className="text-muted-foreground">Try adjusting your search filters or add a new employee.</p>
        </div>
      )}

      {/* Employee Modal */}
      <EmployeeModal
        isOpen={showAddModal}
        onClose={handleModalClose}
        employee={editingEmployee}
        onSuccess={handleModalSuccess}
      />
    </div>
  )
}

export default EmployeeList