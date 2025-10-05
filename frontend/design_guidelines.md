# Design Guidelines: Minimal Stock Chat Interface

## Design Approach
**System:** Clean Minimal Design with Chat UI Best Practices
**Justification:** User explicitly requested "minimal," "simple styling," "barebones," and "lightweight" - prioritizing clarity, speed, and distraction-free interaction for financial decision-making.

## Core Design Elements

### A. Color Palette

**Dark Mode (Primary):**
- Background: 240 10% 8% (deep charcoal)
- Surface: 240 8% 12% (chat container)
- User messages: 210 100% 50% (bright blue)
- AI messages: 240 5% 18% (neutral gray surface)
- Text primary: 0 0% 98%
- Text secondary: 240 5% 65%
- Border: 240 8% 20%
- Accent/Loading: 210 100% 50%

**Light Mode:**
- Background: 0 0% 98%
- Surface: 0 0% 100%
- User messages: 210 100% 50%
- AI messages: 240 5% 96%
- Text primary: 240 10% 10%
- Text secondary: 240 5% 45%

### B. Typography
- **Font Family:** System fonts (`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`)
- **Sizes:** Message text (base), input (base), timestamps (sm), headers (lg)
- **Weights:** Regular (400) for body, Medium (500) for emphasis

### C. Layout System
**Spacing Units:** Tailwind units of 2, 4, 6, 8, 12, 16
- Chat container: max-w-3xl centered with p-4 to p-6
- Messages: mb-4 gap between
- Input area: p-4 fixed bottom positioning
- Message bubbles: px-4 py-3

### D. Component Library

**Chat Container:**
- Full height viewport with fixed header (optional, minimal branding)
- Scrollable message area with auto-scroll to bottom
- Fixed input area at bottom with subtle shadow/border separation

**Message Bubbles:**
- User messages: Right-aligned, blue background, white text, rounded-2xl
- AI messages: Left-aligned, gray surface, primary text, rounded-2xl
- Max-width: 80% of container to prevent overly wide messages
- Timestamps: Small, muted text below each message

**Input Area:**
- Single-line text input with rounded borders
- Send button (icon or text) positioned inline-right
- Input grows/shrinks based on content (textarea with max height)
- Border highlight on focus

**Loading Indicator:**
- Three animated dots in AI message position
- Subtle pulse animation
- Appears immediately when message sent

**Stock Display (within AI responses):**
- Clean card/list format for stock recommendations
- Ticker symbol in monospace or bold
- Price/change data in tabular layout or inline
- Positive changes: green text, Negative: red text

### E. Animations
**Minimal Only:**
- Message fade-in (150ms) when new message appears
- Loading dots pulse (600ms cycle)
- Smooth scroll to bottom (200ms)
- Input focus border transition (150ms)
- NO elaborate scroll effects, page transitions, or decorative animations

## Interaction Patterns
- Enter key sends message
- Auto-focus input after sending
- Clear input after sending
- Disable input/send button while loading
- Show typing indicator for AI response
- Mobile-responsive: Full-width layout on small screens

## Images
**No Hero Image** - This is a utility chat interface, not a marketing page
**Optional:** Small subtle logo/icon in top-left corner (24x24 to 32x32)

## Accessibility
- High contrast ratios (WCAG AA minimum)
- Keyboard navigation support
- Focus indicators on interactive elements
- Semantic HTML for screen readers
- Sufficient touch targets (min 44x44px) on mobile