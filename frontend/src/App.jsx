import { useState } from 'react';
import AnalyticsDashboard from './AnalyticsDashboard';
import './index.css';

function App() {
  const [formData, setFormData] = useState({
    amount: '',
    category: 'Expense',
    description: ''
  });
  
  const [showConfirm, setShowConfirm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleInitialSubmit = async (e) => {
    e.preventDefault();
    if (!formData.amount || !formData.description) {
      alert("Please fill in all required fields.");
      return;
    }
    
    setIsSubmitting(true);
    setStatusMessage(null);
    try {
      const response = await fetch('/api/validate-transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(formData.amount),
          category: formData.category,
          description: formData.description
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        // FastAPI validation errors (e.g., negative amount)
        throw new Error(data.detail || 'Something went wrong with the Agent.');
      }
      
      if (data.status === 'approved') {
        setStatusMessage({ type: 'success', text: data.user_message });
        setFormData({ amount: '', category: 'Expense', description: '' });
        setRefreshTrigger(prev => prev + 1);
      } else {
        // Warning or rejected
        setStatusMessage({ type: data.status === 'rejected' ? 'error' : 'warning', text: data.user_message });
        setShowConfirm(true);
      }
    } catch (error) {
      setStatusMessage({ type: 'error', text: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const confirmAndSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/force-submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(formData.amount),
          category: formData.category,
          description: formData.description
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong with the forced submit.');
      }
      
      setStatusMessage({ type: 'success', text: 'Intentional record tracked successfully!' });
      setFormData({ amount: '', category: 'Expense', description: '' });
      setShowConfirm(false);
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      setStatusMessage({ type: 'error', text: error.message });
      setShowConfirm(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Intentional Spending</h1>
        <p>Track your flow, shape your future.</p>
      </header>

      {statusMessage && (
        <div className={`status-banner ${statusMessage.type}`}>
          {statusMessage.text}
        </div>
      )}

      <div className="main-layout">
        <div className="form-section">
          <div className="card glass-panel">
            <h2 className="card-title">Track a Spend</h2>
            <form onSubmit={handleInitialSubmit} className="tracking-form">
              <div className="form-group">
                <label htmlFor="amount">Amount (€)</label>
                <input 
                  type="number" 
                  id="amount" 
                  name="amount" 
                  value={formData.amount} 
                  onChange={handleChange} 
                  step="0.01"
                  min="0.01"
                  placeholder="0.00"
                  required 
                />
              </div>

              <div className="form-group">
                <label htmlFor="category">Category</label>
                <select 
                  id="category" 
                  name="category" 
                  value={formData.category} 
                  onChange={handleChange}
                >
                  <option value="Expense">Expense</option>
                  <option value="Income">Income</option>
                  <option value="Savings">Savings</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea 
                  id="description" 
                  name="description" 
                  value={formData.description} 
                  onChange={handleChange} 
                  placeholder="What was this intentional spend for?"
                  rows="3"
                  required 
                />
              </div>

              <button type="submit" className="btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Processing AI...' : 'Review & Track'}
              </button>
            </form>
          </div>
        </div>

        <div className="analytics-section">
          <AnalyticsDashboard refreshTrigger={refreshTrigger} />
        </div>
      </div>

      {showConfirm && (
        <div className="modal-overlay">
          <div className="modal glass-panel">
            <h2>Confirm Intent</h2>
            
            {statusMessage && (
              <div className={`status-banner ${statusMessage.type}`} style={{marginBottom: "1.5rem", fontSize: "0.9rem"}}>
                {statusMessage.text}
              </div>
            )}

            <div className="summary-details">
              <div className="summary-item">
                <span className="label">Amount:</span>
                <span className="value">${parseFloat(formData.amount).toFixed(2)}</span>
              </div>
              <div className="summary-item">
                <span className="label">Category:</span>
                <span className={`badge ${formData.category.toLowerCase()}`}>{formData.category}</span>
              </div>
              <div className="summary-item">
                <span className="label">Description:</span>
                <span className="value">{formData.description}</span>
              </div>
            </div>
            
            <div className="modal-actions">
              <button 
                onClick={() => setShowConfirm(false)} 
                className="btn-secondary"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button 
                onClick={confirmAndSubmit} 
                className="btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Processing...' : 'Confirm Anyway'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
