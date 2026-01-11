import { useState } from 'react'
import { GraduationCap, TrendingUp, BookOpen } from 'lucide-react'
import SkillGapAnalysis from '../components/SkillGapAnalysis'

const TalentLab = () => {
  const [selectedEmployee, setSelectedEmployee] = useState(null)

  // Mock training recommendations
  const mockRecommendations = [
    {
      skill: 'Azure Certification',
      currentMatch: '70%',
      targetMatch: '100%',
      project: 'Project X',
      description: 'Complete Azure Fundamentals certification to improve match for cloud projects',
    },
    {
      skill: 'React Advanced',
      currentMatch: '65%',
      targetMatch: '95%',
      project: 'Project Y',
      description: 'Advanced React patterns and hooks to qualify for frontend lead roles',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Talent Lab</h1>
        <p className="text-muted-foreground mt-2">Training & Skills Matrix</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skills Matrix */}
        <div className="bg-background rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-primary mb-4 flex items-center">
            <BookOpen className="w-6 h-6 mr-2 text-accent" />
            Skills Matrix
          </h2>
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Select an employee to view their skill profile and training recommendations.
            </div>
            {/* In production, this would be a searchable list of employees */}
          </div>
        </div>

        {/* Skill Gap Analysis & Training */}
        <SkillGapAnalysis />
      </div>

      <div className="bg-background rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-primary mb-4 flex items-center">
          <GraduationCap className="w-6 h-6 mr-2 text-success" />
          AI Career Path Recommendations
        </h2>
        <div className="space-y-4">
          {mockRecommendations.map((rec, idx) => (
            <div key={idx} className="border border-border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-primary">{rec.skill}</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-muted-foreground">{rec.currentMatch}</span>
                  <TrendingUp className="w-4 h-4 text-success" />
                  <span className="text-sm font-semibold text-success">{rec.targetMatch}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{rec.description}</p>
              <div className="text-xs text-muted-foreground">
                For: <span className="font-medium">{rec.project}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

        <div className="bg-info/10 border border-info/20 rounded-lg p-4">
          <p className="text-sm text-info">
            <strong>Feature:</strong> The Mentor Agent analyzes skill gaps and recommends targeted training
            to improve project match rates. Example: "You are a 70% match for Project X. Take this Azure Cert to become 100%."
        </p>
      </div>
    </div>
  )
}

export default TalentLab
