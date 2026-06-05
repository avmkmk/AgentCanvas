/**
 * AgentCanvas — application entry point.
 *
 * React 18 createRoot API.
 * StrictMode is enabled to surface potential issues during development.
 * Coding Standard 2: no resource leaks — React handles root cleanup.
 * AuthProvider wraps the app to enforce Keycloak PKCE login before rendering.
 */
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import { AuthProvider } from "./auth/AuthProvider.tsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
);
