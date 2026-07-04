import { createContext, useContext, useMemo, useState } from "react";

const ThemeContext = createContext(null);

export const themeOptions = [
    { id: "hard", label: "Hard Court", description: "Night-session blue with mint lines" },
    { id: "clay", label: "Clay", description: "Roland Garros warmth and clay contrast" },
    { id: "grass", label: "Wimbledon", description: "Grass green with ivory lines" },
    { id: "night", label: "Night Slam", description: "Deep arena mode for big fixtures" },
];

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState("hard");
    const value = useMemo(() => ({ theme, setTheme }), [theme]);

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const context = useContext(ThemeContext);

    if (!context) {
        throw new Error("useTheme must be used inside ThemeProvider");
    }

    return context;
}
