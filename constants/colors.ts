// Palette keys keep the names used by the screens (wine, terracotta, ...) so the layout code is
// shared with the Italian app. The VALUES are the Arabic app's deep-blue + gold theme.
const palette = {
  wine: "#1F3B73",          // primary (deep blue)
  wineDark: "#14274F",
  terracotta: "#C26A3D",    // secondary (clay)
  terracottaLight: "#D88A5F",
  gold: "#C9933A",
  goldLight: "#E8B85A",
  cream: "#F6F1E7",
  creamDark: "#EAE3D3",
  inkDark: "#0B1220",
  inkMid: "#2A3A5C",
  inkLight: "#5A6A8A",
  white: "#FFFFFF",
  success: "#2E7D52",
  error: "#B03030",
  errorLight: "#FFE8E8",
  successLight: "#E8F5EE",
};

export default {
  palette,
  light: {
    background: palette.cream,
    backgroundSecondary: palette.creamDark,
    card: palette.white,
    text: palette.inkDark,
    textSecondary: palette.inkLight,
    textMuted: "#8A94AA",
    tint: palette.wine,
    accent: palette.gold,
    tabIconDefault: "#8A94AA",
    tabIconSelected: palette.wine,
    border: "#DAD3C2",
    separator: "#D5CDBA",
  },
  dark: {
    background: "#0B1220",
    backgroundSecondary: "#14203A",
    card: "#1B2A4A",
    text: palette.cream,
    textSecondary: "#B4BED3",
    textMuted: "#6B7A99",
    tint: "#9DB8F5",
    accent: palette.goldLight,
    tabIconDefault: "#6B7A99",
    tabIconSelected: "#9DB8F5",
    border: "#2A3B63",
    separator: "#1B2A4A",
  },
};
