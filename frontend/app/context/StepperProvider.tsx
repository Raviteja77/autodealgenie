"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  ReactNode,
  useMemo,
} from "react";
import { usePathname, useRouter } from "next/navigation";

/**
 * Step definition interface
 */
export interface Step {
  id: number;
  label: string;
  path: string;
  requiresPrevious: boolean;
}

/**
 * Default steps configuration matching the application flow
 */
export const STEPS: Step[] = [
  {
    id: 0,
    label: "Search",
    path: "/dashboard/search",
    requiresPrevious: false,
  },
  {
    id: 1,
    label: "Results",
    path: "/dashboard/results",
    requiresPrevious: true,
  },
  {
    id: 2,
    label: "Evaluate",
    path: "/dashboard/evaluation",
    requiresPrevious: true,
  },
  {
    id: 3,
    label: "Negotiate",
    path: "/dashboard/negotiation",
    requiresPrevious: true,
  },
  // { id: 4, label: "Finalize", path: "/deals", requiresPrevious: true },
];

/**
 * Paths where stepper should be hidden
 */
const STEPPER_HIDDEN_PATHS = [
  "/dashboard/favorites",
  "/deals",
  "/dashboard/profile",
  "/dashboard/settings",
];

/**
 * Stepper state interface
 */
interface StepperState {
  currentStep: number;
  completedSteps: Set<number>;
  stepData: Record<number, unknown>;
  isNavigating: boolean;
}

/**
 * Stepper context interface
 */
interface StepperContextType {
  state: StepperState;
  steps: Step[];
  currentStep: number;
  completedSteps: Set<number>;
  isStepCompleted: (stepId: number) => boolean;
  canNavigateToStep: (stepId: number) => boolean;
  completeStep: (stepId: number, data?: unknown) => void;
  navigateToStep: (stepId: number) => void;
  getStepData: <T = unknown>(stepId: number) => T | undefined;
  setStepData: (stepId: number, data: unknown) => void;
  resetStepper: () => void;
  goToNextStep: () => void;
  goToPreviousStep: () => void;
  shouldShowStepper: () => boolean; // NEW: Function to determine if stepper should be shown
  isStepperPath: (path: string) => boolean; // NEW: Check if path is a stepper path
}

const StepperContext = createContext<StepperContextType | undefined>(undefined);

/**
 * Storage keys for persistence
 */
const STORAGE_KEY_COMPLETED = "stepper_completed_steps";
const STORAGE_KEY_DATA = "stepper_step_data";
const STORAGE_KEY_CURRENT = "stepper_current_step";

/**
 * Initial stepper state
 */
const initialState: StepperState = {
  currentStep: 0,
  completedSteps: new Set<number>(),
  stepData: {},
  isNavigating: false,
};

/**
 * Get the step ID from a pathname
 */
function getStepIdFromPath(pathname: string): number {
  const step = STEPS.find((s) => pathname.startsWith(s.path));
  return step?.id ?? 0;
}

/**
 * Check if a path should show the stepper
 */
function shouldShowStepperForPath(pathname: string): boolean {
  // Check if path is in the hidden paths list
  if (
    STEPPER_HIDDEN_PATHS.some((hiddenPath) => pathname.startsWith(hiddenPath))
  ) {
    return false;
  }

  // Check if path is one of the stepper steps
  return STEPS.some((step) => pathname.startsWith(step.path));
}

/**
 * Load persisted state from sessionStorage
 */
function loadPersistedState(): Partial<StepperState> {
  if (typeof window === "undefined") return {};

  try {
    const completedStepsJson = sessionStorage.getItem(STORAGE_KEY_COMPLETED);
    const stepDataJson = sessionStorage.getItem(STORAGE_KEY_DATA);
    const currentStepJson = sessionStorage.getItem(STORAGE_KEY_CURRENT);

    return {
      completedSteps: completedStepsJson
        ? new Set(JSON.parse(completedStepsJson))
        : new Set<number>(),
      stepData: stepDataJson ? JSON.parse(stepDataJson) : {},
      currentStep: currentStepJson ? parseInt(currentStepJson, 10) : 0,
    };
  } catch (error) {
    console.error("Error loading persisted stepper state:", error);
    return {};
  }
}

/**
 * Persist state to sessionStorage
 */
function persistState(state: StepperState): void {
  if (typeof window === "undefined") return;

  try {
    sessionStorage.setItem(
      STORAGE_KEY_COMPLETED,
      JSON.stringify(Array.from(state.completedSteps))
    );
    sessionStorage.setItem(STORAGE_KEY_DATA, JSON.stringify(state.stepData));
    sessionStorage.setItem(STORAGE_KEY_CURRENT, state.currentStep.toString());
  } catch (error) {
    console.error("Error persisting stepper state:", error);
  }
}

/**
 * StepperProvider component for managing navigation state
 */
