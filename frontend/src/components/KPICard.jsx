export default function KPICard({ label, value }) {
  return (
    <div className="card">
      <h4>{label}</h4>
      <p>{value}</p>
    </div>
  )
}
