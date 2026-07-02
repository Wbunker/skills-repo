# Worked example: assignments-view.tsx save flow

Source (internal_portal, feature 078/084): `src/components/sales/commissions/assignments-view.tsx`
+ `src/components/sales/commissions/assignment-dialog.tsx`. This is a real, currently-shipping
list + edit-dialog pattern that repeats across both portals (list owns rows, a dialog child
mutates one row, the list waits for a full `router.refresh()` to show the change).

## Before

`AssignmentsView` renders a table from a `rows` prop. Row edit opens `AssignmentDialog`. On
save, the dialog calls `saveAssignment()` directly, closes itself, and either calls an
`onSaved` callback or calls `router.refresh()` itself:

```tsx
// assignment-dialog.tsx (existing)
async function handleSave() {
  if (!canSave) return;
  setSubmitting(true);
  setError(null);
  try {
    const result = await saveAssignment({ customerId: customer.customerId, /* ... */ });
    if (!result.ok) {
      setError(result.error);
      return;
    }
    onOpenChange(false);
    if (onSaved) {
      const rep = reps.find((r) => r.userId === Number(owningUserId));
      if (rep) onSaved(rep);
    } else {
      router.refresh(); // <-- full round trip before the table shows the new rep
    }
  } catch {
    setError('Failed to save assignment');
  } finally {
    setSubmitting(false);
  }
}
```

Between clicking Save and `router.refresh()` completing, the table still shows the old rep —
on a slow connection this is a visible stall for a one-field change.

## After

Lift the optimistic state to `AssignmentsView` (it already owns `rows`, which is exactly what
`useOptimistic` needs as its base state), and have the dialog report the *chosen values*
upward instead of driving navigation itself.

```tsx
// assignments-view.tsx
import { useOptimistic, useTransition } from 'react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { saveAssignment } from '@/app/(app)/sales/operations/commissions/actions';

export function AssignmentsView({ rows, reps }: AssignmentsViewProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [optimisticRows, setOptimisticRow] = useOptimistic(
    rows,
    (state, patch: { customerId: number; owningUserId: number; ownerName: string; accountTypeCode: string }) =>
      state.map((r) =>
        r.customerId === patch.customerId
          ? { ...r, owningUserId: patch.owningUserId, owningRepName: patch.ownerName, accountTypeCode: patch.accountTypeCode, assignmentSource: 'explicit' as const }
          : r,
      ),
  );

  // ...existing search/filter state, unchanged, but derive `filtered` from `optimisticRows`
  // instead of `rows`.

  function handleAssignmentSave(input: {
    customerId: number;
    owningUserId: number;
    accountTypeCode: AccountTypeCode;
    changeReason?: string;
    effectiveFrom?: string;
  }) {
    const rep = reps.find((r) => r.userId === input.owningUserId);
    startTransition(async () => {
      if (rep) {
        setOptimisticRow({
          customerId: input.customerId,
          owningUserId: input.owningUserId,
          ownerName: rep.name,
          accountTypeCode: input.accountTypeCode,
        });
      }
      const result = await saveAssignment(input);
      if (!result.ok) {
        toast.error('Could not save assignment', { description: result.error });
        return; // optimisticRows reverts to `rows` once this transition ends
      }
      router.refresh(); // brings in the real row + any cascade side effects (gh#60)
    });
  }

  // Pass handleAssignmentSave down instead of letting the dialog call
  // saveAssignment()/router.refresh() itself:
  // <AssignmentDialog ... onSave={handleAssignmentSave} submitting={isPending} />
}
```

```tsx
// assignment-dialog.tsx — becomes a pure form, mutation moves to the parent
export interface AssignmentDialogProps {
  // ...customer, reps, open, onOpenChange as before
  onSave: (input: {
    customerId: number;
    owningUserId: number;
    accountTypeCode: AccountTypeCode;
    changeReason?: string;
    effectiveFrom?: string;
  }) => void;
  submitting: boolean;
}

function handleSaveClick() {
  if (!canSave) return;
  onSave({
    customerId: customer.customerId,
    owningUserId: Number(owningUserId),
    accountTypeCode: accountTypeCode as AccountTypeCode,
    changeReason: reason.trim() || undefined,
    effectiveFrom: effectiveFrom || undefined,
  });
  onOpenChange(false); // close immediately — the row updates optimistically behind it
}
```

## What changed and why

- **Error surfacing moved from an inline dialog `Alert` to a `toast`.** Once the dialog closes
  immediately (optimistic UX expects that), there's no dialog left to show an inline error in —
  the failure has to reach the user via toast instead, same as `close-period-card.tsx` already
  does for its non-optimistic mutations.
- **`saveAssignment` moved from the dialog to the list.** The list owns `rows`/`useOptimistic`;
  the mutation must be triggered from wherever the optimistic state lives, or the update-and-
  revert lifecycle doesn't line up with the transition.
- **`router.refresh()` still happens on success.** `useOptimistic` renders a *guess*; it doesn't
  replace the need for real data. In this feature specifically, saving an assignment can
  cascade to child customers server-side (gh#60) — the optimistic guess only ever covers the
  one row the user edited, so the post-success refresh is what makes cascaded rows correct.
- **On failure, nothing is done beyond the toast.** No manual "set it back" call — `rows` never
  changed, so `useOptimistic` reverts to it automatically once `startTransition`'s callback
  finishes.
