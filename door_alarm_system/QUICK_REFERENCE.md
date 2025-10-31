# 🎨 eDOMOS Premium UI - Quick Reference Card

## Color Palette 🌈

### Backgrounds
```
Space Black:   #0a0e1a  ██████  Primary
Space Dark:    #0f1729  ██████  Cards
Space Deeper:  #151d33  ██████  Modals
Space Deep:    #1a2340  ██████  Sections
```

### Neon Accents
```
Neon Blue:     #00d4ff  ██████  Primary
Neon Green:    #00ff88  ██████  Success
Neon Red:      #ff0055  ██████  Danger
Neon Yellow:   #ffdd00  ██████  Warning
Neon Purple:   #8833ff  ██████  Special
Neon Cyan:     #00ffff  ██████  Info
```

### Text Colors
```
Primary:       #ffffff  ██████  White
Secondary:     #b8c5d6  ██████  Light Gray
Tertiary:      #8091a7  ██████  Medium Gray
Muted:         #5a6b7f  ██████  Dark Gray
```

---

## Typography 📝

### Font Families
- **Orbitron**: Brand, headings (400-900)
- **Sora**: Body text (300-800)
- **Inter**: System fallback (300-900)

### Sizes
```
h1  48px  900  ████████████████
h2  40px  800  ██████████████
h3  32px  700  ████████████
h4  24px  700  ██████████
h5  20px  600  ████████
h6  16px  600  ██████
```

---

## Components Cheatsheet 🎯

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-warning">Warning</button>
<button class="btn btn-secondary">Secondary</button>
```

### Badges
```html
<span class="badge bg-primary">Primary</span>
<span class="badge bg-success">Online</span>
<span class="badge bg-danger">Alert</span>
<span class="badge bg-warning">Warning</span>
<span class="badge bg-info">Info</span>
```

### Status Indicators
```html
<span class="status-indicator online"></span>   Green
<span class="status-indicator offline"></span>  Gray
<span class="status-indicator alert"></span>    Red
<span class="status-indicator warning"></span>  Yellow
```

### Cards
```html
<div class="card">
    <div class="card-header bg-primary">
        <h5>Card Title</h5>
    </div>
    <div class="card-body">
        Card content
    </div>
</div>
```

### Alerts
```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-info">Info message</div>
```

---

## Utility Classes 🛠️

### Glass Effect
```html
<div class="glass-panel">Translucent blur panel</div>
```

### Neon Text
```html
<span class="neon-text-blue">Blue glow text</span>
<span class="neon-text-green">Green glow text</span>
<span class="neon-text-red">Red glow text</span>
```

### Neon Border
```html
<div class="neon-border">Glowing border</div>
```

### Glow Animation
```html
<div class="glow-effect">Pulsing glow</div>
```

---

## Gradients 🌈

### CSS Variables
```css
var(--gradient-primary)  /* Blue gradient */
var(--gradient-success)  /* Green gradient */
var(--gradient-danger)   /* Red gradient */
var(--gradient-warning)  /* Yellow gradient */
var(--gradient-purple)   /* Purple gradient */
var(--gradient-glass)    /* Glass overlay */
```

---

## Spacing Scale 📐

```
--space-1   4px    ▪
--space-2   8px    ▪▪
--space-3   12px   ▪▪▪
--space-4   16px   ▪▪▪▪
--space-5   20px   ▪▪▪▪▪
--space-6   24px   ▪▪▪▪▪▪
--space-8   32px   ▪▪▪▪▪▪▪▪
--space-10  40px   ▪▪▪▪▪▪▪▪▪▪
--space-12  48px   ▪▪▪▪▪▪▪▪▪▪▪▪
```

---

## Border Radius 🔲

```
--radius-sm    8px   ╭─╮
--radius-md    12px  ╭──╮
--radius-lg    16px  ╭───╮
--radius-xl    20px  ╭────╮
--radius-2xl   24px  ╭─────╮
--radius-full  ∞     ●
```

---

## Shadows & Glows ✨

### Shadows
```css
var(--shadow-sm)   /* Small: 2px */
var(--shadow-md)   /* Medium: 4px */
var(--shadow-lg)   /* Large: 8px */
var(--shadow-xl)   /* Extra: 12px */
```

### Glows
```css
var(--glow-blue)    /* Blue neon */
var(--glow-green)   /* Green neon */
var(--glow-red)     /* Red neon */
var(--glow-purple)  /* Purple neon */
```

---

## Animations ⚡

### Available Animations
```css
backgroundPulse     /* 15s ambient */
brandPulse          /* 2s logo */
statusPulse         /* 2s indicator */
statusPulseDanger   /* 1s fast */
statusRipple        /* 2s expand */
badgePulse          /* 2s glow */
glowPulse           /* 2s glow */
```

---

## Transitions ⏱️

```css
var(--transition-fast)  /* 200ms */
var(--transition-base)  /* 300ms */
var(--transition-slow)  /* 500ms */
```

---

## Responsive Breakpoints 📱

```
Mobile:   < 768px   📱
Tablet:   768-1024  📱
Desktop:  > 1024px  🖥️
```

---

## Quick Deploy 🚀

```bash
# 1. Restart app
python3 app.py

