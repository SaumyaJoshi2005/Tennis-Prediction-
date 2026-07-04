import "./Footer.css";
import { Link } from "react-router-dom";

function Footer() {
    return (
        <footer className="footer">
            <p>Copyright 2026 Tennis Prediction Engine</p>
            <Link to="/how-it-works">How the prediction works</Link>
        </footer>
    );
}

export default Footer;
