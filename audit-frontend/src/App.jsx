import React, { useRef, useState, useCallback } from "react";
import ReactMarkdown from "react-markdown";

function App() {
  const [files, setFiles] = useState([]);
  const [mergedOutput, setMergedOutput] = useState([]);
  const [auditSummary, setAuditSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  const ocrExtensions = ["pdf", "jpg", "jpeg", "png", "tif", "tiff"];
  const structuredExtensions = ["csv", "xlsx", "xml"];

  const isValidExtension = (ext) =>
    [...ocrExtensions, ...structuredExtensions].includes(ext);

  const handleFileChange = useCallback((e) => {
    const selected = Array.from(e.target.files);
    const validated = selected.filter((file) => {
      const ext = file.name.split(".").pop().toLowerCase();
      if (!isValidExtension(ext)) {
        alert(`${file.name} is not a supported format.`);
        return false;
      }
      return true;
    });

    setFiles((prev) => [...prev, ...validated]);
  }, []);

  const triggerFilePicker = useCallback(() => {
    if (inputRef.current) inputRef.current.click();
  }, []);

  const removeFile = useCallback((indexToRemove) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  }, []);

  const processFiles = useCallback(async () => {
    setLoading(true);
    const results = [];

    for (const file of files) {
      const ext = file.name.split(".").pop().toLowerCase();
      const formData = new FormData();
      formData.append("file", file);
      const route = ocrExtensions.includes(ext) ? "/extract" : "/convert";

      try {
        const response = await fetch(`http://localhost:5000${route}`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (route === "/extract") {
          results.push({
            fileName: file.name,
            textLines: data.text_lines,
            formFields: data.form_fields,
            tableCells: data.table_cells,
          });
        } else {
          results.push({
            fileName: file.name,
            structuredData: data.structuredData || [],
          });
        }
      } catch (err) {
        results.push({ fileName: file.name, error: err.message });
      }
    }

    setMergedOutput(results);

    try {
      const auditResponse = await fetch("http://localhost:5000/audit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(results),
      });

      const auditData = await auditResponse.json();
      setAuditSummary(auditData.summary);
    } catch (err) {
      setAuditSummary("Error: Failed to generate audit summary.");
    }

    setLoading(false);
  }, [files]);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4 py-8">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-xl p-8 text-center">
        <h1 className="text-3xl font-bold mb-6 text-gray-700">
          Upload Documents for Auditing
        </h1>

        <div
          className="border-4 border-dashed border-blue-400 p-10 rounded-xl cursor-pointer hover:bg-blue-50 transition"
          onClick={triggerFilePicker}
        >
          <p className="text-lg text-blue-600 font-semibold">
            Click or tap to select documents
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Accepted formats: PDF, JPG, PNG, TIFF, CSV, XLSX, XML
          </p>
        </div>

        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.tif,.tiff,.csv,.xlsx,.xml"
          onChange={handleFileChange}
          ref={inputRef}
          className="hidden"
        />

        {files.length > 0 && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-4 text-gray-600">
              Selected Files
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="relative bg-gray-50 border border-gray-300 rounded-md p-4 text-left shadow-sm"
                >
                  <button
                    onClick={() => removeFile(index)}
                    className="absolute top-2 right-2 text-red-500 hover:text-red-700 font-bold text-sm"
                  >
                    ×
                  </button>
                  <p className="text-sm font-medium text-gray-800 truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-center gap-4">
          <button
            onClick={triggerFilePicker}
            className="bg-blue-600 text-white px-6 py-2 rounded-md shadow hover:bg-blue-700 transition"
          >
            Add More Files
          </button>
          <button
            onClick={processFiles}
            disabled={files.length === 0 || loading}
            className="bg-green-600 text-white px-6 py-2 rounded-md shadow hover:bg-green-700 transition disabled:opacity-50"
          >
            {loading ? "Processing..." : "Start Audit"}
          </button>
        </div>

        {auditSummary && (
          <div className="mt-10 text-left">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              Audit Summary
            </h2>
            <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-x-auto max-h-96 whitespace-pre-wrap">
              <ReactMarkdown>{auditSummary}</ReactMarkdown>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
