import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import Header from "../../components/layout/Header";
import { apiService } from "../../services/api";
import "./Evaluation.css";

export const Evaluation = () => {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("not_started"); // not_started, running_eval, running_udyam, success_eval, success_udyam, failed_eval, failed_udyam, error_eval, error_udyam
  const [timerVal, setTimerVal] = useState("00:00");
  const [googleSheetsUrl, setGoogleSheetsUrl] = useState("https://docs.google.com/spreadsheets/d/1wkYCypcvEWqS1Uz-zOfoIpR9gdNjDoktTm50jc-eTL0/edit?usp=sharing");
  
  const timerIntervalRef = useRef(null);
  const finalTimeRef = useRef("00:00");

  const location = useLocation();
  const { autoStart, targetFiles } = location.state || {};

  useEffect(() => {
    // Fetch uploaded files list on mount
    apiService.getFiles().then((data) => {
      setFiles(data.files || []);
    }).catch((err) => {
      console.error("Failed to fetch files on mount:", err);
    });

    // Cleanup timer on unmount
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (autoStart && targetFiles && targetFiles.length > 0) {
      handleStartEvaluation(targetFiles);
      // Clear history state to prevent re-trigger on reload
      window.history.replaceState({}, document.title);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart]);

  const startTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }
    setTimerVal("00:00");
    let seconds = 0;
    
    timerIntervalRef.current = setInterval(() => {
      seconds++;
      const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
      const secs = (seconds % 60).toString().padStart(2, '0');
      const timeStr = `${mins}:${secs}`;
      setTimerVal(timeStr);
      finalTimeRef.current = timeStr;
    }, 1000);
  };

  const stopTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  };

  const handleStartEvaluation = async (filesToRun) => {
    const target = (filesToRun && Array.isArray(filesToRun)) ? filesToRun : files;
    if (!target || target.length === 0) {
      alert("No files available for evaluation.");
      return;
    }

    setStatus("running_eval");
    startTimer();

    try {
      // Call backend to trigger n8n evaluation workflow
      const result = await apiService.startEvaluation(target);
      stopTimer();

      if (result.success) {
        setStatus("success_eval");
        if (result.google_sheets_url) {
          setGoogleSheetsUrl(result.google_sheets_url);
        }
        
        // Redirect to Google Sheets after 5 seconds, preserving original flow
        setTimeout(() => {
          window.location.href = result.google_sheets_url || googleSheetsUrl;
        }, 5000);
      } else {
        setStatus("failed_eval");
      }
    } catch (err) {
      console.error("Evaluation error:", err);
      stopTimer();
      setStatus("error_eval");
    }
  };



  return (
    <div className="evaluation-page-container">
      {/* Header */}
      <Header />

      {/* Main Section */}
      <main className="hero-center">
        <div className="hero-content">
          <h1>Workflow Status</h1>

          {/* Status Area */}
          {status === "not_started" && (
            <div className="status-message warning">
              <p>⚠️ Workflow not started yet.</p>
            </div>
          )}

          {status === "running_eval" && (
            <div className="status-message warning">
              <p>
                <span className="rotate">⏳</span> Evaluation started... Please wait.
              </p>
              <p>Elapsed Time: <span className="timer">{timerVal}</span></p>
            </div>
          )}

          {status === "success_eval" && (
            <div className="status-message success">
              <p>✅ Evaluation Completed Successfully!</p>
              <p className="time-info">Time taken: {finalTimeRef.current}</p>
              <p>Redirecting to report...</p>
            </div>
          )}

          {status === "failed_eval" && (
            <div className="status-message warning">
              <p>⚠️ Evaluation failed. Check console.</p>
              <p className="time-info">Time taken: {finalTimeRef.current}</p>
            </div>
          )}

          {status === "error_eval" && (
            <div className="status-message warning">
              <p>❌ Error: Unable to reach server.</p>
              <p className="time-info">Check your connection.</p>
            </div>
          )}



          {/* Back Link */}
          <Link to="/merge" className="back-link">
            ← Back
          </Link>
        </div>
      </main>
    </div>
  );
};

export default Evaluation;
