import Navbar from "./Navbar";
import Footer from "./Footer";
import { useTheme } from "../../contexts/ThemeContext";

import "./Layout.css";

function Layout({ children }) {
    const { theme } = useTheme();

    return (

        <div className={`layout theme-${theme}`}>

            <Navbar />

            <main className="layout-content">

                {children}

            </main>

            <Footer />

        </div>

    );

}

export default Layout;
