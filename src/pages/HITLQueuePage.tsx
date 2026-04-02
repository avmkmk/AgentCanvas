/**
 * HITLQueuePage — lists pending HITL reviews at route /hitl.
 *
 * FE-13, FE-14: uses useHitl hook; owns selectedReview state.
 * Initial data fetch is triggered by useHitl's internal useEffect.
 * Polling is owned by App.tsx — this page does NOT start/stop polling.
 * reviewed_by is intentionally omitted in all payloads — no auth context in MVP.
 *
 * Coding Standard 6: one component, one job — table rendering extracted to HITLReviewTable.
 * Coding Standard 5: all submitDecision calls wrapped in try/catch.
 */
import React, { useState } from "react";
import { HITLReviewModal } from "../components/hitl/HITLReviewModal";
import { useHitl } from "../hooks/useHitl";
import type { HITLDecisionRequest, HITLReview } from "../types/index";

// ─── HITLReviewTable ──────────────────────────────────────────────────────────

interface HITLReviewTableProps {
  pendingReviews: HITLReview[];
  onReview: (review: HITLReview) => void;
}

function HITLReviewTable({ pendingReviews, onReview }: HITLReviewTableProps): JSX.Element {
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
      <thead>
        <tr style={{ background: "#1a1a2e", textAlign: "left" }}>
          {["Review ID", "Agent ID", "Gate Type", "Created At", "Action"].map((h) => (
            <th key={h} style={thStyle}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {pendingReviews.map((review) => (
          <tr
            key={review.id}
            style={{ background: "#16213e", borderBottom: "1px solid #0f3460" }}
          >
            <td style={tdStyle}>{review.id.slice(0, 8)}…</td>
            <td style={tdStyle}>
              {review.agent_id !== null ? review.agent_id.slice(0, 8) + "…" : "—"}
            </td>
            <td style={tdStyle}>{review.gate_type}</td>
            <td style={tdStyle}>{new Date(review.created_at).toLocaleString()}</td>
            <td style={tdStyle}>
              <button onClick={() => onReview(review)} style={reviewBtnStyle}>
                Review
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ─── HITLQueuePage ────────────────────────────────────────────────────────────

function HITLQueuePage(): JSX.Element {
  const { pendingReviews, isLoading, isSubmitting, error, submitDecision } = useHitl();
  const [selectedReview, setSelectedReview] = useState<HITLReview | null>(null);

  async function handleApprove(reviewId: string, comment: string): Promise<void> {
    const payload: HITLDecisionRequest = { decision: "approved", reviewer_comments: comment };
    try {
      await submitDecision(reviewId, payload);
      setSelectedReview(null);
    } catch {
      // error already set in store — displayed below heading
    }
  }

  async function handleReject(reviewId: string, comment: string): Promise<void> {
    const payload: HITLDecisionRequest = { decision: "rejected", reviewer_comments: comment };
    try {
      await submitDecision(reviewId, payload);
      setSelectedReview(null);
    } catch {
      // error already set in store
    }
  }

  async function handleProceed(reviewId: string): Promise<void> {
    const payload: HITLDecisionRequest = { decision: "approved", reviewer_comments: null };
    try {
      await submitDecision(reviewId, payload);
      setSelectedReview(null);
    } catch {
      // error already set in store
    }
  }

  return (
    <div style={{ padding: "2rem", color: "#e0e0e0" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>HITL Review Queue</h1>

      {error !== null && (
        <p style={{ color: "#ff6b6b", marginBottom: "1rem" }}>{error}</p>
      )}

      {isLoading && pendingReviews.length === 0 && (
        <p style={{ opacity: 0.5 }}>Loading reviews…</p>
      )}

      {!isLoading && pendingReviews.length === 0 && (
        <p style={{ opacity: 0.5 }}>No pending reviews</p>
      )}

      {pendingReviews.length > 0 && (
        <HITLReviewTable
          pendingReviews={pendingReviews}
          onReview={setSelectedReview}
        />
      )}

      <HITLReviewModal
        review={selectedReview}
        isOpen={selectedReview !== null}
        isSubmitting={isSubmitting}
        onApprove={handleApprove}
        onReject={handleReject}
        onProceed={handleProceed}
        onClose={() => setSelectedReview(null)}
      />
    </div>
  );
}

// ─── Style constants ──────────────────────────────────────────────────────────

const thStyle: React.CSSProperties = {
  padding: "0.6rem 1rem",
  fontWeight: 600,
  opacity: 0.7,
};

const tdStyle: React.CSSProperties = { padding: "0.6rem 1rem" };

const reviewBtnStyle: React.CSSProperties = {
  background: "#4dabf7",
  border: "none",
  borderRadius: 4,
  color: "#1a1a2e",
  cursor: "pointer",
  fontWeight: 700,
  padding: "0.3rem 0.9rem",
};

export default HITLQueuePage;
