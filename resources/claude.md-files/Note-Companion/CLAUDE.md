# File Organizer 2000 - Developer Guide

## Styling Guidelines

To avoid styling conflicts between Obsidian's styles and our plugin, follow these guidelines:

### 1. Tailwind Configuration

- Tailwind is configured with custom Obsidian CSS variables
- Preflight is disabled to avoid conflicts with Obsidian's global styles
- Component isolation is achieved through `StyledContainer` wrapper
- **No prefix needed** - we removed the `fo-` prefix to allow JIT compilation to work properly

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

3. Use the `tw()` function (alias for `cn()`) for class names with proper merging:
```tsx
import { tw } from "../../lib/utils";

// ...

<div className={tw("bg-white rounded-lg p-4")}>
  {/* content */}
</div>
```

4. For conditional classes, use `tw()` with multiple arguments:
```tsx
<div className={tw("bg-white rounded-lg", isActive && "border-blue-500")}>
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
3. Ensure no hardcoded CSS class names are being added (like `card` or `chat-component`)
4. Add more specific reset styles to the `.fo-container` class in styles.css if needed
5. Use browser dev tools to check if Tailwind classes are being applied

## Audio Transcription

### File Size Handling

The audio transcription feature uses a two-tier approach to handle files of different sizes:

1. **Small Files (< 4MB)**: Direct upload via multipart/form-data
   - Fastest method for smaller audio files
   - Direct to transcription API endpoint
   
2. **Large Files (4MB - 25MB)**: Pre-signed URL upload to R2
   - Bypasses Vercel's 4.5MB body size limit
   - Plugin gets a pre-signed URL from `/api/create-upload-url`
   - Uploads directly to R2 cloud storage
   - Backend downloads from R2 and transcribes
   - Reuses existing R2 infrastructure from file upload flow

3. **Files > 25MB**: Error message
   - OpenAI Whisper API has a hard 25MB limit
   - Users are instructed to compress or split audio

### Implementation Details

**Plugin-side** (`packages/plugin/index.ts`):
- `transcribeAudio()` (line ~515): Routes to appropriate upload method based on file size
- `transcribeAudioViaPresignedUrl()` (line ~547): Handles large file upload via R2

**Server-side**:
- `packages/web/app/api/(newai)/transcribe/route.ts`: 
  - Handles both direct uploads and pre-signed URL flow
  - `handlePresignedUrlTranscription()`: Downloads from R2 and transcribes
- `packages/web/app/api/create-upload-url/route.ts`: 
  - Generates pre-signed S3/R2 URLs (shared with file upload flow)

### Benefits of Pre-signed URL Approach

- ✅ No Vercel body size limitations (bypasses API gateway)
- ✅ Reuses existing R2 infrastructure
- ✅ Scalable to larger files (up to 25MB OpenAI limit)
- ✅ Better memory usage (streaming from R2)
- ✅ Same pattern as mobile app file uploads
