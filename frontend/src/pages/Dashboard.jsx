import { useEffect, useState } from 'react'
import BenchGauge from '../components/BenchGauge'
import { getKPI, getForecast } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import MonitoringDashboard from '../components/MonitoringDashboard'

const Dashboard = () => {
  const [kpiData, setKpiData] = useState(null)
  const [forecastData, setForecastData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [kpiResponse, forecastResponse] = await Promise.all([
        getKPI(),
        getForecast()
      ])
      setKpiData(kpiResponse)
      setForecastData(forecastResponse.forecast || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Dashboard</h1>
        <p className="text-muted-foreground mt-2">Financials & Utilization Overview</p>
      </div>

      {kpiData && (
        <BenchGauge
          benchBurn={kpiData.bench_burn}
          utilization={kpiData.utilization}
        />
      )}

      {/* Revenue Forecast Chart */}
      <div className="bg-background rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-primary mb-4">Revenue Forecast</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={forecastData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="revenue" stroke="#4F46E5" name="Revenue" />
            <Line type="monotone" dataKey="saved" stroke="#10B981" name="Revenue Saved" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Quick Stats */}
      {kpiData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-background rounded-lg shadow-md p-6">
            <div className="text-sm text-muted-foreground">Total Employees</div>
            <div className="text-3xl font-bold text-primary mt-2">
              {kpiData.utilization.total_employees}
            </div>
          </div>
          <div className="bg-background rounded-lg shadow-md p-6">
            <div className="text-sm text-muted-foreground">Active Projects</div>
            <div className="text-3xl font-bold text-primary mt-2">
              {kpiData.projects.active}
            </div>
          </div>
          <div className="bg-background rounded-lg shadow-md p-6">
            <div className="text-sm text-muted-foreground">Bench Utilization</div>
            <div className="text-3xl font-bold text-primary mt-2">
              {kpiData.utilization.bench_utilization}%
            </div>
          </div>
          <div className="bg-background rounded-lg shadow-md p-6">
            <div className="text-sm text-muted-foreground">Allocated Resources</div>
            <div className="text-3xl font-bold text-primary mt-2">
              {kpiData.utilization.allocated}
            </div>
          </div>
        </div>
      )}

      <MonitoringDashboard />
    </div>
  )
}

export default Dashboard
