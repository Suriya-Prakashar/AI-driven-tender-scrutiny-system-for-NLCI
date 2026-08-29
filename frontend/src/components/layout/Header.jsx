import React from "react";
import "./Header.css";

export const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <img src="/nlc.jpg" alt="Organization Logo" className="logo" />
        <h1 className="title">Tender Document Evaluation Utility</h1>
      </div>
    </header>
  );
};

export default Header;
