import { useState, useEffect } from 'react'
import ReactFlow, { Background, Controls, MiniMap } from 'react-flow-renderer'

const Canvas = () => {
  const [elements, setElements] = useState([])

  // Mock data for timeline view
  useEffect(() => {
    // In production, this would fetch from API
    const mockElements = [
      {
        id: '1',
        type: 'input',
        data: { label: 'Project Alpha' },
        position: { x: 100, y: 100 },
      },
      {
        id: '2',
        type: 'default',
        data: { label: 'Employee 1' },
        position: { x: 300, y: 100 },
      },
      {
        id: 'e1-2',
        source: '1',
        target: '2',
        animated: true,
      },
    ]
    setElements(mockElements)
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Canvas</h1>
        <p className="text-muted-foreground mt-2">Timeline/Gantt view of allocations</p>
      </div>

      <div className="bg-white rounded-lg shadow-md" style={{ height: '600px' }}>
        <ReactFlow
          elements={elements}
          style={{ width: '100%', height: '100%' }}
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> This is a placeholder. In production, this would show a timeline view with:
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Employee rows (timeline tracks)</li>
            <li>Active project nodes</li>
            <li>Ghost project nodes (from pipeline)</li>
            <li>Drag-and-drop functionality to trigger allocation</li>
          </ul>
        </p>
      </div>
    </div>
  )
}

export default Canvas
