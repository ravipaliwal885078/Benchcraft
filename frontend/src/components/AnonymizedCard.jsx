import { useState } from 'react'
import { User, MapPin, Briefcase, Star } from 'lucide-react'

const AnonymizedCard = ({ profile, onReveal, projects = [] }) => {
  const [showModal, setShowModal] = useState(false)
  const [allocationData, setAllocationData] = useState({
    project_id: '',
    start_date: '',
    end_date: '',
    billing_rate: '',
  })

  const handleReveal = () => {
    setShowModal(true)
  }

  const handleAllocate = async () => {
    if (!allocationData.project_id || !allocationData.start_date) {
      alert('Please fill in required fields')
      return
    }

    try {
      await onReveal(profile.uuid, allocationData)
      setShowModal(false)
    } catch (error) {
      alert('Allocation failed: ' + error.message)
    }
  }

  const matchPercentage = Math.round((profile.match_score || 0) * 100)

  return (
    <>
      <div className="bg-background rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-accent rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary">
                {profile.candidate_id}
              </h3>
              <p className="text-sm text-muted-foreground">{profile.role_level}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Star className="w-5 h-5 text-warning fill-warning" />
            <span className="text-lg font-bold text-primary">{matchPercentage}%</span>
          </div>
        </div>

        <div className="space-y-2 mb-4">
          {profile.base_location && (
            <div className="flex items-center text-sm text-muted-foreground">
              <MapPin className="w-4 h-4 mr-2" />
              {profile.base_location}
              {profile.remote_pref && (
                <span className="ml-2 px-2 py-0.5 bg-success/10 text-success text-xs rounded">
                  Remote
                </span>
              )}
            </div>
          )}

          {profile.bio_summary && (
            <p className="text-sm text-gray-600 line-clamp-2">{profile.bio_summary}</p>
          )}

          {profile.skills && profile.skills.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {profile.skills.slice(0, 5).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  {skill.skill_name} ({skill.proficiency}/5)
                </span>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={handleReveal}
          className="w-full mt-4 bg-primary text-white py-2 px-4 rounded-md hover:bg-primary-dark transition-colors font-medium"
        >
          Reveal & Allocate
        </button>
      </div>

      {/* Allocation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Allocate Resource</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project *
                </label>
                <select
                  value={allocationData.project_id}
                  onChange={(e) => setAllocationData({ ...allocationData, project_id: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Select a project</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.client_name} - {project.project_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date *
                </label>
                <input
                  type="date"
                  value={allocationData.start_date}
                  onChange={(e) => setAllocationData({ ...allocationData, start_date: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={allocationData.end_date}
                  onChange={(e) => setAllocationData({ ...allocationData, end_date: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Billing Rate (Optional)
                </label>
                <input
                  type="number"
                  value={allocationData.billing_rate}
                  onChange={(e) => setAllocationData({ ...allocationData, billing_rate: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="e.g., 150"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAllocate}
                className="flex-1 bg-primary text-white py-2 px-4 rounded-md hover:bg-primary-dark"
              >
                Allocate
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default AnonymizedCard
