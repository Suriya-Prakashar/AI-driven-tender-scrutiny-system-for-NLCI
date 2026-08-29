import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../components/layout/Header";
import { apiService } from "../../services/api";
import "./Home.css";

export const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Clear temporary uploaded and merged files on home load, preserving original flow
    apiService.clearFiles().catch((err) => {
      console.error("Failed to clear files on mount:", err);
    });
  }, []);

  const handleStartMerge = (e) => {
    e.preventDefault();
    navigate("/merge");
  };

  return (
    <div className="home-page-container">
      <Header />

      {/* Centered hero container */}
      <section className="hero-center">
        <div className="hero-content">
          <h1>Welcome to File Merge Workflow</h1>
          <form onSubmit={handleStartMerge} className="actions">
            <button type="submit">Merge File</button>
          </form>
        </div>
      </section>

      {/* Cards section */}
      <section className="footer">
        <div className="cards-section">
          <div className="cards">
            <article className="card">
              <img
                src="https://img.icons8.com/ios/100/00a693/company.png"
                alt="Company Icon"
                width="50"
                height="50"
              />
              <h3>About MMC</h3>
              <p>
                NLCIL Material Management Complex efficiently handles procurement,
                inventory, logistics, and supply chain operations supporting
                lignite mining and power generation.
              </p>
            </article>

            <article className="card">
              <img
                src="https://img.icons8.com/ios/100/00a693/services.png"
                alt="Services Icon"
                width="50"
                height="50"
              />
              <h3>About Project</h3>
              <p>
                Our project streamlines tender document evaluation, merging PDFs,
                tracking workflow status, and simplifying file management with an
                intuitive, elegant interface.
              </p>
            </article>

            <article className="card">
              <img
                src="https://img.icons8.com/ios/100/00a693/portfolio.png"
                alt="Portfolio Icon"
                width="50"
                height="50"
              />
              <h3>Credit</h3>
              <p>
                This project was proudly developed by the students of Jeppiaar
                Engineering College for NLCIL, Material Management Complex, as
                part of our academic endeavor to integrate innovation with
                industrial excellence.
              </p>
            </article>
          </div>
        </div>
      </section>

      {/* Footer note */}
      <div className="footer-note">
        <p>
          © 2025 Tender Document Evaluation Utility |{" "}
          <a
            href="https://youtu.be/xvFZjo5PgG0?si=sER4bvcxkh6xolrm"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "rgb(255, 255, 255)", textDecoration: "none" }}
          >
            Designed for NLC Team
          </a>
        </p>
      </div>
    </div>
  );
};

export default Home;
