import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
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

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Global Navigation */}
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
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/market"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Marketplace
                  </Link>
                  <Link
                    to="/canvas"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Canvas
                  </Link>
                  <Link
                    to="/talent-lab"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Talent Lab
                  </Link>
                  <Link
                    to="/pipeline"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Pipeline
                  </Link>
                  <Link
                    to="/employees"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Employees
                  </Link>
                  <Link
                    to="/risk"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Risk
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

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
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
