import { useLocation } from "react-router-dom";
import ImageUploader from "../components/ImageUploader";

const HomePage = () => {
  const location = useLocation();

  return (
    <main className="min-h-screen p-8">
      <ImageUploader key={location.key} />
    </main>
  );
};

export default HomePage;