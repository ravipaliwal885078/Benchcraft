import { TrendingUp, Users, DollarSign } from 'lucide-react'

const BenchGauge = ({ benchBurn, utilization }) => {
  const utilizationRate = utilization?.utilization_rate || 0
  const benchCount = benchBurn?.bench_count || 0
  const monthlyCost = benchBurn?.total_monthly_cost || 0

  // Calculate gauge percentage (inverse of utilization)
  const benchPercentage = 100 - utilizationRate

  return (
    <div className="bg-background rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-primary mb-4">Bench Burn Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Bench Count */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <Users className="w-8 h-8 text-destructive" />
          </div>
          <div className="text-3xl font-bold text-primary">{benchCount}</div>
          <div className="text-sm text-muted-foreground">On Bench</div>
        </div>

        {/* Monthly Cost */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <DollarSign className="w-8 h-8 text-warning" />
          </div>
          <div className="text-3xl font-bold text-primary">
            ${(monthlyCost / 1000).toFixed(1)}k
          </div>
          <div className="text-sm text-muted-foreground">Monthly Cost</div>
        </div>

        {/* Utilization Rate */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <TrendingUp className="w-8 h-8 text-success" />
          </div>
          <div className="text-3xl font-bold text-primary">
            {utilizationRate.toFixed(1)}%
          </div>
          <div className="text-sm text-muted-foreground">Utilization</div>
        </div>
      </div>

      {/* Visual Gauge */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">Bench Time</span>
          <span className="text-sm font-medium text-muted-foreground">{benchPercentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-4">
          <div
            className="bg-destructive h-4 rounded-full transition-all duration-300"
            style={{ width: `${benchPercentage}%` }}
          />
        </div>
      </div>
    </div>
  )
}

export default BenchGauge
