import { X } from 'lucide-react'

const ROLE_OPTIONS = [
  'Architect',
  'Project Manager',
  'Senior Developer',
  'Developer',
  'Business Analyst',
  'QA Engineer',
  'Tech Lead',
  'Designer'
]

const Step2TeamStructure = ({ structure, onChange, onAdd, onRemove, onRoleChange, errors }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Team Structure Requirements</h3>
        <button
          onClick={onAdd}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
        >
          + Add Role
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Required Count</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Utilization (%)</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {structure.map((item, index) => (
              <tr key={index}>
                <td className="px-4 py-3">
                  <select
                    value={item.role_name}
                    onChange={(e) => onRoleChange(index, 'role_name', e.target.value)}
                    className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_role`] ? 'border-red-500' : 'border-gray-300'}`}
                  >
                    <option value="">Select Role</option>
                    {ROLE_OPTIONS.map(role => (
                      <option key={role} value={role}>{role}</option>
                    ))}
                  </select>
                  {errors[`${index}_role`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`${index}_role`]}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    min="1"
                    value={item.required_count}
                    onChange={(e) => onRoleChange(index, 'required_count', parseInt(e.target.value) || 1)}
                    className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_count`] ? 'border-red-500' : 'border-gray-300'}`}
                  />
                  {errors[`${index}_count`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`${index}_count`]}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={item.utilization_percentage}
                    onChange={(e) => onRoleChange(index, 'utilization_percentage', parseInt(e.target.value) || 0)}
                    className={`w-full border rounded-md px-2 py-1 text-sm ${errors[`${index}_utilization`] ? 'border-red-500' : 'border-gray-300'}`}
                  />
                  {errors[`${index}_utilization`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`${index}_utilization`]}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  {structure.length > 1 && (
                    <button
                      onClick={() => onRemove(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Step2TeamStructure
