import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function AnalyticsDashboard({ refreshTrigger }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/analytics');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [refreshTrigger]);

  if (loading) {
    return (
      <div className="card" style={{ marginTop: '20px', textAlign: 'center', padding: '40px' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading financial analytics...</p>
      </div>
    );
  }

  if (!data || !data.chart_data) {
    return null;
  }

  const { intentional_savings_rate } = data.metrics || {};

  return (
    <div className="card glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '10px' }}>Financial Analytics</h2>
      
      {intentional_savings_rate !== undefined && (
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.9rem' }}>Intentional Savings Rate</p>
          <h1 style={{ color: 'var(--primary)', margin: '5px 0 0 0', fontSize: '2.5rem' }}>
            {intentional_savings_rate.toFixed(1)}%
          </h1>
        </div>
      )}

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <BarChart data={data.chart_data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="name" stroke="#888" tick={{ fill: '#888' }} />
            <YAxis stroke="#888" tick={{ fill: '#888' }} tickFormatter={(value) => `€${value}`} />
            <Tooltip 
              cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
              contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: 'none', borderRadius: '8px' }}
              itemStyle={{ color: 'var(--text-primary)' }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {data.chart_data.map((entry, index) => {
                let color = 'var(--primary)';
                if (entry.name === 'Income') color = '#10B981'; // Green
                if (entry.name === 'Expenses') color = '#EF4444'; // Red
                if (entry.name === 'Savings') color = '#8B5CF6'; // Purple
                return <Cell key={`cell-${index}`} fill={color} />;
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