export function StepperProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  // Initialize state with persisted data
  const [state, setState] = useState<StepperState>(() => {
    const persistedState = loadPersistedState();
    return {
      ...initialState,
      ...persistedState,
      currentStep: getStepIdFromPath(pathname),
    };
  });

  /**
   * Sync current step with pathname changes
   */
  useEffect(() => {
    const stepId = getStepIdFromPath(pathname);
    if (stepId !== state.currentStep) {
      setState((prev) => ({
        ...prev,
        currentStep: stepId,
      }));
    }
  }, [pathname, state.currentStep]);

  /**
   * Persist state changes to sessionStorage
   */
  useEffect(() => {
    persistState(state);
  }, [state]);

  /**
   * Check if a step is completed
   */
  const isStepCompleted = useCallback(
    (stepId: number): boolean => {
      return state.completedSteps.has(stepId);
    },
    [state.completedSteps]
  );

  /**
   * Check if navigation to a step is allowed
   */
  const canNavigateToStep = useCallback(
    (stepId: number): boolean => {
      const targetStep = STEPS.find((s) => s.id === stepId);
      if (!targetStep) return false;

      if (state.completedSteps.has(stepId)) return true;
      if (stepId === state.currentStep) return true;

      if (targetStep.requiresPrevious && stepId > 0) {
        const previousStepCompleted = state.completedSteps.has(stepId - 1);
        return previousStepCompleted;
      }

      return stepId === 0;
    },
    [state.completedSteps, state.currentStep]
  );

  /**
   * Mark a step as completed and optionally store data
   */
  const completeStep = useCallback((stepId: number, data?: unknown) => {
    setState((prev) => {
      const newCompletedSteps = new Set(prev.completedSteps);
      newCompletedSteps.add(stepId);

      return {
        ...prev,
        completedSteps: newCompletedSteps,
        stepData: data ? { ...prev.stepData, [stepId]: data } : prev.stepData,
      };
    });
  }, []);

  /**
   * Navigate to a specific step with validation
   */
  const navigateToStep = useCallback(
    (stepId: number) => {
      if (!canNavigateToStep(stepId)) {
        console.warn(
          `Cannot navigate to step ${stepId}. Complete prerequisite steps first.`
        );
        return;
      }

      const targetStep = STEPS.find((s) => s.id === stepId);
      if (targetStep) {
        setState((prev) => ({ ...prev, isNavigating: true }));
        router.push(targetStep.path);
        setTimeout(() => {
          setState((prev) => ({ ...prev, isNavigating: false }));
        }, 100);
      }
    },
    [canNavigateToStep, router]
  );

  /**
   * Get data stored for a specific step
   */
  const getStepData = useCallback(
    <T = unknown,>(stepId: number): T | undefined => {
      return state.stepData[stepId] as T | undefined;
    },
    [state.stepData]
  );

  /**
   * Set data for a specific step
   */
  const setStepData = useCallback((stepId: number, data: unknown) => {
    setState((prev) => ({
      ...prev,
      stepData: { ...prev.stepData, [stepId]: data },
    }));
  }, []);

  /**
   * Reset stepper to initial state
   */
  const resetStepper = useCallback(() => {
    setState(initialState);
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(STORAGE_KEY_COMPLETED);
      sessionStorage.removeItem(STORAGE_KEY_DATA);
      sessionStorage.removeItem(STORAGE_KEY_CURRENT);
    }
  }, []);

  /**
   * Navigate to the next step
   */
  const goToNextStep = useCallback(() => {
    const nextStepId = state.currentStep + 1;
    if (nextStepId < STEPS.length) {
      navigateToStep(nextStepId);
    }
  }, [state.currentStep, navigateToStep]);

  /**
   * Navigate to the previous step
   */
  const goToPreviousStep = useCallback(() => {
    const prevStepId = state.currentStep - 1;
    if (prevStepId >= 0) {
      navigateToStep(prevStepId);
    }
  }, [state.currentStep, navigateToStep]);

  /**
   * NEW: Determine if stepper should be shown based on current path
   */
  const shouldShowStepper = useCallback(() => {
    return shouldShowStepperForPath(pathname);
  }, [pathname]);

  /**
   * NEW: Check if a given path is a stepper path
   */
  const isStepperPath = useCallback((path: string) => {
    return STEPS.some((step) => path.startsWith(step.path));
  }, []);

  // {
    /* const contextValue: StepperContextType = {
    state,
    steps: STEPS,
    currentStep: state.currentStep,
    completedSteps: state.completedSteps,
    isStepCompleted,
    canNavigateToStep,
    completeStep,
    navigateToStep,
    getStepData,
    setStepData,
    resetStepper,
    goToNextStep,
    goToPreviousStep,
    shouldShowStepper,
    isStepperPath,
  }; */
  // }
  const contextValue: StepperContextType = useMemo(
    () => ({
      state,
      steps: STEPS,
      currentStep: state.currentStep,
      completedSteps: state.completedSteps,
      isStepCompleted,
      canNavigateToStep,
      completeStep,
      navigateToStep,
      getStepData,
      setStepData,
      resetStepper,
      goToNextStep,
      goToPreviousStep,
      shouldShowStepper,
      isStepperPath,
    }),
    [
      state,
      isStepCompleted,
      canNavigateToStep,
      completeStep,
      navigateToStep,
      getStepData,
      setStepData,
      resetStepper,
      goToNextStep,
      goToPreviousStep,
      shouldShowStepper,
      isStepperPath,
    ]
  );

  return (
    <StepperContext.Provider value={contextValue}>
      {children}
    </StepperContext.Provider>
  );
}

/**
 * Hook to use the stepper context
 */
export function useStepper() {
  const context = useContext(StepperContext);
  if (context === undefined) {
    throw new Error("useStepper must be used within a StepperProvider");
  }
  return context;
}

export type { StepperState, StepperContextType };
