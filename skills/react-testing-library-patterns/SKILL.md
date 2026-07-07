---
name: react-testing-library-patterns
description: Vitest + React Testing Library — component testing, user interactions, async behavior
---

# React Testing Library Patterns

Testing patterns for React components using Vitest and React Testing Library.

## When to use

- You need to test React component behavior
- You want to verify user interactions work correctly
- You need to test async loading states and error handling

## Instructions

1. **Read the component** — understand props, state, effects, and event handlers
2. **Identify test scenarios**:
   - Render with default props → verify content
   - User interaction (click, type, submit) → verify response
   - Async behavior (loading → success / error) → verify states
   - Edge cases (empty data, error responses, missing props)
3. **Query by accessibility role** — prefer `getByRole`, `getByLabelText`, `getByText`
4. **Use `userEvent`** over `fireEvent` for realistic interactions
5. **Test behavior, not implementation** — don't assert on internal state

## Example

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Counter } from './Counter';

describe('Counter', () => {
  it('increments when clicked', async () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });
    await userEvent.click(button);
    expect(screen.getByText('1')).toBeInTheDocument();
  });
});
```

## Patterns to avoid

- Testing internal state or implementation details
- Snapshot testing entire component trees (fragile)
- Using `container.querySelector` instead of accessible queries
- Mocking child components (test the real composition)