# 2. Hard refresh browser
Ctrl + Shift + R

# 3. Login
http://192.168.31.22:5000
admin / admin
```

---

## Common Patterns 📋

### Hero Section
```html
<div class="card">
    <div class="card-header bg-primary">
        <h3><i class="fas fa-shield"></i> Status</h3>
    </div>
    <div class="card-body">
        <span class="status-indicator online"></span>
        <span class="neon-text-green">OPERATIONAL</span>
    </div>
</div>
```

### Action Group
```html
<div class="d-flex gap-2">
    <button class="btn btn-primary">
        <i class="fas fa-lock"></i> Lock
    </button>
    <button class="btn btn-success">
        <i class="fas fa-unlock"></i> Unlock
    </button>
</div>
```

### Status Display
```html
<div class="d-flex align-items-center gap-2">
    <span class="status-indicator online"></span>
    <span class="badge bg-success">ONLINE</span>
    <span class="neon-text-green">Active</span>
</div>
```

---

## Browser DevTools 🔧

### Inspect Element
```
F12          Open DevTools
Ctrl+Shift+C  Select element
Ctrl+Shift+R  Hard refresh
```

### Check CSS
```
1. Right-click element
2. Click "Inspect"
3. View "Styles" tab
4. See computed values
```

---

## Customization Tips 💡

### Change Primary Color
```css
:root {
    --neon-blue: #YOUR_COLOR;
    --neon-blue-bright: #BRIGHT_VERSION;
    --neon-blue-glow: rgba(R, G, B, 0.5);
}
```

### Adjust Blur
```css
.card {
    backdrop-filter: blur(30px); /* From 20px */
}
```

### Slow Down Animations
```css
:root {
    --transition-base: 500ms; /* From 300ms */
}
```

---

## Troubleshooting 🔍

### Blur Not Working
- Update browser
- Enable GPU acceleration
- Check browser support

### Fonts Not Loading
- Check internet
- Clear cache
- Verify CDN

### Slow Performance
- Reduce blur (20px → 10px)
- Disable animations
- Close other tabs

---

## Documentation 📚

1. **PREMIUM_UI_GUIDE.md** - Full technical docs
2. **UI_TRANSFORMATION.md** - Visual guide
3. **PREMIUM_UI_COMPLETE.md** - Implementation summary
4. **THIS FILE** - Quick reference

---

## Success Metrics ✅

- **Visual Appeal**: ⭐⭐⭐⭐⭐
- **Modern Design**: ⭐⭐⭐⭐⭐
- **Accessibility**: ⭐⭐⭐⭐⭐
- **Performance**: ⭐⭐⭐⭐☆
- **Responsive**: ⭐⭐⭐⭐⭐

---

**🎨 Premium UI 2.0**  
**Date**: Oct 21, 2025  
**Status**: Ready ✅
