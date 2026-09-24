import { useEffect, useState } from 'react'
import CategoryChart from '../components/analytics/CategoryChart'
import HotspotMap from '../components/map/HotspotMap'
import { analyticsService } from '../services/analyticsService'

const Analytics = () => {
  const [categories, setCategories] = useState(null)
  const [hotspots, setHotspots] = useState(null)

  useEffect(() => {
    analyticsService.getCategories().then(setCategories).catch(() => {})
    analyticsService.getHotspots().then(setHotspots).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Analytics</h1>
        <p className="text-sm text-slate-500 mt-1">Deep insights into citizen demand patterns</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CategoryChart data={categories} />
        <HotspotMap hotspots={hotspots?.hotspots || []} />
      </div>
    </div>
  )
}

export default Analytics