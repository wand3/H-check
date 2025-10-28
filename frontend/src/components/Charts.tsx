import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import { useMemo } from 'react';
import type { FhirQueryResponse } from '../schemas/fhirResponse';

export function FhirQueryVisualizer({ data }: { data: FhirQueryResponse }) {
  const patients = data.processed_results.patients;

  const ageBuckets = useMemo(() => {
    const buckets: Record<string, number> = { '0-20': 0, '21-40': 0, '41-60': 0, '61+': 0 };
    patients.forEach((p) => {
      const a = p.age ?? 0;
      if (a <= 20) buckets['0-20']++;
      else if (a <= 40) buckets['21-40']++;
      else if (a <= 60) buckets['41-60']++;
      else buckets['61+']++;
    });
    return Object.entries(buckets).map(([name, count]) => ({ name, count }));
  }, [patients]);

  const genderPie = useMemo(() => {
    const map: Record<string, number> = {};
    patients.forEach((p) => {
      const g = p.gender || 'unknown';
      map[g] = (map[g] || 0) + 1;
    });
    return Object.entries(map).map(([name, value]) => ({ name, value }));
  }, [patients]);

  const COLORS = ['#4f46e5', '#f97316', '#10b981', '#ef4444'];

  return (
    <div className="p-4 bg-white border rounded-md shadow-sm my-3">
      <h3 className="font-medium mb-2">Query: {data.original_query}</h3>
      <p className="text-sm mb-4 text-gray-600">
        Total Patients: {data.processed_results.total_patients} | Execution Time: {data.execution_time}ms
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Patient Table */}
        <div className="lg:col-span-2 overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr>
                <th className="py-1">Name</th>
                <th className="py-1">Age</th>
                <th className="py-1">Gender</th>
                <th className="py-1">Conditions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((p) => (
                <tr key={p.id} className="border-t">
                  <td className="py-1">{p.name}</td>
                  <td className="py-1">{p.age}</td>
                  <td className="py-1 capitalize">{p.gender}</td>
                  <td className="py-1">{p.conditions.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Charts */}
        <div className="space-y-4">
          <div className="h-56">
            <h4 className="font-medium mb-2">Age Distribution</h4>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={ageBuckets}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" name="Patients" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="h-56">
            <h4 className="font-medium mb-2">Gender Breakdown</h4>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie data={genderPie} dataKey="value" nameKey="name" outerRadius={70} label>
                  {genderPie.map((_, i) => (
                    <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
