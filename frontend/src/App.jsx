import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Canvas from './pages/Canvas'
import TalentLab from './pages/TalentLab'
import Pipeline from './pages/Pipeline'
import EmployeeList from './pages/EmployeeList'
import EmployeeView from './pages/EmployeeView'
import ProjectView from './pages/ProjectView'
import Employees from './pages/Employees'
import Projects from './pages/Projects'
import Risk from './pages/Risk'
import AllocationReport from './pages/AllocationReport'

function Navigation() {
  const location = useLocation()
  
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }
  
  const getLinkClassName = (path) => {
    const baseClasses = "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
    if (isActive(path)) {
      return `${baseClasses} border-indigo-500 text-indigo-600`
    }
    return `${baseClasses} border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700`
  }

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-indigo-600">BenchCraft AI</h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/"
                className={getLinkClassName('/')}
              >
                Dashboard
              </Link>
              <Link
                to="/market"
                className={getLinkClassName('/market')}
              >
                Marketplace
              </Link>
              <Link
                to="/canvas"
                className={getLinkClassName('/canvas')}
              >
                Canvas
              </Link>
              <Link
                to="/talent-lab"
                className={getLinkClassName('/talent-lab')}
              >
                Talent Lab
              </Link>
              <Link
                to="/pipeline"
                className={getLinkClassName('/pipeline')}
              >
                Project
              </Link>
              <Link
                to="/employees"
                className={getLinkClassName('/employees')}
              >
                Employees
              </Link>
              <Link
                to="/risk"
                className={getLinkClassName('/risk')}
              >
                Risk
              </Link>
              <Link
                to="/allocation-report"
                className={getLinkClassName('/allocation-report')}
              >
                Allocation Report
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Global Navigation */}
        <Navigation />

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/market" element={<Market />} />
            <Route path="/canvas" element={<Canvas />} />
            <Route path="/talent-lab" element={<TalentLab />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/employees/list" element={<EmployeeList />} />
            <Route path="/employees/:id" element={<EmployeeView />} />
            <Route path="/projects/:id" element={<ProjectView />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/risk" element={<Risk />} />
            <Route path="/allocation-report" element={<AllocationReport />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
