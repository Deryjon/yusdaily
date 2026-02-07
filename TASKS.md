# Planner Replan: Frontend UI + Backend (Python) Task List

This document outlines the concrete implementation tasks for the two requested features:

1. **Daily Activities (recurring habits + progress)**
2. **Wallet Analysis (daily purchases + analytics)**

---

## 1) Daily Activities (Recurring Habits + Progress)

### Backend (Python / FastAPI) — Habits
- [ ] **Data model**
  - Add a `habit` (daily activity) entity:
    - `id`, `user_id`, `title`, `description`, `target_per_day` (int, default 1),
      `is_active` (bool), `created_at`, `updated_at`.
  - Add a `habit_entry` (daily completion) entity:
    - `id`, `habit_id`, `user_id`, `date`, `completed_count` (int), `notes` (optional),
      unique constraint on `(habit_id, date)`.
- [ ] **Schemas**
  - Pydantic schemas for create/update/read of `habit` and `habit_entry`.
- [ ] **API endpoints**
  - `GET /habits` (list)
  - `POST /habits` (create)
  - `PATCH /habits/{habit_id}` (update)
  - `DELETE /habits/{habit_id}` (archive or delete)
  - `GET /habits/{habit_id}/entries?from=YYYY-MM-DD&to=YYYY-MM-DD`
  - `POST /habits/{habit_id}/entries` (create/update daily completion)
- [ ] **Services**
  - Ensure idempotent upsert for a daily entry (same date updates the count).
  - Calculate progress summaries (weekly/monthly completion rate).
- [ ] **Migrations**
  - Alembic migration for new tables and indexes.
- [ ] **Auth + permissions**
  - Enforce user ownership on all habit and entry actions.

### Frontend (UI) — Habits
- [ ] **Daily activities settings page**
  - Add/edit/remove recurring activities (habit list with form).
  - Set “target per day” (e.g., 1, 2, 3).
- [ ] **Today view**
  - Show today’s activities as checkboxes with progress counters.
  - Support “mark done” and incrementing count for multi-target habits.
- [ ] **Progress & stats**
  - Weekly and monthly progress charts (completion rate).
  - Streak display (optional).
- [ ] **Empty state**
  - If no habits exist, guide user to set up daily activities.

---

## 2) Wallet Analysis (Daily Purchases + Analytics)

### Backend (Python / FastAPI) — Wallet
- [ ] **Data model**
  - Add `purchase` entity:
    - `id`, `user_id`, `amount`, `currency`, `category`, `note`,
      `purchase_date`, `created_at`.
- [ ] **Schemas**
  - Pydantic schemas for create/update/read of `purchase`.
- [ ] **API endpoints**
  - `GET /purchases?from=YYYY-MM-DD&to=YYYY-MM-DD` (list/filter)
  - `POST /purchases` (create)
  - `PATCH /purchases/{purchase_id}` (update)
  - `DELETE /purchases/{purchase_id}` (delete)
  - `GET /purchases/summary?period=week|month` (aggregates by day/category)
- [ ] **Services**
  - Aggregations for daily totals, category totals, and spending trends.
- [ ] **Migrations**
  - Alembic migration for purchases table and indexes.
- [ ] **Auth + permissions**
  - Enforce user ownership on all purchase actions.

### Frontend (UI) — Wallet
- [ ] **Add purchase flow**
  - Form to add amount, category, date, and optional note.
- [ ] **Purchases list**
  - Filter by date range and category.
  - Inline edit and delete actions.
- [ ] **Wallet analytics**
  - Charts: daily spend, category breakdown, monthly total.
  - Summary cards (total spend, average per day).
- [ ] **Empty state**
  - Onboarding guidance for first purchase.

---

## 3) Shared UX/Tech Tasks

- [ ] **Navigation**
  - Add navigation tabs or menu entries for “Daily Activities” and “Wallet”.
- [ ] **Loading & error states**
  - Consistent loading spinners and error messages for API failures.
- [ ] **Validation**
  - Input validation on amounts (wallet) and habit target counts.
- [ ] **Localization**
  - Ensure text is ready for future localization (i18n-friendly).
