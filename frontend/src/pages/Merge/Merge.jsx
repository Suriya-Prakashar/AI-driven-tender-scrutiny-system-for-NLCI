import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import Header from "../../components/layout/Header";
import { apiService } from "../../services/api";
import "./Merge.css";

export const Merge = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [selectedLocalFiles, setSelectedLocalFiles] = useState([]);
  const [selectedUploadedFiles, setSelectedUploadedFiles] = useState([]);
  const [mergedFilename, setMergedFilename] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [confirmDialog, setConfirmDialog] = useState({ isOpen: false, message: "", onConfirm: null });

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const data = await apiService.getFiles();
      const fetchedFiles = data.files || [];
      setFiles(fetchedFiles);
      // Clean up selected checkboxes if files were removed
      setSelectedUploadedFiles((prev) => prev.filter((name) => fetchedFiles.includes(name)));
    } catch (err) {
      console.error("Failed to fetch files:", err);
      setMessage("Error loading uploaded files list.");
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setSelectedLocalFiles(Array.from(e.target.files));
    }
  };

  const handleRemoveLocalFile = (indexToRemove) => {
    const updated = selectedLocalFiles.filter((_, idx) => idx !== indexToRemove);
    setSelectedLocalFiles(updated);
    if (updated.length === 0) {
      const fileInput = document.getElementById("files");
      if (fileInput) fileInput.value = "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedLocalFiles || selectedLocalFiles.length === 0) {
      alert("Please select at least one PDF file to upload or merge.");
      return;
    }

    setIsLoading(true);
    setMessage("");

    try {
      const result = await apiService.mergeFiles(selectedLocalFiles, mergedFilename);
      if (result.success) {
        setMessage("PDF file(s) uploaded and merged successfully!");
        setMergedFilename("");
        setSelectedLocalFiles([]);
        const fileInput = document.getElementById("files");
        if (fileInput) fileInput.value = "";
        await fetchFiles();
      } else {
        setMessage(result.message || "Failed to upload or merge files.");
      }
    } catch (err) {
      console.error("Merge error:", err);
      setMessage(err.response?.data?.message || "An error occurred during upload/merge.");
    } finally {
      setIsLoading(false);
    }
  };

  const requestDelete = (filename, e) => {
    if (e) e.preventDefault();
    setConfirmDialog({
      isOpen: true,
      message: `Are you sure you want to delete "${filename}"?`,
      onConfirm: () => performDelete(filename)
    });
  };

  const performDelete = async (filename) => {
    setConfirmDialog({ isOpen: false, message: "", onConfirm: null });
    setIsLoading(true);
    try {
      const result = await apiService.deleteFile(filename);
      if (result.success) {
        setMessage(`File '${filename}' deleted successfully.`);
        setSelectedUploadedFiles((prev) => prev.filter((name) => name !== filename));
        await fetchFiles();
      } else {
        setMessage(result.message || "Failed to delete file.");
      }
    } catch (err) {
      console.error("Delete error:", err);
      setMessage(err.response?.data?.message || "An error occurred while deleting the file.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSelectFile = (filename) => {
    setSelectedUploadedFiles((prev) =>
      prev.includes(filename)
        ? prev.filter((name) => name !== filename)
        : [...prev, filename]
    );
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedUploadedFiles([...files]);
    } else {
      setSelectedUploadedFiles([]);
    }
  };

  const requestDeleteSelected = (e) => {
    if (e) e.preventDefault();
    if (selectedUploadedFiles.length === 0) {
      alert("Please select at least one uploaded file to delete.");
      return;
    }
    setConfirmDialog({
      isOpen: true,
      message: `Are you sure you want to delete the ${selectedUploadedFiles.length} selected file(s)?`,
      onConfirm: performDeleteSelected
    });
  };

  const performDeleteSelected = async () => {
    setConfirmDialog({ isOpen: false, message: "", onConfirm: null });
    setIsLoading(true);
    let successCount = 0;
    let failCount = 0;

    try {
      for (const filename of selectedUploadedFiles) {
        const result = await apiService.deleteFile(filename);
        if (result.success) {
          successCount++;
        } else {
          failCount++;
        }
      }

      if (successCount > 0) {
        setMessage(
          `Successfully deleted ${successCount} file(s).${
            failCount > 0 ? ` Failed to delete ${failCount} file(s).` : ""
          }`
        );
      } else {
        setMessage("Failed to delete selected files.");
      }

      setSelectedUploadedFiles([]);
      await fetchFiles();
    } catch (err) {
      console.error("Batch delete error:", err);
      setMessage("An error occurred while deleting selected files.");
    } finally {
      setIsLoading(false);
    }
  };


  const handleContinue = (e) => {
    if (files.length === 0) {
      e.preventDefault();
      alert("⚠️ Please upload or merge at least one PDF file before continuing to evaluation!");
    } else {
      navigate("/evaluation");
    }
  };

  return (
    <div className="merge-page-container">
      {/* Loading Overlay */}
      {isLoading && (
        <div id="loadingOverlay" className="loading-overlay">
          <div className="loading-modal">
            <div className="spinner"></div>
            <p className="loading-text">
              Processing file operation...
              <br />
              <span>Please wait a moment.</span>
            </p>
            <div className="progress-bar">
              <div className="progress-bar-fill"></div>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Dialog Overlay */}
      {confirmDialog.isOpen && (
        <div className="loading-overlay">
          <div className="loading-modal">
            <h3 style={{ marginTop: 0, marginBottom: "16px", color: "#1f2937" }}>Confirm Deletion</h3>
            <p className="loading-text" style={{ marginBottom: "24px", color: "#4b5563" }}>
              {confirmDialog.message}
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button 
                type="button"
                className="btn" 
                style={{ background: "#e5e7eb", color: "#374151" }}
                onClick={() => setConfirmDialog({ isOpen: false, message: "", onConfirm: null })}
              >
                Cancel
              </button>
              <button 
                type="button"
                className="btn-danger" 
                style={{ marginTop: 0, width: "auto" }}
                onClick={confirmDialog.onConfirm}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <Header />

      {/* Hero Section */}
      <main className="hero-center">
        <div className="hero-content">
          <h1>Merge or Upload PDF Files</h1>
          <p>
            You can upload a single PDF file or select multiple files to merge into one document.
          </p>

          {/* Flash / Custom Message */}
          {message && <p className="message">{message}</p>}

          {/* Upload / Merge Form */}
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="form-group">
              <label htmlFor="files">Select PDF file(s):</label>
              <input
                type="file"
                id="files"
                name="files"
                multiple
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                required={selectedLocalFiles.length === 0}
              />
              <small>(Select one or more PDF files to upload/merge)</small>

              {/* Selected Local Files List */}
              {selectedLocalFiles.length > 0 && (
                <div className="local-selected-files">
                  <p className="local-files-title">Selected files to upload ({selectedLocalFiles.length}):</p>
                  <ul className="local-files-list">
                    {selectedLocalFiles.map((file, idx) => (
                      <li key={`${file.name}-${idx}`} className="local-file-item">
                        <span className="local-file-name">{file.name}</span>
                        <button
                          type="button"
                          className="remove-local-btn"
                          onClick={() => handleRemoveLocalFile(idx)}
                          title="Remove file from selection"
                        >
                          ✕ Remove
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="merged_filename">Enter name for merged/single file:</label>
              <input
                type="text"
                id="merged_filename"
                name="merged_filename"
                placeholder="output.pdf"
                value={mergedFilename}
                onChange={(e) => setMergedFilename(e.target.value)}
              />
            </div>

            <button type="submit" className="merge-btn">
              Upload / Merge PDFs
            </button>
          </form>

          {/* Merged / Uploaded Files Section */}
          <div className="merged-files-section">
            <h2>Uploaded / Merged Files (Temporary Folder)</h2>
            <hr />

            {files.length > 0 ? (
              <>
                {/* Select All & Action Bar */}
                <div className="files-action-bar">
                  <label className="select-all-label">
                    <input
                      type="checkbox"
                      onChange={handleSelectAll}
                      checked={
                        files.length > 0 && selectedUploadedFiles.length === files.length
                      }
                    />
                    Select All ({selectedUploadedFiles.length}/{files.length})
                  </label>

                  {selectedUploadedFiles.length > 0 && (
                    <button
                      type="button"
                      className="btn-delete-selected"
                      onClick={requestDeleteSelected}
                    >
                      Delete Selected ({selectedUploadedFiles.length})
                    </button>
                  )}
                </div>

                <div className="file-list">
                  {files.map((file) => (
                    <div
                      className={`file-card ${
                        selectedUploadedFiles.includes(file) ? "selected-card" : ""
                      }`}
                      key={file}
                    >
                      <input
                        type="checkbox"
                        className="file-checkbox"
                        checked={selectedUploadedFiles.includes(file)}
                        onChange={() => handleToggleSelectFile(file)}
                      />
                      <img src="/download.png" alt="File Icon" className="file-icon" />
                      <span className="file-name">{file}</span>

                      {/* Action buttons inside file card */}
                      <div className="file-actions">
                        {/* Download Button */}
                        <a
                          className="btn btn--primary download-link-btn"
                          href={apiService.getDownloadUrl(file)}
                          download={file}
                        >
                          Download
                        </a>

                        {/* Delete Button for single file */}
                        <button
                          type="button"
                          className="delete-btn"
                          onClick={(e) => requestDelete(file, e)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

              </>
            ) : (
              <p className="no-files">
                No files in upload folder. Upload or merge PDFs to see them here.
              </p>
            )}

            {/* Continue Button */}
            <div className="button-group">
              <button
                onClick={handleContinue}
                id="continueEvaluationBtn"
                className="btn btn--primary"
              >
                Continue to Evaluation
              </button>
            </div>
          </div>

          {/* Back to Home */}
          <Link to="/" className="back-link">
            ← Back to Home
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Merge;

