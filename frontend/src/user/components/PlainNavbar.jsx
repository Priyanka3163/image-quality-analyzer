import { Link } from "react-router-dom";

const PlainNavbar = () => {
    return (
        <div className="navbar bg-gray-900 border-b border-gray-800 shadow-sm px-6">

            {/* Logo / Title */}

            <div className="flex-1">
                <Link
                    to="/"
                    className="btn btn-ghost text-xl text-gray-100"
                >
                    AI Image Quality Analyzer
                </Link>
            </div>

            {/* Navigation */}

            <div className="flex-none">

                <ul className="menu menu-horizontal px-1 gap-2">

                    <li>
                        <Link
                            to="/"
                            className="text-gray-300 hover:text-white"
                        >
                            Home
                        </Link>
                    </li>

                    <li>
                        <Link
                            to="/history"
                            className="text-gray-300 hover:text-white"
                        >
                            History
                        </Link>
                    </li>

                </ul>

            </div>

        </div>
    );
};

export default PlainNavbar;

