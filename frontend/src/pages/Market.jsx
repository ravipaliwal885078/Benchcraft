import { useState, useEffect } from 'react'
import AnonymizedCard from '../components/AnonymizedCard'
import { searchTalent, allocateResource, getProjects } from '../services/api'
import { Search, Filter, X } from 'lucide-react'
import SmartMatch from '../components/SmartMatch'

const Market = () => {
  const [query, setQuery] = useState('')
  const [minProficiency, setMinProficiency] = useState(1)
  const [maxBudget, setMaxBudget] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState([])
  const [showFilters, setShowFilters] = useState(false)

  // Additional filters
  const [roleLevel, setRoleLevel] = useState('')
  const [location, setLocation] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [visaRequired, setVisaRequired] = useState('')
  const [projectType, setProjectType] = useState('')

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await getProjects()
      setProjects(data.projects || [])
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('Please enter a search query')
      return
    }
    try {
      // Collect advanced filters into an object
      const advancedFilters = {
        roleLevel,
        location,
        remoteOnly,
        visaRequired,
        projectType
      }

      const data = await searchTalent(
        query,
        minProficiency,
        maxBudget ? parseFloat(maxBudget) : null,
        advancedFilters // Pass the new object here
      )
      setResults(data.results || [])
    } catch (error) {
      console.error('Search failed:', error)
      alert('Search failed: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAllocate = async (empUuid, allocationData) => {
    try {
      const result = await allocateResource(
        empUuid,
        allocationData.project_id,
        allocationData.start_date,
        allocationData.end_date || null,
        allocationData.billing_rate || null
      )
      alert('Resource allocated successfully!')
      // Refresh search results
      handleSearch()
      return result
    } catch (error) {
      console.error('Allocation failed:', error)
      throw error
    }
  }

  const clearFilters = () => {
    setRoleLevel('')
    setLocation('')
    setRemoteOnly(false)
    setVisaRequired('')
    setProjectType('')
    setMinProficiency(1)
    setMaxBudget('')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Marketplace</h1>
        <p className="text-gray-600 mt-2">Blind Match Interface - Search for talent using natural language</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Description / Search Query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Need a Senior Python dev with FinTech exp."
              className="w-full border border-gray-300 rounded-md px-4 py-2 h-24"
            />
          </div>

          {/* Basic Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Proficiency: {minProficiency}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={minProficiency}
                onChange={(e) => setMinProficiency(parseInt(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Budget (Optional)
              </label>
              <input
                type="number"
                value={maxBudget}
                onChange={(e) => setMaxBudget(e.target.value)}
                placeholder="e.g., 15000"
                className="w-full border border-gray-300 rounded-md px-4 py-2"
              />
            </div>
          </div>

          {/* Advanced Filters Toggle */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 text-indigo-600 hover:text-indigo-800"
            >
              <Filter className="w-4 h-4" />
              <span>{showFilters ? 'Hide' : 'Show'} Advanced Filters</span>
            </button>
            {(roleLevel || location || remoteOnly || visaRequired || projectType) && (
              <button
                onClick={clearFilters}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
              >
                <X className="w-4 h-4" />
                <span>Clear Filters</span>
              </button>
            )}
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role Level
                </label>
                <select
                  value={roleLevel}
                  onChange={(e) => setRoleLevel(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Any Level</option>
                  <option value="JR">Junior</option>
                  <option value="MID">Mid</option>
                  <option value="SR">Senior</option>
                  <option value="LEAD">Lead</option>
                  <option value="PRINCIPAL">Principal</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g., New York, NY"
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Visa Status
                </label>
                <select
                  value={visaRequired}
                  onChange={(e) => setVisaRequired(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Any Visa</option>
                  <option value="H1B">H1B</option>
                  <option value="Green Card">Green Card</option>
                  <option value="US Citizen">US Citizen</option>
                  <option value="TN">TN</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Type
                </label>
                <select
                  value={projectType}
                  onChange={(e) => setProjectType(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Any Type</option>
                  <option value="WEB">Web Development</option>
                  <option value="MOBILE">Mobile App</option>
                  <option value="DATA">Data Science</option>
                  <option value="DEVOPS">DevOps</option>
                  <option value="SECURITY">Security</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="remoteOnly"
                  checked={remoteOnly}
                  onChange={(e) => setRemoteOnly(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="remoteOnly" className="ml-2 text-sm text-gray-700">
                  Remote work only
                </label>
              </div>
            </div>
          )}

          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full bg-primary text-white py-3 px-4 rounded-md hover:bg-primary-dark transition-colors font-medium flex items-center justify-center space-x-2"
          >
            <Search className="w-5 h-5" />
            <span>{loading ? 'Searching...' : 'Search Talent'}</span>
          </button>
        </div>
      </div>

      {/* Smart Match Component */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          AI-Powered Smart Match
        </h2>
        <p className="text-gray-700 mb-4">
          Use our Smart Match feature to find the best candidates for your projects
          based on AI-powered analysis of skills, experience, and project requirements.
        </p>
        <SmartMatch />
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Found {results.length} matching candidates
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((profile, idx) => (
              <AnonymizedCard
                key={profile.uuid || idx}
                profile={profile}
                onReveal={handleAllocate}
                projects={projects}
              />
            ))}
          </div>
        </div>
      )}

      {results.length === 0 && !loading && query && (
        <div className="text-center py-12 text-gray-500">
          No results found. Try adjusting your search criteria.
        </div>
      )}
    </div>
  )
}

export default Market
