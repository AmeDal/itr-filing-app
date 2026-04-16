---
description: Step-by-step guide to add a new React page component following project conventions.
---

# Add New Page

Follow these steps **in order** when adding a new page to the frontend.

---

## Step 1: Create Page Component

Create a new file in `frontend/src/pages/` named after the page (e.g., `ProfilePage.jsx`).

1. One component per page — this is the top-level page component
2. Keep it focused on layout and composition
3. If the page has tabs or distinct sections, create sub-components immediately

```jsx
import React from 'react';
import { ProfileHeader } from '../components/profile/ProfileHeader';
import { ProfileTabs } from '../components/profile/ProfileTabs';

const ProfilePage = () => {
  return (
    <div className="profile-page">
      <ProfileHeader />
      <ProfileTabs />
    </div>
  );
};

export default ProfilePage;
```

---

## Step 2: Create Sub-Components (if needed)

If the page has multiple sections, create sub-components in `frontend/src/components/<page-name>/`.

- One file per logical section or tab
- Keep components under ~300 lines
- Extract reusable elements into `frontend/src/components/shared/`

---

## Step 3: Create API Service (if needed)

If the page calls backend APIs, create or update `frontend/src/services/<domain>Service.js`.

- Centralize all API calls — never use `fetch`/`axios` directly in components
- Use async/await patterns

```javascript
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export const getProfile = async (userId) => {
  const response = await fetch(`${API_BASE}/users/${userId}`);
  return response.json();
};
```

---

## Step 4: Add Route

Register the new page in your router configuration (e.g., `App.jsx` or `router.jsx`).

---

## Step 5: Update AGENTS.md

Add entries for all new files created.

---

## Checklist

- [ ] Page component created (one per page)
- [ ] Sub-components extracted for tabs/sections
- [ ] API service created (centralized, async)
- [ ] Route registered
- [ ] `AGENTS.md` updated
