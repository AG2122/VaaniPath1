---
name: VaniPath
colors:
  surface: '#faf8ff'
  surface-dim: '#d9d9e5'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3fe'
  surface-container: '#ededf9'
  surface-container-high: '#e7e7f3'
  surface-container-highest: '#e1e2ed'
  on-surface: '#191b23'
  on-surface-variant: '#434655'
  inverse-surface: '#2e3039'
  inverse-on-surface: '#f0f0fb'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#712ae2'
  on-secondary: '#ffffff'
  secondary-container: '#8a4cfc'
  on-secondary-container: '#fffbff'
  tertiary: '#006243'
  on-tertiary: '#ffffff'
  tertiary-container: '#007d57'
  on-tertiary-container: '#bdffdc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#eaddff'
  secondary-fixed-dim: '#d2bbff'
  on-secondary-fixed: '#25005a'
  on-secondary-fixed-variant: '#5a00c6'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#faf8ff'
  on-background: '#191b23'
  surface-variant: '#e1e2ed'
typography:
  display-lg:
    fontFamily: Lexend
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Lexend
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style
The design system is rooted in the "Path to Voice" philosophy—creating a bridge between technology and education that feels both professional and intimately accessible. The personality is that of an expert mentor: calm, reliable, and encouraging.

The aesthetic follows a **Modern Humanist** approach. It leverages high-quality whitespace and a structured layout to reduce cognitive load, ensuring that learners can focus on content without distraction. Visual interest is generated through soft depth and clear purposeful color rather than decorative ornamentation. The design system prioritizes clarity and accessibility, adhering strictly to WCAG AA standards to serve a diverse, bilingual user base.

## Colors
The palette is functional and semantic. The **Primary Blue** (#2563EB) represents the core learning path and structural UI elements. **AI Purple** (#7C3AED) is reserved strictly for generative features, automated translations, and smart insights, creating a clear mental model for the user. 

The background uses a soft **Slate White** (#F8FAFC) to reduce eye strain during long study sessions. High-contrast Slate (#0F172A) is used for primary text to ensure maximum readability against the soft background.

## Typography
This design system utilizes **Lexend** for headings because of its research-backed design specifically intended to improve reading proficiency. It provides a friendly, open character that feels welcoming to students. 

**Inter** is used for all body text and UI labels for its exceptional clarity and systematic nature, particularly in bilingual contexts where character density may vary. All body text is set to a minimum of 16px to ensure accessibility across mobile devices.

## Layout & Spacing
The layout follows a **Mobile-First Fluid Grid**. For mobile devices, a 4-column system is used with 16px margins. For desktop, this scales to a 12-column system with a maximum container width of 1280px.

Spacing is based on a **4px baseline grid**, though components primarily use increments of 8px (8, 16, 24, 32) to maintain a generous, airy feel. Vertical rhythm is critical; maintain 32px or 40px of space between major content sections to prevent visual clutter and support learners with ADHD or cognitive processing needs.

## Elevation & Depth
Depth is communicated through **Tonal Elevation** and soft, diffused shadows. This design system avoids harsh borders, preferring to use light-grey strokes (#E2E8F0) and subtle shadows to define boundaries.

- **Level 0 (Base):** #F8FAFC (Background).
- **Level 1 (Cards/Surface):** #FFFFFF with a subtle shadow (Y: 2px, Blur: 4px, Color: 0,0,0, 0.05). Used for static content.
- **Level 2 (Interactive/Hover):** #FFFFFF with an ambient shadow (Y: 8px, Blur: 16px, Color: 0,0,0, 0.08). Used for active cards or elements being interacted with.
- **Level 3 (Overlay):** High-diffusion shadow (Y: 12px, Blur: 24px, Color: 0,0,0, 0.12). Used for modals and dropdown menus.

## Shapes
The shape language is "Approachable Geometric." Standard components utilize a **0.5rem (8px)** radius, while larger container elements and cards use **1rem (16px) to 1.5rem (24px)**. 

Interactive elements like buttons and chips should feel "soft" to the touch; buttons use a 12px corner radius to distinguish them from cards. This consistency in roundedness reinforces the friendly, non-intimidating nature of the educational environment.

## Components
### Buttons
Buttons must have a minimum height of **48px** for touch accessibility. Primary buttons use the Primary Blue with white text. AI-specific buttons use a Purple gradient (bottom-left to top-right) or a Purple solid fill with a subtle glow effect on hover.

### Cards
Learning modules are housed in cards with **24px padding** and **24px corner radius**. Cards should feature a 1px border (#E2E8F0) to ensure definition against the soft background.

### Bilingual Displays
When displaying two languages simultaneously, the primary language (Target) should be in Lexend Bold, while the secondary language (Native/Translation) should be in Inter Regular, 14px, muted Slate (#64748B), positioned directly below or in a separate shaded block.

### Iconography
Icons use a **2px stroke weight** with rounded terminals.
- **Translation:** A stylized "A" and a character from a non-Latin script joined by a subtle arc.
- **Classroom:** A simple desk or a group of three stylized figures.
- **Offline:** A cloud with a diagonal slash or a "stored" download icon.
- **AI Features:** A four-point sparkle (sparkle-fill) in AI Purple.

### Inputs
Text inputs feature a 48px height, 12px corner radius, and a 2px blue border only when focused. Placeholder text must meet color contrast requirements.