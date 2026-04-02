/**
 * HITLReviewModal — three-button decision modal for HITL reviews.
 *
 * Three actions:
 *   Approve     — requires a comment; sends decision:"approved" + comment
 *   Proceed     — no comment required; sends decision:"approved" + null
 *   Reject      — requires a comment; sends decision:"rejected" + comment
 *
 * Coding Standard 6: split into renderOutput(), HITLCommentSection,
 * HITLActionBar, and HITLReviewModal so each function stays under 50 lines.
 * Coding Standard 5: Approve/Reject buttons are disabled (not just guarded)
 * when comment is empty, giving clear visual feedback before submission.
 */
import React, { useState } from "react";
import type { HITLReview } from "../../types/index";

export interface HITLReviewModalProps {
  review: HITLReview | null;
  isOpen: boolean;
  isSubmitting: boolean;
  onApprove: (reviewId: string, comment: string) => Promise<void>;
  onReject: (reviewId: string, comment: string) => Promise<void>;
  onProceed: (reviewId: string) => Promise<void>;
  onClose: () => void;
}

function renderOutput(review: HITLReview): JSX.Element {
  const raw = review.output_to_review;
  const outputVal = raw["output"];
  if (typeof outputVal === "string") {
    return <p style={{ margin: 0, lineHeight: 1.6 }}>{outputVal}</p>;
  }
  // Fallback: always render something — never show empty output
  return (
    <pre
      style={{
        margin: 0,
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
        fontSize: "0.8rem",
      }}
    >
      {JSON.stringify(raw, null, 2)}
    </pre>
  );
}

interface HITLCommentSectionProps {
  comment: string;
  onChange: (val: string) => void;
  showError: boolean;
  disabled: boolean;
}

function HITLCommentSection(props: HITLCommentSectionProps): JSX.Element {
  const { comment, onChange, showError, disabled } = props;
  return (
    <div>
      <label
        style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.4rem" }}
      >
        Comments
      </label>
      <textarea
        value={comment}
        onChange={(e) => onChange(e.target.value)}
        maxLength={2000}
        rows={4}
        disabled={disabled}
        style={{
          width: "100%",
          background: "#0d0d1a",
          border: "1px solid #0f3460",
          color: "#e0e0e0",
          borderRadius: 4,
          padding: "0.5rem",
          resize: "vertical",
          boxSizing: "border-box",
        }}
      />
      {showError && (
        <p
          style={{ margin: "0.25rem 0 0", color: "#ff6b6b", fontSize: "0.8rem" }}
        >
          Comment is required
        </p>
      )}
    </div>
  );
}

interface HITLActionBarProps {
  commentEmpty: boolean;
  isSubmitting: boolean;
  onProceed: () => void;
  onReject: () => void;
  onApprove: () => void;
}

interface HITLModalHeaderProps {
  reviewId: string;
  isSubmitting: boolean;
  onClose: () => void;
}

function HITLModalHeader({ reviewId, isSubmitting, onClose }: HITLModalHeaderProps): JSX.Element {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <h2 style={{ margin: 0, fontSize: "1rem" }}>Review: {reviewId.slice(0, 8)}…</h2>
      <button onClick={onClose} disabled={isSubmitting} style={closeBtnStyle}>✕</button>
    </div>
  );
}

interface HITLOutputSectionProps {
  review: HITLReview;
}

function HITLOutputSection({ review }: HITLOutputSectionProps): JSX.Element {
  return (
    <div>
      <p style={{ margin: "0 0 0.5rem", fontSize: "0.8rem", opacity: 0.6 }}>
        Agent output
      </p>
      <div
        style={{
          background: "#0d0d1a",
          borderRadius: 4,
          padding: "0.75rem",
          maxHeight: 200,
          overflowY: "auto",
        }}
      >
        {renderOutput(review)}
      </div>
    </div>
  );
}

function HITLActionBar(props: HITLActionBarProps): JSX.Element {
  const { commentEmpty, isSubmitting, onProceed, onReject, onApprove } = props;
  return (
    <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
      <button
        onClick={onProceed}
        disabled={isSubmitting}
        style={{ ...actionBtnStyle, background: "#4dabf7" }}
      >
        Proceed as-is
      </button>
      <button
        onClick={onReject}
        disabled={commentEmpty || isSubmitting}
        style={{ ...actionBtnStyle, background: "#ff6b6b" }}
      >
        Reject
      </button>
      <button
        onClick={onApprove}
        disabled={commentEmpty || isSubmitting}
        style={{ ...actionBtnStyle, background: "#69db7c" }}
      >
        Approve
      </button>
    </div>
  );
}

interface HITLModalShellProps {
  review: HITLReview;
  isSubmitting: boolean;
  comment: string;
  commentEmpty: boolean;
  showCommentError: boolean;
  onClose: () => void;
  onCommentChange: (val: string) => void;
  onProceed: () => void;
  onReject: () => void;
  onApprove: () => void;
}

function HITLModalShell(props: HITLModalShellProps): JSX.Element {
  const { review, isSubmitting, comment, commentEmpty, showCommentError } = props;
  const { onClose, onCommentChange, onProceed, onReject, onApprove } = props;
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(26,26,46,0.92)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "#16213e", border: "1px solid #0f3460", borderRadius: 8, padding: "1.5rem", width: "min(600px, 90vw)", color: "#e0e0e0", display: "flex", flexDirection: "column", gap: "1rem" }}>
        <HITLModalHeader reviewId={review.id} isSubmitting={isSubmitting} onClose={onClose} />
        <HITLOutputSection review={review} />
        <HITLCommentSection comment={comment} onChange={onCommentChange} showError={showCommentError} disabled={isSubmitting} />
        <HITLActionBar commentEmpty={commentEmpty} isSubmitting={isSubmitting} onProceed={onProceed} onReject={onReject} onApprove={onApprove} />
      </div>
    </div>
  );
}

export function HITLReviewModal(props: HITLReviewModalProps): JSX.Element | null {
  const { review, isOpen, isSubmitting, onApprove, onReject, onProceed, onClose } = props;
  const [comment, setComment] = useState("");
  const [showCommentError, setShowCommentError] = useState(false);

  if (!isOpen || review === null) return null;

  const commentEmpty = comment.trim() === "";

  async function handleApproveClick(): Promise<void> {
    if (commentEmpty) { setShowCommentError(true); return; }
    setShowCommentError(false);
    await onApprove(review.id, comment);
  }

  async function handleRejectClick(): Promise<void> {
    if (commentEmpty) { setShowCommentError(true); return; }
    setShowCommentError(false);
    await onReject(review.id, comment);
  }

  async function handleProceedClick(): Promise<void> { await onProceed(review.id); }

  return (
    <HITLModalShell
      review={review}
      isSubmitting={isSubmitting}
      comment={comment}
      commentEmpty={commentEmpty}
      showCommentError={showCommentError}
      onClose={onClose}
      onCommentChange={setComment}
      onProceed={() => { void handleProceedClick(); }}
      onReject={() => { void handleRejectClick(); }}
      onApprove={() => { void handleApproveClick(); }}
    />
  );
}

const closeBtnStyle: React.CSSProperties = {
  background: "transparent",
  border: "none",
  color: "#e0e0e0",
  cursor: "pointer",
  fontSize: "1rem",
  padding: "0.25rem",
};

const actionBtnStyle: React.CSSProperties = {
  border: "none",
  borderRadius: 4,
  color: "#1a1a2e",
  cursor: "pointer",
  fontWeight: 700,
  padding: "0.5rem 1.25rem",
};

export default HITLReviewModal;
