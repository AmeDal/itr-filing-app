---
name: react-frontend
description: Activate this skill when the user is working on frontend React code, UI components, pages, routing, or API integration. This skill provides component patterns, sub-component extraction rules, and API service conventions.
---

# React Frontend Skill

## Project Structure

```
frontend/
├── src/
│   ├── pages/           # One component per page
│   ├── components/
│   │   ├── shared/      # Reusable UI elements
│   │   └── <page>/      # Page-specific sub-components
│   ├── services/        # Centralized API calls
│   ├── hooks/           # Custom React hooks
│   ├── styles/          # CSS files
│   └── App.jsx          # Root component + routing
```

## Component Patterns

### Page Component
```jsx
// pages/DashboardPage.jsx
import React from 'react';
import { DashboardSummary } from '../components/dashboard/DashboardSummary';
import { DashboardCharts } from '../components/dashboard/DashboardCharts';

const DashboardPage = () => {
  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>
      <DashboardSummary />
      <DashboardCharts />
    </div>
  );
};

export default DashboardPage;
```

### Sub-Component Extraction Rules

Extract a sub-component when:
- A page has **multiple tabs** → one component per tab
- A page has **distinct sections** → one component per section
- A **UI pattern repeats** across pages → shared component
- A component exceeds **~300 lines**

```jsx
// components/dashboard/DashboardSummary.jsx
import React from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';

export const DashboardSummary = () => {
  const { summary, loading } = useDashboardData();

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="dashboard-summary">
      <div className="stat-card">
        <span className="label">Total Filed</span>
        <span className="value">{summary.totalFiled}</span>
      </div>
    </div>
  );
};
```

## API Service Pattern

**Never call `fetch` or `axios` directly in components.** Centralize in `services/`.

```javascript
// services/userService.js
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const userService = {
  getProfile: async (userId) => {
    const response = await fetch(`${API_BASE}/users/${userId}`);
    if (!response.ok) throw new Error('Failed to fetch profile');
    return response.json();
  },

  updateProfile: async (userId, data) => {
    const response = await fetch(`${API_BASE}/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update profile');
    return response.json();
  },
};
```

## Custom Hook Pattern

Extract data-fetching and stateful logic into hooks:

```javascript
// hooks/useDashboardData.js
import { useState, useEffect } from 'react';
import { dashboardService } from '../services/dashboardService';

export const useDashboardData = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await dashboardService.getSummary();
        setSummary(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return { summary, loading, error };
};
```

## Routing

```jsx
// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

## Decision Flow

```
User Interaction → Page Component → Sub-Components
                                       ↓
                                   Custom Hook → API Service → Backend
```
