import { themeOptions, useTheme } from "../../contexts/ThemeContext";
import "./ThemeSelector.css";

function ThemeSelector() {
    const { theme, setTheme } = useTheme();

    return (
        <div className="theme-selector" aria-label="Court theme selector">
            {themeOptions.map((option) => (
                <button
                    key={option.id}
                    type="button"
                    className={theme === option.id ? "active" : ""}
                    onClick={() => setTheme(option.id)}
                    title={option.description}
                >
                    {option.label}
                </button>
            ))}
        </div>
    );
}

export default ThemeSelector;
