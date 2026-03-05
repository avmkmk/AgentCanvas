/**
 * AgentCanvas — application entry point.
 *
 * React 18 createRoot API.
 * StrictMode is enabled to surface potential issues during development.
 * Coding Standard 2: no resource leaks — React handles root cleanup.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

const rootElement = document.getElementById("root");

// Guard: root element must exist — fail loudly at startup if HTML is misconfigured
if (rootElement === null) {
  throw new Error(
    "Root element #root not found in index.html. Cannot mount React app."
  );
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);
