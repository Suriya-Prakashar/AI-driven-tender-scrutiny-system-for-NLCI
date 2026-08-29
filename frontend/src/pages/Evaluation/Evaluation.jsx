import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Header from "../../components/layout/Header";
import { apiService } from "../../services/api";
import "./Evaluation.css";

export const Evaluation = () => {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("not_started"); // not_started, running_eval, running_udyam, success_eval, success_udyam, failed_eval, failed_udyam, error_eval, error_udyam
  const [timerVal, setTimerVal] = useState("00:00");
  const [buttonsDisabled, setButtonsDisabled] = useState(false);
  const [googleSheetsUrl, setGoogleSheetsUrl] = useState("https://docs.google.com/spreadsheets/d/1wkYCypcvEWqS1Uz-zOfoIpR9gdNjDoktTm50jc-eTL0/edit?usp=sharing");
  
  const timerIntervalRef = useRef(null);
  const finalTimeRef = useRef("00:00");

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

  const handleStartEvaluation = async () => {
    setButtonsDisabled(true);
    setStatus("running_eval");
    startTimer();

    try {
      // Call backend to trigger n8n evaluation workflow
      const result = await apiService.startEvaluation(files);
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
    } finally {
      setButtonsDisabled(false);
    }
  };

  const handleStartUdyam = async () => {
    setButtonsDisabled(true);
    setStatus("running_udyam");
    startTimer();

    try {
      // Call backend to trigger Udyam verification
      const result = await apiService.verifyUdyam("webhook", files);
      stopTimer();

      if (result.success) {
        setStatus("success_udyam");
      } else {
        setStatus("failed_udyam");
      }
    } catch (err) {
      console.error("Udyam error:", err);
      stopTimer();
      setStatus("error_udyam");
    } finally {
      setButtonsDisabled(false);
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

          {status === "running_udyam" && (
            <div className="status-message warning">
              <p>
                <span className="rotate">⏳</span> Udyam Verification started... Please
                wait.
              </p>
              <p>Elapsed Time: <span className="timer">{timerVal}</span></p>
            </div>
          )}

          {status === "success_udyam" && (
            <div className="status-message success">
              <p>✅ Udyam Verification Completed!</p>
              <p className="time-info">Time taken: {finalTimeRef.current}</p>
            </div>
          )}

          {status === "failed_udyam" && (
            <div className="status-message warning">
              <p>⚠️ Udyam process failed. Check console.</p>
              <p className="time-info">Time taken: {finalTimeRef.current}</p>
            </div>
          )}

          {status === "error_udyam" && (
            <div className="status-message warning">
              <p>❌ Error: Unable to reach Udyam server.</p>
              <p className="time-info">Check your connection.</p>
            </div>
          )}

          {/* Buttons */}
          <div className="button-group">
            <button
              onClick={handleStartEvaluation}
              disabled={buttonsDisabled}
              className="btn btn--primary"
            >
              {status === "running_eval" ? "Running..." : "Start Evaluation"}
            </button>
            <button
              onClick={handleStartUdyam}
              disabled={buttonsDisabled}
              className="btn btn--secondary"
            >
              {status === "running_udyam" ? "Running..." : "Udyam Verification"}
            </button>
          </div>

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
