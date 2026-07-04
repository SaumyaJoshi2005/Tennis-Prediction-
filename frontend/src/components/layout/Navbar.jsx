import { Link, NavLink } from "react-router-dom";
import ThemeSelector from "../theme/ThemeSelector";

import "./Navbar.css";

function Navbar() {
    return (
        <header className="app-navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    Tennis Prediction Engine
                </Link>

                <nav className="navbar-links" aria-label="Primary navigation">
                    <NavLink to="/" end>
                        Home
                    </NavLink>

                    <NavLink to="/predictions">
                        Predictions
                    </NavLink>

                    <NavLink to="/fixtures">
                        Fixtures
                    </NavLink>

                    <NavLink to="/players">
                        Players
                    </NavLink>

                    <NavLink to="/how-it-works">
                        Model BG
                    </NavLink>
                </nav>

                <ThemeSelector />
            </div>
        </header>
    );
}

export default Navbar;
