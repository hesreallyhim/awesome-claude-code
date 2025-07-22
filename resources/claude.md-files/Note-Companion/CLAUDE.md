# File Organizer 2000 - Developer Guide

## Styling Guidelines

To avoid styling conflicts between Obsidian's styles and our plugin, follow these guidelines:

### 1. Tailwind Configuration

- The Tailwind configuration has been updated to add the `fo-` prefix to all Tailwind classes.
- This ensures our styles don't conflict with Obsidian's built-in styles.

### 2. Component Style Isolation

For all new components:

1. Import the `StyledContainer` component from components/ui/utils.tsx:
```tsx
import { StyledContainer } from "../../components/ui/utils";
```

2. Wrap your component's root element with StyledContainer:
```tsx
return (
  <StyledContainer>
    {/* Your component content */}
  </StyledContainer>
);
```

3. Use the `tw()` function for class names to ensure proper prefixing:
```tsx
import { tw } from "../../lib/utils";

// ...

<div className={tw("bg-white rounded-lg p-4")}>
  {/* content */}
</div>
```

4. For conditional classes, combine `tw()` with string interpolation:
```tsx
<div className={tw(`bg-white rounded-lg ${isActive ? "border-blue-500" : "border-gray-200"}`)}>
  {/* content */}
</div>
```

### 3. Using Existing Components

Our UI components in `components/ui/` are already configured to use the proper prefixing.
Always prefer using these components when available:

- Button
- Card
- Dialog
- Badge
- etc.

### 4. Troubleshooting Style Issues

If you encounter style conflicts:

1. Check if the component is wrapped in a `StyledContainer`
2. Verify all classNames use the `tw()` function
3. Inspect the rendered HTML to see if classes have the `fo-` prefix
4. Add more specific reset styles to the `.fo-container` class in styles.css if needed