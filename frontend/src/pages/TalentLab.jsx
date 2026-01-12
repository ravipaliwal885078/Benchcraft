import { useState, useEffect } from 'react'
import { GraduationCap, TrendingUp, BookOpen, DollarSign, Clock, Target, Users, Lightbulb } from 'lucide-react'
import SkillGapAnalysis from '../components/SkillGapAnalysis'
import { getTrainingRecommendations } from '../services/api'

const TalentLab = () => {
  const [recommendations, setRecommendations] = useState([])
  const [summary, setSummary] = useState(null)
  const [aiInsights, setAiInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedRecommendation, setSelectedRecommendation] = useState(null)

  useEffect(() => {
    loadTrainingRecommendations()
  }, [])

  const loadTrainingRecommendations = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getTrainingRecommendations()
      setRecommendations(data.recommendations || [])
      setSummary(data.summary || {})
      setAiInsights(data.ai_insights)
    } catch (err) {
      console.error('Failed to load training recommendations:', err)
      setError(err.response?.data?.error || err.message || 'Failed to load training recommendations')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(1)}K`
    }
    return `$${amount.toFixed(0)}`
  }

  const getProficiencyColor = (current, required) => {
    if (current === 0) return 'text-red-600'
    if (current < required) return 'text-yellow-600'
    return 'text-green-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Talent Lab</h1>
        <p className="text-gray-600 mt-2">AI-Powered Training Recommendations - Upskilling over Hiring</p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Projects Analyzed</p>
            <p className="text-2xl font-bold text-gray-900">{summary.total_projects_analyzed || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Training Recommendations</p>
            <p className="text-2xl font-bold text-blue-600">{summary.total_recommendations || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Estimated Cost Savings</p>
            <p className="text-2xl font-bold text-green-600">
              {formatCurrency(summary.estimated_cost_savings || 0)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Time Savings</p>
            <p className="text-2xl font-bold text-indigo-600">
              {summary.estimated_time_savings_days || 0} days
            </p>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {aiInsights && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Strategic Insights</h3>
              <p className="text-gray-700 whitespace-pre-line">{aiInsights}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-gray-600">Analyzing skill gaps and generating recommendations...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Recommendations</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadTrainingRecommendations}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Training Recommendations */}
      {!loading && !error && recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <GraduationCap className="w-6 h-6 mr-2 text-indigo-600" />
              Training Recommendations
            </h2>
            <button
              onClick={loadTrainingRecommendations}
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
            >
              Refresh
            </button>
          </div>

          <div className="space-y-4">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition cursor-pointer"
                onClick={() => setSelectedRecommendation(selectedRecommendation === idx ? null : idx)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {rec.employee_name}
                      </h3>
                      <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                        {rec.employee_role}
                      </span>
                      <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 font-semibold">
                        {rec.match_score}% Match
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">
                      <span className="font-medium">Project:</span> {rec.project_name} ({rec.client_name})
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Required Skill:</span> {rec.required_skill}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600 mb-1">
                      {formatCurrency(rec.cost_savings)}
                    </div>
                    <div className="text-xs text-gray-500">Cost Savings</div>
                  </div>
                </div>

                {/* Skill Proficiency */}
                <div className="flex items-center gap-4 mb-4 p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <div className="text-xs text-gray-500 mb-1">Current Proficiency</div>
                    <div className={`text-lg font-semibold ${getProficiencyColor(rec.current_proficiency, rec.required_proficiency)}`}>
                      {rec.current_proficiency > 0 ? `${rec.current_proficiency}/5` : 'No Experience'}
                    </div>
                  </div>
                  <TrendingUp className="w-5 h-5 text-indigo-600" />
                  <div className="flex-1 text-right">
                    <div className="text-xs text-gray-500 mb-1">Required Proficiency</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {rec.required_proficiency}/5
                    </div>
                  </div>
                </div>

                {/* Training Recommendation */}
                <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
                  <div className="text-sm font-semibold text-blue-900 mb-1">Training Recommendation</div>
                  <div className="text-sm text-blue-700">{rec.training_recommendation}</div>
                </div>

                {/* Cost Breakdown */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-500 mb-1">Training Cost</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {formatCurrency(rec.training_cost)}
                    </div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-500 mb-1">Hiring Cost</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {formatCurrency(rec.hiring_cost)}
                    </div>
                  </div>
                </div>

                {/* Employee Availability */}
                <div className="flex items-center gap-4 mb-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600">
                      Current Utilization: <span className="font-semibold">{rec.current_utilization}%</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600">
                      Available Capacity: <span className="font-semibold text-green-600">{rec.available_capacity}%</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-600">
                      Time Savings: <span className="font-semibold text-indigo-600">{rec.time_savings_days} days</span>
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {selectedRecommendation === idx && (
                  <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
                    {/* Business Benefits */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                        <DollarSign className="w-4 h-4 mr-2 text-green-600" />
                        Business Benefits
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                        {rec.business_benefits?.map((benefit, i) => (
                          <li key={i}>{benefit}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Employee Benefits */}
                    <div>
                      <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                        <TrendingUp className="w-4 h-4 mr-2 text-blue-600" />
                        Employee Benefits
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                        {rec.employee_benefits?.map((benefit, i) => (
                          <li key={i}>{benefit}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && recommendations.length === 0 && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <GraduationCap className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Training Recommendations</h3>
          <p className="text-gray-600 mb-4">
            {summary?.message || 'No upcoming projects found in pipeline or no skill gaps identified.'}
          </p>
          <button
            onClick={loadTrainingRecommendations}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Refresh Analysis
          </button>
        </div>
      )}

      {/* Skills Matrix Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <BookOpen className="w-6 h-6 mr-2 text-indigo-600" />
            Skills Matrix
          </h2>
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              Select an employee to view their skill profile and training recommendations.
            </div>
            {/* In production, this would be a searchable list of employees */}
          </div>
        </div>

        {/* Skill Gap Analysis Component */}
        <SkillGapAnalysis />
      </div>
    </div>
  )
}

export default TalentLab
