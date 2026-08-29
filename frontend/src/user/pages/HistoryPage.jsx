import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

const HistoryPage = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/api/analyses`);

      if (!response.ok) {
        throw new Error("Failed to load analysis history.");
      }

      const data = await response.json();
      setAnalyses(data);
    } catch (err) {
      console.error("History error:", err);
      setError("Unable to load analysis history. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 80) {
      return "text-green-400";
    }

    if (score >= 60) {
      return "text-yellow-400";
    }

    return "text-red-400";
  };

  const getLabelClass = (label) => {
    if (label === "ACCEPTABLE") {
      return "badge badge-success";
    }

    if (label === "CORRUPTED" || label === "BLUR") {
      return "badge badge-error";
    }

    return "badge badge-warning";
  };

  const formatDate = (dateString) => {
    if (!dateString) {
      return "Unknown date";
    }

    return new Date(dateString).toLocaleString();
  };

  return (
    <main className="min-h-screen p-8">
      <div className="w-full max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-100">
            Analysis History
          </h1>
          <p className="mt-2 text-gray-400">
            View your previously analyzed images and their results.
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="card bg-gray-900 border border-gray-800 shadow-xl">
            <div className="card-body">
              <div className="flex flex-col items-center justify-center py-16">
                <span className="loading loading-spinner loading-lg text-primary"></span>
                <p className="text-gray-400 mt-4">
                  Loading analysis history...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="card bg-gray-900 border border-gray-800 shadow-xl">
            <div className="card-body">
              <div className="alert alert-error">
                <span>{error}</span>
              </div>
              <div className="flex justify-center mt-4">
                <button
                  className="btn btn-primary"
                  onClick={fetchHistory}
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && analyses.length === 0 && (
          <div className="card bg-gray-900 border border-gray-800 shadow-xl">
            <div className="card-body">
              <div className="text-center py-16">
                <div className="text-5xl mb-4">🖼️</div>
                <h2 className="text-2xl font-semibold text-gray-100">
                  No Analyses Yet
                </h2>
                <p className="text-gray-400 mt-2">
                  Upload an image to see your analysis results here.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* History List */}
        {!loading && !error && analyses.length > 0 && (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="card bg-gray-900 border border-gray-800 shadow-lg"
              >
                <div className="card-body">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                    {/* File information */}
                    <div className="flex-1 min-w-0">
                      <h2 className="text-lg font-semibold text-gray-100 break-all">
                        {analysis.filename}
                      </h2>
                      <p className="text-sm text-gray-400 mt-1">
                        {formatDate(analysis.created_at)}
                      </p>
                    </div>

                    {/* Result */}
                    <div className="flex items-center gap-6">
                      {/* Score */}
                      <div className="text-center">
                        <p className="text-xs text-gray-500 uppercase">
                          Quality Score
                        </p>
                        <p
                          className={`text-3xl font-bold ${getScoreClass(
                            analysis.quality_score
                          )}`}
                        >
                          {analysis.quality_score}
                        </p>
                        <p className="text-xs text-gray-500">/ 100</p>
                      </div>

                      {/* Label */}
                      <div className="text-center">
                        <p className="text-xs text-gray-500 uppercase mb-2">
                          Result
                        </p>
                        <span
                          className={getLabelClass(
                            analysis.quality_label
                          )}
                        >
                          {analysis.quality_label}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="border-t border-gray-800 mt-4 pt-4">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">Confidence</p>
                        <p className="text-gray-200 font-medium">
                          {(analysis.confidence * 100).toFixed(1)}%
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500">Severity</p>
                        <p className="text-gray-200 font-medium capitalize">
                          {analysis.severity || "None"}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500">Analysis ID</p>
                        <p className="text-gray-200 font-medium">
                          #{analysis.id}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Refresh */}
        {!loading && !error && analyses.length > 0 && (
          <div className="flex justify-center mt-8">
            <button
              className="btn btn-outline"
              onClick={fetchHistory}
            >
              Refresh History
            </button>
          </div>
        )}
      </div>
    </main>
  );
};

export default HistoryPage;

