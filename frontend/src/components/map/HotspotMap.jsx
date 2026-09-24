import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

const HotspotMap = ({ hotspots = [] }) => {
  const center = [20.5937, 78.9629]

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Demand Hotspots</h3>
      <div className="rounded-lg overflow-hidden" style={{ height: '400px' }}>
        <MapContainer center={center} zoom={5} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          {hotspots.map((spot, idx) => (
            <CircleMarker
              key={idx}
              center={[20 + idx * 0.5, 78 + idx * 0.5]}
              radius={Math.min(spot.count * 2, 30)}
              pathOptions={{
                color: spot.priority === 'High' ? '#ef4444' : '#f59e0b',
                fillOpacity: 0.5,
              }}
            >
              <Popup>
                <strong>{spot.location}</strong>
                <br />
                Complaints: {spot.count}
                <br />
                Priority: {spot.priority}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
}

export default HotspotMap