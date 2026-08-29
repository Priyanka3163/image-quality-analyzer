import { BrowserRouter, Routes, Route } from "react-router-dom";

import PlainNavbar from "./user/components/PlainNavbar";
import HomePage from "./user/pages/HomePage";
import HistoryPage from "./user/pages/HistoryPage";

import "./App.css";

function App() {

    return (

        <BrowserRouter>

            <div className="w-full min-h-screen bg-gray-950">

                <PlainNavbar />

                <Routes>

                    <Route
                        path="/"
                        element={<HomePage />}
                    />

                    <Route
                        path="/history"
                        element={<HistoryPage />}
                    />

                </Routes>

            </div>

        </BrowserRouter>

    );
}

export default App;

