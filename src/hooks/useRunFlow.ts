/**
 * useRunFlow — convenience hook for triggering a flow execution.
 *
 * FE-09: used by RunButton to start execution and surface loading/error state.
 * Coding Standard 6: one hook, one job — delegates all logic to executionStore.
 */
import { useExecutionStore } from "../store/executionStore";

export interface UseRunFlowResult {
  /** Start a new execution for the given flow. */
  run: () => void;
  /** True while the POST /executions request is in flight. */
  isStarting: boolean;
  /** Non-null when the last start attempt failed. */
  error: string | null;
  /** Status of the active execution, or undefined if none. */
  status: string | undefined;
}

export function useRunFlow(flowId: string): UseRunFlowResult {
  const startExecution = useExecutionStore((s) => s.startExecution);
  const isStarting = useExecutionStore((s) => s.isStarting);
  const error = useExecutionStore((s) => s.error);
  const activeExecution = useExecutionStore((s) => s.activeExecution);

  function run(): void {
    void startExecution({ flow_id: flowId, input_data: {} });
  }

  return {
    run,
    isStarting,
    error: error ?? null,
    status: activeExecution?.status,
  };
}
