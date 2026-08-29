import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const [error, setError] = useState("");

  /*
   * ---------------------------------------
   * Select Image
   * ---------------------------------------
   */

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setError("");

    if (!file) {
      return;
    }

    const allowedTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError(
        "Please select a JPG, JPEG, PNG, or WebP image."
      );
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError(
        "Image must be smaller than 10 MB."
      );
      return;
    }

    setSelectedFile(file);

    const imageUrl = URL.createObjectURL(file);
    setPreview(imageUrl);
  };

  /*
   * ---------------------------------------
   * Analyze Image
   * ---------------------------------------
   */

  const handleAnalyze = async () => {

    if (!selectedFile || loading) {
      return;
    }

    setLoading(true);
    setError("");

    try {

      const formData = new FormData();

      formData.append(
        "image",
        selectedFile
      );

      const response = await fetch(
        `${API_URL}/api/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {

        const errorData =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          errorData?.detail ||
          "Failed to analyze image."
        );
      }

      const analysis =
        await response.json();

      /*
       * Keep loading state visible
       * for at least 2 seconds.
       */

      await new Promise(
        (resolve) =>
          setTimeout(resolve, 2000)
      );

      /*
       * Store result.
       *
       * This automatically changes
       * the card from LOADING → RESULT.
       */

      setResult(analysis);

    } catch (err) {

      console.error(
        "Analysis error:",
        err
      );

      setError(
        err.message ||
        "Something went wrong while analyzing the image."
      );

    } finally {

      setLoading(false);

    }
  };

  /*
   * ---------------------------------------
   * Upload / Change Image
   * ---------------------------------------
   */

  const handleNewImage = () => {

    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError("");
    setLoading(false);

  };

  /*
   * ---------------------------------------
   * INITIAL STATE
   * ---------------------------------------
   */

  if (!selectedFile) {

    return (
      <div className="w-full max-w-3xl mx-auto">

        <section className="text-center py-12">

          <h1 className="text-4xl md:text-5xl font-bold">
            AI Image Quality Analyzer
          </h1>

          <p className="mt-4 text-gray-500 text-lg">
            Upload an image and let our AI evaluate its visual quality.
          </p>

        </section>

        <div className="border-2 border-dashed border-gray-700 rounded-2xl p-12 text-center bg-gray-900">

          <div className="text-5xl mb-4">
            📷
          </div>

          <h2 className="text-2xl font-semibold mb-2">
            Upload an Image
          </h2>

          <p className="text-gray-400 mb-6">
            Upload an image to evaluate its visual quality
          </p>

          <label className="btn btn-primary cursor-pointer">

            Choose Image

            <input
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              onChange={handleFileChange}
              className="hidden"
            />

          </label>

          <p className="text-sm text-gray-400 mt-4">
            JPG, JPEG, PNG or WebP • Maximum 10 MB
          </p>

          {error && (

            <div className="alert alert-error mt-6">
              <span>{error}</span>
            </div>

          )}

        </div>

      </div>
    );
  }

  /*
   * ---------------------------------------
   * RESULT STATE
   * ---------------------------------------
   */

  if (result) {

    const issue =
      result.issues &&
      result.issues.length > 0
        ? result.issues[0]
        : null;

    return (


        <div className="w-full max-w-3xl mx-auto">

        <div className="card bg-gray-900 border border-gray-800 shadow-xl">

            <div className="card-body">

            <h2 className="card-title text-2xl mb-6 text-gray-100">
                Analysis Result
            </h2>

            {/* Quality Score */}

            <div className="text-center mb-8">

                <div className="text-6xl font-bold text-gray-100">
                {result.quality_score}
                </div>

                <p className="text-gray-400">
                Quality Score / 100
                </p>

                <div className="badge badge-lg mt-3">
                {result.quality_label}
                </div>

            </div>

            {/* Issue */}

            {issue ? (

                <div className="bg-gray-800 rounded-xl p-5 mb-6 border border-gray-700">

                <h3 className="font-semibold text-lg mb-4 text-gray-100">
                    Detected Issue
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

                    <div>
                    <p className="text-sm text-gray-400">
                        Type
                    </p>

                    <p className="font-medium text-gray-100">
                        {issue.type}
                    </p>
                    </div>

                    <div>
                    <p className="text-sm text-gray-400">
                        Severity
                    </p>

                    <p className="font-medium text-gray-100">
                        {issue.severity}
                    </p>
                    </div>

                    <div>
                    <p className="text-sm text-gray-400">
                        Confidence
                    </p>

                    <p className="font-medium text-gray-100">
                        {(issue.confidence * 100).toFixed(1)}%
                    </p>
                    </div>

                </div>

                </div>

            ) : (

                <div className="alert alert-success mb-6">

                <span>
                    No significant image-quality issues detected.
                </span>

                </div>

            )}

            {/* Image Information */}

            <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">

                <h3 className="font-semibold text-lg mb-4 text-gray-100">
                Image Information
                </h3>

                <div className="grid grid-cols-2 gap-4">

                <div>

                    <p className="text-sm text-gray-400">
                    Filename
                    </p>

                    <p className="font-medium text-gray-100 break-all">
                    {result.filename}
                    </p>

                </div>

                <div>

                    <p className="text-sm text-gray-400">
                    Dimensions
                    </p>

                    <p className="font-medium text-gray-100">
                    {result.image?.width} ×{" "}
                    {result.image?.height}
                    </p>

                </div>

                <div>

                    <p className="text-sm text-gray-400">
                    Confidence
                    </p>

                    <p className="font-medium text-gray-100">
                    {(result.confidence * 100).toFixed(1)}%
                    </p>

                </div>

                <div>

                    <p className="text-sm text-gray-400">
                    Severity
                    </p>

                    <p className="font-medium text-gray-100">
                    {result.issues?.[0]?.severity || "None"}
                    </p>

                </div>

                </div>

            </div>

            {/* Statistics */}

            {result.statistics && (

                <div className="mt-6">

                <h3 className="font-semibold text-lg mb-4 text-gray-100">
                    Image Statistics
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">

                    {Object.entries(
                    result.statistics
                    ).map(([name, value]) => (

                    <div
                        key={name}
                        className="bg-gray-800 rounded-lg p-3 border border-gray-700"
                    >

                        <p className="text-xs text-gray-400 break-words">
                        {name.replaceAll("_", " ")}
                        </p>

                        <p className="font-medium mt-1 text-gray-100">
                        {value}
                        </p>

                    </div>

                    ))}

                </div>

                </div>

            )}

            {/* Upload New Image */}

            <div className="flex justify-center mt-8">

                <button
                className="btn btn-primary"
                onClick={handleNewImage}
                >
                Upload New Image
                </button>

            </div>

            </div>

        </div>

        </div>


    );
  }

  /*
   * ---------------------------------------
   * IMAGE PREVIEW / LOADING STATE
   * ---------------------------------------
   */

  return (

    <div className="w-full max-w-3xl mx-auto">

    <div className="card bg-gray-900 border border-gray-800 shadow-xl">

        <div className="card-body">

        <h2 className="card-title text-2xl mb-4 text-gray-100">

            {loading
            ? "Analyzing Image"
            : "Image Preview"}

        </h2>

        {/* Preview / Loading */}

        <div className="flex justify-center items-center bg-gray-950 border border-gray-800 rounded-xl p-4 min-h-[400px]">

            {loading ? (

            <div className="flex flex-col items-center text-center">

                <span className="loading loading-spinner text-primary loading-lg"></span>

                <p className="text-lg font-medium mt-6 text-gray-100">
                Analyzing image...
                </p>

                <p className="text-sm text-gray-400 mt-2">
                Please wait while we evaluate the image quality.
                </p>

            </div>

            ) : (

            <img
                src={preview}
                alt="Selected image"
                className="max-h-96 max-w-full rounded-lg object-contain"
            />

            )}

        </div>

        {/* File Information */}

        {!loading && (

            <div className="mt-4">

            <p className="font-medium text-gray-100">
                {selectedFile.name}
            </p>

            <p className="text-sm text-gray-400">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
            </p>

            </div>

        )}

        {/* Error */}

        {error && (

            <div className="alert alert-error mt-4">
            <span>{error}</span>
            </div>

        )}

        {/* Buttons */}

        {!loading && (

            <div className="flex justify-end gap-3 mt-6">

            <button
                className="btn btn-secondary"
                onClick={handleNewImage}
            >
                Change Image
            </button>

            <button
                className="btn btn-primary"
                onClick={handleAnalyze}
            >
                Analyze Image
            </button>

            </div>

        )}

        </div>

    </div>

    </div>



  );
};

export default ImageUploader;