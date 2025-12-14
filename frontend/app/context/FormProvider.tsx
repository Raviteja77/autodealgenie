"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { z } from "zod";

/**
 * Zod schema for general form validation
 */
export const FormSchema = z.object({
  email: z.string().email("Invalid email address"),
  name: z.string().min(1, "Name is required").max(255, "Name is too long"),
  phone: z.string().optional(),
  message: z
    .string()
    .min(1, "Message is required")
    .max(1000, "Message is too long"),
});

export type FormData = z.infer<typeof FormSchema>;

/**
 * Form state interface
 */
interface FormState {
  data: Partial<FormData>;
  errors: Record<string, string>;
  isSubmitting: boolean;
  isValid: boolean;
}

/**
 * Form context interface
 */
interface FormContextType {
  state: FormState;
  updateField: (field: keyof FormData, value: string) => void;
  validateField: (field: keyof FormData) => boolean;
  validateForm: () => boolean;
  resetForm: () => void;
  submitForm: (onSubmit: (data: FormData) => Promise<void>) => Promise<void>;
  setFormData: (data: Partial<FormData>) => void;
}

const FormContext = createContext<FormContextType | undefined>(undefined);

/**
 * Initial form state
 */
const initialState: FormState = {
  data: {},
  errors: {},
  isSubmitting: false,
  isValid: false,
};

/**
 * FormProvider component for managing general form state
 * Provides form state management, validation using Zod, and submission handling
 */
export function FormProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<FormState>(initialState);

  /**
   * Update a single field in the form
   */
  const updateField = useCallback((field: keyof FormData, value: string) => {
    setState((prev) => ({
      ...prev,
      data: { ...prev.data, [field]: value },
      errors: { ...prev.errors, [field]: "" }, // Clear error on update
    }));
  }, []);

  /**
   * Validate a single field using Zod
   */
  const validateField = useCallback(
    (field: keyof FormData): boolean => {
      try {
        const fieldSchema = FormSchema.shape[field];
        if (!fieldSchema) {
          return true; // Field doesn't exist in schema, skip validation
        }
        fieldSchema.parse(state.data[field]);
        setState((prev) => ({
          ...prev,
          errors: { ...prev.errors, [field]: "" },
        }));
        return true;
      } catch (error) {
        if (error instanceof z.ZodError) {
          const zodError = error as z.ZodError<FormData>;
          setState((prev) => ({
            ...prev,
            errors: {
              ...prev.errors,
              [field]: zodError.issues[0]?.message || "Invalid value",
            },
          }));
        }
        return false;
      }
    },
    [state.data],
  );

  /**
   * Validate the entire form using Zod
   */
  const validateForm = useCallback((): boolean => {
    try {
      FormSchema.parse(state.data);
      setState((prev) => ({ ...prev, errors: {}, isValid: true }));
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const zodError = error as z.ZodError<FormData>;
        const errors: Record<string, string> = {};
        zodError.issues.forEach((err: z.ZodIssue) => {
          if (err.path[0]) {
            errors[err.path[0].toString()] = err.message;
          }
        });
        setState((prev) => ({ ...prev, errors, isValid: false }));
      }
      return false;
    }
  }, [state.data]);

  /**
   * Reset the form to initial state
   */
  const resetForm = useCallback(() => {
    setState(initialState);
  }, []);

  /**
   * Submit the form with validation
   */
  const submitForm = useCallback(
    async (onSubmit: (data: FormData) => Promise<void>) => {
      if (!validateForm()) {
        return;
      }

      setState((prev) => ({ ...prev, isSubmitting: true }));

      try {
        await onSubmit(state.data as FormData);
        resetForm();
      } catch (error) {
        console.error("Form submission error:", error);
        throw error;
      } finally {
        setState((prev) => ({ ...prev, isSubmitting: false }));
      }
    },
    [state.data, validateForm, resetForm],
  );

  /**
   * Set multiple form fields at once
   */
  const setFormData = useCallback((data: Partial<FormData>) => {
    setState((prev) => ({
      ...prev,
      data: { ...prev.data, ...data },
    }));
  }, []);

  return (
    <FormContext.Provider
      value={{
        state,
        updateField,
        validateField,
        validateForm,
        resetForm,
        submitForm,
        setFormData,
      }}
    >
      {children}
    </FormContext.Provider>
  );
}

/**
 * Hook to use the form context
 * Must be used within a FormProvider
 */
export function useForm() {
  const context = useContext(FormContext);
  if (context === undefined) {
    throw new Error("useForm must be used within a FormProvider");
  }
  return context;
}

/**
 * Type exports for external use
 */
export type { FormState, FormContextType };
