---
name: optimistic-updates
description: >
  Apply optimistic UI updates for mutations in the Mender portals (Next.js 16 App
  Router, React 19, Server Actions, sonner toasts). Use when building or modifying
  any feature that calls a Server Action to mutate data — status changes, rep/owner
  assignment, list add/remove/toggle, form submits — and the current code waits on
  `useTransition` + `router.refresh()` before the UI reflects the change. Also use
  when reviewing a PR that adds a mutation and asking "should this be optimistic?"
  Covers: the useOptimistic + useTransition pattern for this stack, rollback and
  reconciliation on error, when NOT to go optimistic (irreversible/high-risk writes),
  and a full grounded before/after example.
---

# Optimistic UI Updates

Update the UI immediately when a user triggers a mutation, before the Server Action
resolves — then let the real server state reconcile (or roll back) automatically.
Both portals are React 19 / Next.js 16 App Router, so `useOptimistic` is available
and is the standard for this codebase (not swr's `optimisticData`, not TanStack
Query — neither is used here; data fetching is `swr` for reads, Server Actions for
writes).

## Decision: optimistic or not?

| Use optimistic | Leave as request → wait → refresh |
|---|---|
| Fast, near-certain-to-succeed writes | Multi-step or slow server work (file generation, external API calls) |
| Reversible by re-doing the action | Irreversible or hard to undo (locking a period, deleting) |
| Low blast radius if it fails (one row, one field) | Financial/compliance-sensitive (commission locks, payouts) |
| The user is waiting on it to feel the UI respond | The user already expects to wait (a "Generate" / "Lock" button) |

Grounded examples from this codebase:
- **Optimistic-worthy**: `assignments-view.tsx` + `assignment-dialog.tsx` (`src/components/sales/commissions/`) — saving a customer's owning rep. Reversible (just reassign again), low blast radius (one row), currently pays a full `router.refresh()` round-trip just to show the new rep name. See `references/nextjs-worked-example.md` for the full before/after.
- **Correctly NOT optimistic, leave alone**: `close-period-card.tsx` — `generatePacket()` and `lockPeriod()`. Locking freezes rates/plans/assignments/load data for the period and never reopens; the UI must reflect the server's real success/failure, not a guess. Keep the existing `useTransition` → toast → `router.refresh()` pattern for writes like this.

When unsure, default to NOT optimistic. A wrong optimistic update that silently reverts is more confusing than a half-second wait.

## The pattern for this stack

```tsx
'use client';
import { useOptimistic, useTransition } from 'react';
import { toast } from 'sonner';
import { someAction } from '@/app/(app)/.../actions';

export function RowList({ rows }: { rows: Row[] }) {
  const [optimisticRows, setOptimisticRow] = useOptimistic(
    rows,
    (state, updated: Row) => state.map((r) => (r.id === updated.id ? updated : r)),
  );
  const [isPending, startTransition] = useTransition();

  function handleSave(updated: Row) {
    startTransition(async () => {
      setOptimisticRow(updated); // renders immediately
      const result = await someAction(updated);
      if (!result.ok) {
        toast.error('Could not save', { description: result.error });
        // No manual rollback call needed — useOptimistic reverts to `rows`
        // automatically once this transition ends and `rows` hasn't changed.
      }
      // On success, the parent Server Component must actually refetch (router.refresh()
      // or revalidatePath in the action) so `rows` catches up to the optimistic guess —
      // otherwise the optimistic value reverts to the STALE pre-mutation value once the
      // transition settles.
    });
  }

  return rows.map((_, i) => <Row key={optimisticRows[i].id} row={optimisticRows[i]} onSave={handleSave} />);
}
```

Key mechanics, specific to this stack:
- `setOptimisticRow` **must** be called inside the `startTransition` callback (or inside an action passed to it) — calling it outside a transition throws.
- `useOptimistic`'s state is derived from its first argument (`rows` here, the real server-backed prop). It automatically snaps back to `rows` when the transition that set it completes — **only if `rows` itself has been updated to match**. If the mutation succeeds but nothing causes the parent Server Component to re-render with fresh data (`router.refresh()`, a revalidated `swr` key, or a `revalidatePath`/`revalidateTag` call inside the Server Action), the optimistic value reverts to the old value even though the write succeeded on the server. Always pair an optimistic update with a real revalidation trigger.
- On error: don't call `setOptimisticRow` with a "rolled back" value — just `toast.error()` and let the natural revert happen (see above). Manual rollback state is unnecessary complexity `useOptimistic` already handles.
- Keep using the existing `sonner` `toast.success()/error()` calls for success/failure messaging — optimistic rendering changes *when* the UI updates, not how errors are surfaced.

## Worked example

`references/nextjs-worked-example.md` walks through converting the real
`assignments-view.tsx` / `assignment-dialog.tsx` save flow to this pattern —
lifting the optimistic state to the list (`AssignmentsView`) since that's what
owns `rows`, and having the dialog call a passed-down `onOptimisticSave` instead
of calling `router.refresh()` itself.

## Gotchas

- `useOptimistic` requires the component to be inside a `<Suspense>` boundary or
  hydrated client component tree that already receives `rows` as a real prop —
  it's a transform over existing state, not a data source of its own.
- Don't wrap the Server Action call itself in a `try/catch` that swallows the
  error before `toast.error()` runs — the existing action return shape in this
  codebase is `{ ok: true, ... } | { ok: false, error: string }`, not a thrown
  exception, so check `result.ok` (see `references/nextjs-worked-example.md`).
- Cascading server-side effects (e.g. commission rep-assignment cascade to child
  customers, gh#60) are NOT knowable client-side — the optimistic update can only
  guess the one row the user directly edited. The revalidation step after success
  is what brings in any server-side side effects the client couldn't predict.
- Don't reach for optimistic updates on a mutation that already feels instant
  (a single fast `UPDATE` with no visible latency) — it's added complexity for no
  perceptible UX gain. Reserve it for mutations where the round-trip is
  noticeable.
